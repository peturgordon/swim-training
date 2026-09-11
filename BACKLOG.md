# Backlog

Ideas and alternatives raised along the way but not acted on — not urgent, worth revisiting later. Distinct from the "Open questions" in [`research/research_findings.md`](research/research_findings.md), which are gaps in the *evidence*; these are practical proposals that were considered and deliberately set aside for now, not things research left unresolved.

## Alternative weekly rotation: sprint on Saturday, endurance on Wednesday

Current schedule (see [`WORKFLOW.md`](WORKFLOW.md)): Monday = Technique + Aerobic Base, Wednesday = Speed Bridge (sprint), Saturday = Race Distance (endurance).

The fixed three training days give an asymmetric rest pattern: 2 days between Sat→Mon, 2 days between Mon→Wed, 3 days between Wed→Sat. Sprint work is the archetype most sensitive to residual fatigue — quality degrades fastest without full recovery — so there's a case for giving it the *longest* gap rather than one of the 2-day ones. That would mean: Mon = Technique + Aerobic Base, Wed = Endurance, Sat = Sprint.

**Trade-off:** this puts the hardest, most neurologically demanding session on a weekend day, and 2 days between a Saturday max-effort sprint session and Monday's technique work is plausible but unproven as enough neuromuscular recovery.

**Not evidence-mandated either way** — [`research/research_findings.md`](research/research_findings.md) doesn't resolve scheduling at this resolution (see [Training Framework](guides/training-framework.html)'s principle 6, on periodization for limited-hours swimmers being an acknowledged evidence gap). Worth reconsidering if the current arrangement doesn't feel right in practice — especially if Wednesday sprint sessions feel undercooked on only 2 days' recovery from Monday.

## A practical logistics landing page

Right now, the schedule (Mon/Wed/Sat, one hour, which archetype on which day) only lives buried inside [`WORKFLOW.md`](WORKFLOW.md) — a maintenance runbook, not somewhere a visitor would think to look for "when does this actually happen." Location isn't recorded anywhere in the repo at all, and time-of-day isn't either.

Idea: a simple page (could just become the main content of [`index.md`](index.md), or a separate page linked from it) stating plainly: where (pool/location), which days, what time, how long, and the split — the practical facts, distinct from the research/framework/guides, which are about *what* to swim rather than *when and where*.

## Practical metrics capture at poolside

[Training Framework's tracking section](guides/training-framework.html#tracking) already recommends what to record (stroke count, CSS, heart rate, RPE, SWOLF) but assumes some way to actually capture it mid-session — and that part is unsolved. Pen and paper doesn't survive pool water, and relying on memory for exact numbers (stroke counts per rep, split times) after a hard set isn't reliable.

The "how" side is now researched and answered — see [`research/poolside_tools.md`](research/poolside_tools.md) (waterproof slates, swim-tracking smartwatches, smart goggles, voice memo, training partner, and which metrics need instant capture vs. survive memory). Still open: actually picking one and adopting it in practice — the research lays out options, it doesn't make the choice for Petur.

## A CSV (or similar) schema for aggregating metrics over the season

The plan is to capture metrics poolside somehow (see above), then periodically aggregate results into a CSV or similar in this repo to track progress over the season — but nothing defines what that file looks like yet: no fixed column names, no location, no process for turning a practice file's prose "Metrics to capture" section into a structured row. Each archetype tracks different things (stroke count for Technique/Race Distance days, RPE/pulse for Speed Bridge days), so the schema needs to accommodate that rather than force one flat table. Worth settling column names and format before there are several weeks of inconsistently-worded entries to reconcile by hand.

## Calibrating a real personal heart-rate-zone table

The framework's zones are pace/CSS-based, not heart-rate-based, and no validated numeric HR-zone table exists for masters swimmers specifically. A single-pass (non-adversarially-verified) research pass — see [`research/heart_rate_zones.md`](research/heart_rate_zones.md) — worked out an age-formula-based z1–z5 bpm table for age 43–44 (Tanaka formula, ~178bpm estimated max) and traced the log's "z1 white … z5 purple" naming to Jon Urbanchek's color system, whose absolute bpm values are calibrated for young elite swimmers, not scaled to age — a likely explanation for why the earlier anecdotal ~120bpm anchor (logged then reverted 2026-09-08) read as too low against a real pulse count.

Still open: the formula-based table is a placeholder, not a personal measurement. A real resting HR + a genuine max-effort HR reading (e.g. right after the hardest rep of a Speed Bridge day, or during/after the next CSS time trial) would replace it with an actual personal number.

## Evolving the training over the season

How should sessions change as fitness genuinely improves — raising the distance cap, tightening target paces, shifting the effort-zone balance — separate from what happens if a target meet or endurance event gets added to the calendar? [Training Framework](guides/training-framework.html#framework)'s own principle 6 (train in blocks, not a straight line) and its "meet calendar" open question already flag the meet-driven side of this as an acknowledged evidence gap. This is the broader version: ongoing progression logic even with no meet in sight, and how the CSS retest already recommended every 6–8 weeks should actually feed back into adjusting the framework, rather than just being logged and left there.
