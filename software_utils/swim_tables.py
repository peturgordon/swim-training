#!/usr/bin/env python3
"""
Tabbed viewer for the swim_data.py objects -- four tabs, built on native
Qt6 widgets (QTableWidget) plus embedded matplotlib figures for the graphs:

  1. Laps      -- Object 1 (tag_lap_segments) plus a pace column (lap_pace),
     with one control row selecting which distance pace is normalized to
     (per length -- the pool's own lapLength, i.e. unscaled elapsed_s -- per
     50m, or per 100m), driving two inner sub-tabs, Graph (shown by default;
     pace vs. lap #, HR vs. lap # above it, horizontal gridlines, y-axis
     auto-limited to exclude outlier laps) and Table (row background
     alternating by segment ID, not by lap, so every lap sharing a segment
     reads as one visual block). Switching the pace unit re-renders both
     immediately, live, same as Recovery below.
  2. Segments  -- Object 2 (segment_table): every segment, with its derived
     distance_m column.
  3. Heart Rate -- the raw heartRateData trace, unmodified, plotted against
     elapsed time, with each lap's own start->end span optionally ("Show lap
     shading", on by default) shaded (alternating by segment, same colors as
     the Laps tab) so rest/turn gaps stand out as unshaded. Clicking a lap's
     span selects it: that span darkens and its lap # + elapsed_s are shown
     centered over it. "Show derivative (bpm/min)" (off by default) splits
     the figure into two x-linked subplots, 2/3 HR on top and 1/3 dHR/dt
     below, rather than overlaying it on the same axes.
  4. Recovery  -- one shared parameter-control row (min duration, max peak
     offset, grid step, truncation threshold) driving two inner sub-tabs,
     Graph (shown by default) and Table, both generated from
     segment_gap_recovery_curves with the exact same current parameter
     values, live -- every control change re-generates both immediately, no
     separate step -- so the two views can never silently drift out of sync
     with each other. Table: one column per surviving rest gap (labeled by
     that gap's own start time), rows = seconds since that gap's own peak
     HR. Graph: aggregate_recovery_curves' mean line plus both bands layered
     together (not toggled) -- the wider min/max range and the narrower
     mean ± 1σ range in a different hue on top, plus HRR30/HRR60
     (recovery_hrr) in the top-right corner when the current min_duration is
     long enough to cover them.

First tool built fresh on top of swim_data.py -- no logic here predates the
object model. See software_utils/legacy/ for the archived pre-object tools
this replaces as the basis for new work.

Usage:
    python3 swim_tables.py [path/to/Pool Swim-*.json] [--min-duration SECONDS]

If no path is given, the newest "Pool Swim-*.json" in ../biometrics/ph is used
(archives/ is for the raw HealthAutoExport .zip files, not the exported JSON).
--min-duration sets the Recovery tab's minimum rest-gap length
(default 60s, matching the value validated during development). Use File ->
Open (Ctrl+O) in the running app to switch to a different export without
relaunching.

Requires: pandas, numpy, matplotlib, PyQt6
"""
import argparse
import colorsys
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec
from matplotlib.transforms import blended_transform_factory
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QColor, QKeySequence
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QButtonGroup,
    QCheckBox,
    QDoubleSpinBox,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QMessageBox,
    QRadioButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from swim_data import (
    find_repo_root,
    newest_json,
    load_workout,
    intervals_to_df,
    heart_rate_df,
    tag_lap_segments,
    segment_table,
    lap_pace,
    segment_gap_heart_rate,
    segment_gap_recovery_curves,
    aggregate_recovery_curves,
    recovery_hrr,
)


def format_value(value, workout_start: pd.Timestamp | None = None) -> str:
    """Elapsed mm:ss for a Timestamp when workout_start is known (the
    convention used throughout this project's tables/plots), 2 decimals for
    floats, blank for NaN (e.g. the Recovery tab's out-of-range cells), plain
    str() otherwise."""
    if isinstance(value, pd.Timestamp):
        if workout_start is not None:
            s = int(round((value - workout_start).total_seconds()))
            return f"{s // 60}:{s % 60:02d}"
        return str(value)
    if isinstance(value, float):
        if np.isnan(value):
            return ""
        return f"{value:.2f}"
    return str(value)


# Display labels only -- swim_data.py's DataFrames keep their original
# snake_case column names, since this file (and any future visualization)
# references them directly (df["hr_avg"], df["seg_idx"], etc.). Renaming the
# columns themselves would entangle a presentation concern into the one
# module explicitly meant to have none. Columns not listed here (e.g. the
# Recovery tab's gap-start-timestamp columns) fall through to format_value.
COLUMN_LABELS: dict[str, str] = {
    "index": "#",
    "start": "Start",
    "end": "End",
    "elapsed_s": "Elapsed (s)",
    "active_s": "Active (s)",
    "hr_avg": "Avg HR",
    "hr_min": "Min HR",
    "hr_max": "Max HR",
    "seg_idx": "Segment",
    "seg_laps": "# Laps",
    "distance_m": "Distance (m)",
}


def column_label(col, workout_start: pd.Timestamp | None = None) -> str:
    """Display label for a DataFrame column: COLUMN_LABELS' friendly name for
    a known data column, otherwise format_value's Timestamp/str handling
    (e.g. for the Recovery tab's per-gap timestamp columns)."""
    return COLUMN_LABELS.get(col, format_value(col, workout_start))


# The one shared palette for every row-background color coding in this app:
# every tab draws from these same two high-lightness, blue-family endpoints
# (every channel >= 170) rather than each tab picking its own colors, so hue
# and lightness stay consistent across tabs. NEAR_WHITE/PALE_BLUE are used as
# a sequential ramp's endpoints (segment_length_colors) and, unmixed, as an
# alternating pair (segment_row_colors) -- same two colors, two different
# encodings.
NEAR_WHITE = (245, 250, 255)
PALE_BLUE = (175, 210, 235)
NEUTRAL_GRAY = (220, 220, 220)

# Plot-only variant: keeps PALE_BLUE (the darker accent -- reads fine on a
# plot as-is) but swaps NEAR_WHITE for a green matching PALE_BLUE's own
# lightness/saturation (via colorsys HLS, not hand-picked) -- not NEAR_WHITE's
# own (much lighter) lightness, since NEAR_WHITE is specifically the swatch
# that all but disappears against a plot's white background; a green that
# merely repeated that same near-white lightness would have the same problem.
# Tables keep the all-blue pair (it works there); only graph shading
# (HeartRateGraph, LapsGraph) uses this one.
def _hue_rotate(rgb: tuple[int, int, int], hue: float) -> tuple[int, int, int]:
    h, l, s = colorsys.rgb_to_hls(*(c / 255 for c in rgb))
    r, g, b = colorsys.hls_to_rgb(hue, l, s)
    return tuple(round(c * 255) for c in (r, g, b))


_GREEN_HUE = 120 / 360
ACCENT_GREEN = _hue_rotate(PALE_BLUE, _GREEN_HUE)
PLOT_PALETTE = (ACCENT_GREEN, PALE_BLUE)

# Applied on top of PLOT_PALETTE wherever it shades a plot (HeartRateGraph,
# LapsGraph) -- overrides qcolor_to_mpl's own alpha=1.0, fainter than the
# table backgrounds so the shading reads as a background cue even next to a
# busier plot (e.g. the derivative overlay) rather than competing with it.
PLOT_SHADING_ALPHA = 0.3


def segment_length_colors(distance_m: pd.Series) -> list[QColor]:
    """Sequential color ramp keyed to each segment's own distance_m (Object
    2's derived column): NEAR_WHITE for the shortest segment in this session,
    PALE_BLUE for the longest, everything in between interpolated linearly.
    Understated by construction (see the shared palette above), so it reads
    as a subtle background cue -- distinguishable, but not competing with
    text legibility."""
    d = distance_m.astype(float)
    lo, hi = d.min(), d.max()
    span = hi - lo
    colors = []
    for value in d:
        frac = 0.0 if span == 0 else (value - lo) / span
        rgb = tuple(round(a + frac * (b - a)) for a, b in zip(NEAR_WHITE, PALE_BLUE))
        colors.append(QColor(*rgb))
    return colors


def segment_row_colors(
    seg_idx: pd.Series,
    palette: tuple[tuple[int, int, int], tuple[int, int, int]] = (NEAR_WHITE, PALE_BLUE),
) -> list[QColor]:
    """Alternates a light/dark pair by segment parity -- by default NEAR_WHITE/
    PALE_BLUE, the same two colors segment_length_colors uses as its ramp's
    endpoints, so the Laps and Segments tables share one visual language
    (same hue, same lightness) instead of each tab having its own unrelated
    palette. Pass palette=PLOT_PALETTE for graph shading, where the near-white
    end of the blue pair reads as barely-there against a plot's white
    background. A lap with no matching segment (not seen in practice, but
    tag_lap_segments doesn't guarantee it can't happen) falls back to
    NEUTRAL_GRAY rather than crashing on int(None)."""
    light, dark, neutral = QColor(*palette[0]), QColor(*palette[1]), QColor(*NEUTRAL_GRAY)
    colors = []
    for s in seg_idx:
        if pd.isna(s):
            colors.append(neutral)
        else:
            colors.append(light if int(s) % 2 == 0 else dark)
    return colors


def qcolor_to_mpl(color: QColor) -> tuple[float, float, float, float]:
    """QColor -> the (r, g, b, a) 0-1 float tuple matplotlib color args
    expect, so the same Qt-native colors used for table row backgrounds
    (segment_row_colors, segment_length_colors) can also shade a plot."""
    return color.getRgbF()


def _darken_mpl_color(
    rgba: tuple[float, float, float, float], factor: float = 0.6
) -> tuple[float, float, float, float]:
    """Reduces an mpl (r, g, b, a) color's HLS lightness by factor (hue/
    saturation/alpha unchanged) -- used by HeartRateGraph to mark the
    selected lap's shaded span, since PLOT_SHADING_ALPHA already makes the
    unselected spans faint and a hue-only change wouldn't read as clearly as
    a lightness drop against that faint background."""
    h, l, s = colorsys.rgb_to_hls(*rgba[:3])
    r, g, b = colorsys.hls_to_rgb(h, l * factor, s)
    return (r, g, b, rgba[3])


# The exact blue a selected lap's span darkens to on the Heart Rate/Laps
# graphs (_darken_mpl_color applied to PALE_BLUE) -- RecoveryGraph reuses
# this constant rather than matplotlib's own "tab:blue" so the two graphs'
# blues are actually the same color, not just visually similar.
SELECTED_LAP_BLUE = _darken_mpl_color(qcolor_to_mpl(QColor(*PALE_BLUE)))


def _outlier_robust_ylim(values: pd.Series) -> tuple[float, float]:
    """(lo, hi) y-limits covering everything except values Tukey's IQR*1.5
    fence would call an outlier (e.g. a partial last lap dragging the axis
    out to 100+s while every real lap sits in a tight band), padded by 10% of
    the inlier range so edge points aren't clipped by the axis border itself.
    Falls back to the full data range if the fence would exclude everything
    (e.g. too few points for a fence to be meaningful)."""
    arr = values.to_numpy()
    q1, q3 = np.percentile(arr, [25, 75])
    iqr = q3 - q1
    lo_fence, hi_fence = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    inliers = arr[(arr >= lo_fence) & (arr <= hi_fence)]
    if inliers.size == 0:
        inliers = arr
    lo, hi = inliers.min(), inliers.max()
    pad = (hi - lo) * 0.1 or 1.0
    return lo - pad, hi + pad


def dataframe_to_table(
    df: pd.DataFrame,
    workout_start: pd.Timestamp | None = None,
    row_colors: list[QColor] | None = None,
) -> QTableWidget:
    """Generic, read-only DataFrame -> QTableWidget. The DataFrame's own
    index becomes the vertical header (via format_value -- e.g. the Recovery
    tab's seconds-since-peak index) and its columns the horizontal header
    (via column_label, so known data columns get a friendly name and
    anything else, like the Recovery tab's per-gap timestamp columns, still
    gets format_value's Timestamp handling)."""
    table = QTableWidget(len(df), len(df.columns))
    table.setHorizontalHeaderLabels([column_label(c, workout_start) for c in df.columns])
    table.setVerticalHeaderLabels([format_value(i, workout_start) for i in df.index])
    table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

    for row in range(len(df)):
        color = row_colors[row] if row_colors is not None else None
        for col in range(len(df.columns)):
            item = QTableWidgetItem(format_value(df.iat[row, col], workout_start))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if color is not None:
                item.setBackground(color)
            table.setItem(row, col, item)
    return table


def load_objects(
    json_path: Path,
) -> tuple[pd.DataFrame, float, pd.DataFrame, list[pd.DataFrame], pd.DataFrame, pd.Timestamp]:
    """JSON path -> (laps_tagged, lap_length_m, segments_table, gaps, hr,
    workout_start). Object 3 (gaps) and the raw hr series are returned as-is,
    not reduced to recovery curves here -- that computation now depends on
    RecoveryTab's own current parameter values, which don't exist until the
    tab is built. lap_length_m is returned rather than a precomputed
    lap_pace(...) result, since LapsTab now has its own configurable
    parameter too (which distance to normalize pace to) and calls lap_pace
    itself whenever that changes. segments_table has no configurable
    parameters (segment_table is a fixed function of lapLength), so it's
    computed once, here, like Object 1 itself. Pulled out on its own so both
    the initial load and File -> Open's reload go through one path."""
    workout = load_workout(json_path)
    laps = intervals_to_df(workout["laps"])
    segments = intervals_to_df(workout["segments"])
    hr = heart_rate_df(workout["heartRateData"])
    workout_start = pd.to_datetime(workout["start"])
    lap_length_m = workout["lapLength"]["qty"]

    laps_tagged = tag_lap_segments(laps, segments)
    seg_table_df = segment_table(laps_tagged, segments, lap_length_m)
    gaps = segment_gap_heart_rate(segments, hr)
    return laps_tagged, lap_length_m, seg_table_df, gaps, hr, workout_start


class RecoveryGraph(QWidget):
    """The Graph sub-tab: aggregate_recovery_curves' mean line plus both
    bands at once, layered rather than toggled -- the wider min/max range
    (gray, drawn first/underneath) and the narrower mean ± 1σ range
    (SELECTED_LAP_BLUE, drawn on top -- the same blue a selected lap's span
    darkens to on the Heart Rate/Laps graphs, not matplotlib's own
    "tab:blue"), so both are visible together with no control needed to
    switch between them. Both come from the one aggregate_recovery_curves
    call RecoveryTab.generate() feeds in via set_summary. HRR30/HRR60 (see
    recovery_hrr) are shown as text in the axes' top-right corner (HRR30
    above HRR60) when the current min_duration_s guarantees every
    contributing gap actually reaches that far -- i.e. only when
    min_duration_s >= 30 / >= 60 respectively -- rather than whenever the
    data happens to reach that far by chance for however many gaps."""

    def __init__(self):
        super().__init__()
        self.summary: pd.DataFrame | None = None
        self.min_duration_s: float = 0.0

        layout = QVBoxLayout(self)
        self.figure = Figure(figsize=(6, 4))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.ax = self.figure.add_subplot(111)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

    def set_summary(self, summary: pd.DataFrame, min_duration_s: float) -> None:
        self.summary = summary
        self.min_duration_s = min_duration_s
        self.render()

    def render(self) -> None:
        self.ax.clear()
        if self.summary is not None and not self.summary.empty:
            s = self.summary
            self.ax.fill_between(
                s.index, s["min"], s["max"], alpha=0.20, color="tab:gray", label="min / max"
            )
            self.ax.fill_between(
                s.index, s["mean"] - s["std"], s["mean"] + s["std"],
                alpha=0.35, color=SELECTED_LAP_BLUE, label="mean ± 1σ",
            )
            self.ax.plot(s.index, s["mean"], color=SELECTED_LAP_BLUE, lw=2, label="mean")
            self.ax.axhline(0, color="gray", lw=0.8, ls="--", zorder=0)
            self.ax.set_xlabel("seconds since peak HR")
            self.ax.set_ylabel("heart rate change from peak (bpm)")
            self.ax.legend()

            hrr_lines = []
            if self.min_duration_s >= 30:
                hrr30 = recovery_hrr(s, 30)
                if hrr30 is not None:
                    hrr_lines.append(f"HRR30 = {hrr30:.1f} bpm")
            if self.min_duration_s >= 60:
                hrr60 = recovery_hrr(s, 60)
                if hrr60 is not None:
                    hrr_lines.append(f"HRR60 = {hrr60:.1f} bpm")
            if hrr_lines:
                self.ax.text(
                    0.98, 0.98, "\n".join(hrr_lines),
                    transform=self.ax.transAxes, ha="right", va="top", fontsize=10,
                    bbox=dict(facecolor="white", edgecolor="none", alpha=1.0, pad=4),
                )

            self.figure.tight_layout()
        self.canvas.draw()


class RecoveryTab(QWidget):
    """The Recovery tab as a single unit: one parameter-control row (min
    duration, an optional max peak offset, grid step, and the aggregate
    truncation threshold -- segment_gap_recovery_curves' three parameters
    plus aggregate_recovery_curves' min_n) sitting above two inner sub-tabs,
    Graph and Table (Graph first/shown by default). Both sub-tabs are meant
    to always reflect the exact same current parameter values -- there is
    exactly one control row, not one
    per view -- so the table and the graph can never silently disagree about
    what parameters produced what's on screen. Live-updating: every control
    change (typing/spinning a value, toggling a checkbox) calls generate()
    directly, no separate Generate button to press first."""

    def __init__(self, initial_min_duration_s: float = 60.0):
        super().__init__()
        self.gaps: list[pd.DataFrame] = []
        self.hr: pd.DataFrame | None = None
        self.workout_start: pd.Timestamp | None = None

        layout = QVBoxLayout(self)

        controls = QHBoxLayout()
        controls.addWidget(QLabel("Min duration (s):"))
        self.min_duration_spin = QDoubleSpinBox()
        self.min_duration_spin.setRange(0, 3600)
        self.min_duration_spin.setDecimals(1)
        self.min_duration_spin.setValue(initial_min_duration_s)
        self.min_duration_spin.valueChanged.connect(self.generate)
        controls.addWidget(self.min_duration_spin)

        self.max_offset_check = QCheckBox("Max peak offset (s):")
        controls.addWidget(self.max_offset_check)
        self.max_offset_spin = QDoubleSpinBox()
        self.max_offset_spin.setRange(0, 3600)
        self.max_offset_spin.setDecimals(1)
        self.max_offset_spin.setEnabled(False)
        self.max_offset_check.toggled.connect(self.max_offset_spin.setEnabled)
        self.max_offset_check.toggled.connect(self.generate)
        self.max_offset_spin.valueChanged.connect(self.generate)
        controls.addWidget(self.max_offset_spin)

        self.step_auto_check = QCheckBox("Auto grid step")
        self.step_auto_check.setChecked(True)
        controls.addWidget(self.step_auto_check)
        controls.addWidget(QLabel("Step (s):"))
        self.step_spin = QDoubleSpinBox()
        self.step_spin.setRange(0.1, 300)
        self.step_spin.setDecimals(1)
        self.step_spin.setValue(5.0)
        self.step_spin.setEnabled(False)
        self.step_auto_check.toggled.connect(lambda checked: self.step_spin.setEnabled(not checked))
        self.step_auto_check.toggled.connect(self.generate)
        self.step_spin.valueChanged.connect(self.generate)
        controls.addWidget(self.step_spin)

        controls.addWidget(QLabel("Truncate below:"))
        self.min_n_spin = QSpinBox()
        self.min_n_spin.setRange(1, 100)
        self.min_n_spin.setValue(5)
        self.min_n_spin.valueChanged.connect(self.generate)
        controls.addWidget(self.min_n_spin)
        controls.addWidget(QLabel("samples"))
        controls.addStretch()
        layout.addLayout(controls)

        self.sub_tabs = QTabWidget()
        layout.addWidget(self.sub_tabs)
        self.graph = RecoveryGraph()
        self.sub_tabs.addTab(self.graph, "Graph")
        self.sub_tabs.addTab(QTableWidget(), "Table")

    def set_data(self, gaps: list[pd.DataFrame], hr: pd.DataFrame, workout_start: pd.Timestamp) -> None:
        """Called on every load/reload (new gaps/hr/workout_start), then
        immediately generates once so the tab isn't left showing stale data
        from a previously-loaded file."""
        self.gaps = gaps
        self.hr = hr
        self.workout_start = workout_start
        self.generate()

    def generate(self) -> None:
        if self.hr is None:
            return
        # Preserved and restored at the end rather than left alone, since
        # removeTab/insertTab below can otherwise shift which sub-tab ends up
        # current -- every live update should refresh both views without
        # forcing whichever one (Table or Graph) you weren't looking at back
        # to front.
        current_sub_tab = self.sub_tabs.currentIndex()

        max_peak_offset_s = self.max_offset_spin.value() if self.max_offset_check.isChecked() else None
        step_s = None if self.step_auto_check.isChecked() else self.step_spin.value()
        recovery_curves = segment_gap_recovery_curves(
            self.gaps, self.hr,
            min_duration_s=self.min_duration_spin.value(),
            max_peak_offset_s=max_peak_offset_s,
            step_s=step_s,
        )
        table = dataframe_to_table(recovery_curves, self.workout_start)
        old_table = self.sub_tabs.widget(1)
        self.sub_tabs.removeTab(1)
        old_table.deleteLater()
        self.sub_tabs.insertTab(1, table, "Table")

        self.graph.set_summary(
            aggregate_recovery_curves(recovery_curves, min_n=self.min_n_spin.value()),
            self.min_duration_spin.value(),
        )

        self.sub_tabs.setCurrentIndex(current_sub_tab)


class HeartRateGraph(QWidget):
    """The raw heart rate trace -- heartRateData straight from the JSON, no
    derivation -- plotted against elapsed time (minutes since workout_start,
    the same elapsed-time convention this app's tables use for their mm:ss
    columns), optionally (set_show_shading, on by default) annotated with each
    lap's own [start, end] span shaded via segment_row_colors -- the same
    NEAR_WHITE/PALE_BLUE-alternating-by-segment-parity colors the Laps tab
    uses, so a segment still reads as one visual block here too. Rest gaps
    between segments and turn-time gaps between laps are left unshaded, so
    they read as the trace's own quiet periods rather than being folded into
    either neighboring lap. Shading is drawn on both panels when the
    derivative is split out (same spans, same colors, one flag controls
    both) and is independently toggleable from the trace itself since it
    competes for visual attention -- most useful together with a clean
    trace, busiest with both on at once. Clicking
    anywhere inside a lap's shaded span selects it: that lap's span is drawn
    at reduced lightness (_darken_mpl_color) so the selection itself is
    visible even with shading off elsewhere, and its lap # and elapsed_s (the
    same duration the Laps table's "Elapsed (s)" column shows) are shown
    near the top of the panel, centered horizontally over that lap's own
    span -- x pinned to the lap's midpoint in data coordinates, y pinned near
    the top in axes-fraction coordinates via a blended transform, so the
    label tracks the lap horizontally under pan/zoom but never drifts
    off-screen vertically. A click while the toolbar's pan/zoom tool is
    engaged is left alone (selection would otherwise fight the drag), and a
    selection click otherwise preserves the current zoom/pan across the
    redraw (_render_preserving_view) rather than resetting it. set_show_
    derivative optionally splits the figure into two stacked, x-linked
    subplots (2/3 HR on top, 1/3 dHR/dt in bpm/min below -- np.gradient
    against elapsed *minutes*, so no separate unit conversion is needed)
    rather than overlaying the derivative on a twin y-axis, since a twin
    axis competed too much with the shading and the selection label for
    visual attention. self.ax and self.ax_deriv are two persistent Axes
    created once in __init__ and never destroyed -- splitting the
    derivative in/out reassigns which cell(s) of one shared GridSpec each
    occupies (set_subplotspec) and toggles ax_deriv's visibility, rather
    than figure.clear()-ing and recreating them on every render. That
    matters because NavigationToolbar2QT's pan/zoom history is keyed by
    axes identity -- recreating the Axes object on every click or checkbox
    toggle (the original approach) silently orphaned that history, making
    Home/Back/Forward stop working after the first interaction. A
    NavigationToolbar2QT (pan/zoom-rectangle/home/save) makes it
    interactive rather than a static image."""

    def __init__(self):
        super().__init__()
        self.laps_tagged: pd.DataFrame | None = None
        self.workout_start: pd.Timestamp | None = None
        self.hr: pd.DataFrame | None = None
        self.show_derivative: bool = False
        self.show_shading: bool = True
        self.selected_lap_idx: int | None = None

        layout = QVBoxLayout(self)
        self.figure = Figure(figsize=(8, 4))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        # One GridSpec, reused for this graph's whole life -- self.ax and
        # self.ax_deriv are created once and never destroyed. Splitting the
        # derivative in/out is done by reassigning which GridSpec cell(s)
        # each axes occupies (set_subplotspec) and toggling ax_deriv's
        # visibility, not by figure.clear()-ing and recreating Axes objects.
        # Recreating axes on every render (the original approach) orphaned
        # NavigationToolbar2QT's pan/zoom history -- it's keyed by axes
        # identity, so Home/Back/Forward silently stopped working after the
        # first click-to-select or checkbox toggle. Verified directly: with
        # the old approach, id(self.ax) changed on every _render() call, and
        # toolbar.home() no-op'd once a stale axes was in its nav stack.
        self._gridspec = GridSpec(2, 1, figure=self.figure, height_ratios=(2, 1))
        self.ax = self.figure.add_subplot(self._gridspec[:, 0])
        self.ax_deriv = self.figure.add_subplot(self._gridspec[1, 0], sharex=self.ax)
        self.ax_deriv.set_visible(False)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.lap_label = None
        self.canvas.mpl_connect("button_press_event", self._on_click)

    def set_data(self, hr: pd.DataFrame, laps_tagged: pd.DataFrame, workout_start: pd.Timestamp) -> None:
        self.hr = hr
        self.laps_tagged = laps_tagged
        self.workout_start = workout_start
        self.selected_lap_idx = None
        self._render()

    def set_show_derivative(self, show: bool) -> None:
        self.show_derivative = show
        self._render_preserving_view()

    def set_show_shading(self, show: bool) -> None:
        self.show_shading = show
        self._render_preserving_view()

    def _render(self) -> None:
        self.ax.clear()
        self.ax_deriv.clear()
        if self.show_derivative:
            self.ax.set_subplotspec(self._gridspec[0, 0])
            self.ax_deriv.set_subplotspec(self._gridspec[1, 0])
            self.ax_deriv.set_visible(True)
        else:
            self.ax.set_subplotspec(self._gridspec[:, 0])
            self.ax_deriv.set_visible(False)
        self.lap_label = None

        hr, laps_tagged, workout_start = self.hr, self.laps_tagged, self.workout_start
        if hr is not None and not hr.empty:
            selected_mid = None
            selected_text = None
            if laps_tagged is not None and not laps_tagged.empty:
                starts = (laps_tagged["start"] - workout_start).dt.total_seconds() / 60
                ends = (laps_tagged["end"] - workout_start).dt.total_seconds() / 60
                colors = segment_row_colors(laps_tagged["seg_idx"], palette=PLOT_PALETTE)
                for start, end, color, lap_idx, elapsed_s in zip(
                    starts, ends, colors, laps_tagged["index"], laps_tagged["elapsed_s"]
                ):
                    idx_int = int(lap_idx)
                    mpl_color = qcolor_to_mpl(color)
                    if idx_int == self.selected_lap_idx:
                        mpl_color = _darken_mpl_color(mpl_color)
                        selected_mid = (start + end) / 2
                        selected_text = f"Lap {idx_int}\n{elapsed_s:.2f} s"
                    if self.show_shading:
                        self.ax.axvspan(start, end, color=mpl_color, alpha=PLOT_SHADING_ALPHA, zorder=0)
                        if self.show_derivative:
                            self.ax_deriv.axvspan(start, end, color=mpl_color, alpha=PLOT_SHADING_ALPHA, zorder=0)

            elapsed_min = (hr["date"] - workout_start).dt.total_seconds() / 60
            self.ax.plot(elapsed_min, hr["hr_avg"], color="tab:red", lw=1, zorder=2)
            self.ax.set_ylabel("heart rate (bpm)")

            if self.show_derivative:
                d_hr = np.gradient(hr["hr_avg"].to_numpy(), elapsed_min.to_numpy())
                self.ax_deriv.plot(elapsed_min, d_hr, color="tab:purple", lw=0.8, zorder=2)
                self.ax_deriv.axhline(0, color="gray", lw=0.5, ls="--", zorder=0)
                self.ax_deriv.set_ylabel("dHR/dt (bpm/min)", fontsize=9)
                self.ax_deriv.set_xlabel("elapsed time (min)")
                self.ax.tick_params(axis="x", labelbottom=False)
            else:
                # Axes.clear() does not reset tick_params overrides (unlike
                # the old recreate-the-axes-every-render approach, where a
                # brand new Axes always started with default tick
                # visibility) -- without this, toggling the derivative on
                # then off again left the x-axis tick numbers hidden forever
                # on this now-reused, persistent Axes.
                self.ax.tick_params(axis="x", labelbottom=True)
                self.ax.set_xlabel("elapsed time (min)")

            if selected_mid is not None:
                self.lap_label = self.ax.text(
                    selected_mid, 0.95, selected_text,
                    transform=blended_transform_factory(self.ax.transData, self.ax.transAxes),
                    ha="center", va="top", fontsize=10,
                    bbox=dict(facecolor="white", edgecolor="none", alpha=1.0, pad=4),
                )
            self.figure.tight_layout()
        self.canvas.draw()

    def _render_preserving_view(self) -> None:
        """Like _render, but keeps the current zoom/pan across the redraw.
        _render only clears and repositions the two persistent Axes (it no
        longer recreates them), but a fresh render still means fresh
        auto-scaled limits unless we explicitly restore the prior view --
        used by every re-render that isn't a brand new file load, where
        resetting to the full view is correct instead. ax_deriv's ylim is
        only restored if it was already visible going into this call: the
        first time the derivative panel appears, its "current" ylim is just
        matplotlib's untouched (0, 1) default (it's never had real data
        plotted on it before), and forcing that back on top of the fresh
        autoscaled range -- which set_ylim would also do, disabling
        autoscale on that axis in the process -- left it permanently stuck
        showing (0, 1) instead of the real dHR/dt range. Verified directly:
        toggling "Show derivative" on used to show a blank (0, 1) y-axis
        with only the shading spans visible, no purple line."""
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        deriv_was_visible = self.ax_deriv.get_visible()
        deriv_ylim = self.ax_deriv.get_ylim() if deriv_was_visible else None
        self._render()
        self.ax.set_xlim(xlim)
        self.ax.set_ylim(ylim)
        if deriv_ylim is not None and self.ax_deriv.get_visible():
            self.ax_deriv.set_ylim(deriv_ylim)
        self.canvas.draw_idle()

    def _on_click(self, event) -> None:
        if self.laps_tagged is None or self.laps_tagged.empty:
            return
        if self.toolbar.mode:
            # A pan/zoom drag is in progress (toolbar button engaged) -- let
            # NavigationToolbar2QT handle it rather than reselecting a lap
            # mid-drag.
            return
        # self.ax_deriv is always a real Axes (never None), still positioned
        # at its own GridSpec cell even when hidden (set_visible(False)
        # doesn't move it) -- but matplotlib's hit-testing excludes
        # invisible axes from event.inaxes entirely (verified directly), so
        # in single-panel mode a click there always resolves to self.ax
        # regardless. Accepting both here just avoids hardcoding which one
        # of the two is "the" click target, since that already varies
        # correctly by layout on its own.
        if event.inaxes not in (self.ax, self.ax_deriv) or event.xdata is None:
            return
        elapsed_min = event.xdata
        starts = (self.laps_tagged["start"] - self.workout_start).dt.total_seconds() / 60
        ends = (self.laps_tagged["end"] - self.workout_start).dt.total_seconds() / 60
        match = self.laps_tagged[(starts <= elapsed_min) & (elapsed_min <= ends)]
        self.selected_lap_idx = int(match.iloc[0]["index"]) if not match.empty else None
        self._render_preserving_view()


class HeartRateTab(QWidget):
    """Heart Rate tab: HeartRateGraph plus two independent checkboxes --
    "Show lap shading" (on by default) and "Show derivative (bpm/min)" (off
    by default) -- controlling its lap-span shading and its stacked dHR/dt
    subplot separately, since showing both together reads as busy. Checkboxes
    rather than LapsTab/RecoveryTab's radio-group patterns, since these are
    independent on/off toggles, not mutually exclusive options."""

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        controls = QHBoxLayout()
        self.shading_check = QCheckBox("Show lap shading")
        self.shading_check.setChecked(True)
        self.shading_check.toggled.connect(self._on_shading_toggle)
        controls.addWidget(self.shading_check)
        self.derivative_check = QCheckBox("Show derivative (bpm/min)")
        self.derivative_check.toggled.connect(self._on_derivative_toggle)
        controls.addWidget(self.derivative_check)
        controls.addStretch()
        layout.addLayout(controls)

        self.graph = HeartRateGraph()
        layout.addWidget(self.graph)

    def set_data(self, hr: pd.DataFrame, laps_tagged: pd.DataFrame, workout_start: pd.Timestamp) -> None:
        self.graph.set_data(hr, laps_tagged, workout_start)

    def _on_derivative_toggle(self, checked: bool) -> None:
        self.graph.set_show_derivative(checked)

    def _on_shading_toggle(self, checked: bool) -> None:
        self.graph.set_show_shading(checked)


class LapsGraph(QWidget):
    """Pace per lap, stacked with heart rate: two panels sharing one lap-#
    x-axis (matplotlib sharex, so pan/zoom on either panel via the toolbar
    moves both together). Upper panel: each lap's hr_avg (already in the
    table -- no recomputation) as a red dot, hr_min/hr_max as an error bar,
    the same overlay style used in legacy/swim_primitives.py's
    overlay_hr_metrics. Lower panel: the pace line+markers, in whatever unit
    LapsTab currently has selected (its y-label is set by the caller on
    every set_data call, since that unit can change), with horizontal
    gridlines and its y-axis auto-limited to _outlier_robust_ylim's Tukey-
    fence range -- excludes rare extreme laps (e.g. a partial last length)
    from the visible range rather than compressing every other lap's detail
    to fit them in. The pace line uses SELECTED_LAP_BLUE, the same blue as
    a selected lap on the Heart Rate graph and the Recovery graph's mean
    line/band, rather than matplotlib's own "tab:blue". Both panels get the
    same per-lap background band from segment_row_colors -- the exact same
    NEAR_WHITE/PALE_BLUE-by-segment-parity colors the Laps Table sub-tab
    uses for its row backgrounds, so a segment reads as one visual block the
    same way across table, pace and HR. A NavigationToolbar2QT (pan/zoom-
    rectangle/home/save, the standard matplotlib Qt toolbar) makes the plot
    interactive rather than a static image."""

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.figure = Figure(figsize=(6, 6))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.ax_hr = self.figure.add_subplot(211)
        self.ax_pace = self.figure.add_subplot(212, sharex=self.ax_hr)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

    def set_data(self, laps_with_pace: pd.DataFrame, y_label: str) -> None:
        self.ax_hr.clear()
        self.ax_pace.clear()
        if laps_with_pace is not None and not laps_with_pace.empty:
            lap_index = laps_with_pace["index"]
            colors = segment_row_colors(laps_with_pace["seg_idx"], palette=PLOT_PALETTE)
            for x, color in zip(lap_index, colors):
                mpl_color = qcolor_to_mpl(color)
                self.ax_hr.axvspan(x - 0.5, x + 0.5, color=mpl_color, alpha=PLOT_SHADING_ALPHA, zorder=0)
                self.ax_pace.axvspan(x - 0.5, x + 0.5, color=mpl_color, alpha=PLOT_SHADING_ALPHA, zorder=0)

            yerr = np.vstack([
                laps_with_pace["hr_avg"] - laps_with_pace["hr_min"],
                laps_with_pace["hr_max"] - laps_with_pace["hr_avg"],
            ])
            self.ax_hr.errorbar(
                lap_index, laps_with_pace["hr_avg"], yerr=yerr,
                fmt="o", ms=4, color="tab:red", ecolor="tab:red",
                elinewidth=1, capsize=2, zorder=2,
            )
            self.ax_hr.set_ylabel("heart rate (bpm)")
            self.ax_hr.tick_params(axis="x", labelbottom=False)

            pace = laps_with_pace["pace_s"]
            self.ax_pace.plot(
                lap_index, pace,
                color=SELECTED_LAP_BLUE, marker="o", ms=4, lw=1, zorder=2,
            )
            self.ax_pace.set_xlim(lap_index.min() - 0.5, lap_index.max() + 0.5)
            self.ax_pace.set_ylim(_outlier_robust_ylim(pace))
            self.ax_pace.grid(axis="y", color="gray", alpha=0.3, lw=0.5, zorder=1)
            self.ax_pace.set_xlabel("lap #")
            self.ax_pace.set_ylabel(y_label)
            self.figure.tight_layout()
        self.canvas.draw()


class LapsTab(QWidget):
    """Laps -- Object 1 (tag_lap_segments) plus a pace column from lap_pace,
    with one control row selecting which distance pace is normalized to: per
    length (the pool's own lapLength from the JSON, i.e. pace_s == elapsed_s
    unscaled), per 50m, or per 100m (the two standard swim-pace conventions).
    Driving two inner sub-tabs, Graph and Table (Graph first/shown by
    default), exactly like Recovery's structure -- switching the pace unit
    re-renders both immediately, live, same as every Recovery control now
    does too."""

    def __init__(self):
        super().__init__()
        self.laps_tagged: pd.DataFrame | None = None
        self.lap_length_m: float | None = None
        self.workout_start: pd.Timestamp | None = None

        layout = QVBoxLayout(self)

        controls = QHBoxLayout()
        controls.addWidget(QLabel("Pace:"))
        self.per_length_radio = QRadioButton("Per length")
        self.per_length_radio.setChecked(True)
        self.per_50_radio = QRadioButton("Per 50m")
        self.per_100_radio = QRadioButton("Per 100m")
        self.pace_group = QButtonGroup(self)
        for radio in (self.per_length_radio, self.per_50_radio, self.per_100_radio):
            self.pace_group.addButton(radio)
            controls.addWidget(radio)
            # Connected individually (not just one, as with a 2-button group
            # elsewhere in this file) because with 3+ mutually exclusive
            # buttons, a direct switch between the two NOT connected would
            # otherwise fire neither's toggled(True) on the button we're
            # listening to.
            radio.toggled.connect(self._render)
        controls.addStretch()
        layout.addLayout(controls)

        self.sub_tabs = QTabWidget()
        layout.addWidget(self.sub_tabs)
        self.graph = LapsGraph()
        self.sub_tabs.addTab(self.graph, "Graph")
        self.sub_tabs.addTab(QTableWidget(), "Table")

    def _target_distance_m(self) -> float:
        if self.per_50_radio.isChecked():
            return 50.0
        if self.per_100_radio.isChecked():
            return 100.0
        return self.lap_length_m

    def _pace_label(self) -> str:
        if self.per_50_radio.isChecked():
            return "Pace (s/50m)"
        if self.per_100_radio.isChecked():
            return "Pace (s/100m)"
        return f"Pace (s/{self.lap_length_m:.0f}m)"

    def set_data(self, laps_tagged: pd.DataFrame, lap_length_m: float, workout_start: pd.Timestamp) -> None:
        self.laps_tagged = laps_tagged
        self.lap_length_m = lap_length_m
        self.workout_start = workout_start
        self.per_length_radio.setText(f"Per length ({lap_length_m:.0f}m)")
        self._render()

    def _render(self) -> None:
        if self.laps_tagged is None:
            return
        # Captured/restored for the same reason as RecoveryTab.generate():
        # removeTab/insertTab on the Table tab (index 1) can otherwise shift
        # which sub-tab ends up current.
        current_sub_tab = self.sub_tabs.currentIndex()

        label = self._pace_label()
        paced = lap_pace(self.laps_tagged, self.lap_length_m, self._target_distance_m())
        display_df = paced.rename(columns={"pace_s": label})

        table = dataframe_to_table(
            display_df, self.workout_start, row_colors=segment_row_colors(display_df["seg_idx"])
        )
        old_table = self.sub_tabs.widget(1)
        self.sub_tabs.removeTab(1)
        old_table.deleteLater()
        self.sub_tabs.insertTab(1, table, f"Table ({len(display_df)} laps)")

        self.graph.set_data(paced, label)

        self.sub_tabs.setCurrentIndex(current_sub_tab)


def populate_tabs(
    tabs: QTabWidget,
    laps_tagged: pd.DataFrame,
    lap_length_m: float,
    segments_table: pd.DataFrame,
    gaps: list[pd.DataFrame],
    hr: pd.DataFrame,
    workout_start: pd.Timestamp,
    initial_min_duration_s: float = 60.0,
) -> None:
    """Clears tabs and rebuilds all three from scratch -- called both for the
    initial load and every File -> Open reload, so a QTabWidget can be reused
    in place rather than the whole window being torn down and rebuilt."""
    tabs.clear()

    laps_tab = LapsTab()
    laps_tab.set_data(laps_tagged, lap_length_m, workout_start)
    tabs.addTab(laps_tab, f"Laps ({len(laps_tagged)})")

    seg_table = dataframe_to_table(
        segments_table, workout_start, row_colors=segment_length_colors(segments_table["distance_m"])
    )
    tabs.addTab(seg_table, f"Segments ({len(segments_table)})")

    hr_tab = HeartRateTab()
    hr_tab.set_data(hr, laps_tagged, workout_start)
    tabs.addTab(hr_tab, "Heart Rate")

    recovery_tab = RecoveryTab(initial_min_duration_s)
    recovery_tab.set_data(gaps, hr, workout_start)
    tabs.addTab(recovery_tab, "Recovery")


class SwimTablesWindow(QMainWindow):
    """Owns the QTabWidget and the File -> Open action that reloads it
    in place from a newly chosen 'Pool Swim-*.json' export."""

    def __init__(self, repo_root: Path, min_duration_s: float = 60.0):
        super().__init__()
        self.repo_root = repo_root
        self.min_duration_s = min_duration_s

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.resize(1100, 800)

        open_action = QAction("&Open...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_file_dialog)
        self.menuBar().addMenu("&File").addAction(open_action)

    def open_file_dialog(self) -> None:
        start_dir = str(self.repo_root / "biometrics" / "ph")
        # Native dialog restored. A plain extension glob (*.json/*.JSON) is
        # the default (first) filter -- the native chooser was hiding
        # lowercase-.json files under a "Pool Swim-*.json" pattern that
        # combines a literal prefix with the extension wildcard in one glob;
        # a pure extension pattern is the most universally well-supported
        # filter shape. The more specific pattern is still offered as a
        # second option in the dropdown.
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Pool Swim export",
            start_dir,
            "JSON files (*.json *.JSON);;Pool Swim JSON (Pool Swim-*.json Pool Swim-*.JSON);;All files (*)",
        )
        if path:
            self.load(Path(path))

    def load(self, json_path: Path) -> None:
        try:
            laps_tagged, lap_length_m, seg_table_df, gaps, hr, workout_start = load_objects(json_path)
        except Exception as exc:
            QMessageBox.critical(self, "Couldn't load file", f"{json_path.name}:\n{exc}")
            return
        populate_tabs(
            self.tabs, laps_tagged, lap_length_m, seg_table_df, gaps, hr, workout_start, self.min_duration_s
        )
        self.setWindowTitle(f"Swim data objects -- {json_path.name}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("json_path", nargs="?", help="Path to a 'Pool Swim-*.json' export; defaults to the newest one")
    parser.add_argument(
        "--min-duration", type=float, default=60.0,
        help="Minimum rest-gap duration (s) kept in the Recovery tab (default: 60)",
    )
    parser.add_argument("--selftest", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()

    if args.json_path:
        json_path = Path(args.json_path).expanduser()
        repo_root = find_repo_root(json_path)
    else:
        repo_root = find_repo_root(Path.cwd())
        json_path = newest_json(repo_root / "biometrics" / "ph")

    app = QApplication.instance() or QApplication(sys.argv)
    window = SwimTablesWindow(repo_root, min_duration_s=args.min_duration)
    window.load(json_path)

    if args.selftest:
        window.show()
        QApplication.processEvents()
        date_str = pd.to_datetime(load_workout(json_path)["start"]).strftime("%Y-%m-%d")
        out_path = repo_root / "biometrics" / "ph" / "plots" / f"{date_str}_swim_tables.png"
        window.grab().save(str(out_path))
        print(f"[selftest] saved {out_path}")
        window.close()
    else:
        window.show()
        print("Interactive window open -- File > Open (Ctrl+O) to switch exports, close the window to exit.")
        app.exec()


if __name__ == "__main__":
    main()
