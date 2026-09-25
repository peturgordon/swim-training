#!/usr/bin/env python3
"""
Interactive explorer for a HealthAutoExport "Pool Swim-*.json" export (Apple Watch).

Opens a live matplotlib window with pace-per-length (colored by segment: 400m TT /
200m TT / warmup-recovery-cooldown) and heart rate plotted together on twin y-axes,
alternating shaded bands per 100m, plus a radio-button toggle (top right) that
switches the x-axis between lap # and elapsed time. Pan/zoom/save via the normal
matplotlib toolbar; close the window to exit.

Reuses the JSON-loading/lap-processing helpers from explore_pool_swim_json.py --
this script is the interactive counterpart, not a replacement for its PNG-saving
batch mode.

Usage:
    python3 swim_explorer.py [path/to/Pool Swim-*.json]

If no path is given, the newest "Pool Swim-*.json" in ../biometrics/ph/archives is
used.

Requires: pandas, numpy, matplotlib, PyQt6 (for the qtagg interactive backend)
"""
import argparse
import os
from pathlib import Path

import matplotlib

# This tool's whole point is the live window, so qtagg (PyQt6) is the default --
# unlike explore_pool_swim_json.py, which defaults headless. SWIM_EXPLORER_AGG=1
# forces Agg instead, for headless verification (see --selftest below); it must be
# set before matplotlib picks a backend, so it's read here, not via argparse.
matplotlib.use("Agg" if os.environ.get("SWIM_EXPLORER_AGG") else "qtagg")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.transforms import blended_transform_factory
from matplotlib.widgets import RadioButtons

from explore_pool_swim_json import (
    find_repo_root,
    newest_json,
    load_workout,
    intervals_to_df,
    heart_rate_df,
    tag_lap_segments,
    add_true_duration,
    interpolate_lap_position,
)


def lap_block_spans(laps: pd.DataFrame, laps_per_block: int = 4) -> list[tuple[float, float]]:
    """(left, right) lap-# boundaries of every other 100m block (the shaded ones),
    grouped by lap index -- mirrors explore_pool_swim_json.shade_100m_blocks."""
    idx_min, idx_max = int(laps["index"].min()), int(laps["index"].max())
    spans = []
    block_start = idx_min
    block = 0
    while block_start <= idx_max:
        block_end = min(block_start + laps_per_block, idx_max + 1)
        if block % 2 == 0:
            spans.append((block_start - 0.5, block_end - 0.5))
        block_start = block_end
        block += 1
    return spans


def time_block_spans(laps: pd.DataFrame, t0: pd.Timestamp, laps_per_block: int = 4) -> list[tuple[float, float]]:
    """Same alternating 100m blocks, but boundaries are real elapsed minutes since t0 --
    mirrors explore_pool_swim_json.shade_100m_blocks_time."""
    laps = laps.sort_values("index").reset_index(drop=True)
    n = len(laps)
    spans = []
    block = 0
    i = 0
    while i < n:
        j = min(i + laps_per_block, n)
        left = (laps["start"].iloc[i] - t0).total_seconds() / 60
        right_ts = laps["start"].iloc[j] if j < n else laps["true_end"].iloc[j - 1]
        right = (right_ts - t0).total_seconds() / 60
        if block % 2 == 0:
            spans.append((left, right))
        i = j
        block += 1
    return spans


class SwimExplorer:
    """Owns the figure and both x-axis "modes" (lap # / elapsed time). Toggling
    swaps x-data on the existing artists and redraws the shaded bands, rather than
    rebuilding the figure, so pan/zoom state on the y-axis and the legend survive
    a toggle."""

    def __init__(self, laps: pd.DataFrame, hr: pd.DataFrame, workout_start: pd.Timestamp):
        self.laps = laps
        self.hr = hr

        self.modes = {
            "Lap #": {
                "pace_x": laps["index"].to_numpy(dtype=float),
                "hr_x": interpolate_lap_position(hr["date"], laps).to_numpy(),
                "spans": lap_block_spans(laps),
                "xlabel": "lap #",
                "title": "Heart rate and pace per length, vs. lap #",
            },
            "Elapsed time": {
                "pace_x": ((laps["start"] - workout_start).dt.total_seconds() / 60).to_numpy(),
                "hr_x": ((hr["date"] - workout_start).dt.total_seconds() / 60).to_numpy(),
                "spans": time_block_spans(laps, workout_start),
                "xlabel": "elapsed time (min)",
                "title": "Heart rate and pace per length, vs. elapsed time",
                # Only meaningful on a real time axis -- on the lap-# axis every
                # lap already occupies exactly one integer step, so a start/end
                # marker would just duplicate the tick grid. "start" reuses
                # pace_x (each lap's start time); "end" is true_end (see
                # add_true_duration), which is what actually varies -- back-to-
                # back laps run right up to the next one's start, but a rest
                # gap or the final lap's own long tail shows up as a gap
                # between one lap's end line and the next lap's start line.
                "lap_end_x": ((laps["true_end"] - workout_start).dt.total_seconds() / 60).to_numpy(),
            },
        }
        self.pace_y = laps["true_dur_s"].to_numpy()
        self.hr_y = hr["hr_avg"].to_numpy()

        # A dedicated gridspec column for the radio buttons (rather than an
        # axes carved out of the main plot's own margin) keeps it clear of the
        # twin HR axis's label/ticks, which live in that margin too;
        # constrained_layout then resolves both automatically.
        self.fig = plt.figure(figsize=(12, 5), constrained_layout=True)
        gs = self.fig.add_gridspec(1, 2, width_ratios=(6, 1))
        self.ax_pace = self.fig.add_subplot(gs[0, 0])
        self.ax_hr = self.ax_pace.twinx()
        self._band_patches: list = []

        first = self.modes["Lap #"]
        # A figure-level suptitle, not an axes title -- the legend now lives
        # in a horizontal strip directly above the axes (see _apply_mode), so
        # an axes title there would collide with it.
        self._suptitle = self.fig.suptitle(first["title"], fontsize=13)
        self.hr_line, = self.ax_hr.plot(first["hr_x"], self.hr_y, color="tab:blue", lw=1.2, zorder=2)

        # The pace curve itself (one dot per lap + trend line) is always on,
        # in both modes -- it's the actual data. The lap start/end markers
        # are a separate, second layer: only meaningful in elapsed-time mode
        # (on the lap-# axis every lap is already exactly one integer step
        # apart, so start == end == that step), and deliberately NOT drawn at
        # the lap's pace value -- tying them to pace would scatter them all
        # over the chart at whatever height that lap happened to swim,
        # defeating the point of a start/stop *timeline*. Instead they live
        # on their own fixed reference line near the top of the axes, via a
        # blended transform (x in data coords, y in axes-fraction coords) so
        # that line stays put regardless of the pace/HR data's actual scale.
        # Alternating +/- stagger off that one reference line keeps
        # consecutive laps' dots from sitting on top of each other when
        # they're close in time; each lap's own start-end line stays
        # (near-)horizontal since both its ends get the same stagger sign.
        self.pace_scatter = self.ax_pace.scatter(first["pace_x"], self.pace_y, color="tab:orange", s=22, zorder=3)
        self.pace_line, = self.ax_pace.plot(first["pace_x"], self.pace_y, color="lightgray", lw=1, zorder=1)

        timeline_transform = blended_transform_factory(self.ax_pace.transData, self.ax_pace.transAxes)
        self._timeline_baseline = 0.94
        self._timeline_stagger = 0.03
        self.lap_segment_line, = self.ax_pace.plot(
            [], [], color="gray", lw=1.3, alpha=0.6, zorder=4, transform=timeline_transform)
        self.lap_start_scatter = self.ax_pace.scatter(
            [], [], color="tab:green", s=18, zorder=5, transform=timeline_transform)
        self.lap_end_scatter = self.ax_pace.scatter(
            [], [], color="tab:red", s=18, zorder=5, transform=timeline_transform)

        self.ax_pace.set_ylabel("time per 25m (s)")
        self.ax_hr.set_ylabel("heart rate (bpm)", color="tab:blue")
        self.ax_hr.tick_params(axis="y", labelcolor="tab:blue")

        # Full autoscale on both axes, on both dimensions, once -- captures
        # whatever range this session's data actually spans (no hardcoded
        # y-limits to clip an unusually fast/slow session). Later toggles only
        # re-autoscale x (see _apply_mode) so this initial y-range persists
        # across mode switches and any manual zoom the user has done.
        self.ax_pace.relim()
        self.ax_pace.autoscale_view()
        self.ax_hr.relim()
        self.ax_hr.autoscale_view()

        ax_radio = self.fig.add_subplot(gs[0, 1])
        ax_radio.set_title("x-axis", fontsize=9)
        ax_radio.set_xticks([])
        ax_radio.set_yticks([])
        for spine in ax_radio.spines.values():
            spine.set_visible(False)
        self.radio = RadioButtons(ax_radio, tuple(self.modes.keys()))
        self.radio.on_clicked(self._on_toggle)

        self._apply_mode("Lap #")

    def _apply_mode(self, name: str) -> None:
        mode = self.modes[name]

        for patch in self._band_patches:
            patch.remove()
        self._band_patches = [
            self.ax_pace.axvspan(left, right, color="gray", alpha=0.10, zorder=0, lw=0)
            for left, right in mode["spans"]
        ]

        self.pace_scatter.set_offsets(np.column_stack([mode["pace_x"], self.pace_y]))
        self.pace_line.set_data(mode["pace_x"], self.pace_y)

        empty = np.empty((0, 2))
        if "lap_end_x" in mode:
            starts, ends = mode["pace_x"], mode["lap_end_x"]
            # Alternate +/- stagger per lap (not per dot) off the fixed
            # reference line, so each lap's own start-end line stays
            # (near-)horizontal -- only its height alternates.
            sign = np.where(np.arange(len(starts)) % 2 == 0, 1.0, -1.0)
            y = self._timeline_baseline + sign * self._timeline_stagger

            xs = np.empty(3 * len(starts))
            ys = np.empty(3 * len(starts))
            xs[0::3], xs[1::3], xs[2::3] = starts, ends, np.nan
            ys[0::3], ys[1::3], ys[2::3] = y, y, np.nan

            self.lap_segment_line.set_data(xs, ys)
            self.lap_start_scatter.set_offsets(np.column_stack([starts, y]))
            self.lap_end_scatter.set_offsets(np.column_stack([ends, y]))
        else:
            self.lap_segment_line.set_data([], [])
            self.lap_start_scatter.set_offsets(empty)
            self.lap_end_scatter.set_offsets(empty)

        self.hr_line.set_data(mode["hr_x"], self.hr_y)

        self.ax_pace.set_xlabel(mode["xlabel"])
        self._suptitle.set_text(mode["title"])
        # A horizontal legend strip above the axes, rather than an in-plot
        # corner box -- an in-plot legend (semi-transparent by default) sat
        # right on top of the lap-start/end timeline, which lives near the
        # top of the axes deliberately (see __init__) to stay clear of the
        # actual pace/HR data.
        handles = self._legend_handles(mode)
        self.ax_pace.legend(
            handles=handles, loc="lower left", bbox_to_anchor=(0, 1.02, 1, 0.1),
            mode="expand", ncol=len(handles), borderaxespad=0, fontsize=9, frameon=False,
        )
        self.ax_pace.relim()
        self.ax_pace.autoscale_view(scaley=False)
        self.ax_hr.relim()
        self.ax_hr.autoscale_view(scaley=False)
        self.fig.canvas.draw_idle()

    @staticmethod
    def _legend_handles(mode: dict) -> list:
        handles = [
            Line2D([0], [0], color="tab:blue", lw=1.5, label="heart rate (right axis)"),
            Line2D([0], [0], marker="o", color="w", markerfacecolor="tab:orange", label="pace (left axis)", ms=8),
        ]
        if "lap_end_x" in mode:
            handles += [
                Line2D([0], [0], marker="o", color="w", markerfacecolor="tab:green", label="lap start", ms=7),
                Line2D([0], [0], marker="o", color="w", markerfacecolor="tab:red", label="lap end", ms=7),
            ]
        return handles

    def _on_toggle(self, label: str) -> None:
        self._apply_mode(label)

    def show(self) -> None:
        print("Interactive window open -- toggle Lap #/Elapsed time top-right, "
              "scroll/drag to pan+zoom, close the window to exit.")
        plt.show()

    def selftest_save(self, out_dir: Path, date_str: str) -> None:
        """Exercises both toggle states and saves each to a PNG, without opening a
        live window -- for headless verification (see SWIM_EXPLORER_AGG above)."""
        for name in self.modes:
            self._apply_mode(name)
            slug = name.lower().replace(" ", "_").replace("#", "num")
            out_path = out_dir / f"{date_str}_swim_explorer_{slug}.png"
            self.fig.savefig(out_path, dpi=150)
            print(f"[selftest] saved {out_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("json_path", nargs="?", help="Path to a 'Pool Swim-*.json' export; defaults to the newest one")
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

    laps = tag_lap_segments(laps, segments)
    laps = add_true_duration(laps, segments)

    explorer = SwimExplorer(laps, hr, pd.to_datetime(workout["start"]))

    if args.selftest:
        date_str = pd.to_datetime(workout["start"]).strftime("%Y-%m-%d")
        explorer.selftest_save(repo_root / "biometrics" / "ph" / "plots", date_str)
    else:
        explorer.show()


if __name__ == "__main__":
    main()
