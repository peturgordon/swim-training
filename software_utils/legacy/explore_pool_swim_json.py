#!/usr/bin/env python3
"""
One-off exploration script for a HealthAutoExport "Pool Swim-*.json" export
(Apple Watch, e.g. biometrics/ph/archives/Pool Swim-*.json) -- a different
shape from the "Pool Swim-Heart Rate-*.csv" files hr_labeler.py works with:
a single JSON with laps/segments already computed on-device, not a flat
heart-rate-only time series.

No stroke count is present in this export (checked directly -- zero
"stroke" keys anywhere in the file); everything below is heart-rate and
timing only. If stroke count matters, check the Health app for whether
Apple actually recorded it for this workout, or whether HealthAutoExport's
data-type selection needs to include it.

Structure (workout = data["data"]["workouts"][0]):
  - laps: one per pool-length (auto wall-touch detection), each with
    start/end/elapsedDuration/activeDuration and an optional
    metrics.heartRate{Average,Min,Max} -- missing metrics means no HR
    sample fell in that lap, not an error.
  - segments: higher-level blocks bounded by pause/resume events (your
    actual sets, roughly), same HR-summary shape as laps.
  - heartRateData: the raw time series (date, Min/Avg/Max, units).
  - top-level summary: distance, duration, avgHeartRate, maxHeartRate,
    speed, activeEnergyBurned.

This is deliberately standalone -- not wired into hr_labeler.py's
_segments.csv/_annotated.csv pipeline.

Usage:
    python3 explore_pool_swim_json.py [path/to/Pool Swim-*.json] [--interactive]

If no path is given, the newest "Pool Swim-*.json" in ../biometrics/ph/archives
is used. --interactive/-i opens the pace plot in a live, pannable/zoomable
matplotlib window (qtagg backend, via PyQt6, already a project dependency)
instead of just saving a PNG -- it still saves the PNG too.

Requires: pandas, matplotlib
"""
import argparse
import sys
from pathlib import Path

import matplotlib

# Headless by default (no Qt/X needed to just save PNGs) -- only switch to an
# interactive GUI backend when --interactive/-i is actually requested, and do
# it before pyplot is imported/creates any figure, since backend switching
# after the fact doesn't reliably apply to already-created figures. Guarded by
# __name__ so importing this module (e.g. swim_explorer.py, for its helper
# functions) never clobbers a backend the importer already chose -- this
# argv-sniffing only makes sense for this file's own command-line invocation.
if __name__ == "__main__" and not ({"-i", "--interactive"} & set(sys.argv)):
    matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# swim_data.py lives one directory up (software_utils/), not next to this
# file (software_utils/legacy/) -- this script predates that split, so add
# the parent dir to sys.path rather than duplicating swim_data's contents.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from swim_data import (
    find_repo_root,
    newest_json,
    load_workout,
    intervals_to_df,
    heart_rate_df,
    tag_lap_segments,
)


def summarize(workout: dict, laps: pd.DataFrame, segments: pd.DataFrame) -> None:
    print(f"Source:      {workout['source']['name']}")
    print(f"Start/end:   {workout['start']}  ->  {workout['end']}")
    print(f"Duration:    {workout['duration']/60:.1f} min")
    print(f"Distance:    {workout['distance']['qty']} {workout['distance']['units']}")
    print(f"Avg/Max HR:  {workout['avgHeartRate']['qty']:.0f} / {workout['maxHeartRate']['qty']:.0f} bpm")
    print(f"Laps:        {len(laps)} ({laps['hr_avg'].isna().sum()} with no HR samples)")
    print(f"Segments:    {len(segments)}")


def add_true_duration(laps: pd.DataFrame, segments: pd.DataFrame) -> pd.DataFrame:
    """Apple's per-lap elapsedDuration only counts the "confident straight-swimming" portion
    of each length -- it excludes the turn/wall-touch-detection time at each end, so summed
    lap durations undercount the real segment total (checked directly: ~65s missing across
    16 laps in one 400m time trial, exactly matching small real gaps between every
    consecutive lap's end and the next lap's start). Recomputes each lap's true duration as
    (next lap's start) - (this lap's start) -- or (this lap's own segment's end) - (this
    lap's start) for the last lap in a segment, so no rest time bleeds in from the gap to
    the next block. This fully accounts for every second with no gaps, and by construction
    sums exactly back to each segment's own total duration."""
    laps = laps.sort_values("start").reset_index(drop=True).copy()
    seg_end_by_idx = segments.set_index("index")["end"]

    next_start = laps["start"].shift(-1)
    same_segment_as_next = laps["seg_idx"] == laps["seg_idx"].shift(-1)
    fallback_end = laps["seg_idx"].map(seg_end_by_idx)

    laps["true_end"] = next_start.where(same_segment_as_next, fallback_end)
    laps["true_dur_s"] = (laps["true_end"] - laps["start"]).dt.total_seconds()
    return laps


def interpolate_lap_position(timestamps: pd.Series, laps: pd.DataFrame) -> pd.Series:
    """Maps arbitrary timestamps onto a continuous 'lap #' position by linear interpolation
    against known lap start times. Lets the full-resolution heartRateData series (642
    samples, ~5s median interval, no gaps -- unlike the per-lap HR summaries, which are
    missing wherever a lap has zero HR samples or, more visibly, during the whole recovery
    interval where the watch was paused and no laps exist at all) be plotted on the same
    lap-# x-axis as pace, continuously through those gaps instead of breaking there."""
    lap_times = laps.sort_values("start")
    t0 = lap_times["start"].iloc[0]
    known_t = (lap_times["start"] - t0).dt.total_seconds().to_numpy()
    known_x = lap_times["index"].to_numpy()
    query_t = (timestamps - t0).dt.total_seconds().to_numpy()
    return pd.Series(np.interp(query_t, known_t, known_x), index=timestamps.index)


def find_time_trial_segment(laps: pd.DataFrame, segments: pd.DataFrame, distance_m: int) -> int | None:
    """Finds the segment whose lap count times 25m matches distance_m. Lap count alone is
    ambiguous (an easy warmup/cooldown block can happen to be the same distance as a time
    trial -- e.g. an 8-lap/200m easy warmup vs. an 8-lap/200m all-out TT), so among matches,
    picks the one with the highest average HR -- the genuine maximal effort."""
    n_laps = distance_m // 25
    candidates = laps.loc[laps["seg_laps"] == n_laps, "seg_idx"].unique()
    if not len(candidates):
        return None
    hr_by_seg = segments.set_index("index")["hr_avg"]
    return max(candidates, key=lambda s: hr_by_seg.get(s, -1))


def plot_lap_pace(
    laps: pd.DataFrame, segments: pd.DataFrame, out_path: Path, ylim: tuple = (15, 30), interactive: bool = False
) -> None:
    seg_400 = find_time_trial_segment(laps, segments, 400)
    seg_200 = find_time_trial_segment(laps, segments, 200)

    colors = laps["seg_idx"].map(
        lambda s: "tab:red" if s == seg_400 else ("tab:green" if s == seg_200 else "tab:gray")
    )

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.scatter(laps["index"], laps["true_dur_s"], c=colors, s=25, zorder=3)
    ax.plot(laps["index"], laps["true_dur_s"], color="lightgray", lw=1, zorder=1)

    # legend via proxy handles, since scatter color is per-point not per-series
    from matplotlib.lines import Line2D
    handles = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor="tab:red", label="400m time trial", ms=8),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="tab:green", label="200m time trial", ms=8),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="tab:gray", label="warmup/recovery/cooldown", ms=8),
    ]
    ax.legend(handles=handles)

    ax.set_xlabel("lap #")
    ax.set_ylabel("time per 25m (s)")
    ax.set_title("Time per 25m across the whole practice")
    ax.set_ylim(*ylim)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    print(f"Saved plot: {out_path}")
    if interactive:
        # the saved PNG stays pre-zoomed (ylim above), but the live window starts
        # fully zoomed out -- the whole point of interactive is to let the user
        # zoom in themselves, rather than deciding the interesting range for them
        ax.autoscale(enable=True, axis="both")
        ax.relim()
        ax.autoscale_view()
        print("Opening interactive window, fully zoomed out (scroll/drag to pan+zoom, cursor position shown bottom-right) -- close it to continue.")
        plt.show()


def shade_100m_blocks(ax, laps: pd.DataFrame, laps_per_block: int = 4) -> None:
    """Alternating light-gray/white background bands, one per 100m (4 laps of 25m each),
    grouped by lap index -- a rest gap with no laps just leaves that stretch unshaded,
    it doesn't shift the grouping of the laps on either side of it."""
    idx_min, idx_max = int(laps["index"].min()), int(laps["index"].max())
    block_start = idx_min
    block = 0
    while block_start <= idx_max:
        block_end = min(block_start + laps_per_block, idx_max + 1)
        if block % 2 == 0:
            ax.axvspan(block_start - 0.5, block_end - 0.5, color="gray", alpha=0.10, zorder=0, lw=0)
        block_start = block_end
        block += 1


def shade_100m_blocks_time(ax, laps: pd.DataFrame, t0: pd.Timestamp, laps_per_block: int = 4) -> None:
    """Same alternating 100m bands as shade_100m_blocks, but on a real-elapsed-minutes axis --
    each block's edges are the actual start times of its first lap and the next block's first
    lap (or, for the last block, its own last lap's true_end), converted to minutes since t0."""
    laps = laps.sort_values("index").reset_index(drop=True)
    n = len(laps)
    block = 0
    i = 0
    while i < n:
        j = min(i + laps_per_block, n)
        left = (laps["start"].iloc[i] - t0).total_seconds() / 60
        right_ts = laps["start"].iloc[j] if j < n else laps["true_end"].iloc[j - 1]
        right = (right_ts - t0).total_seconds() / 60
        if block % 2 == 0:
            ax.axvspan(left, right, color="gray", alpha=0.10, zorder=0, lw=0)
        i = j
        block += 1


def plot_combined_time(
    laps: pd.DataFrame,
    segments: pd.DataFrame,
    hr: pd.DataFrame,
    workout_start: pd.Timestamp,
    out_path: Path,
    pace_ylim: tuple = (15, 30),
    interactive: bool = False,
) -> None:
    """Same as plot_combined, but x-axis is real elapsed minutes since workout start instead
    of lap #. HR no longer needs interpolate_lap_position -- it's plotted directly against
    its own real timestamps, which is simpler and exactly as continuous as the source data."""
    from matplotlib.lines import Line2D

    seg_400 = find_time_trial_segment(laps, segments, 400)
    seg_200 = find_time_trial_segment(laps, segments, 200)
    pace_colors = laps["seg_idx"].map(
        lambda s: "tab:red" if s == seg_400 else ("tab:green" if s == seg_200 else "tab:gray")
    )
    pace_x = (laps["start"] - workout_start).dt.total_seconds() / 60
    hr_x = (hr["date"] - workout_start).dt.total_seconds() / 60

    fig, ax_pace = plt.subplots(figsize=(11, 5))
    ax_hr = ax_pace.twinx()

    shade_100m_blocks_time(ax_pace, laps, workout_start)
    ax_hr.plot(hr_x, hr["hr_avg"], color="tab:blue", lw=1.2, zorder=2)
    ax_pace.scatter(pace_x, laps["true_dur_s"], c=pace_colors, s=22, zorder=3)
    ax_pace.plot(pace_x, laps["true_dur_s"], color="lightgray", lw=1, zorder=1)

    ax_pace.set_xlabel("elapsed time (min)")
    ax_pace.set_ylabel("time per 25m (s)")
    ax_hr.set_ylabel("heart rate (bpm)", color="tab:blue")
    ax_hr.tick_params(axis="y", labelcolor="tab:blue")
    ax_pace.set_ylim(*pace_ylim)
    ax_pace.set_title("Heart rate and pace per length, vs. elapsed time")

    handles = [
        Line2D([0], [0], color="tab:blue", lw=1.5, label="heart rate (right axis)"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="tab:red", label="pace -- 400m TT (left axis)", ms=8),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="tab:green", label="pace -- 200m TT (left axis)", ms=8),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="tab:gray", label="pace -- warmup/recovery/cooldown", ms=8),
    ]
    ax_pace.legend(handles=handles, loc="upper left")

    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    print(f"Saved plot: {out_path}")
    if interactive:
        ax_pace.set_ylim(auto=True)
        ax_pace.relim()
        ax_pace.autoscale_view()
        print("Opening interactive window, fully zoomed out (scroll/drag to pan+zoom, cursor position shown bottom-right) -- close it to continue.")
        plt.show()


def plot_combined(
    laps: pd.DataFrame,
    segments: pd.DataFrame,
    hr: pd.DataFrame,
    out_path: Path,
    pace_ylim: tuple = (15, 30),
    interactive: bool = False,
) -> None:
    """HR and pace-per-length together, on twin y-axes sharing the same lap-# x-axis. HR uses
    the full-resolution heartRateData series (via interpolate_lap_position), not the per-lap
    summaries, so it stays continuous through rest gaps instead of breaking there."""
    from matplotlib.lines import Line2D

    seg_400 = find_time_trial_segment(laps, segments, 400)
    seg_200 = find_time_trial_segment(laps, segments, 200)
    pace_colors = laps["seg_idx"].map(
        lambda s: "tab:red" if s == seg_400 else ("tab:green" if s == seg_200 else "tab:gray")
    )
    hr_x = interpolate_lap_position(hr["date"], laps)

    fig, ax_pace = plt.subplots(figsize=(11, 5))
    ax_hr = ax_pace.twinx()

    shade_100m_blocks(ax_pace, laps)
    ax_hr.plot(hr_x, hr["hr_avg"], color="tab:blue", lw=1.2, zorder=2)
    ax_pace.scatter(laps["index"], laps["true_dur_s"], c=pace_colors, s=22, zorder=3)
    ax_pace.plot(laps["index"], laps["true_dur_s"], color="lightgray", lw=1, zorder=1)

    ax_pace.set_xlabel("lap #")
    ax_pace.set_ylabel("time per 25m (s)")
    ax_hr.set_ylabel("heart rate (bpm)", color="tab:blue")
    ax_hr.tick_params(axis="y", labelcolor="tab:blue")
    ax_pace.set_ylim(*pace_ylim)
    ax_pace.set_title("Heart rate and pace per length, together")

    handles = [
        Line2D([0], [0], color="tab:blue", lw=1.5, label="heart rate (right axis)"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="tab:red", label="pace -- 400m TT (left axis)", ms=8),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="tab:green", label="pace -- 200m TT (left axis)", ms=8),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="tab:gray", label="pace -- warmup/recovery/cooldown", ms=8),
    ]
    ax_pace.legend(handles=handles, loc="upper left")

    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    print(f"Saved plot: {out_path}")
    if interactive:
        # saved PNG stays pre-zoomed; the live window starts fully zoomed out
        ax_pace.set_ylim(auto=True)
        ax_pace.relim()
        ax_pace.autoscale_view()
        print("Opening interactive window, fully zoomed out (scroll/drag to pan+zoom, cursor position shown bottom-right) -- close it to continue.")
        plt.show()


def plot_lap_hr(laps: pd.DataFrame, segments: pd.DataFrame, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(laps["index"], laps["hr_avg"], marker="o", ms=3, lw=1, label="avg HR per lap")

    # shade each segment's lap range so sets are visible against rest gaps
    for _, seg in segments.iterrows():
        in_range = laps[(laps["start"] >= seg["start"]) & (laps["end"] <= seg["end"])]
        if in_range.empty:
            continue
        ax.axvspan(in_range["index"].min() - 0.5, in_range["index"].max() + 0.5, color="tab:blue", alpha=0.06)

    ax.set_xlabel("lap #")
    ax.set_ylabel("heart rate (bpm)")
    ax.set_title("Average HR per lap, segments shaded")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    print(f"Saved plot: {out_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("json_path", nargs="?", help="Path to a 'Pool Swim-*.json' export; defaults to the newest one")
    parser.add_argument("--interactive", "-i", action="store_true", help="Open the pace plot in a live matplotlib window")
    args = parser.parse_args()

    if args.json_path:
        json_path = Path(args.json_path).expanduser()
    else:
        repo_root = find_repo_root(Path.cwd())
        json_path = newest_json(repo_root / "biometrics" / "ph" / "archives")

    workout = load_workout(json_path)
    laps = intervals_to_df(workout["laps"])
    segments = intervals_to_df(workout["segments"])
    hr = heart_rate_df(workout["heartRateData"])

    summarize(workout, laps, segments)

    repo_root = find_repo_root(json_path)
    date_str = pd.to_datetime(workout["start"]).strftime("%Y-%m-%d")
    plots_dir = repo_root / "biometrics" / "ph" / "plots"
    plot_lap_hr(laps, segments, plots_dir / f"{date_str}_pool_swim_lap_hr.png")

    laps = tag_lap_segments(laps, segments)
    laps = add_true_duration(laps, segments)
    # Only one plot opens interactively -- plt.show() blocks until closed, and each newer
    # view here supersedes the previous one for interactive use, so opening more than one
    # in sequence would just mean closing earlier windows before a later one ever appears.
    # The time-axis combined plot is the most complete view, so it's the one that goes live.
    plot_lap_pace(laps, segments, plots_dir / f"{date_str}_pool_swim_lap_pace.png")
    plot_combined(laps, segments, hr, plots_dir / f"{date_str}_pool_swim_combined.png")
    plot_combined_time(
        laps,
        segments,
        hr,
        pd.to_datetime(workout["start"]),
        plots_dir / f"{date_str}_pool_swim_combined_time.png",
        interactive=args.interactive,
    )


if __name__ == "__main__":
    main()
