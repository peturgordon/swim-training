# Backlog (software_utils)

Ideas and prototypes for the swim-data tooling raised along the way but not yet built into a real module — distinct from the root [`BACKLOG.md`](../BACKLOG.md), which is about training-methodology/scheduling ideas, not code.

## Segment-gap heart-rate recovery curve

Built as a one-off scratch script (not saved anywhere persistent) to see how heart rate decays during the rest gaps between segments — i.e. Object 3 (`segment_gap_heart_rate` in [`swim_data.py`](swim_data.py)), turned into an actual recovery-curve plot. The working pipeline, validated against the 2026-09-23 session:

1. Take Object 3's list of per-gap HR DataFrames.
2. Filter out gaps shorter than some minimum (60s worked well — shorter gaps are noisy and sometimes still catching the tail of HR ramp-up rather than real recovery, e.g. a few showed the "recovery" value going *up* instead of down at the very start).
3. For each kept gap, reference it at its own **peak HR sample** (not necessarily the first sample) — zero both the timestamp and the HR value there, and drop everything before the peak.
4. Determine the grid step from the *most common* interval between consecutive samples across the full raw `heartRateData` series (5s for the 2026-09-23 file, via `.diff().dt.total_seconds().round().mode()`), and interpolate (`np.interp`, with `left=right=np.nan` so it never extrapolates past a gap's own observed range) each gap's HR-drop curve onto that fixed grid.
5. At each grid point, compute `nanmean`/`nanstd` (or `nanmin`/`nanmax`) across whichever gaps actually reach that far, and plot mean ± 2·SD as a shaded band (seaborn-`lineplot`-`errorbar`-style), plotting only where at least `MIN_N` gaps contribute — truncating the far tail (past ~145s in that session) where the "average" would otherwise silently collapse to a single gap's raw trajectory with a zero-width, falsely-confident band.

Still open: this whole pipeline lives only as ad hoc code typed into the conversation, never saved to a file. Turning it into a real function (or a couple of functions: reference-at-peak, interpolate-to-grid, and plot-with-band, so the pieces are reusable separately) that lives alongside `swim_data.py`'s three objects — and deciding the default `MIN_N`, minimum-gap-duration, and min/max-vs-2SD choices, since all three were picked ad hoc during the exploration, not on any principled basis.

## Rebuilding the visualization layer on the three objects

Per the plan agreed while building `swim_data.py`: all future visualization should sit on top of Object 1 (lap↔segment join), Object 2 (segment table with distance), Object 3 (segment-gap HR), plus the raw HR timeseries — not on raw laps/segments directly. [`swim_primitives.py`](swim_primitives.py) still has the *pre*-object-era visualization code (`bars()`, `overlay_hr_metrics()`, `plot_primitives()`, the Qt `lap_segment_table()` widget) sitting alongside the object-building functions it used to own before they moved to `swim_data.py`. That old code still works but wasn't designed with the three-object structure in mind, and hasn't been revisited since the split. Needs a deliberate redesign pass, not just left as legacy scaffolding indefinitely.

## True lap duration bridging as a fourth object

`add_true_duration()` (still living in [`explore_pool_swim_json.py`](explore_pool_swim_json.py), never moved to `swim_data.py`) recovers the turn-time Apple's raw `elapsedDuration` excludes, by bridging each lap's true end to the next lap's start (or the segment's own end, for the last lap in a segment) — it depends on Object 1 (`tag_lap_segments`) already existing, which is exactly why it was proposed as the natural next step right after the lap↔segment join was verified solid. Got shelved when the conversation pivoted to reorganizing into `swim_data.py` instead. Still worth doing, and now has a natural home once it's ported over.

## Horizontal zoom + scrollbar for `swim_explorer.py`

Raised, then tabled pending a design decision that was never made: real elapsed time is highly irregular (turn gaps of ~5-16s vs. rest gaps up to 200s+ in one session), so a naive linear zoom/scrollbar over true elapsed time makes rest periods eat disproportionate screen space when zoomed in on a tight set. Three options were on the table — real elapsed time as-is (simplest, most faithful), visually compressing large gaps (more complex, distorts true timing), or just adding standard pan/zoom controls now and revisiting gap compression only if it's still annoying in practice. No decision was made before the conversation moved to `swim_primitives.py`/`swim_data.py` instead.
