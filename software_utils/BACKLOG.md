# Backlog (software_utils)

Ideas and prototypes for the swim-data tooling raised along the way but not yet built into a real module — distinct from the root [`BACKLOG.md`](../BACKLOG.md), which is about training-methodology/scheduling ideas, not code.

## Building the new visualization layer on `swim_data.py`

The three old tools (now in [`legacy/`](legacy/): `explore_pool_swim_json.py`, `swim_explorer.py`, `swim_primitives.py`) all predate the object model and have been set aside as the basis for new work — they still run and still produce their existing output, but nothing new gets built on them. All new visualization is meant to sit on top of `swim_data.py`'s objects (lap↔segment join, segment table with distance, segment-gap HR) plus the raw HR timeseries and the recovery-curve pipeline (`segment_gap_recovery_curves`/`aggregate_recovery_curves`) — starting fresh, not extending or porting logic from the legacy tools. First concrete piece: a plot of `aggregate_recovery_curves`' output as a mean line with a shaded band (min/max or ±2 SD, seaborn-`lineplot`-`errorbar`-style) — the recovery-curve pipeline itself is done (in `swim_data.py`), but nothing plots it yet.

## True lap duration bridging as a fourth object

`add_true_duration()` (still living in [`legacy/explore_pool_swim_json.py`](legacy/explore_pool_swim_json.py), never moved to `swim_data.py`) recovers the turn-time Apple's raw `elapsedDuration` excludes, by bridging each lap's true end to the next lap's start (or the segment's own end, for the last lap in a segment) — it depends on Object 1 (`tag_lap_segments`) already existing, which is exactly why it was proposed as the natural next step right after the lap↔segment join was verified solid. Got shelved when the conversation pivoted to reorganizing into `swim_data.py` instead. Still worth doing, and now has a natural home once it's ported over.

## Horizontal zoom + scrollbar for an interactive pace/HR viewer

Raised against [`legacy/swim_explorer.py`](legacy/swim_explorer.py), then tabled pending a design decision that was never made: real elapsed time is highly irregular (turn gaps of ~5-16s vs. rest gaps up to 200s+ in one session), so a naive linear zoom/scrollbar over true elapsed time makes rest periods eat disproportionate screen space when zoomed in on a tight set. Three options were on the table — real elapsed time as-is (simplest, most faithful), visually compressing large gaps (more complex, distorts true timing), or just adding standard pan/zoom controls now and revisiting gap compression only if it's still annoying in practice. Since `swim_explorer.py` is now archived rather than being extended, this decision applies to whatever new interactive viewer eventually replaces it, not to the old file itself.
