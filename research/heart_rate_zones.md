# Heart Rate Zones for a Masters Swimmer (Age 43–44)

A single-pass research pass, run 2026-09-11, working out real, sourced z1–z5 heart-rate zones for a 43–44 year-old masters swimmer — replacing the anecdotal ~120bpm anchor that was logged then reverted on 2026-09-08 (see `git show cf131ea` / `835ffeb` in this repo's history).

This is single-search-pass research, not the adversarially-verified process [`research_findings.md`](research_findings.md) runs (three independent reviewer agents instructed to try to refute each claim, only keeping what survives a 2/3 vote) — but the same standard applies: nothing below is stated as fact without a source, and confidence is flagged per finding rather than implied uniformly.

## Estimated max heart rate — *cross-checked across multiple secondary sources, primary formula source is a large meta-analysis*
Two competing age-based formulas, both from land-based (running/cycling) research, not swimming:
- **Fox: 220 − age** → 177 bpm (age 43) / 176 bpm (age 44). Standard error of estimate ~7–12 bpm.
- **Tanaka, Monahan & Seals, *JACC* 2001, "Age-predicted maximal heart rate revisited"** — 208 − 0.7×age → 178 bpm (43) / 177 bpm (44). Meta-analysis of 351 studies, n=18,712; SEE ~10 bpm. Widely cited as the more accurate formula, particularly past 40, despite many organizations still defaulting to Fox's older formula.
- At this specific age the two formulas nearly coincide (~177–178 bpm) — a coincidence of this age band, not unusual precision. The ±10bpm error margin on either formula means a real individual value anywhere from roughly 167–188 bpm is plausible without an actual test.
- Sources: [Age-predicted maximal heart rate revisited (JACC/ScienceDirect)](https://www.sciencedirect.com/science/article/pii/S0735109700010548), [secondary summary](https://getfitcraft.com/science/max-heart-rate-formula-research), [Fox vs. Tanaka in recreational runners](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5862813/)

## z1–z5 as % of estimated max — *practitioner convention, converges across sources but not vote-tested*
A generic 5-zone sports-science breakdown and **U.S. Masters Swimming's own guidance** ("Heart Rate Training Part II") converge almost exactly on the same cutoffs:

| Zone | % HRmax | bpm (HRmax≈178) | 10s pulse count |
|---|---|---|---|
| z1 (recovery/easy) | 50–60% | 89–107 | ~15–18 |
| z2 (base/aerobic) | 60–70% | 107–125 | ~18–21 |
| z3 (moderate/tempo) | 70–80% | 125–142 | ~21–24 |
| z4 (threshold) | 80–90% | 142–160 | ~24–27 |
| z5 (anaerobic/max) | 90–100% | 160–178 | ~27–30 |

Sources: [USMS, Heart Rate Training Part II](https://www.usms.org/fitness-and-training/articles-and-videos/articles/heart-rate-training-part-ii?Oldid=110) (masters-swimming-specific, but a practitioner article, not a study), general convergence across [FORM Swim](https://www.formswim.com/blogs/all/using-heart-rate-training-zones-to-improve-your-swim-training), [padlie.com zone breakdown](https://padlie.com/en/blog/swimming-training-zones).

## Where this repo's "z1 white … z5 purple" naming likely comes from — *inference from sourcing, not itself tested*
The color-coded zone naming in the Garpar log almost certainly traces back to **Jon Urbanchek's color-zone system** (University of Michigan): White 120–130bpm, Pink 130–140, Red 150–170, Blue 170–180, Purple >90% of max. Critically, **these are fixed absolute bpm values calibrated for young elite/collegiate swimmers with HRmax around 195–200bpm — not scaled to age at all.** Applied unmodified to a 43–44 year-old (est. HRmax ~178), "Blue 170–180" would sit at ~95–100% of that person's actual max, not the sub-threshold aerobic zone it represents for a 19-year-old. This is a plausible explanation for why the ~120bpm z1–z2 anchor pulled from the Garpar log read as too low when checked against a real pulse count on 2026-09-07 — but it's an inference from how the numbers line up, not something a study directly confirmed.
- Sources: [Learning the Color System — Swim Like A Fish](https://swimlikeafish.org/jon-urbancheks-workouts-learning-the-color-system/), [Urbanchek color chart, secondary](https://www.swimwarrior.com/post/urbanchek-s-training-color-system-the-palette-of-swimming)

## Swimming lowers heart rate vs. land exercise at the same effort — *real effect, size not well pinned down for this population*
Deep-water running studies show heart rate ~8–15 bpm lower than land running at matched oxygen uptake. A small study of elite swimmers (n=12, mean age 18.8) found max HR ~6.7±5.3 bpm lower swimming front crawl vs. running (193.6 vs. 199.8 bpm, p=0.015) — the study's own authors recommend sport-specific max-HR testing over applying any fixed offset, given high individual variability (SD 5.3bpm) and a youth-elite-only sample.
- Sources: [Heart-Rate Response to Exercise in the Water](https://scholarworks.bgsu.edu/cgi/viewcontent.cgi?article=1309&context=ijare), [Maximal Heart Rate for Swimmers, PMC6915385](https://pmc.ncbi.nlm.nih.gov/articles/PMC6915385/)

## Evidence gaps — flagged, not papered over
- **No validated masters-specific z1–z5 HR table exists.** Every number in the table above is either generic sports-science convention or a youth-elite color system re-purposed — nothing was tested on adults in their 40s specifically.
- **No confirmed correction factor for translating a land-based %HRmax table to swimming.** The water-lowers-HR effect is real, but the two studies above measure different things (submaximal HR at matched VO2 vs. max HR) in different populations (deep-water runners; elite teenage swimmers) — there's no single number to subtract from the table above with any real confidence.
- **The single best fix remains what's already in [`BACKLOG.md`](../BACKLOG.md#calibrating-a-real-personal-heart-rate-zone-table): a measured resting HR + a genuine max-effort HR reading**, which would replace every number on this page with an actual personal one rather than an age-formula estimate.
