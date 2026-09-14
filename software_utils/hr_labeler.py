#!/usr/bin/env python3
"""
Heart-rate segment labeler.

Loads a "Pool Swim-Heart Rate-*.csv" export. There's no upfront count to
set: it starts with exactly one segment, and confirming the last segment
in the list is what adds the next one -- there's no other way to add a
segment (short of deleting everything, which bootstraps a fresh one).
Segments have no free-text name, just a running number reflecting current
table position (stays correct through Sort by Start and deletions). You
describe each one by hand: stroke, distance, and which accessories were on
(pull buoy / fins / paddles / kickboard) -- via a table on the right.
Pressing Delete while a row is the active one removes that segment
outright, confirmed or not -- there's no separate delete button. The
matching practices/YYYY-MM-DD.md, if found, is shown verbatim in a
read-only panel above the table purely as a reference, so you don't have
to remember the plan; nothing is auto-parsed from it.

Segments are fully INDEPENDENT: each has its own start and end, not shared
with any neighbor. There's no assumption that one segment's end is the next
one's start -- real rest happens between them. A freshly added segment is
UNDEFINED (no start/end at all, nothing drawn for it) until you drag out
its rough span directly on the plot -- only then do the usual green
(start) / red (end) fine-tuning markers appear, sitting near the top of
the plot (not on the trace, so they never obscure the data), each with a
thin guide line down to the trace for alignment. Click any row to jump
straight to it (any order), drag a marker or nudge it one real sample at a
time with the arrow keys (↑/↓ picks which marker the arrows move), then
press Enter to accept it -- from the plot OR from the table, it's the same
key -- that's the ONLY thing that marks a segment confirmed (dragging alone
does not); a confirmed segment's shading turns light gray and stays that
way even after you move on to another one. Enter again on an
already-confirmed segment unconfirms it in place, to fix one you thought
was done. A segment can't be confirmed until it has a Distance entered.

Markers are not prevented from crossing anything -- another segment's
edges, or even the segment's own other edge. The only hard limit is the
recording's own start/end, since there's no data beyond that to snap to.
Overlapping segments aren't blocked either, just flagged by name in a
small ambient label (not a popup).

Pool length and indoor/outdoor are set once per pool, not per segment --
two dropdowns above the practice outline. They're remembered across runs
(in software_utils/.hr_labeler_config.json, gitignored) since you're
usually at the same pool session after session, but stay editable per file.

Repo layout this script expects: itself in <repo>/software_utils/, HR
recordings (and their exports) in the sibling <repo>/metrics/, matched
practice write-ups in <repo>/practices/YYYY-MM-DD.md.

Export writes two files next to the recording, named deterministically
from ITS OWN filename -- there's no save dialog, on purpose, so a later
batch process can predict the output names. Neither file names segments by
number (no segment_name/segment_type column) -- start/end times already
identify a row, and the table only ever shows a running number anyway.
"<name>_segments.csv" has one row per CONFIRMED segment: pool
length/environment, stroke, distance (with its unit, e.g. "200 m"),
start/end/duration, HR columns uniformly prefixed hr_ (hr_start, hr_end,
hr_mean, hr_peak, hr_min), then the four equipment booleans last.
"<name>_annotated.csv" has every original HR sample row, with pool/stroke/
distance/equipment columns added the same way (equipment last) -- blank/
False for samples that fall in a rest gap outside any tracked segment.
Unconfirmed ("unfilled") segments -- typically just the spare one
auto-added after the last confirm -- are left out of both exports
entirely. If two segments overlap, the later one in the table wins for any
sample in the overlap.

Usage:
    python3 hr_labeler.py [path/to/Pool Swim-Heart Rate-*.csv]

If no path is given, the newest *.csv in ../metrics is used (excluding any
previously-exported *_segments.csv/*_annotated.csv files). A different
recording can also be opened later via the "Load CSV..." button, without
restarting.

Requires: pandas, matplotlib, PyQt6
"""
import sys
import os
import json
from pathlib import Path

os.environ.setdefault("QT_API", "pyqt6")

import pandas as pd
import matplotlib
matplotlib.use("QtAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QLabel, QFileDialog,
    QMessageBox, QHeaderView, QSplitter, QComboBox, QCheckBox,
    QPlainTextEdit, QStyledItemDelegate, QLineEdit,
)
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QColor

STROKE_OPTIONS = ["Free", "Back", "Breast", "Fly", "IM", "Mixed"]
ACCESSORY_KEYS = ["pull_buoy", "fins", "paddles", "kickboard"]

POOL_LENGTH_PRESETS = ["25 m", "50 m", "25 yd", "Other"]
ENVIRONMENT_OPTIONS = ["Indoor", "Outdoor"]

# Pool length/environment are properties of the POOL, not any one recording
# -- you're usually at the same pool session after session, so the last
# choice is remembered here (next to the script, not the recording) and
# pre-fills next time, rather than being re-picked from scratch every load.
CONFIG_PATH = Path(__file__).resolve().parent / ".hr_labeler_config.json"


def _load_config():
    try:
        return json.loads(CONFIG_PATH.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def _save_config(cfg):
    try:
        CONFIG_PATH.write_text(json.dumps(cfg))
    except OSError:
        pass  # remembering the default is a convenience, not worth crashing over

# row background tints -- confirmed segments stay a mild green even after you
# move on, the active row (while not everything is confirmed) is a soft
# yellow, so status doesn't need its own column.
COLOR_ACTIVE = QColor(255, 255, 153)
COLOR_CONFIRMED = QColor(198, 239, 206)
COLOR_DEFAULT = QColor(255, 255, 255)

# radius (px) around a marker's on-screen position that still counts as a hit --
# a bit generous since it's a small point target, not a full-height line
MARKER_PIXEL_TOLERANCE = 14

# how far up the plot (0=bottom, 1=top) the start/end markers sit -- kept off
# the trace itself so they never obscure the data while fine-tuning
MARKER_Y_FRAC = 0.94


class _EnterConfirmDelegate(QStyledItemDelegate):
    """Lets Enter confirm/unconfirm the active segment even while editing a
    table cell (e.g. typing the Distance) -- Qt's own cell editor would
    otherwise just consume Enter to commit and move to the next row."""
    def __init__(self, confirm_callback, parent=None):
        super().__init__(parent)
        self._confirm_callback = confirm_callback

    def eventFilter(self, editor, event):
        if event.type() == QEvent.Type.KeyPress and event.key() in (
                Qt.Key.Key_Return, Qt.Key.Key_Enter):
            # Explicitly commit the typed text to the model and close the
            # editor FIRST (rather than relying on the base delegate's own
            # Enter handling, which doesn't fire synchronously here) --
            # otherwise the confirm callback would run against the
            # still-stale (pre-edit) Distance value.
            self.commitData.emit(editor)
            self.closeEditor.emit(editor)
            self._confirm_callback()
            return True
        return super().eventFilter(editor, event)


def find_practice_md(csv_path, date_str):
    """Look for practices/YYYY-MM-DD.md as a sibling of the recording's own
    metrics/ folder (repo layout: <repo>/metrics/, <repo>/practices/) --
    derived from csv_path, not this script's own location. Shown verbatim
    as reference text only -- nothing here is parsed."""
    repo_root = Path(csv_path).resolve().parent.parent
    candidate = repo_root / "practices" / f"{date_str}.md"
    return candidate if candidate.exists() else None


def load_hr_csv(path):
    df = pd.read_csv(path)
    df["t"] = pd.to_datetime(df["Date/Time"])
    df = df.sort_values("t").reset_index(drop=True)
    df["hr"] = df["Avg (count/min)"].astype(float)
    return df


class LabelerWindow(QMainWindow):
    def __init__(self, csv_path):
        super().__init__()
        self._reset_segment_state()
        self._build_ui()
        self.load_csv(csv_path)

    def _reset_segment_state(self):
        """Everything that must go back to a blank slate whenever a CSV is
        (re)loaded -- shared by __init__ and load_csv (switching files on an
        already-open window) so there's exactly one place this can drift
        out of sync."""
        # Each segment is a fully independent record -- its own start/end,
        # not shared with any neighbor. See module docstring. A freshly
        # added segment has start=end=None ("undefined") until the user
        # drags out its span on the plot -- see _finalize_creation.
        self.segments = []  # list of dicts, grown one at a time via _add_new_segment
        self.active_idx = 0
        self.dragging_which = None     # None | "create" | "start" | "end"
        self.keyboard_target = "end"   # which marker arrow keys currently move

        # dynamic plot artists, rebuilt each render
        self._active_patch = None
        self._confirmed_patches = []   # persistent gray shading, one per confirmed segment
        self._start_marker = None      # green draggable start handle (sits above the plot)
        self._end_marker = None        # red draggable end handle (sits above the plot)
        self._start_guide = None       # thin vertical line down to the trace, for alignment
        self._end_guide = None
        self._title_artist = None
        self._finished_patch = None
        self._creating_patch = None    # live preview span while drag-creating a new segment
        self._creating_start_x = None
        self._creating_last_x = None

    def load_csv(self, csv_path):
        """Load (or switch to) a specific HR recording. Resets every
        per-file bit of state -- segments, plot, table, matched practice
        outline -- so this can be called again on an already-open window
        (see the "Load CSV..." button) instead of needing a fresh one per
        file."""
        self.csv_path = csv_path
        self.df = load_hr_csv(csv_path)
        self.t0 = self.df["t"].iloc[0]
        self.t_end = self.df["t"].iloc[-1]
        self.total_minutes = (self.t_end - self.t0).total_seconds() / 60
        self.min_elapsed = (self.df["t"] - self.t0).dt.total_seconds() / 60

        date_str = self.t0.strftime("%Y-%m-%d")
        self.practice_md_path = find_practice_md(csv_path, date_str)
        self.practice_text = (
            self.practice_md_path.read_text() if self.practice_md_path is not None
            else f"No matching practices/{date_str}.md found next to this recording's date."
        )
        self.outline.setPlainText(self.practice_text)

        self.setWindowTitle(f"HR Segment Labeler — {os.path.basename(csv_path)}")

        self._reset_segment_state()
        self._plot_base()
        self._add_new_segment()
        self._render_active()

    def _prompt_load_csv(self):
        start_dir = os.path.dirname(self.csv_path) if self.csv_path else os.getcwd()
        path, _ = QFileDialog.getOpenFileName(
            self, "Load HR recording", start_dir, "CSV files (*.csv)")
        if path:
            self.load_csv(path)

    # ---------------------------------------------------- pool metadata --
    def _on_pool_length_changed(self, text):
        self.pool_length_other_edit.setVisible(text == "Other")
        self._save_session_config()

    def _save_session_config(self):
        _save_config({
            "pool_length_combo": self.pool_length_combo.currentText(),
            "pool_length_other": self.pool_length_other_edit.text(),
            "environment": self.environment_combo.currentText(),
        })

    def _current_pool_length(self):
        if self.pool_length_combo.currentText() == "Other":
            return self.pool_length_other_edit.text().strip() or "Other"
        return self.pool_length_combo.currentText()

    def _current_environment(self):
        return self.environment_combo.currentText()

    @property
    def n_segments(self):
        return len(self.segments)

    @property
    def finished(self):
        return all(s["confirmed"] for s in self.segments)

    # ---------------------------------------------------------------- UI --
    def _build_ui(self):
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(splitter)

        left_widget = QWidget()
        left = QVBoxLayout(left_widget)
        self.fig, self.ax = plt.subplots(figsize=(11, 6))
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.toolbar = NavigationToolbar(self.canvas, self)
        left.addWidget(self.toolbar)
        left.addWidget(self.canvas)

        self.keyboard_hint = QLabel(
            "A new segment has no span yet -- drag across the plot to set one. Once defined: "
            "←/→ nudges the selected marker by one sample, ↑/↓ switches which marker (green/red) "
            "is selected, Enter confirms the segment and adds a new one (a Distance is required "
            "first) -- Enter again unconfirms it. Works from the plot or from the table. Delete "
            "removes the active segment outright."
        )
        self.keyboard_hint.setWordWrap(True)
        left.addWidget(self.keyboard_hint)

        zoom_row = QHBoxLayout()
        zoom_row.addWidget(QLabel("X-axis:"))
        self.pan_left_btn = QPushButton("◀ Pan")
        self.pan_left_btn.clicked.connect(lambda: self.pan_x(-1))
        zoom_row.addWidget(self.pan_left_btn)
        self.zoom_in_btn = QPushButton("Zoom In ⟷")
        self.zoom_in_btn.clicked.connect(lambda: self.zoom_x(0.5))
        zoom_row.addWidget(self.zoom_in_btn)
        self.zoom_out_btn = QPushButton("Zoom Out ⟷")
        self.zoom_out_btn.clicked.connect(lambda: self.zoom_x(2.0))
        zoom_row.addWidget(self.zoom_out_btn)
        self.zoom_reset_btn = QPushButton("Reset")
        self.zoom_reset_btn.clicked.connect(self.zoom_reset)
        zoom_row.addWidget(self.zoom_reset_btn)
        self.pan_right_btn = QPushButton("Pan ▶")
        self.pan_right_btn.clicked.connect(lambda: self.pan_x(1))
        zoom_row.addWidget(self.pan_right_btn)
        zoom_row.addStretch(1)
        left.addLayout(zoom_row)

        right_widget = QWidget()
        right = QVBoxLayout(right_widget)

        file_row = QHBoxLayout()
        self.load_csv_btn = QPushButton("Load CSV…")
        self.load_csv_btn.clicked.connect(self._prompt_load_csv)
        file_row.addWidget(self.load_csv_btn)
        file_row.addStretch(1)
        right.addLayout(file_row)

        # Pool length/environment: a property of the pool, not any one
        # recording -- see CONFIG_PATH. Pre-filled from the last-used
        # values, saved to both exported CSVs as constant columns.
        session_cfg = _load_config()
        session_row = QHBoxLayout()
        session_row.addWidget(QLabel("Pool:"))
        self.pool_length_combo = QComboBox()
        self.pool_length_combo.addItems(POOL_LENGTH_PRESETS)
        if session_cfg.get("pool_length_combo") in POOL_LENGTH_PRESETS:
            self.pool_length_combo.setCurrentText(session_cfg["pool_length_combo"])
        session_row.addWidget(self.pool_length_combo)
        self.pool_length_other_edit = QLineEdit()
        self.pool_length_other_edit.setPlaceholderText("e.g. 33 m")
        self.pool_length_other_edit.setText(session_cfg.get("pool_length_other", ""))
        self.pool_length_other_edit.setVisible(self.pool_length_combo.currentText() == "Other")
        self.pool_length_other_edit.setMaximumWidth(90)
        session_row.addWidget(self.pool_length_other_edit)
        session_row.addWidget(QLabel("Environment:"))
        self.environment_combo = QComboBox()
        self.environment_combo.addItems(ENVIRONMENT_OPTIONS)
        if session_cfg.get("environment") in ENVIRONMENT_OPTIONS:
            self.environment_combo.setCurrentText(session_cfg["environment"])
        session_row.addWidget(self.environment_combo)
        session_row.addStretch(1)
        right.addLayout(session_row)
        # connected AFTER pre-filling from config, so restoring the saved
        # values on startup doesn't immediately rewrite the config file
        self.pool_length_combo.currentTextChanged.connect(self._on_pool_length_changed)
        self.pool_length_other_edit.editingFinished.connect(self._save_session_config)
        self.environment_combo.currentTextChanged.connect(lambda _text: self._save_session_config())

        right.addWidget(QLabel("Practice outline (reference only -- not parsed):"))
        self.outline = QPlainTextEdit()
        self.outline.setReadOnly(True)
        self.outline.setMaximumHeight(220)
        right.addWidget(self.outline)

        count_row = QHBoxLayout()
        count_row.addWidget(QLabel(
            "Starts with one segment; confirming the last one adds a new one."))
        count_row.addStretch(1)
        self.sort_btn = QPushButton("Sort by Start")
        self.sort_btn.clicked.connect(self.sort_by_start)
        count_row.addWidget(self.sort_btn)
        right.addLayout(count_row)

        self.overlap_label = QLabel("")
        self.overlap_label.setStyleSheet("color: #b45309;")  # muted amber, ambient not alarming
        self.overlap_label.setWordWrap(True)
        right.addWidget(self.overlap_label)

        self.table = QTableWidget(0, 13)
        self.table.setHorizontalHeaderLabels(
            ["Stroke", "Distance [m]", "Duration", "Buoy", "Fins", "Paddles", "Board",
             "Start", "End", "HR Start", "HR End", "HR Mean", "HR Peak"]
        )
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setStretchLastSection(True)
        self.table.itemChanged.connect(self._on_table_item_changed)
        self.table.cellClicked.connect(self._on_row_clicked)
        # Enter confirms/unconfirms from the table too, not just the plot --
        # the event filter catches it when a row/cell is merely selected,
        # the delegate catches it while actively editing Distance (col 1),
        # since Qt would otherwise just consume Enter there to move on.
        # The same event filter also catches Delete, to drop the active
        # segment outright -- there's no separate delete button.
        self.table.installEventFilter(self)
        self.table.setItemDelegateForColumn(
            1, _EnterConfirmDelegate(self.toggle_confirm_active, self.table))
        right.addWidget(self.table)

        self.export_btn = QPushButton("Export CSV")
        self.export_btn.clicked.connect(self.export_csv)
        right.addWidget(self.export_btn)

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        self.canvas.mpl_connect("button_press_event", self._on_press)
        self.canvas.mpl_connect("motion_notify_event", self._on_motion)
        self.canvas.mpl_connect("button_release_event", self._on_release)
        self.canvas.mpl_connect("key_press_event", self._on_key_press)

    def eventFilter(self, obj, event):
        """Enter confirms/unconfirms and Delete removes the active segment,
        whenever focus is somewhere in the table (a selected cell, the
        stroke dropdown, an equipment checkbox) -- installed on those
        widgets in _build_ui/_rebuild_segment_rows. "Active" here means
        self.active_idx, the same segment the plot is showing -- clicking a
        row makes it active, so Delete always acts on whichever row you
        most recently clicked into, not on Qt's own (separate) cell-editing
        focus. Editing the Distance cell is handled separately, by
        _EnterConfirmDelegate, since that editor consumes Enter itself
        (Delete there just edits the text, as expected)."""
        if event.type() == QEvent.Type.KeyPress:
            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                self.toggle_confirm_active()
                return True
            if event.key() == Qt.Key.Key_Delete:
                self.delete_row(self.active_idx)
                return True
        return super().eventFilter(obj, event)

    # ----------------------------------------------------------- plotting --
    def _plot_base(self):
        """(Re)draws the static HR trace onto self.ax. Safe to call more
        than once on the same axes -- clears it first -- since load_csv
        calls this again when switching to a different recording."""
        self.ax.clear()
        self.ax.plot(self.min_elapsed, self.df["hr"], lw=1, color="tab:blue", zorder=2)
        self.ax.set_xlabel("minutes elapsed")
        self.ax.set_ylabel("HR (bpm)")
        self.ax.grid(True, alpha=0.3)
        self.ax.set_ylim(self.df["hr"].min() - 5, self.df["hr"].max() + 10)
        # always show the whole trace -- the active segment is highlighted, not
        # zoomed into, so the surrounding shape stays visible for recognition.
        self.ax.set_xlim(0, self.total_minutes)

    def _minutes(self, ts):
        return (ts - self.t0).total_seconds() / 60

    def _seg_label(self, idx):
        """Segments have no free-text name -- just a running number
        reflecting current table position, so it stays correct through
        Sort by Start and deletions without needing to be re-typed."""
        return f"Segment {idx + 1}"

    def _snap_to_data(self, minutes_value):
        """Nearest actual recorded sample to a raw position, so a segment
        edge (and the stats computed from it) always lands on a real data
        point rather than an interpolated moment between two."""
        idx = (self.min_elapsed - minutes_value).abs().idxmin()
        return self.df["t"].iloc[idx]

    # ------------------------------------------------------- segment count --
    def _add_new_segment(self):
        """Append one fresh, unconfirmed, UNDEFINED segment (start=end=None)
        -- nothing is auto-populated. The user defines its span by dragging
        on the plot (see _on_press/_finalize_creation), and only after that
        do the usual green/red fine-tuning markers appear."""
        self.segments.append({
            "stroke": STROKE_OPTIONS[0], "distance": "",
            "pull_buoy": False, "fins": False, "paddles": False, "kickboard": False,
            "start": None, "end": None, "confirmed": False,
        })
        self._rebuild_segment_rows()

    # -------------------------------------------------------------- zoom --
    def _zoom_center_minutes(self, lo, hi):
        """Where to center a zoom: the active segment's own midpoint if
        it's defined (drag-to-created already), otherwise the current
        view's midpoint -- so zooming in brings the segment you're
        working on into view rather than just tightening around wherever
        you happened to be looking."""
        if self.n_segments > 0:
            seg = self.segments[self.active_idx]
            if seg["start"] is not None:
                x0, x1 = self._minutes(seg["start"]), self._minutes(seg["end"])
                return (min(x0, x1) + max(x0, x1)) / 2
        return (lo + hi) / 2

    def _clamp_view(self, lo, hi):
        """Shift (never shrink) a [lo, hi] view so it fits inside the
        recording's own bounds -- shared by zoom_x and pan_x, which both
        need to slide a same-width window back in bounds rather than
        clipping it down to a narrower one."""
        if lo < 0:
            hi -= lo
            lo = 0
        if hi > self.total_minutes:
            lo -= (hi - self.total_minutes)
            hi = self.total_minutes
        return max(0.0, lo), min(self.total_minutes, hi)

    def zoom_x(self, factor):
        """Stretch (factor<1) or shrink (factor>1) the x-axis range only,
        centered on the active segment if there is one, clamped to the
        recording."""
        lo, hi = self.ax.get_xlim()
        center = self._zoom_center_minutes(lo, hi)
        half_width = (hi - lo) / 2 * factor
        half_width = max(0.1, min(half_width, self.total_minutes / 2))
        new_lo, new_hi = self._clamp_view(center - half_width, center + half_width)
        self.ax.set_xlim(new_lo, new_hi)
        self.canvas.draw_idle()

    def zoom_reset(self):
        self.ax.set_xlim(0, self.total_minutes)
        self.canvas.draw_idle()

    def pan_x(self, direction):
        """Shift the current view left (direction=-1) or right (+1) by 30%
        of its width, clamped to the recording -- no need to reach for the
        matplotlib toolbar's pan tool for a simple nudge."""
        lo, hi = self.ax.get_xlim()
        shift = (hi - lo) * 0.3 * direction
        new_lo, new_hi = self._clamp_view(lo + shift, hi + shift)
        self.ax.set_xlim(new_lo, new_hi)
        self.canvas.draw_idle()

    # ----------------------------------------------------------- plotting --
    def _clear_dynamic_artists(self):
        artists = [self._active_patch, self._start_marker, self._end_marker,
                   self._start_guide, self._end_guide, self._creating_patch,
                   self._title_artist, self._finished_patch] + self._confirmed_patches
        for artist in artists:
            if artist is not None:
                artist.remove()
        self._active_patch = self._start_marker = self._end_marker = None
        self._start_guide = self._end_guide = self._creating_patch = None
        self._title_artist = self._finished_patch = None
        self._confirmed_patches = []

    def _update_active_patch(self):
        """Redraw the active shading from wherever the active segment's own
        start/end currently sit -- via min/max so it still renders sanely
        even if the user has dragged them past each other (self-crossing
        isn't blocked; a negative-duration segment just shows up honestly
        in the table)."""
        seg = self.segments[self.active_idx]
        x0, x1 = self._minutes(seg["start"]), self._minutes(seg["end"])
        self._active_patch.set_x(min(x0, x1))
        self._active_patch.set_width(abs(x1 - x0))

    def _render_active(self):
        self._clear_dynamic_artists()

        # persistent gray shading for every OTHER confirmed segment, so
        # progress stays visible even after moving on -- segments are
        # independent now (can overlap or leave gaps), so this is a real
        # shaded span per segment, not just a thin tick.
        for i, seg in enumerate(self.segments):
            if seg["confirmed"] and i != self.active_idx:
                x0, x1 = self._minutes(seg["start"]), self._minutes(seg["end"])
                patch = self.ax.axvspan(min(x0, x1), max(x0, x1),
                                        color="lightgray", alpha=0.5, zorder=1)
                self._confirmed_patches.append(patch)

        if self.n_segments == 0:
            self._title_artist = self.ax.text(
                0.5, 1.02, "No tracked segments -- press Enter to add one.",
                transform=self.ax.transAxes, ha="center", va="bottom", fontsize=10)
        else:
            if self.finished:
                self._finished_patch = self.ax.axvspan(
                    0, self.total_minutes, color="lightgreen", alpha=0.1, zorder=0)
            seg = self.segments[self.active_idx]

            if seg["start"] is None:
                # undefined -- nothing to shade or show markers for yet;
                # drag on the plot (handled in _on_press) to define it.
                self._title_artist = self.ax.text(
                    0.5, 1.02, f"Segment {self.active_idx + 1}/{self.n_segments}: "
                               f"drag on the plot to set its span",
                    transform=self.ax.transAxes, ha="center", va="bottom", fontsize=10)
            else:
                seg_start_min = self._minutes(seg["start"])
                seg_end_min = self._minutes(seg["end"])
                self._active_patch = self.ax.axvspan(
                    min(seg_start_min, seg_end_min), max(seg_start_min, seg_end_min),
                    color="tab:orange", alpha=0.25, zorder=2)

                xaxis_t = self.ax.get_xaxis_transform()  # x in data coords, y in axes fraction

                self._start_guide = self.ax.axvline(seg_start_min, color="tab:green", lw=1, alpha=0.5, zorder=3)
                start_w = 3 if self.keyboard_target == "start" else 1
                self._start_marker, = self.ax.plot(
                    [seg_start_min], [MARKER_Y_FRAC], transform=xaxis_t, marker="o", ms=12,
                    color="tab:green", markeredgecolor="black", markeredgewidth=start_w,
                    clip_on=False, zorder=4)

                self._end_guide = self.ax.axvline(seg_end_min, color="tab:red", lw=1, alpha=0.5, zorder=3)
                end_w = 3 if self.keyboard_target == "end" else 1
                self._end_marker, = self.ax.plot(
                    [seg_end_min], [MARKER_Y_FRAC], transform=xaxis_t, marker="o", ms=12,
                    color="tab:red", markeredgecolor="black", markeredgewidth=end_w,
                    clip_on=False, zorder=4)

                status_word = "confirmed" if seg["confirmed"] else "not yet confirmed"
                finished_note = " — all segments confirmed" if self.finished else ""
                distance_note = (
                    " (enter a Distance to allow confirming)"
                    if not seg["confirmed"] and not str(seg["distance"]).strip() else ""
                )
                self._title_artist = self.ax.text(
                    0.5, 1.02, f"Segment {self.active_idx + 1}/{self.n_segments} ({status_word}): "
                               f"drag markers or use arrow keys (bold ring = keyboard target) — "
                               f"Enter confirms/unconfirms{finished_note}{distance_note}",
                    transform=self.ax.transAxes, ha="center", va="bottom", fontsize=10,
                )

        self._refresh_table()
        self.canvas.draw_idle()

    # ------------------------------------------------------------- drag --
    def _marker_display_xy(self, marker):
        x_data, y_data = marker.get_xdata()[0], marker.get_ydata()[0]
        return marker.get_transform().transform((x_data, y_data))

    def _on_press(self, event):
        if self.n_segments == 0 or event.inaxes != self.ax or self.toolbar.mode != "":
            return
        if event.x is None or event.y is None:
            return
        seg = self.segments[self.active_idx]
        if seg["start"] is None:
            # undefined segment -- this press begins a drag-to-create gesture
            # rather than grabbing a marker (there isn't one yet).
            if event.xdata is None:
                return
            self.dragging_which = "create"
            self._creating_start_x = self._creating_last_x = event.xdata
            self._creating_patch = self.ax.axvspan(
                event.xdata, event.xdata, color="tab:blue", alpha=0.2, zorder=2)
            self.canvas.draw_idle()
            return
        candidates = [("start", self._start_marker), ("end", self._end_marker)]
        best, best_dist = None, None
        for name, marker in candidates:
            mx, my = self._marker_display_xy(marker)
            dist = ((event.x - mx) ** 2 + (event.y - my) ** 2) ** 0.5
            if dist <= MARKER_PIXEL_TOLERANCE and (best_dist is None or dist < best_dist):
                best, best_dist = name, dist
        if best is not None:
            self.dragging_which = best

    def _on_motion(self, event):
        if self.dragging_which is None or event.inaxes != self.ax or event.xdata is None:
            return
        if self.dragging_which == "create":
            self._creating_last_x = event.xdata
            x0, x1 = sorted((self._creating_start_x, event.xdata))
            self._creating_patch.set_x(x0)
            self._creating_patch.set_width(x1 - x0)
            self.canvas.draw_idle()
            return
        if self.dragging_which == "end":
            self._drag_end(event.xdata)
        else:
            self._drag_start(event.xdata)
        self._refresh_table()
        self.canvas.draw_idle()

    def _finalize_creation(self):
        if self._creating_patch is not None:
            self._creating_patch.remove()
            self._creating_patch = None
        x0, x1 = sorted((self._creating_start_x, self._creating_last_x))
        start_ts, end_ts = self._snap_to_data(x0), self._snap_to_data(x1)
        if start_ts == end_ts:
            return  # too small a drag to resolve to two distinct samples -- try again
        seg = self.segments[self.active_idx]
        seg["start"], seg["end"] = start_ts, end_ts

    def _drag_end(self, xdata):
        raw_x = min(max(xdata, 0.0), self.total_minutes)
        snapped_ts = self._snap_to_data(raw_x)
        self.segments[self.active_idx]["end"] = snapped_ts
        self.keyboard_target = "end"
        new_x = self._minutes(snapped_ts)
        self._end_marker.set_data([new_x], [MARKER_Y_FRAC])
        self._end_guide.set_xdata([new_x, new_x])
        self._update_active_patch()

    def _drag_start(self, xdata):
        raw_x = min(max(xdata, 0.0), self.total_minutes)
        snapped_ts = self._snap_to_data(raw_x)
        self.segments[self.active_idx]["start"] = snapped_ts
        self.keyboard_target = "start"
        new_x = self._minutes(snapped_ts)
        self._start_marker.set_data([new_x], [MARKER_Y_FRAC])
        self._start_guide.set_xdata([new_x, new_x])
        self._update_active_patch()

    def _on_release(self, event):
        if self.dragging_which == "create":
            self._finalize_creation()
            self.dragging_which = None
            self._render_active()
        elif self.dragging_which is not None:
            self.dragging_which = None
            self._render_active()  # refresh title/marker emphasis, not just the table

    # ---------------------------------------------------------- keyboard --
    def _on_key_press(self, event):
        if event.key == "enter":
            self.toggle_confirm_active()
            return
        if self.n_segments == 0 or self.segments[self.active_idx]["start"] is None:
            return  # nothing to nudge/target-switch until the segment is defined
        if event.key in ("up", "down", "tab"):
            self.keyboard_target = "start" if self.keyboard_target == "end" else "end"
            self._render_active()
            return
        if event.key not in ("left", "right"):
            return
        self._nudge(self.keyboard_target, -1 if event.key == "left" else 1)

    def _nudge(self, target, direction):
        seg = self.segments[self.active_idx]
        current_idx = (self.df["t"] - seg[target]).abs().idxmin()
        new_idx = current_idx + direction
        if not (0 <= new_idx < len(self.df)):
            return  # only real hard limit: no data exists beyond the recording
        seg[target] = self.df["t"].iloc[new_idx]
        self._render_active()

    # -------------------------------------------------------- navigation --
    def _navigate_to(self, new_idx):
        if new_idx == self.active_idx:
            self._render_active()
            return
        self.active_idx = new_idx
        self._render_active()

    def confirm_active(self):
        """Confirm the active segment. If no OTHER segment is currently
        unconfirmed, that's the signal to add a fresh new one and move to
        it -- there's no separate "add segment" control; confirming is the
        only way new ones appear (besides bootstrapping back from zero).
        Revisiting and re-confirming an already-spare segment (one that
        still has another unconfirmed segment sitting elsewhere in the
        list) just confirms it in place and adds nothing.

        Deliberately NOT based on array position (e.g. "am I the last
        segment in the list") -- Sort by Start reorders the list by start
        time, which has nothing to do with which segment is the active
        "working" one, and using position caused Enter to stop adding a
        new line after a sort.

        A segment that's still undefined (no drag-to-create done yet) has
        nothing to confirm -- this is a no-op until it's been drawn. Same
        for one with no Distance entered yet -- that's a required field
        before a segment counts as confirmed."""
        if self.n_segments == 0:
            self._add_new_segment()
            self.active_idx = 0
            self._render_active()
            return
        seg = self.segments[self.active_idx]
        if seg["start"] is None or not str(seg["distance"]).strip():
            return
        self.segments[self.active_idx]["confirmed"] = True
        other_unconfirmed = any(
            not s["confirmed"] for i, s in enumerate(self.segments) if i != self.active_idx
        )
        if not other_unconfirmed:
            self._add_new_segment()
            self.active_idx = self.n_segments - 1
        self._render_active()

    def toggle_confirm_active(self):
        """The Confirm/Unconfirm button: confirms if not yet confirmed
        (adding a new segment if it was the last one, as above), or
        un-confirms in place if it already was -- e.g. to come back and
        fix a segment you thought was done."""
        if self.n_segments == 0:
            self.confirm_active()
            return
        if self.segments[self.active_idx]["confirmed"]:
            self.segments[self.active_idx]["confirmed"] = False
            self._render_active()
        else:
            self.confirm_active()

    def delete_row(self, row):
        """Remove the segment at row -- active or not, confirmed or not --
        via the Delete key while that row is active (see eventFilter).
        Fixes up active_idx accordingly. If it was the only segment left, a
        fresh undefined one takes its place, since there must always be one
        to work with."""
        if not (0 <= row < self.n_segments):
            return
        was_active = row == self.active_idx
        del self.segments[row]
        if not self.segments:
            self._add_new_segment()
            self.active_idx = 0
        else:
            if was_active:
                self.active_idx = min(row, len(self.segments) - 1)
            elif row < self.active_idx:
                self.active_idx -= 1
            self._rebuild_segment_rows()
        self._render_active()

    def _on_row_clicked(self, row, column):
        self._navigate_to(row)

    def sort_by_start(self):
        """Reorder the table by each segment's start time. Tracks the
        active segment by identity (not by old index, which would now
        point at the wrong segment) so it doesn't jump around."""
        active_seg = self.segments[self.active_idx] if self.segments else None
        # undefined (start=None) segments sort after every real one, using
        # a stable placeholder among themselves rather than comparing None
        self.segments.sort(
            key=lambda s: (s["start"] is None, s["start"] if s["start"] is not None else self.t0))

        if active_seg is not None:
            self.active_idx = next(
                i for i, s in enumerate(self.segments) if s is active_seg)
        self._rebuild_segment_rows()
        self._render_active()

    # -------------------------------------------------------- overlaps --
    def _overlapping_indices(self):
        spans = [None if s["start"] is None else (min(s["start"], s["end"]), max(s["start"], s["end"]))
                 for s in self.segments]
        overlaps = set()
        for i in range(len(spans)):
            if spans[i] is None:
                continue
            for j in range(i + 1, len(spans)):
                if spans[j] is None:
                    continue
                lo1, hi1 = spans[i]
                lo2, hi2 = spans[j]
                if lo1 < hi2 and lo2 < hi1:
                    overlaps.add(i)
                    overlaps.add(j)
        return overlaps

    def _update_overlap_label(self):
        overlaps = self._overlapping_indices()
        if not overlaps:
            self.overlap_label.setText("")
            return
        names = [self._seg_label(i) for i in sorted(overlaps)]
        self.overlap_label.setText("⚠ Overlapping segments: " + ", ".join(names))

    # ----------------------------------------------------------- table --
    def _hr_at(self, ts):
        idx = (self.df["t"] - ts).abs().idxmin()
        return self.df["hr"].iloc[idx]

    def _segment_stats(self, t_start, t_end):
        lo, hi = min(t_start, t_end), max(t_start, t_end)
        mask = (self.df["t"] >= lo) & (self.df["t"] <= hi)
        hr = self.df.loc[mask, "hr"]
        if len(hr) == 0:
            avg_hr = peak_hr = min_hr = float("nan")
        else:
            avg_hr, peak_hr, min_hr = hr.mean(), hr.max(), hr.min()
        # hr_start/hr_end use the segment's own (possibly inverted) start/end,
        # not the normalized lo/hi -- the actual reading at each marker.
        return dict(
            hr_start=self._hr_at(t_start), hr_end=self._hr_at(t_end),
            avg_hr=avg_hr, peak_hr=peak_hr, min_hr=min_hr,
        )

    def _row_qcolor(self, row):
        """Confirmed state is shown via row background, not a status
        column: mild green once confirmed (persists even off-active),
        soft yellow while active (unless everything is already confirmed,
        in which case green wins), plain white otherwise."""
        if row == self.active_idx and not self.finished:
            return COLOR_ACTIVE
        if self.segments[row]["confirmed"]:
            return COLOR_CONFIRMED
        return COLOR_DEFAULT

    @staticmethod
    def _fmt_duration(total_seconds):
        """mm:ss, with a leading '-' for a negative (inverted) duration --
        shown honestly rather than hidden or clamped to zero."""
        total_seconds = int(round(total_seconds))
        sign = "-" if total_seconds < 0 else ""
        m, s = divmod(abs(total_seconds), 60)
        return f"{sign}{m}:{s:02d}"

    @staticmethod
    def _format_distance(value):
        """The table only asks for a bare number (see the "Distance [m]"
        header), but the _segments.csv export should carry the unit
        explicitly -- e.g. "200 m" -- since that file is meant to stand on
        its own for later batch processing. Left alone if it already ends
        in "m" (someone typed the unit anyway) or is empty."""
        text = str(value).strip()
        if not text or text.lower().endswith("m"):
            return text
        return f"{text} m"

    def _rebuild_segment_rows(self):
        """Full rebuild of the table's rows and input widgets -- only called
        when the segment COUNT changes, so typing in Distance or toggling a
        checkbox never gets clobbered by a routine re-render."""
        self.table.blockSignals(True)
        self.table.setRowCount(len(self.segments))
        for row, seg in enumerate(self.segments):
            stroke_combo = QComboBox()
            stroke_combo.addItems(STROKE_OPTIONS)
            stroke_combo.setCurrentText(seg["stroke"])
            stroke_combo.currentTextChanged.connect(
                lambda text, r=row: self._on_stroke_changed(r, text))
            stroke_combo.installEventFilter(self)
            self.table.setCellWidget(row, 0, stroke_combo)

            self.table.setItem(row, 1, QTableWidgetItem(str(seg["distance"])))

            dur_item = QTableWidgetItem("")
            dur_item.setFlags(dur_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 2, dur_item)

            for col, key in zip((3, 4, 5, 6), ACCESSORY_KEYS):
                cb = QCheckBox()
                cb.setChecked(seg[key])
                cb.toggled.connect(lambda checked, r=row, k=key: self._on_accessory_toggled(r, k, checked))
                cb.installEventFilter(self)
                container = QWidget()
                lay = QHBoxLayout(container)
                lay.addWidget(cb)
                lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
                lay.setContentsMargins(0, 0, 0, 0)
                self.table.setCellWidget(row, col, container)

            for col in (7, 8, 9, 10, 11, 12):
                item = QTableWidgetItem("")
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, col, item)
        self.table.blockSignals(False)
        self._refresh_table()

    def _refresh_table(self):
        """Lightweight per-render update: only the computed/read-only
        columns. Never touches Stroke/Distance/accessory widgets, except to
        re-tint their background to match the row's confirmed/active state."""
        self.table.blockSignals(True)
        for row, seg in enumerate(self.segments):
            if seg["start"] is None:
                self.table.item(row, 2).setText("—")
                for col in (7, 8, 9, 10, 11, 12):
                    self.table.item(row, col).setText("—")
            else:
                stats = self._segment_stats(seg["start"], seg["end"])

                def fmt(v):
                    return f"{v:.0f}" if v == v else ""  # v==v is False only for NaN

                self.table.item(row, 2).setText(
                    self._fmt_duration((seg["end"] - seg["start"]).total_seconds()))
                self.table.item(row, 7).setText(seg["start"].strftime("%H:%M:%S"))
                self.table.item(row, 8).setText(seg["end"].strftime("%H:%M:%S"))
                self.table.item(row, 9).setText(fmt(stats["hr_start"]))
                self.table.item(row, 10).setText(fmt(stats["hr_end"]))
                self.table.item(row, 11).setText(fmt(stats["avg_hr"]))
                self.table.item(row, 12).setText(fmt(stats["peak_hr"]))

            color = self._row_qcolor(row)
            for col in (1, 2, 7, 8, 9, 10, 11, 12):
                self.table.item(row, col).setBackground(color)
            hexcolor = color.name()
            stroke_widget = self.table.cellWidget(row, 0)
            if stroke_widget is not None:
                stroke_widget.setStyleSheet(f"background-color: {hexcolor};")
            for col in (3, 4, 5, 6):
                w = self.table.cellWidget(row, col)
                if w is not None:
                    w.setStyleSheet(f"background-color: {hexcolor};")
        self.table.blockSignals(False)
        self._update_overlap_label()

    def _on_table_item_changed(self, item):
        row, col = item.row(), item.column()
        if row >= len(self.segments):
            return
        if col == 1:
            self.segments[row]["distance"] = item.text()

    def _on_stroke_changed(self, row, text):
        if row < len(self.segments):
            self.segments[row]["stroke"] = text

    def _on_accessory_toggled(self, row, key, checked):
        if row < len(self.segments):
            self.segments[row][key] = checked

    # ------------------------------------------------------------- export --
    def _build_summary_rows(self):
        """One row per CONFIRMED segment -- an unconfirmed one (most often
        just the spare segment auto-added after the last confirm, never
        filled in) is left out entirely, not exported as a blank row."""
        date_str = self.t0.strftime("%Y-%m-%d")
        pool_length = self._current_pool_length()
        environment = self._current_environment()
        rows = []
        for seg in self.segments:
            if not seg["confirmed"]:
                continue
            stats = self._segment_stats(seg["start"], seg["end"])
            rows.append({
                "date": date_str,
                "pool_length": pool_length,
                "environment": environment,
                "stroke": seg["stroke"],
                "distance": self._format_distance(seg["distance"]),
                "start_time": seg["start"].isoformat(),
                "end_time": seg["end"].isoformat(),
                "duration_s": round((seg["end"] - seg["start"]).total_seconds(), 1),
                "hr_start": round(stats["hr_start"], 1),
                "hr_end": round(stats["hr_end"], 1),
                "hr_mean": round(stats["avg_hr"], 1),
                "hr_peak": round(stats["peak_hr"], 1),
                "hr_min": round(stats["min_hr"], 1),
                "pull_buoy": seg["pull_buoy"],
                "fins": seg["fins"],
                "paddles": seg["paddles"],
                "kickboard": seg["kickboard"],
            })
        return rows

    def _build_annotated_df(self):
        """The original recording's own rows, untouched, with pool/stroke/
        distance/accessory columns added -- blank/False for samples that
        fall outside every tracked segment (i.e. rest). If segments
        overlap, later ones in the table win for samples in the overlap.
        Equipment columns are added last, after distance, so they land at
        the end of the file rather than in the middle of it."""
        raw = pd.read_csv(self.csv_path)
        t = pd.to_datetime(raw["Date/Time"])
        raw["pool_length"] = self._current_pool_length()
        raw["environment"] = self._current_environment()
        raw["stroke"] = ""
        raw["distance"] = ""
        for key in ACCESSORY_KEYS:
            raw[key] = False
        for seg in self.segments:
            if not seg["confirmed"]:
                continue  # unfilled entries are ignored, same as the summary export
            lo, hi = min(seg["start"], seg["end"]), max(seg["start"], seg["end"])
            mask = (t >= lo) & (t <= hi)
            raw.loc[mask, "stroke"] = seg["stroke"]
            raw.loc[mask, "distance"] = seg["distance"]
            for key in ACCESSORY_KEYS:
                raw.loc[mask, key] = seg[key]
        return raw

    def export_csv(self):
        """Writes both files next to the loaded recording, named
        deterministically from ITS filename -- <stem>_segments.csv and
        <stem>_annotated.csv. Deliberately not user-chosen: later batch
        processing needs a fixed, predictable naming scheme, not whatever
        name someone happened to type into a save dialog.

        The suffix is only ever APPENDED, never stripped first -- an
        earlier version tried to strip a pre-existing _segments/_annotated
        suffix (to cover loading an already-exported file by mistake), but
        stripping-then-reappending can collapse right back to the INPUT
        file's own path, silently overwriting and corrupting the loaded
        recording. Always appending makes that collision impossible: the
        derived name is strictly longer than the input's, no matter what
        the input happens to be named."""
        p = Path(self.csv_path)
        summary_path = p.with_name(p.stem + "_segments.csv")
        annotated_path = p.with_name(p.stem + "_annotated.csv")

        summary_rows = self._build_summary_rows()
        pd.DataFrame(summary_rows).to_csv(summary_path, index=False)
        self._build_annotated_df().to_csv(annotated_path, index=False)
        skipped = self.n_segments - len(summary_rows)
        note = f" ({skipped} unfilled segment{'s' if skipped != 1 else ''} ignored)" if skipped else ""
        QMessageBox.information(self, "Exported",
                                 f"Saved {len(summary_rows)} segment(s){note}:\n{summary_path}\n{annotated_path}")


def _default_metrics_dir():
    """<repo>/metrics -- this script lives in <repo>/software_utils, a
    sibling directory, since metrics/ holds only CSV data (recordings and
    their exports), not tooling."""
    return Path(__file__).resolve().parent.parent / "metrics"


def _default_csv_path():
    metrics_dir = _default_metrics_dir()
    candidates = sorted(metrics_dir.glob("*.csv"))
    candidates = [c for c in candidates
                  if not (c.name.endswith("_segments.csv") or c.name.endswith("_annotated.csv"))]
    if not candidates:
        print(f"No HR CSV found in {metrics_dir}, and none given on the command line.")
        sys.exit(1)
    return str(candidates[-1])


def main():
    csv_path = sys.argv[1] if len(sys.argv) > 1 else _default_csv_path()
    app = QApplication(sys.argv)
    win = LabelerWindow(csv_path)
    win.resize(1650, 850)
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
