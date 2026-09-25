#!/usr/bin/env python3
"""
Raw-primitives viewer for a HealthAutoExport "Pool Swim-*.json" export (Apple Watch).

Shows the three JSON primitives -- laps, segments, heartRateData -- exactly as
recorded, with nothing derived or inferred: no true_end bridging, no pace, no
TT-segment coloring, no lap<->segment tagging. Three stacked panels share one
real-elapsed-time x-axis:
  - heart rate (top): the raw Avg HR series, continuous
  - segments (middle): one horizontal bar per segment, raw start->end
  - laps (bottom): one horizontal bar per lap, raw start->end

Gaps between bars are exactly the watch's own reported gaps (turn time between
laps, rest time between segments) -- nothing here bridges or infers across
them. This is meant as a starting point for deciding, separately, how to
combine these three into derived metrics (pace, true lap duration, etc.).

Usage:
    python3 swim_primitives.py [path/to/Pool Swim-*.json]

If no path is given, the newest "Pool Swim-*.json" in ../biometrics/ph/archives is
used.

Requires: pandas, matplotlib, PyQt6 (for the qtagg interactive backend)
"""
import argparse
import sys
from pathlib import Path

import matplotlib

# Always qtagg (PyQt6) -- this tool's whole point is the live window, and
# it's the same Qt binding the native table widget (see lap_segment_table)
# uses. Do NOT switch this to Agg for headless testing: Agg's own PNG/font
# rendering and PyQt6's bundled Qt libraries conflict when both are exercised
# in the same process (verified directly -- forcing Agg while also creating
# a QApplication segfaults, in either order). savefig() works fine under
# qtagg without ever entering the Qt event loop, so headless verification
# doesn't need Agg anyway -- see --selftest below.
matplotlib.use("qtagg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QAbstractItemView, QApplication, QHeaderView, QTableWidget, QTableWidgetItem

from swim_data import (
    find_repo_root,
    newest_json,
    load_workout,
    intervals_to_df,
    heart_rate_df,
    tag_lap_segments,
    segment_table,
    segment_gap_heart_rate,
)


def bars(df: pd.DataFrame, workout_start: pd.Timestamp) -> tuple[list[tuple[float, float]], list[str]]:
    """(start_min, width_min) per row, straight from that row's own raw
    start/end -- no bridging across gaps -- plus alternating colors so
    back-to-back items with zero visible gap are still distinguishable."""
    starts = (df["start"] - workout_start).dt.total_seconds() / 60
    widths = (df["end"] - df["start"]).dt.total_seconds() / 60
    # Light/faint colors -- visible enough to show each bar's extent and the
    # gaps between them, but pale enough that the red HR overlay (see
    # overlay_hr_metrics) stays the visually dominant layer. The second color
    # is a distinctly different hue (green, not just a paler blue) so
    # adjacent bars stay distinguishable even at low saturation.
    colors = ["lightblue" if i % 2 == 0 else "lightgreen" for i in range(len(df))]
    return list(zip(starts, widths)), colors


def overlay_hr_metrics(ax: plt.Axes, df: pd.DataFrame, workout_start: pd.Timestamp) -> plt.Axes:
    """Each row's own metrics.heartRateAverage/Minimum/Maximum (Apple's own
    per-interval HR summary -- see the JSON's "metrics" block on every lap and
    segment) as a point at that interval's midpoint, min-max as error bars.
    On a twin y-axis, since the underlying bar axis (0-1) carries no real
    scale. Rows with no HR samples (missing metrics) are skipped rather than
    plotted as zero."""
    valid = df.dropna(subset=["hr_avg", "hr_min", "hr_max"])
    mid = (valid["start"] + (valid["end"] - valid["start"]) / 2 - workout_start).dt.total_seconds() / 60
    yerr = np.vstack([valid["hr_avg"] - valid["hr_min"], valid["hr_max"] - valid["hr_avg"]])

    ax_hr = ax.twinx()
    ax_hr.errorbar(
        mid, valid["hr_avg"], yerr=yerr, fmt="o", ms=4, color="tab:red",
        ecolor="tab:red", elinewidth=1, capsize=2, alpha=0.8, zorder=3,
    )
    ax_hr.set_ylabel("heart rate (bpm)", color="tab:red", fontsize=9)
    ax_hr.tick_params(axis="y", labelcolor="tab:red")
    return ax_hr


def plot_primitives(
    laps: pd.DataFrame, segments: pd.DataFrame, hr: pd.DataFrame, workout_start: pd.Timestamp,
) -> plt.Figure:
    fig, (ax_hr, ax_lap, ax_seg) = plt.subplots(
        3, 1, sharex=True, figsize=(12, 7), gridspec_kw={"height_ratios": (2, 1, 1)}
    )

    hr_x = (hr["date"] - workout_start).dt.total_seconds() / 60
    ax_hr.plot(hr_x, hr["hr_avg"], color="tab:red", lw=1.2)
    ax_hr.set_ylabel("heart rate (bpm)")
    ax_hr.set_title("Heart rate -- raw heartRateData.Avg")

    seg_bars, seg_colors = bars(segments, workout_start)
    ax_seg.broken_barh([], (0, 1))  # establishes the axes even if segments is empty
    for (start, width), color in zip(seg_bars, seg_colors):
        ax_seg.broken_barh([(start, width)], (0, 1), facecolors=color)
    ax_seg.set_yticks([])
    ax_seg.set_ylabel("segments", rotation=0, ha="right", va="center")
    ax_seg.set_title(f"Segments ({len(segments)} total) -- raw start/end, with per-segment HR avg (min-max)")
    ax_seg.set_xlabel("elapsed time (min)")
    overlay_hr_metrics(ax_seg, segments, workout_start)

    # Bar height = elapsedDuration (raw seconds, straight from the JSON, no
    # normalization) -- unlike the segments row, whose bars stay a fixed
    # placeholder height. Taller bar = longer length = slower lap. Uses
    # elapsedDuration directly rather than recomputing from end-start: the
    # two agree to within ~1s, but elapsedDuration carries sub-second
    # precision that the (whole-second) start/end timestamp strings don't.
    lap_bars, lap_colors = bars(laps, workout_start)
    lap_heights = laps["elapsed_s"].to_numpy()
    for (start, width), color, height in zip(lap_bars, lap_colors, lap_heights):
        ax_lap.broken_barh([(start, width)], (0, height), facecolors=color)
    ax_lap.set_ylim(0, lap_heights.max() * 1.15)
    ax_lap.set_ylabel("elapsedDuration (s)")
    ax_lap.set_title(f"Laps ({len(laps)} total) -- raw start/end, bar height = elapsedDuration, with per-lap HR avg (min-max)")
    overlay_hr_metrics(ax_lap, laps, workout_start)

    fig.tight_layout()
    return fig


def lap_segment_table(laps: pd.DataFrame, workout_start: pd.Timestamp) -> QTableWidget:
    """Renders the lap<->segment join (tag_lap_segments) as a native Qt6
    table widget: one row per lap, background color alternating by *segment*
    index (not by lap), so every lap belonging to the same segment reads as
    one visual block -- the same lightblue/lightgreen pairing used for the
    bars elsewhere, for a consistent visual language across the app."""

    def fmt(ts: pd.Timestamp) -> str:
        s = int(round((ts - workout_start).total_seconds()))
        return f"{s // 60}:{s % 60:02d}"

    columns = ["seg #", "lap #", "start", "stop", "duration (s)", "avg HR", "min HR", "max HR"]
    light_blue, light_green = QColor("lightblue"), QColor("lightgreen")

    laps = laps.sort_values("index").reset_index(drop=True)
    table = QTableWidget(len(laps), len(columns))
    table.setWindowTitle("Laps joined to segments -- background alternates per segment, not per lap")
    table.setHorizontalHeaderLabels(columns)
    table.verticalHeader().setVisible(False)
    table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    for row, r in laps.iterrows():
        seg_idx = int(r["seg_idx"])
        color = light_blue if seg_idx % 2 == 0 else light_green
        values = [
            seg_idx, int(r["index"]), fmt(r["start"]), fmt(r["end"]),
            f'{r["elapsed_s"]:.1f}', f'{r["hr_avg"]:.1f}', f'{r["hr_min"]:.1f}', f'{r["hr_max"]:.1f}',
        ]
        for col, value in enumerate(values):
            item = QTableWidgetItem(str(value))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setBackground(color)
            table.setItem(row, col, item)

    table.resize(900, 900)
    return table


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("json_path", nargs="?", help="Path to a 'Pool Swim-*.json' export; defaults to the newest one")
    parser.add_argument("--table", action="store_true", help="Also open the lap<->segment join as a table window")
    parser.add_argument("--selftest", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()

    if args.json_path:
        json_path = Path(args.json_path).expanduser()
        repo_root = find_repo_root(json_path)
    else:
        repo_root = find_repo_root(Path.cwd())
        json_path = newest_json(repo_root / "biometrics" / "ph" / "archives")

    workout = load_workout(json_path)
    laps = intervals_to_df(workout["laps"])
    segments = intervals_to_df(workout["segments"])
    hr = heart_rate_df(workout["heartRateData"])
    workout_start = pd.to_datetime(workout["start"])

    fig = plot_primitives(laps, segments, hr, workout_start)

    # The table is a native Qt widget, not a matplotlib Figure, so it needs
    # its own QApplication -- reuses the one matplotlib's qtagg backend
    # already created via plot_primitives, above.
    table_widget = None
    if args.table:
        QApplication.instance() or QApplication(sys.argv)
        laps_tagged = tag_lap_segments(laps, segments)
        table_widget = lap_segment_table(laps_tagged, workout_start)

    if args.selftest:
        date_str = workout_start.strftime("%Y-%m-%d")
        out_path = repo_root / "biometrics" / "ph" / "plots" / f"{date_str}_swim_primitives.png"
        fig.savefig(out_path, dpi=150)
        print(f"[selftest] saved {out_path}")
        if table_widget is not None:
            # No savefig equivalent for a Qt widget -- show it briefly,
            # process the paint event, then grab() a screenshot.
            table_widget.show()
            QApplication.processEvents()
            table_out = repo_root / "biometrics" / "ph" / "plots" / f"{date_str}_swim_primitives_table.png"
            table_widget.grab().save(str(table_out))
            table_widget.close()
            print(f"[selftest] saved {table_out}")
    else:
        print("Interactive window(s) open -- pan/zoom via the toolbar, close to exit.")
        if table_widget is not None:
            table_widget.show()
        plt.show()


if __name__ == "__main__":
    main()
