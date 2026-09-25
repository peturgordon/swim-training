#!/usr/bin/env python3
"""
Foundational data structures for a HealthAutoExport "Pool Swim-*.json" export
(Apple Watch). Loads the raw JSON into pandas DataFrames, and builds the three
"objects" later visualization/analysis code is meant to sit on top of:

  Object 1 -- lap<->segment join (tag_lap_segments): one row per lap, tagged
    with the segment it falls inside (seg_idx) and that segment's total lap
    count (seg_laps). This is a containment test (lap.start >= segment.start
    and lap.end <= segment.end), not a native field -- nothing in the JSON
    links a lap to its segment directly.

  Object 2 -- segment table (segment_table): every raw per-segment field,
    unchanged, plus one derived column -- distance_m -- built from Object 1:
    group by seg_idx, count laps, multiply by the watch's own lapLength.
    Segments carry no distance/length field of their own in the JSON.

  Object 3 -- segment-gap heart rate (segment_gap_heart_rate): for each pair
    of time-consecutive segments, the raw HR samples falling in the rest
    window between them. A list of DataFrames, one per gap, each keeping its
    original index and columns untouched -- no re-basing to elapsed-since-
    gap-start, no filtering of near-zero-length gaps. len(result) ==
    len(segments) - 1.

Plus the raw heartRateData timeseries itself (heart_rate_df) -- the fourth
thing later work builds on.

Built on top of Object 3: segment_gap_recovery_curves (filter by duration,
re-reference each gap at its own peak HR, interpolate onto a common grid) and
aggregate_recovery_curves (stack, reduce to n/mean/std/min/max, truncate the
tail where too few gaps remain) -- the segment-gap HR recovery pipeline
prototyped as a one-off and then promoted here once it proved out.

This module has no visualization code and no CLI of its own; it's meant to be
imported. explore_pool_swim_json.py and swim_primitives.py both import their
loading/object-building functions from here rather than duplicating them.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd


def find_repo_root(start: Path) -> Path:
    for p in [start, *start.parents]:
        if (p / "biometrics").is_dir():
            return p
    raise SystemExit("Couldn't find repo root (looked for a biometrics/ folder)")


def newest_json(archives_dir: Path) -> Path:
    candidates = sorted(archives_dir.glob("Pool Swim-*.json"), key=lambda p: p.stat().st_mtime)
    if not candidates:
        raise SystemExit(f"No 'Pool Swim-*.json' files found in {archives_dir}")
    return candidates[-1]


def load_workout(path: Path) -> dict:
    with path.open() as f:
        data = json.load(f)
    return data["data"]["workouts"][0]


def hr_stats(entry: dict) -> dict:
    """Pulls avg/min/max HR out of a lap/segment's optional metrics block."""
    m = entry.get("metrics", {})
    return {
        "hr_avg": m.get("heartRateAverage", {}).get("qty"),
        "hr_min": m.get("heartRateMinimum", {}).get("qty"),
        "hr_max": m.get("heartRateMaximum", {}).get("qty"),
    }


def intervals_to_df(entries: list) -> pd.DataFrame:
    rows = []
    for e in entries:
        rows.append(
            {
                "index": e["index"],
                "start": pd.to_datetime(e["start"]),
                "end": pd.to_datetime(e["end"]),
                "elapsed_s": e["elapsedDuration"],
                "active_s": e["activeDuration"],
                **hr_stats(e),
            }
        )
    return pd.DataFrame(rows).sort_values("index").reset_index(drop=True)


def heart_rate_df(samples: list) -> pd.DataFrame:
    df = pd.DataFrame(samples)
    df["date"] = pd.to_datetime(df["date"])
    return df.rename(columns={"Min": "hr_min", "Avg": "hr_avg", "Max": "hr_max"})


def tag_lap_segments(laps: pd.DataFrame, segments: pd.DataFrame) -> pd.DataFrame:
    """Object 1. Adds a seg_idx/seg_laps column to laps, mapping each lap to
    its containing segment. Nothing here guards against segments overlapping
    in time -- if they did, a lap could match more than one and would
    silently end up tagged with whichever segment is processed last. Verified
    directly (2026-09-23 file) that no two segments overlap and every lap
    matches exactly one segment, but that hasn't been re-checked for every
    file this might ever run on."""
    laps = laps.copy()
    laps["seg_idx"] = None
    laps["seg_laps"] = None
    for _, seg in segments.iterrows():
        in_range = (laps["start"] >= seg["start"]) & (laps["end"] <= seg["end"])
        laps.loc[in_range, "seg_idx"] = seg["index"]
        laps.loc[in_range, "seg_laps"] = in_range.sum()
    return laps


def segment_table(laps_tagged: pd.DataFrame, segments: pd.DataFrame, lap_length_m: float) -> pd.DataFrame:
    """Object 2: every raw per-segment field from the JSON (via intervals_to_df),
    unchanged, plus one derived column -- distance_m -- built from Object 1 (the
    lap<->segment join in laps_tagged, i.e. tag_lap_segments' output). Segments
    carry no distance/length field of their own (confirmed directly: the only
    keys on any segment are start/end/elapsedDuration/activeDuration/metrics),
    so this is the only way to get one: count how many laps tag_lap_segments
    assigned to each segment, multiply by the watch's own lapLength. A segment
    with zero matching laps (not seen in practice, but not impossible) gets
    distance_m = 0 rather than dropping out of the table."""
    n_laps = laps_tagged.groupby("seg_idx").size()
    n_laps = n_laps.reindex(segments["index"], fill_value=0)
    table = segments.copy()
    table["distance_m"] = table["index"].map(n_laps) * lap_length_m
    return table


def segment_gap_heart_rate(segments: pd.DataFrame, hr: pd.DataFrame) -> list[pd.DataFrame]:
    """Object 3: for each pair of time-consecutive segments, the raw HR
    samples (heartRateData, via heart_rate_df) whose timestamp falls in the
    window between one segment's end and the next segment's start -- the rest
    gap between them. Deliberately "pure": each element keeps its original
    date/hr_min/hr_avg/hr_max columns and its original row index from the
    full hr DataFrame untouched (no re-basing to elapsed-since-gap-start, no
    dropping of near-zero-length gaps) -- those are later analysis steps, not
    part of collecting the data. len(result) == len(segments) - 1."""
    segments = segments.sort_values("start").reset_index(drop=True)
    gaps = []
    for i in range(len(segments) - 1):
        seg_end = segments.loc[i, "end"]
        next_start = segments.loc[i + 1, "start"]
        gaps.append(hr[(hr["date"] >= seg_end) & (hr["date"] <= next_start)])
    return gaps


def segment_gap_recovery_curves(
    gaps: list[pd.DataFrame],
    hr: pd.DataFrame,
    min_duration_s: float = 60.0,
    max_peak_offset_s: float | None = None,
    step_s: float | None = None,
) -> pd.DataFrame:
    """Built on top of Object 3 (segment_gap_heart_rate's output): a
    peak-referenced, common-grid view of HR decay during rest gaps, ready for
    aggregation (see aggregate_recovery_curves).

    For each gap: dropped if its own span is under min_duration_s (short gaps
    are noisy and sometimes still catching HR ramp-up rather than real
    recovery -- verified directly on the 2026-09-23 session, where several
    sub-5s gaps showed HR still *rising* right after being "zeroed"). The
    survivors are re-referenced at their own peak HR sample -- not
    necessarily their first sample -- both the timestamp (zeroed) and the HR
    value (subtracted), with everything before that peak dropped. If
    max_peak_offset_s is given, a gap is also dropped when its peak occurs
    more than that many seconds after the gap's own start (dropped outright,
    same as the duration filter -- not flagged-and-kept): a late peak means
    little or no real decline was captured after it.

    The interpolation grid step defaults to the most common (mode) interval
    between consecutive samples across the full hr series (5s on the
    2026-09-23 file) rather than anything computed from just the gaps, since
    that's the watch's own characteristic sampling rate; step_s overrides it.
    The grid runs from 0 to the longest surviving gap's own max relative
    time; every gap is interpolated onto it with left=right=NaN, i.e. no
    extrapolation past what that gap actually observed.

    Returns a DataFrame indexed by seconds-since-peak, one column per
    surviving gap. Columns are labeled by that gap's own first (original,
    absolute) timestamp -- not a segment id: a gap sits between two segments,
    so there's no single segment it "belongs" to, but its own start time is
    unambiguous and traces straight back to Object 3's untouched data."""
    if step_s is None:
        step_s = hr["date"].diff().dt.total_seconds().dropna().round().astype(int).mode().iloc[0]

    kept = []
    for gap in gaps:
        if len(gap) < 2:
            continue
        duration_s = (gap["date"].iloc[-1] - gap["date"].iloc[0]).total_seconds()
        if duration_s < min_duration_s:
            continue

        peak_idx = gap["hr_avg"].idxmax()
        peak_time = gap.loc[peak_idx, "date"]
        peak_hr = gap.loc[peak_idx, "hr_avg"]
        peak_offset_s = (peak_time - gap["date"].iloc[0]).total_seconds()
        if max_peak_offset_s is not None and peak_offset_s > max_peak_offset_s:
            continue

        t_rel = (gap["date"] - peak_time).dt.total_seconds()
        after_peak = t_rel >= 0
        kept.append((
            gap["date"].iloc[0],
            t_rel[after_peak].to_numpy(),
            (gap.loc[after_peak, "hr_avg"] - peak_hr).to_numpy(),
        ))

    if not kept:
        return pd.DataFrame()

    max_t = max(t.max() for _, t, _ in kept)
    n_steps = int(np.floor(max_t / step_s))
    grid = np.arange(n_steps + 1) * step_s

    data = {label: np.interp(grid, t, y, left=np.nan, right=np.nan) for label, t, y in kept}
    return pd.DataFrame(data, index=pd.Index(grid, name="seconds_since_peak"))


def aggregate_recovery_curves(curves: pd.DataFrame, min_n: int | None = 3) -> pd.DataFrame:
    """Takes segment_gap_recovery_curves' output and reduces across its
    columns (gaps) at each row (seconds-since-peak): n (how many gaps
    actually have data there), mean, std, min, max -- all pandas'
    axis=1 reductions, which skip NaN automatically, so a grid point only
    reflects whichever gaps actually reached that far.

    If min_n is given, rows where n falls below it are dropped -- this is
    where an unfiltered average would otherwise quietly collapse to a single
    gap's raw trajectory with a zero-width, falsely-confident band (seen
    directly on the 2026-09-23 session: n dropped from 12 to 1 by t=210s).
    min_n=None skips truncation entirely."""
    summary = pd.DataFrame({
        "n": curves.count(axis=1),
        "mean": curves.mean(axis=1),
        "std": curves.std(axis=1),
        "min": curves.min(axis=1),
        "max": curves.max(axis=1),
    })
    if min_n is not None:
        summary = summary[summary["n"] >= min_n]
    return summary
