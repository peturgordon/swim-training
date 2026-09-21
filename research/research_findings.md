# Swim Training Research — Consolidated Findings

Two deep-research passes, run 2026-08-26/27, both using the same method: search angles → fetch sources → extract claims → adversarial verification (3 independent reviewers per claim, 2/3 votes needed to survive) → synthesis. Combined: 39 sources fetched, 172 candidate claims extracted, 50 claims adversarially verified, 27 confirmed / 23 refuted.

This file is the raw research corpus behind both published guides (see **Related documents** at the bottom) — it exists so the underlying evidence survives independently of any Claude session or account, and so it can seed further guides, training plans, or strategies without re-researching from scratch.

---

# Pass 1 — Core swim training science

Research question: evidence-based (non-anecdotal) swim training methodology for an adult masters swimmer training 3x/week, 1 hour/session, goals of general fitness/endurance and racing faster at masters meets, currently struggling to hold technique together under sprint effort and over longer distances (e.g. 400m). 6 search angles → 24 sources fetched → 106 candidate claims → 25 verified → 14 confirmed, 11 refuted.

## Confirmed findings

Each of these survived adversarial review. Confidence reflects both the vote margin and the strength of the underlying study design.

### 1. Training intensity distribution should be event-dependent, and polarized beats threshold-heavy — *high confidence*
A systematic review found elite sprint-event swimmers typically train polarized/threshold, middle-distance swimmers threshold/pyramidal, and long-distance swimmers primarily pyramidal. In a controlled 6-week crossover RCT on 22 elite junior swimmers, a polarized intensity split (81% low-intensity / 4% moderate / 15% high, by blood lactate zone) produced greater improvement in 100m time-trial performance than a threshold-heavy split (65%/25%/10%) — 0.97%±1.02% vs. 0.09%±0.94% — while also producing **less** perceived fatigue and better recovery quality.
- Vote: 3-0 (both sub-claims)
- Sources: [González-Ravé et al. 2021, systematic review, PMID 33952709](https://pubmed.ncbi.nlm.nih.gov/33952709/) · [Pla et al. 2019, RCT n=22](https://www.researchgate.net/publication/326599627_Effects_of_a_6-Week_Period_of_Polarized_or_Threshold_Training_on_Performance_and_Fatigue_in_Elite_Swimmers)
- Quotes: "The sprint swimmers typically followed a polarized and threshold TID, the middle-distance swimmers followed a threshold and pyramidal TID, and the long-distance swimmers primarily followed a pyramidal TID." / polarized 100m improvement "0.97% ± 1.02%... vs. 0.09% ± 0.94%... with less fatigue and better quality of recovery."

### 2. Race-pace training format affects acute fatigue — but the claim that it specifically protects technique did not survive verification — *medium confidence*
In a crossover study of 14 national-level swimmers, ultra-short race-pace training (USRPT: 20×50m) produced significantly lower blood lactate than volume-matched traditional race-pace repeats (RPT: 10×100m) at the same 1:1 work:rest ratio and target pace (both at 2 and 5 minutes post-effort: RPT 10.8±2.7 / 10.1±2.6 mM/L vs. USRPT 8.3±2.7 [p=0.021] / 7.4±2.8 mM/L [p=0.008]). In the longer-repeat protocol, final reps were measurably 1.5–3% slower than target pace, with a quantified stroke-count increase as swimming time increased. **Important caveat:** the more attractive follow-on claims — that USRPT itself preserves stroke mechanics better than RPT, that stroke-count degradation was significantly worse specifically in RPT, and that the authors concluded USRPT lets swimmers accumulate more race-pace volume with better-preserved technique — were tested and did **not** survive adversarial verification (refuted 0-3 and 1-2). Less fatigue per set is real; "therefore better technique" is not established.
- Vote: 2-1 / 3-0 (mixed across sub-claims)
- Sources: [Cuenca-Fernández et al. 2021](https://www.tandfonline.com/doi/abs/10.1080/15438627.2021.1929227) · [companion analysis, n=14](https://www.researchgate.net/publication/351169031_Lower_fatigue_and_faster_recovery_of_ultra-short_race-pace_swimming_training_sessions)

### 3. Repeated sprint ability correlates with 50m freestyle mainly through raw speed, not fatigue resistance — *medium confidence*
An 8×15m repeated-sprint test (30s rest) correlated against 50m freestyle performance: strongest correlations with fastest sprint time (r=0.83) and mean sprint time (r=0.78); fatigue index (resistance to fatigue) showed a negligible, non-significant correlation (r=0.05, p=0.78). In multiple regression, dry-land peak power was the dominant independent predictor.
- Vote: 2-1
- Source: [Frontiers in Sports and Active Living, 2025](https://www.frontiersin.org/journals/sports-and-active-living/articles/10.3389/fspor.2025.1751687/full)

### 4. At maximal sprint speed, thrust power and drag power are statistically equal — validates the underlying mechanics — *medium confidence*
In elite male front-crawl sprinters (93±2% of 50m WR pace), measured thrust power (399±56 W) and drag power (400±57 W) were not significantly different (p>0.8) — consistent with basic mechanics (propulsion must balance drag at non-accelerating maximal velocity). Authors flag the active-drag correction factor as a methodological limitation.
- Vote: 2-1
- Source: [PLOS ONE 2016, n=10](https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0162387)

### 5. Technique degrades under fatigue through a measurable mechanism — intracycle velocity variation — *medium confidence*
A systematic scoping review (76 studies, 1,440 swimmers) found intracycle velocity variation (IVV — the within-stroke speed wobble) is maintained at submaximal effort but rises at maximal effort as swimmers fatigue and lose mechanical efficiency (hedged "probably" by review authors; heterogeneous evidence base, only 20/68 trials low risk of bias). Better propulsive continuity — a coordination property, not just a fitness property — is what allows stable IVV, particularly in front crawl.
- Vote: 2-1 (both sub-claims)
- Source: [Fernandes et al. 2023, Bioengineering, scoping review](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10044880/)

### 6. Elite swimming coaching remains dominated by isolated "perfect technique" drilling, not training technique to survive race conditions — *medium confidence*
A qualitative study of 20 elite (Australian-institute-affiliated) coaches found task-decomposition (part-task/drill-based) methods remain the dominant training practice, aimed at reinforcing "perfect" technique and mechanical consistency — even though the same coaches report some awareness of contemporary constraints-led/ecological approaches built for robustness under varying conditions. Self-reported coaching culture, not a controlled efficacy trial — but names the technique-doesn't-transfer problem directly.
- Vote: 2-1 / 3-0 (two related sub-claims from the same source)
- Source: [Brackley, Barris, Tor & Farrow 2020, Journal of Sports Sciences, n=20 coaches](https://www.tandfonline.com/doi/full/10.1080/02640414.2020.1792703)

### 7. Contextual interference (variable/spaced practice) reflects the learning-vs-performance distinction — *medium confidence*
A coach-education case study (n=2 elite Para-swimming coaches) found shifting practice design toward greater between-skill variability and temporal spacing draws on the established motor-learning "contextual interference" effect: strong performance within one practice block does not indicate durable learning. Small case study, but grounded in mainstream (not fringe) motor-learning theory.
- Vote: 2-1
- Source: [Powell, Wood, Dagnall, Payton, Gorman 2024, IJSSC](https://journals.sagepub.com/doi/10.1177/17479541241291541)
- Quote (coach): "Just because someone has done something well for thirty minutes, it doesn't mean it's ingrained."

### 8. Practicing a skill while fatigued impairs learning it, distinct from just executing it worse in the moment — *high confidence*
In a controlled experiment, a group practicing a novel motor skill while physically fatigued (via repeated maximal contractions) showed significantly slower within-session learning than a non-fatigued group (learning slope 0.038 fatigued vs. 0.169 non-fatigued, p=0.01). A stronger claim — that this deficit persists for multiple days after fatigue resolves — was tested separately and refuted (0-3): treat the confirmed effect as session-local, not multi-day.
- Vote: 3-0
- Source: [eLife 2019;8:e40578](https://elifesciences.org/articles/40578)

### 9. Evidence gap: no confirmed research addresses periodization for masters/limited-hours swimmers
No confirmed claim from this research pass addresses periodization, weekly/session microcycle design, or set structuring specifically for masters or limited-hours (2–4x/week, ~1hr/session) swimmers. A candidate claim about the dominant periodization model in elite swimming research (wave-like/undulating mesocycles) was tested and refuted (1-2) — even the elite-level literature doesn't cleanly settle this, let alone extend it to masters populations. Program design for this population must be extrapolated from general principles, not drawn from direct verified research.
- Source flagged against: [González-Ravé et al. 2021](https://pubmed.ncbi.nlm.nih.gov/33952709/)

---

## Explicitly refuted claims — do not treat as established

Listed for transparency. These are the intuitively attractive claims that were tested against three independent adversarial reviewers and killed. Neither published document (the audit or the guide) relies on these, even where they would have made a tidier story.

| Claim | Vote | Source |
|---|---|---|
| One dominant "wave-like" (undulating) periodization model is used across elite swimming research, aimed at promoting fitness and technique together | 1-2 | [PMID 33952709](https://pubmed.ncbi.nlm.nih.gov/33952709/) |
| In the longer-repeat RPT protocol, stroke count rose substantially with fatigue while USRPT stayed comparatively stable — i.e. shorter repeats preserve mechanics better | 1-2 | [Cuenca-Fernández et al.](https://www.tandfonline.com/doi/abs/10.1080/15438627.2021.1929227) |
| Study's overall conclusion: USRPT lets swimmers accumulate more race-pace volume while better maintaining stroke patterns, with lower fatigue than traditional RPT | 0-3 | [Cuenca-Fernández et al.](https://www.tandfonline.com/doi/abs/10.1080/15438627.2021.1929227) |
| Stroke-count/performance correlation was strong in RPT (r=0.58–0.64) but weak in USRPT (r=0.10–0.28), indicating better technique preservation in USRPT | 0-3 | [companion analysis](https://www.researchgate.net/publication/351169031_Lower_fatigue_and_faster_recovery_of_ultra-short_race-pace_swimming_training_sessions) |
| Authors conclude USRPT allows more race-pace volume with considerably lower fatigue than RPT, while RPT may still suit lactate-tolerance work for distance swimmers | 0-3 | [companion analysis](https://www.researchgate.net/publication/351169031_Lower_fatigue_and_faster_recovery_of_ultra-short_race-pace_swimming_training_sessions) |
| In elite 50m freestyle, stroke length (not rate) is most strongly correlated with speed; top sprinters achieve high rate without sacrificing length | 1-2 | [Frontiers 2025, fspor.2025.1656633](https://www.frontiersin.org/journals/sports-and-active-living/articles/10.3389/fspor.2025.1656633/full) |
| In elite long-distance events (800–1500m), stroke rate becomes more associated with speed than length, contradicting traditional stroke-length emphasis | 0-3 | [Frontiers 2025, fspor.2025.1656633](https://www.frontiersin.org/journals/sports-and-active-living/articles/10.3389/fspor.2025.1656633/full) |
| Elite (faster) front-crawl swimmers show significantly lower IVV than beginners across all speeds | 1-2 | [PMC4327381](https://pmc.ncbi.nlm.nih.gov/articles/PMC4327381/) |
| Elite swimmers maintain (don't increase) IVV as speed rises toward maximal effort, unlike beginners | 0-3 | [PMC4327381](https://pmc.ncbi.nlm.nih.gov/articles/PMC4327381/) |
| A 6-week coach-education intervention shifted coaches from internal to external/holistic focus-of-attention cueing, consistent with motor-learning theory | 0-3 | [Powell et al. 2024](https://journals.sagepub.com/doi/10.1177/17479541241291541) |
| Fatigue-related learning impairment persists for multiple days after fatigue resolves, even with extra unfatigued practice | 0-3 | [eLife 2019](https://elifesciences.org/articles/40578) |

---

## Caveats on the whole corpus

- **Population mismatch:** nearly all confirmed evidence comes from elite, junior, national-level, or otherwise highly-trained competitive swimmers (n=10–22 typically, one qualitative study n=20 coaches, one case study n=2 coaches). None of the surviving claims come from masters/adult-recreational samples specifically — extrapolation to a masters context is unavoidable.
- **Split votes:** several claims survived only 2-1 rather than unanimous 3-0 — treat those as "reasonably well-supported," not "settled" (flagged individually above).
- **Time-sensitivity:** sources are mostly 2016–2025; a 2025 review (referenced in verifier evidence, not itself a confirmed claim) suggests elite sprint TID conventions may still be evolving — treat the TID-by-event finding as a current descriptive pattern, not a fixed rule.
- **Drill-specific efficacy** (which particular drills — catch-up, fist drill, sculling, high-elbow, etc. — actually transfer to race-pace technique) was not directly addressed by any confirmed claim. The coaching-practice finding (#6) speaks to the part-task drilling *paradigm* being dominant, not to any specific drill being wrong or right.

## Open questions the research did not resolve

1. What does evidence-based periodization/program design actually look like for adult masters swimmers training only 2–4x/week at ~1hr/session? (The most central practical question — essentially unaddressed by confirmed claims.)
2. Does any specific training method actually preserve stroke technique better under fatigue than the alternatives? (The attractive USRPT-preserves-technique version was refuted; the question remains open.)
3. Which specific freestyle technique elements are most commonly under-trained by typical drill-based masters programming, and which specific corrective drills have demonstrated transfer to race-pace performance rather than being tradition/fad?
4. Given that elite coaching is documented as still dominated by part-task drilling, what concrete alternative practice structures (variable/randomized order, representative/race-like drill design, contextual interference protocols) have been tested for efficacy in adult or masters swimmers specifically, rather than only elite/junior populations?

---

## Full source list (24 fetched)

| Source | Quality | Angle |
|---|---|---|
| [González-Ravé et al., systematic review — PMID 33952709](https://pubmed.ncbi.nlm.nih.gov/33952709/) | primary | Aerobic/endurance evidence base |
| [Polarized vs. Threshold TID meta-analysis (ResearchGate)](https://www.researchgate.net/publication/325492365_Polarized_vs_Threshold_Training_Intensity_Distribution_on_Endurance_Sport_Performance_A_Systematic_Review_and_Meta-Analysis_of_Randomized_Controlled_Trials) | unreliable (0 claims survived) | Aerobic/endurance evidence base |
| [Pla et al., polarized/threshold RCT](https://www.researchgate.net/publication/326599627_Effects_of_a_6-Week_Period_of_Polarized_or_Threshold_Training_on_Performance_and_Fatigue_in_Elite_Swimmers) | primary | Aerobic/endurance evidence base |
| [10km open-water CSS pacing study](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12371947/) | primary | Aerobic/endurance evidence base |
| [USMS — CSS interval training](https://www.usms.org/fitness-and-training/articles-and-videos/articles/how-to-train-with-critical-swim-speed-intervals) | secondary | Aerobic/endurance evidence base |
| [Cuenca-Fernández et al., USRPT vs RPT](https://www.tandfonline.com/doi/abs/10.1080/15438627.2021.1929227) | primary | Sprint & race-pace training science |
| [Companion USRPT lactate/recovery analysis](https://www.researchgate.net/publication/351169031_Lower_fatigue_and_faster_recovery_of_ultra-short_race-pace_swimming_training_sessions) | primary | Sprint & race-pace training science |
| [Rushall, USRPT methodology (Coaching Science Abstracts)](https://coachsci.sdsu.edu/swim/bullets/ultra28.htm) | secondary | Sprint & race-pace training science |
| [Repeated sprint ability & 50m freestyle](https://www.frontiersin.org/journals/sports-and-active-living/articles/10.3389/fspor.2025.1751687/full) | primary | Sprint & race-pace training science |
| [Stroke length/rate in elite sprint vs. distance events](https://www.frontiersin.org/journals/sports-and-active-living/articles/10.3389/fspor.2025.1656633/full) | primary | Sprint & race-pace training science |
| [TID for sprinter swimmers (PDF)](https://www.fisiologiadelejercicio.com/wp-content/uploads/2025/11/Training-intensity-distribution-for-sprinter-swimmers.pdf) | secondary | Sprint & race-pace training science |
| [Fernandes et al., IVV scoping review](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10044880/) | primary | Freestyle biomechanics & technical faults |
| [Thrust/drag power in elite sprint front crawl](https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0162387) | primary | Freestyle biomechanics & technical faults |
| [IVV, elite vs. beginner](https://pmc.ncbi.nlm.nih.gov/articles/PMC4327381/) | primary | Freestyle biomechanics & technical faults |
| [Prevalence of biomechanical errors in freestyle (blog)](https://www.mysport.guru/post/prevalence-of-biomechanical-errors-in-swimming-freestyle) | blog | Freestyle biomechanics & technical faults |
| [Brackley et al., coaches' skill-acquisition practices](https://www.tandfonline.com/doi/full/10.1080/02640414.2020.1792703) | primary | Drill efficacy vs. tradition |
| [Powell et al., contextual interference coach education](https://journals.sagepub.com/doi/10.1177/17479541241291541) | primary | Drill efficacy vs. tradition |
| [Fatigue and motor-skill learning (eLife)](https://elifesciences.org/articles/40578) | primary | Motor control/skill degradation under fatigue |
| [PMC11742979](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11742979/) | primary | Motor control/skill degradation under fatigue |
| [PMC10671841](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10671841/) | primary | Motor control/skill degradation under fatigue |
| [Swim coaches' perceptions of periodization (2025)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12411453/) | primary | Masters program design & periodization |
| [USMS — periodization](https://www.usms.org/fitness-and-training/articles-and-videos/articles/periodization) | blog | Masters program design & periodization |
| [USMS — how to develop a training plan](https://www.usms.org/fitness-and-training/articles-and-videos/articles/how-to-develop-your-swim-training-plan) | blog | Masters program design & periodization |
| [USMS — how to write a workout](https://www.usms.org/fitness-and-training/articles-and-videos/articles/how-to-write-a-swimming-workout) | secondary | Masters program design & periodization |

---

# Pass 2 — Detraining, cardiac drift, and return-to-training injury risk

A targeted follow-up covering ground Pass 1 never searched: what happens physiologically to a trained athlete who stops for years and restarts, whether "muscle memory" for technique really outpaces fitness return, whether cardiac drift/decoupling is validated science or coaching heuristic, and what's known about injury risk when ramping volume back up. 5 search angles → 15 sources fetched → 66 candidate claims → 25 verified → 13 confirmed, 12 refuted.

**Headline result: this pass is as valuable for what it could *not* confirm as for what it did.** Two of the three questions the user most wanted answered — does technique retention really outpace fitness retention after a long layoff, and is cardiac decoupling a validated, trainable marker — came back with **no surviving confirmed evidence**. Both are flagged explicitly below as open gaps rather than papered over with plausible-sounding inference.

## Confirmed findings

### 1. Detraining is real but floors above untrained baseline — training history matters — *high confidence*
Detraining causes rapid VO2max decline in previously well-trained athletes (both short-term <4wk and long-term >4wk), but VO2max plateaus **above** the level of an untrained person — a returning masters swimmer with genuine youth training history retains a physiological floor advantage over a true novice. Notably, VO2max gains that were only *recently* acquired (i.e., by less experienced/newly-trained people) are completely lost during long-term detraining, whereas gains built over a longer training history are only partially lost — a genuine training-age effect on long-term retention.
- Confidence: high
- Sources: [Mujika & Padilla, MSSE 2001](https://pubmed.ncbi.nlm.nih.gov/11252068) · [Sports Medicine Part I, 2000](https://pubmed.ncbi.nlm.nih.gov/10966148) · [Part II, 2000](https://pubmed.ncbi.nlm.nih.gov/10999420)

### 2. The cardiovascular mechanism of detraining decline — *high confidence*
The mechanism (short- and long-term alike): blood volume falls, exercise heart rate doesn't rise enough to compensate for reduced stroke volume, so maximal cardiac output drops; cardiac chamber dimensions and ventilatory efficiency also shrink. Verbatim-matched across all three Mujika & Padilla papers — stable, foundational Fick-principle physiology (CO = HR × SV), not a fast-moving or contested area despite the papers' age (~25 years).
- Confidence: high
- Sources: same three as above

### 3. Peripheral/muscular detraining also depends on training history — *high confidence*
At the muscle level, capillarization, arterial-venous oxygen difference, and oxidative enzyme activity decline during long-term detraining in trained athletes, but are *completely* lost in people who were only recently trained. Someone with a genuine youth competitive background retains more residual peripheral adaptation than a novice would after a comparable break — though the source doesn't translate this into a specific "how fast can I rebuild" timeline.
- Confidence: high
- Source: [Mujika & Padilla, Part II, 2000](https://pubmed.ncbi.nlm.nih.gov/10999420)

### 4. EVIDENCE GAP — does technique/"muscle memory" really return faster than fitness? *Not confirmed*
This is the specific comparison the user asked about, and this pass found **no surviving confirmed evidence** for it. Two candidate mechanistic explanations were tested and both failed adversarial verification: a myonuclear-permanence claim (0-3) and a DNA-methylation "molecular muscle memory" claim (0-3). A claim that training history modulates *short-term* detraining rate also failed (1-2). **Treat "technique comes back faster than fitness" as plausible, reasonable-sounding inference — not as something this research substantiates with citable data.** This directly means: the claim in *The Returning Swimmer* guide's "coming back after years away" section is unverified inference, not confirmed science — worth flagging honestly if that guide gets revised or extended.

### 5. Cardiovascular drift is real and starts earlier than popular coaching content suggests — *high confidence*
During sustained submaximal exercise, stroke volume progressively declines starting after only 10-20 minutes, and heart rate rises to partially compensate at constant workload. This contradicts a simplistic "drift only happens in very long efforts" framing sometimes used in coaching content.
- Confidence: high
- Source: [Coyle & González-Alonso, Exercise & Sport Sciences Reviews, 2001](https://pubmed.ncbi.nlm.nih.gov/11337829/)

### 6. Direct swimming-specific evidence for cardiac drift exists — *medium confidence*
A 1984 study directly compared 90 minutes of freestyle leg-kick swimming against 90 minutes of cycling in the same five subjects: the "secondary rise" in heart rate followed a parallel course in both modalities, and late-phase HR drift tracked continuously rising plasma catecholamines (not plasma volume, water balance, or potassium) — suggesting a hormonal/sympathetic-drive component, not purely a fluid-shift mechanism. Confidence is medium, not high, because: n=5, leg-kick-only (not full-stroke) so may not fully generalize, and catecholamine-correlation isn't proof of sole causation — modern literature treats sympathetic drive as one of several contributing mechanisms alongside thermoregulatory vasodilation, not the whole story.
- Confidence: medium
- Source: [Nielsen, Sjøgaard & Bonde-Petersen, Eur J Appl Physiol, 1984](https://pubmed.ncbi.nlm.nih.gov/6542503/)

### 7. EVIDENCE GAP — is decoupling a validated fitness marker, and does anything proven reduce it? *Not confirmed*
No confirmed research in this pass establishes specific training approaches (aerobic base volume, duration progression, heat/hydration management) as effective for reducing cardiac drift, nor validates decoupling as a reliable marker of aerobic fitness progress versus other confounds (heat, hydration, substrate depletion). A 2026 adolescent-runner study that appeared to challenge decoupling-as-fitness-marker (finding thermoregulatory/electrolyte/glucose factors, not VO2max, drove decoupling) was proposed across three claims — all three failed verification (0-3 each), so it can't be cited for *or* against the practitioner heuristic either. **The popular "decoupling %" metric (as used by platforms like TrainingPeaks) should be treated as a practitioner heuristic, not experimentally validated** — pending better evidence. This directly affects *The Returning Swimmer* guide's steady-state protocol: the protocol itself (test at a fixed pace, compare early vs. late heart rate) rests on sound, confirmed physiology (findings #5 and #6 above — drift is real and swimming-specific), but the specific numeric thresholds popular coaching platforms attach to "% decoupling" are not something this research validated.

### 8. Injury evidence exists but its own authors say it's too weak to set safe volume guidelines — *high confidence (that the evidence is weak, not that a guideline exists)*
The best available injury evidence is a 2020 systematic review (12 studies, N=1,460 competitive swimmers, *Journal of Athletic Training*) examining training volume and shoulder pain across the swimmer life span (young <15, adolescent 15-17, adult 18-22, masters 23-77). The review's own authors conclude the evidence is too weak (level II at best, for adolescents) to establish a validated, data-based safe training-volume cutoff for **any** age group, including masters. A separate claim that masters swimmers specifically showed a statistically significant volume/shoulder-pain association was tested and refuted (0-3) — so despite masters being nominally within scope, no confirmed masters-specific quantitative finding survives.
- Confidence: high (on what the evidence does and doesn't show)
- Source: [Feijen, Tate, Kuppens, Claes & Struyf, J Athl Train 2020;55(1):32-41](https://pubmed.ncbi.nlm.nih.gov/?term=Swim-Training+Volume+and+Shoulder+Pain+Across+the+Life+Span+of+the+Competitive+Swimmer)

### 9. EVIDENCE GAP — no confirmed "safe progression rate" guideline, swim-specific or borrowed
No claims addressing running/strength-training progression-rate literature (the 10% rule, acute:chronic workload ratio research) survived verification in this pass, despite being flagged as fallback evidence to check. This should be read as "not yet addressed by this verification round," not as evidence that no such literature exists — a candidate topic for a future pass.

## Explicitly refuted claims — do not treat as established

| Claim | Vote | Source |
|---|---|---|
| Recently-trained subjects show more moderate short-term detraining than highly trained athletes, with a hard 4-week threshold for losing recent VO2max gains | 1-2 | [PMID 11252068](https://pubmed.ncbi.nlm.nih.gov/11252068) |
| Myonuclei are not lost from muscle fibers after 6 weeks of disuse — the "myonuclear permanence" basis for durable neuromuscular muscle memory | 0-3 | [AJP-Cell 2024](https://journals.physiology.org/doi/abs/10.1152/ajpcell.00692.2024) |
| Stroke-volume decline in cardiac drift is driven primarily by heart rate itself rather than cutaneous vasodilation for thermoregulation | 0-3 | [Coyle & González-Alonso 2001](https://pubmed.ncbi.nlm.nih.gov/11337829/) |
| Cardiac drift specifically emerges only after ~100 minutes of prolonged heavy exercise, later than the immediate early-exercise HR rise (two variants tested) | 0-3 / 0-3 | [Coyle & González-Alonso](https://pubmed.ncbi.nlm.nih.gov/11337829/) · [Nielsen et al. 1984](https://pubmed.ncbi.nlm.nih.gov/6542503/) |
| The secondary HR rise tracked catecholamines but was *not* explained by plasma volume/water balance/potassium — ruling out dehydration as the mechanism | 0-3 | [Nielsen et al. 1984](https://pubmed.ncbi.nlm.nih.gov/6542503/) |
| HR-speed decoupling in adolescent runners tracked core temperature/electrolyte loss, not aerobic fitness — challenging decoupling-as-fitness-marker | 0-3 | Wang et al., Front Physiol 2026, doi:10.3389/fphys.2026.1807399 |
| Baseline VO2max did not predict decoupling onset/magnitude in that study — undercutting decoupling as a fitness proxy | 0-3 | Wang et al., Front Physiol 2026 |
| Decoupling drivers are stage-dependent (thermoregulatory early/mid-race, glucose-dynamics late-race) rather than one aerobic-ceiling mechanism | 0-3 | Wang et al., Front Physiol 2026 |
| Masters swimmers (23-77y) showed a statistically significant training-volume/shoulder-pain association (P=.02) | 0-3 | [Feijen et al. 2020](https://pubmed.ncbi.nlm.nih.gov/?term=Swim-Training+Volume+and+Shoulder+Pain+Across+the+Life+Span+of+the+Competitive+Swimmer) |
| Training history changes short-term detraining magnitude (highly trained athletes decline more than recently-trained individuals) | 1-2 | [PMID 10966148](https://pubmed.ncbi.nlm.nih.gov/10966148) |
| Prior resistance training leaves durable DNA-methylation changes at specific loci that persist through detraining, as a molecular substrate for muscle memory | 0-3 | [MDPI Genes 2026](https://www.mdpi.com/2073-4425/17/8/964) |

## Caveats — Pass 2

- **Evidence base skews old and small-N.** The core detraining physiology (Mujika & Padilla, 2000/2001) and the only swimming-specific cardiac-drift data (Nielsen et al., 1984, n=5) are 25-42 years old. Acceptable here because they describe stable, foundational physiology that hasn't been overturned — but no modern swimming-specific detraining or drift study was found to corroborate or update these numbers with current instrumentation or larger samples.
- **Two of five angles produced confirmed evidence gaps, not just "weak" evidence** (see findings #4, #7, #9 above) — these are genuine open questions, flagged rather than filled with plausible-sounding inference.
- **Session constraint:** verifying sub-agents repeatedly exhausted their search budget, so verification relied more on direct primary-source retrieval than broad independent searching for contradicting literature. This strengthens confidence that quoted claims accurately represent their sources, but weakens confidence that all contradicting/superseding literature was checked.

## Open questions — Pass 2

1. Is there any direct research (swimming or cross-sport) comparing motor-skill retention/relearning curves versus cardiovascular fitness retention after a multi-year layoff, in the same subjects? None found; both candidate mechanisms (myonuclear permanence, DNA methylation) failed verification.
2. What does the running/strength-training "too much too soon" and safe-progression-rate literature (10% rule, acute:chronic workload ratio) actually say, and how might it transfer to swimming's non-weight-bearing, shoulder-dominant loading pattern? Flagged as relevant but not covered by any confirmed claim.
3. Is cardiac/aerobic decoupling actually a validated, reproducible marker of aerobic fitness change in longitudinal training studies — does reducing decoupling over a training block correlate with measured VO2max or lactate-threshold gains — or is its popularity mainly a coaching-platform heuristic without controlled validation? Neither confirmed nor refuted claims settle this.
4. The swimming-specific cardiac-drift data is from one 1984 study (n=5, leg-kick only) — does a more recent or larger full-stroke freestyle study exist, and would results differ meaningfully from leg-kick-only given differing muscle mass and thermoregulatory/buoyancy conditions?

## Sources fetched — Pass 2 (15)

| Source | Quality | Angle |
|---|---|---|
| [Mujika & Padilla, Part I (short-term detraining)](https://pubmed.ncbi.nlm.nih.gov/10966148) | secondary | Motor skill retention vs. fitness decay |
| [Mujika & Padilla, Part II (long-term detraining)](https://pubmed.ncbi.nlm.nih.gov/10999420) | secondary | Motor skill retention vs. fitness decay |
| [Mujika & Padilla, MSSE 2001 review](https://pubmed.ncbi.nlm.nih.gov/11252068) | primary | Motor skill retention vs. fitness decay |
| [Myonuclear permanence study, AJP-Cell 2024](https://journals.physiology.org/doi/abs/10.1152/ajpcell.00692.2024) | primary | Motor skill retention vs. fitness decay |
| [DNA-methylation muscle memory, MDPI Genes 2026](https://www.mdpi.com/2073-4425/17/8/964) | secondary | Motor skill retention vs. fitness decay |
| [Coyle & González-Alonso 2001](https://pubmed.ncbi.nlm.nih.gov/11337829/) | primary | Cardiac drift mechanism |
| [PMID 22410803](https://pubmed.ncbi.nlm.nih.gov/22410803/) | secondary | Cardiac drift mechanism |
| [Nielsen, Sjøgaard & Bonde-Petersen 1984](https://pubmed.ncbi.nlm.nih.gov/6542503/) | primary | Cardiac drift mechanism |
| [TrainingPeaks — aerobic decoupling (blog)](https://www.trainingpeaks.com/blog/aerobic-endurance-and-decoupling/) | blog | Cardiac drift mechanism |
| [Wikipedia — Cardiovascular drift](https://en.wikipedia.org/wiki/Cardiovascular_drift) | secondary | Cardiac drift mechanism |
| [PMID 34717912](https://pubmed.ncbi.nlm.nih.gov/34717912/) | secondary | Cardiac drift mechanism |
| Nielsen et al. 1984 (swimming vs. cycling detail) | primary | Swimming-specific decoupling evidence |
| Wang et al., Front Physiol 2026 (adolescent runners) | primary | Swimming-specific decoupling evidence |
| Jones & Kirby, "Physiological Resilience," Scand J Med Sci Sports 2025 | secondary | Swimming-specific decoupling evidence |
| [Feijen et al. 2020, systematic review](https://pubmed.ncbi.nlm.nih.gov/?term=Swim-Training+Volume+and+Shoulder+Pain+Across+the+Life+Span+of+the+Competitive+Swimmer) | primary | Swimmer's shoulder & injury risk |

---

## Cross-check against an independent Gemini research pass (2026-08-27)

The user separately asked Google Gemini to research the same topic (masters-swim training framework, 40+ returning competitive swimmers, 3x/week). Gemini produced a 21-page framework document with 56 citations, exported as PDF to `research/gemini/gemini-masters-swim-training-framework.pdf`. It was reviewed against this research corpus and published as **[Second Opinion](https://peturgordon.github.io/swim-training/research/gemini/second-opinion.html)**.

Headline findings from that cross-check:
- **Genuine convergence** on CSS methodology, the 3-day aerobic/threshold/sprint weekly split, technique-before-fatigue sequencing, and the core tracking metrics — independent agreement that strengthens confidence in all four.
- **Citation quality is weak**: of 56 sources, only ~4 are peer-reviewed/PMC-indexed (one is the same Feijen et al. 2020 shoulder-pain review already in this file); the rest are coaching blogs, brand marketing, forum posts, a Prezi slideshow, and — notably — a claim about human breathing patterns sourced to an *Equine Veterinary Journal* article about horses.
- **Confidence outstrips evidence in specific, identifiable places**: it states USRPT "prevents technical degradation" (the exact sub-claim we tested and refuted), asserts the same unverified "motor memory outpaces tissue tolerance" narrative our own first draft of *The Returning Swimmer* made before Pass 2 corrected it, prescribes an exact 4-phase periodization macrocycle with specific meterage (the precise area we confirmed has *no* masters/limited-hours evidence at all), and offers a specific cardiac-drift fix where we found no confirmed intervention.
- **Worth borrowing regardless of evidence tier**: lane-flow/group-management logistics (Front/Middle/Back of the Bus roles, CSS-based lane grouping) and a dryland prehab structure — neither evidence-graded claims, just useful practical additions our documents didn't cover.

## Pass 3 — Equipment usage: pull buoys, paddles, fins, kickboards

Answers "did the research cover the equipment we use" — it hadn't, until this pass (two runs: main equipment pass + a fins-specific follow-up after the main pass's search budget ran out before touching fins at all).

**Pull buoys.** Removing the kick measurably changes underwater arm-pull kinematics — legs appear to *facilitate* the arm pull (a coordination effect), not just add separate thrust (medium confidence, primary study, n=8). Yet a properly-adjusted arm-propelling-efficiency metric is statistically equivalent between arms-only and full-stroke swimming (medium confidence, split vote) — so pull-buoy work is a useful but imperfect proxy for full-stroke arm mechanics, not a distortion to avoid. Best finding: in masters swimmers specifically, arms-only propelling *efficiency* correlates far more with arms-only speed (R=0.741) than raw arm power does (R=0.419) — pull-set gains are mostly about technique, not just strength (high confidence, n=29 masters swimmers — directly relevant population).

**Paddles.** The "paddles = extra shoulder load" folklore is only half-supported: paddles do *not* increase net mechanical/muscular load at matched pace (three independent biomechanical studies, high confidence — larger surface area compensates for reduced hand velocity) and do *not* disrupt arm-leg coordination timing (high confidence, replicated across 5+ studies). But paddles *do* increase absolute hand-force magnitude (medium confidence) — a plausible mechanism for shoulder strain that **no study has actually tested at the shoulder** (only hand-level forces measured; shoulder EMG/loading/injury data doesn't exist). A 4-week RCT found paddles added **no** measurable speed/strength benefit over that period (high confidence, but underpowered — doesn't rule out longer-term benefit).

**Kickboards.** One observational study (N=285, high-school/college swimmers, not masters) found *greater* kickboard use associated with *lower* odds of lumbar injury (adjusted OR=0.62) — the opposite of the popular "kickboards are risky" narrative. The specific "head-up position strains the neck" claim was tested and refuted. Single study, retrospective, reverse-causation plausible — a signal, not settled science.

**General context.** Of 36 shoulder-injury risk factors swimming experts rate as important, only 6 have supporting evidence, 6 show no association, and 22 have never been studied at all (high confidence, n=27 experts) — equipment folklore in this sport runs well ahead of the evidence generally.

**Fins.** Fins genuinely increase velocity in training (confirmed, e.g. 2.10 vs 1.71 m/s in a 50m sprint; 10–22% faster underwater dolphin kick) — the assisted-velocity mechanism works. But fins substantially *change* kick mechanics rather than just amplifying the natural kick: reduced kick amplitude and depth, altered inter-limb coordination (more discontinuous propulsion), and higher energy cost per meter (all confirmed, 3-0). Ankle plantarflexion range genuinely matters for kick velocity — experimentally restricting it reduces underwater kick speed and efficiency (confirmed, multiple studies) — supporting fins' plausible role in ankle-mobility work, though no study directly tested whether fin *use* improves mobility over time. **Practical read: heavy fin use in technique/drill sets is teaching a mechanically different kick, not a faster version of the same one** — worth using deliberately for conditioning/mobility, with some unfinned kick work to keep the "real" kick pattern grooved.

**Evidence tier, overall:** no systematic review treats any of these four tools as a category — every finding rests on individual primary studies, mostly n=8–29. Treat "confirmed" here as "consistent primary-study evidence," not "established consensus."

## Second Opinion follow-through — ideas folded into the guides (2026-08-27)

Acting on the "worth borrowing" items from the Second Opinion cross-check:

- ***Training Framework*** — added a new **"Lane management for a shared group"** section (CSS-based lane assignment, Front/Middle/Back-of-lane roles, staggered send-offs, fins/buoy as an equalizer), since this is the document framed around the actual shared-lane group context. Added a "Pre-pool prehab · 5min" step to each of the three day-cards (Day A: thoracic mobility + Y-T-W; Day B: rotator-cuff/scapular activation; Day C: core anti-rotation + hip/ankle mobility), each tailored to that day's specific load, with an honesty callout that the dose isn't validated for this population.
- ***The Returning Swimmer*** — expanded the shoulder-injury paragraph with the same three prehab categories in prose form. Lane management was deliberately **not** added here — this guide is framed around individual mental models, not shared-lane logistics, so it stays in the Audit only.
- ***The Returning Swimmer*** — also added a new **"At a Glance — Six Tenets"** panel right after the masthead, condensing the whole guide (three engines, one-job-per-session, weekly rotation, seasonal waves, the steady-state test, and the training-history floor) into six scannable lines. While doing this, found and fixed one more lingering instance of the unverified "muscle memory returns faster than fitness" claim in the guide's opening paragraph — missed in the first consistency pass — and corrected it the same way as the rest.

Both artifacts republished at their existing URLs; local HTML backups refreshed.

## Related documents

- **[Training Framework](https://peturgordon.github.io/swim-training/guides/training-framework.html)** — this research cross-referenced against a full read of the 65-session `garpar_sundaefingar_2025-2026.md` log, with a gap analysis and a 3-session weekly framework.
- **[The Returning Swimmer](https://peturgordon.github.io/swim-training/guides/returning-swimmer-guide.html)** — a simpler mental-model guide (three engines, session/week/season structure, steady-state protocol, do/avoid lists) for a competitive-youth swimmer returning after a long hiatus.
- **[Second Opinion](https://peturgordon.github.io/swim-training/research/gemini/second-opinion.html)** — cross-check of an independent Gemini research pass against this corpus.
- [`garpar_sundaefingar_2025-2026.md`](garpar_sundaefingar_2025-2026.md) — the source training log (66 sessions, Sept 2025–May 2026), already in this folder.
- [`research/gemini/gemini-masters-swim-training-framework.pdf`](gemini/gemini-masters-swim-training-framework.pdf) — the raw Gemini document reviewed above, kept for posterity with its own [README](gemini/README.md) explaining why most of it doesn't hold up.
- [`research/single-pass/`](single-pass/README.md) — single-pass, non-adversarial reports (currently: the stroke-count-efficiency report tested in Pass 4) kept as hypothesis sources, not citable evidence — see its README for why.

The GitHub repo ([peturgordon/swim-training](https://github.com/peturgordon/swim-training)) is ground truth for all of the above — the guides were originally also published as Claude Artifacts, but those are no longer maintained; don't republish there on future edits.

## Consistency pass — both guides updated (2026-08-27)

Both published documents were revised to match Pass 2's findings:

- ***The Returning Swimmer*** — removed the unverified "your stroke came back before your engine did" claim (Do/Avoid list + "coming back after years away" section) and replaced it with the actually-confirmed finding: detraining plateaus above an untrained baseline, so a genuine training history provides a real head start even if skill-vs-fitness timing itself isn't something research has compared. The shoulder-injury caution now notes the evidence is real but too weak (per its own authors) to set a validated volume cutoff. The decoupling section now notes the mechanism has direct swimming-specific confirmation, while numeric "decoupling %" thresholds remain an unvalidated heuristic.
- ***Training Framework*** — the heart-rate tracking recommendation was upgraded from "general endurance physiology, not swim-specific in the verified set" to reflect the Pass 2 finding that swimming-specific cardiac-drift evidence exists, while flagging that specific % thresholds are still unvalidated. Footer source count corrected (6 search angles, not 5) and Pass 2 added to the citation line.

Both artifacts republished at their existing URLs (see below); local HTML backups in `guides/` refreshed to match.

---

## Pass 4 — Stroke count, glide, and efficiency

Research question: does reducing freestyle stroke count below a swimmer's natural optimum (via a longer glide phase) raise physiological cost and heart rate, as claimed by a single-pass, non-adversarial, uncited report ([`single-pass/stroke-count-efficiency-report.md`](single-pass/stroke-count-efficiency-report.md)) — that report is the source of the hypotheses tested here, not itself a source of evidence. Population target: adult masters/recreational freestyle swimmers, 2-4x/week (not elite/junior specifically). 6 search angles → 24 sources fetched → 81 candidate claims → 25 verified → 16 confirmed, 9 refuted.

**Headline result: the glide-heavy, very-low-stroke-count model of efficiency is not supported, and the elite race-pace evidence points the other way.** Of the six specific claims tested, only claim 6 (elite SPL data) survived at high confidence and in the direction the source report predicted (against low-count glide swimming). Claims 1 and 2 (stroke-rate/energy-cost, glide-IVV/energy-cost) rest on real mechanisms but were not demonstrated for freestyle or for deliberate glide manipulation specifically. Claims 3 and 4 (metaboreflex, CO2/breathlessness) have no swimming-glide evidence at all — only general physiology and population/modality-mismatched studies. Claim 5 (a field-testable stroke-count optimization protocol) has no supporting study; it remains an untested proposal, not a validated method. Virtually all quantitative evidence is elite/competitive-population, not masters/recreational.

## Confirmed findings

### 1. Stroke-rate-driven energy cost is confirmed for backstroke, breaststroke and butterfly — not demonstrated for freestyle specifically — *medium confidence*
In 18 elite swimmers (intermittent 200m protocol), increases in stroke frequency were associated with increased energy cost at fixed velocity in backstroke, breaststroke and butterfly — but this relationship was not reported for freestyle in the same study, and increased stroke length reduced energy cost only in breaststroke (R²=0.24, p=0.02), with no significant stroke-length-to-cost relationship in freestyle, backstroke or butterfly. Separately, in 9 elite collegiate swimmers doing arm-only pull-buoy swimming, heart rate rose dose-dependently above an individual's critical stroke rate (CSR): 147.89±11.87 bpm at CSR, 158.67±14.20 bpm at 105% CSR, 163.78±13.65 bpm at 110% CSR (all p<0.001) — but velocity rose along with stroke rate rather than being held fixed, and legs were immobilized, so this cannot cleanly isolate a stroke-count-at-constant-pace effect. No evidence was found for the source report's specific fast-twitch-fiber-recruitment mechanism. Treat claim 1 as a plausible mechanism, confirmed in three of four competitive strokes, not directly demonstrated for the freestyle case it was meant to explain.
- Vote: 3-0 (stroke frequency raises cost in backstroke/breaststroke/butterfly, not reported for freestyle) · 3-0 (stroke length reduces cost only in breaststroke) · 2-1 (HR rises dose-dependently above critical stroke rate, arm-only)
- Sources: [Barbosa et al. 2008, Eur J Appl Physiol](https://link.springer.com/article/10.1007/s00421-008-0676-z) · [Matsuda et al. 2022, PMC9024976](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9024976/)
- Quotes: "At Backstroke, Breaststroke and Butterfly strokes, increases of SF were associated to increases of C, even when controlling the v" / "CSR represents 'the maximum SR that does not cause a continual rise in HR'"

### 2. Glide-induced intracycle velocity variation (IVV) and its link to energy cost — the mechanism is real in principle, but the claim as stated is not confirmed — *medium confidence*
In 10 international-level swimmers doing a maximal 200m front crawl (~91.6% of world-record pace), energy cost correlated significantly with IVV only in the first 50m lap — and the correlation was negative (R=-0.83, p<0.01), meaning higher IVV was associated with *lower* cost in that lap, the opposite of a simple "more IVV = more cost" relationship. Laps 2-4 showed no significant IVV-cost relationship at all, and the study's own authors concluded the IVV-cost relationship "does not present the direct relationship found in the literature" and "could not be used as a performance predictor in competitive events." The general mechanistic principle — that velocity fluctuation within a stroke cycle increases total work versus constant-velocity swimming at the same average speed — is well supported by the underlying power-velocity physics, but this evidence describes naturally-occurring race-pace IVV in already-elite swimmers, not deliberately lengthening glide/streamline. No study located measured glide duration as an independent variable against IVV or cost, so claim 2 is not confirmed as stated.
- Vote: 2-1 (lap-1 IVV-cost correlation, negative direction) · 3-0 (no relationship in laps 2-4) · 3-0 (authors' own conclusion against using IVV as a performance predictor) · 3-0 (general velocity-fluctuation-raises-cost mechanism)
- Sources: [Figueiredo/Barbosa et al. 2011/2012, Eur J Appl Physiol](https://link.springer.com/article/10.1007/s00421-011-2284-6) · [companion analysis, PMID 22262010](https://pubmed.ncbi.nlm.nih.gov/22262010/) · [Figueiredo et al. 2013, PMC3613086](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3613086/)
- Quotes: "the increase in the C was significantly associated with the increase in the IVV... only for the first 50m lap" / the IVV-cost relationship "does not present the direct relationship found in the literature" and "could not be used as a performance predictor in competitive events"
- **Cross-check note:** this is distinct from Pass 1's confirmed finding that IVV rises at maximal effort as swimmers fatigue (Fernandes et al. 2023) — that's a fatigue-driven mechanism, this is a glide-driven one, and the latter is not confirmed. A companion claim in this pass's verification batch — that elite swimmers show ~26% lower IVV than beginners across all speeds — is a re-test of the exact comparison Pass 1 already refuted (1-2), from the same source (PMC4327381); it was refuted again here (0-3), consistently rather than newly.

### 3. The exercise pressor reflex/muscle metaboreflex is established general physiology, but entirely untested in a swimming or glide context — *medium confidence on the mechanism, open on the swimming application*
The exercise pressor reflex — a feedback mechanism triggered by mechano- and metabosensitive skeletal-muscle afferents, producing a reflex rise in heart rate, blood pressure and ventilation in an intensity-dependent manner — is well established in general exercise physiology. However, the review defining it contains no mention of swimming, water immersion, or glide/streamline phases. The closest available evidence is land-based, not in-water: in 20 varsity/competitive swimmers doing land ergometry, breath-holding produced significantly higher exercise heart rate than free breathing (131±17 vs 118±14 bpm, p=0.001) — a sustained tachycardic response — but this is confounded with breath-holding rather than isometric glide posture specifically, elite/competitive-population, and land-based. Claim 3's swimming-glide-specific version remains untested.
- Vote: 3-0 (general exercise pressor reflex mechanism exists) · 3-0 (the defining review's scope contains no swimming/water-immersion content) · 2-1 (land-based breath-holding during ergometry raises exercise HR)
- Sources: [Grotle et al. 2022, Clinical Autonomic Research](https://link.springer.com/article/10.1007/s10286-022-00872-3) · [Walsh et al. 2026, PMC13332321](https://pmc.ncbi.nlm.nih.gov/articles/PMC13332321/)
- Quotes: "The exercise pressor reflex is a feedback mechanism engaged upon stimulation of mechano- and metabosensitive skeletal muscle afferents. Activation of these afferents elicits a reflex increase in heart rate, blood pressure, and ventilation in an intensity-dependent manner."
- **Cross-check note:** a companion claim that breath-holding also raised post-exercise blood pressure (141±14→156±16 mmHg systolic) was tested separately and refuted (0-3) — only the HR finding above survives. A separate, older source on underwater breath-hold swimming was tested and refuted (0-3): it found breath-holding produces an initial HR rise to ~106 bpm followed by diving bradycardia to ~48 bpm — a net bradycardic, not sustained-elevation, response, which runs counter to a simple version of claim 3 rather than supporting it. Kept in the refuted table for transparency; it does not confirm the metaboreflex mechanism for swimming either way.

### 4. EVIDENCE GAP — glide-heavy breathing rhythm and acute CO2/breathlessness — untested by any source found
No source located tested the acute mechanism claim 4 proposes. The closest available evidence — a 6-week chronic breathing-frequency training-adaptation study in 12 male university cyclists — never measured heart rate against breathing frequency and never assessed perceived breathlessness, dyspnea, or RPE; it measured only chronic ventilatory adaptations (vital capacity, CO2 sensitivity), and wasn't swimming. A 16-week monofin fin-swimming study in 28 youth national-level swimmers (~15-16y, 3.5±1.2y competitive experience) involving deliberate intermittent breath-holding drills is both a population (youth elite) and modality (monofin, deliberate apnea training) mismatch from adult recreational front-crawl glide-breathing. Claim 4 is neither confirmed nor refuted — it is an open question.
- Vote: 3-0 (chronic cycling-adaptation study does not test the acute mechanism) · 3-0 (fin-swimming study is a population/modality mismatch)
- Sources: [PMC3873666](https://pmc.ncbi.nlm.nih.gov/articles/PMC3873666/) · [PMC4723185](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4723185/)

### 5. EVIDENCE GAP — no field-testable fixed-pace/stroke-count HR protocol located
No study addressing claim 5 was located in this research pass, nor did any source describe or validate a U-shaped HR-vs-stroke-count curve for an individual swimmer at fixed pace. Treat the fixed-pace/varying-count testing method described in the source report as an untested proposal, not a validated field protocol — see Open questions.

### 6. Elite race-pace data contradicts very-low-count, long-glide swimming as an efficient strategy — stroke rate, not stroke length, tracks speed and race outcomes — *high confidence*
In 324 elite swimmers at the 2019 European Short-Course Championships, long-distance events (men's 1500m, women's 800m) showed stroke rate moderately correlated with speed (men ρ=0.37, women ρ=0.45) while stroke length showed a negligible-to-negative association (men ρ=0.07, women ρ=-0.08); race winners maintained relatively higher stroke rate and lower stroke length than peer competitors. Separately, in 11 elite 100m front crawl sprinters, the velocity decline between the first and second 50m lap was driven by a significant stroke-rate reduction (-6.61%, p<0.01) while stroke length was essentially preserved (+1.07%, not significant, p=0.66) — stroke length behaves as a fatigue floor that gets protected, not a target extended for speed or efficiency.
- Vote: 3-0 (stroke rate/length correlation with speed, distance freestyle) · 3-0 (winners' stroke-rate/length pattern, same source) · 3-0 (stroke length preserved / stroke rate drops under fatigue, 100m sprint)
- Sources: [Frontiers in Sports and Active Living 2025, PMC12541611](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12541611/) · [Frontiers 2025, fspor.2025.1656633](https://www.frontiersin.org/journals/sports-and-active-living/articles/10.3389/fspor.2025.1656633/full) · [PMC10250633](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10250633/)
- **Cross-check note:** this is consistent with, and helps explain, Pass 1's refutations — it is not new confirmation of anything Pass 1 already rejected. Pass 1 refuted "stroke length is THE determinant of speed" in both sprint (0-3) and distance events (0-3), and refuted "gold medallists combine high stroke rate with unreduced stroke length" (1-2, same Frontiers 2025 source). This pass's finding is the complementary positive result — stroke rate, not length, is what actually tracks speed and winning margins in elite distance freestyle — which is consistent with why those length-primacy claims failed verification in Pass 1. 100% elite/international-championship population; no masters/recreational SPL data was located.

### 7. Masters swimmers' season-long stroke-length/efficiency correlation is real but correlational, not causal evidence for deliberately reducing stroke count — *medium confidence*
In 23 masters swimmers (34.9±7.4 yrs, competitive background) tracked across one training season at three timepoints, propelling efficiency rose 6.3% (p<0.001), stroke index rose 6.8% (p=0.04), and stroke length rose 5.1-5.7% (p≤0.02-0.04), all moving together over the season — the study's authors interpret this as reflecting more efficient technique developing with training. This is the one directly population-appropriate source in this pass (masters, not elite) — but it describes naturally-occurring change over a training season, not an experimental manipulation of stroke count or glide, and a stronger, more specific claim apparently drawn from the same dataset ("stroke length rose 5.1% while stroke frequency fell 5%, coinciding with a 4.1% performance improvement") was tested separately in this pass and refuted (1-2). Read this narrowly: these metrics moved together as masters swimmers got fitter over a season — that is not evidence that deliberately lengthening stroke or reducing count *causes* the improvement.
- Vote: 3-0
- Sources: [Marinho et al. 2020, PMC7739371](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7739371/)
- Quotes: "Greater SI and SL indicates a swimmer with a more efficient swimming technique."

---

## Explicitly refuted claims — Pass 4

Listed for transparency. These are the intuitively attractive (or contrarian) claims tested against three independent adversarial reviewers and killed.

| Claim | Vote | Source |
|---|---|---|
| In a longitudinal study of 23 masters swimmers over one training season, stroke length increased 5.1% while stroke frequency decreased 5%, coinciding with a 4.1% improvement in 200m front crawl performance — i.e., fewer/longer strokes at a given effort were associated with better performance | 1-2 | [PMC7739371](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7739371/) |
| In elite freestyle sprint (50m), stroke length is the dominant determinant of speed while stroke rate shows little relationship — but gold medallists combine above-average stroke rate with unreduced stroke length | 0-3 | [PMC12541611](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12541611/) |
| In elite 200m front crawl, increased energy cost per 50m lap was significantly correlated with increased IVV — for the first lap only (R=-0.83, p<0.01) — not the other laps | 0-3 | [PMID 22262010](https://pubmed.ncbi.nlm.nih.gov/22262010/) |
| In front crawl, IVV was significantly lower for skilled/elite swimmers than beginners across all tested velocities, by ~26% (7.28±1.25% vs 9.80±1.70%, p<0.01/p<0.001) | 0-3 | [PMC4327381](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4327381/) |
| Stroke rate contributed slightly more than stroke length to overall 200m performance (17.5% vs 16.2%), though stroke length's contribution rose in the fatigued final lap | 0-3 | [PMC3613086](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3613086/) |
| In human breath-hold underwater swimming, HR rises to ~106 bpm within 10 seconds then falls into diving bradycardia (~48 bpm) — i.e., breath-holding does not produce sustained HR elevation but net bradycardia | 0-3 | [ScienceDirect 0034568787900910](https://www.sciencedirect.com/science/article/pii/0034568787900910) |
| Breath-holding produced significantly higher post-exercise blood pressure than free breathing (systolic 141±14 vs 156±16 mmHg, p=0.002; diastolic 71±14 vs 79±9 mmHg, p=0.01) | 0-3 | [PMC13332321](https://pmc.ncbi.nlm.nih.gov/articles/PMC13332321/) |
| In elite 50m freestyle, stroke length correlates more strongly with speed than stroke rate (SL ρ=0.57 men, ρ=0.50 women; SR trivial/non-significant) | 0-3 | [Frontiers 2025, fspor.2025.1656633](https://www.frontiersin.org/journals/sports-and-active-living/articles/10.3389/fspor.2025.1656633/full) |
| In elite 50m freestyle, gold medallists achieved higher stroke rate without a corresponding decrease in stroke length | 1-2 | [Frontiers 2025, fspor.2025.1656633](https://www.frontiersin.org/journals/sports-and-active-living/articles/10.3389/fspor.2025.1656633/full) |

## Caveats — Pass 4

- **Population mismatch is the dominant caveat of this entire pass.** Essentially all direct quantitative HR, energy-cost, and stroke-per-length evidence comes from elite or competitive populations: 18 elite swimmers (Barbosa 2008), 9 elite collegiate swimmers (Matsuda 2022, arm-only), 10 international-level swimmers (Figueiredo/Barbosa 2011-2013), 324 championship swimmers (Frontiers 2025), 11 elite swimmers (PMC10250633), 20 varsity swimmers (Walsh 2026), and 28 youth national-level fin-swimmers (PMC4723185) — not the adult masters/recreational (2-4x/week) population this pass targets. Only the masters-swimmer study (PMC7739371, n=23) partially matches the target population, and even there subjects were structured-training masters athletes with a competitive background, not purely casual recreational swimmers.
- **No surviving claim isolated "glide phase" as a directly measured or manipulated variable.** IVV studies measured naturally-occurring race-pace velocity fluctuation in already-elite swimmers; stroke-rate/energy-cost studies manipulated stroke rate generally or examined natural variation, not deliberate glide extension. Extrapolating any of these findings to masters/recreational swimmers practicing deliberate glide technique requires an inferential step this literature does not directly support.
- **Time-sensitivity:** sources span 2008-2026, with the core energy-cost and IVV mechanics papers from 2008-2013. These are foundational, still-cited exercise-physiology/biomechanics findings with no signal of being overturned by newer work — the freshest and most directly relevant SPL data (Frontiers 2025) reinforces rather than contradicts the older mechanics papers.

## Open questions — Pass 4

1. Does deliberately lengthening the glide/streamline phase — as opposed to naturally-occurring stroke-cycle IVV in elite race swimming — actually increase intracycle velocity variation and/or energy cost in freestyle specifically? No study directly tested glide duration as an independent variable.
2. Is there a validated field protocol (fixed pace, varying stroke count, HR per rep) for finding a recreational/masters swimmer's efficiency-optimal stroke count, and does it produce a real, repeatable U-shaped HR-vs-stroke-count curve? No study addressing this was located.
3. Does the exercise pressor reflex/muscle metaboreflex activate measurably during an isometric glide/streamline phase specifically in water, as opposed to land-based breath-holding or general terrestrial isometric exercise? Entirely untested in the literature surveyed.
4. Does a slower, glide-heavy breathing rhythm in freestyle acutely raise CO2 accumulation and perceived breathlessness independent of pace, in masters/recreational swimmers specifically? No acute-mechanism study was located; only unrelated chronic-adaptation (cycling) and youth-elite fin-swimming breath-hold-training studies exist.

## Full source list — Pass 4 (24 fetched)

| Source | Quality | Angle |
|---|---|---|
| [Marinho et al. 2020, masters swimmers longitudinal (PMC7739371)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7739371/) | primary | Stroke count / distance-per-stroke energy cost & HR |
| [Barbosa et al. 2008, energy cost & stroke frequency](https://link.springer.com/article/10.1007/s00421-008-0676-z) | primary | Stroke count / distance-per-stroke energy cost & HR |
| [Matsuda et al. 2022, critical stroke rate (PMC9024976)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9024976/) | primary | Stroke count / distance-per-stroke energy cost & HR |
| [USMS — distance per stroke](https://www.usms.org/fitness-and-training/articles-and-videos/articles/distance-per-stroke) | blog | Stroke count / distance-per-stroke energy cost & HR |
| [USMS — your ideal stroke rate](https://www.usms.org/fitness-and-training/articles-and-videos/articles/your-ideal-stroke-rate) | blog | Stroke count / distance-per-stroke energy cost & HR |
| [Frontiers 2025, elite SR/SL 324 swimmers (PMC12541611)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12541611/) | primary | Stroke count / distance-per-stroke energy cost & HR |
| [Figueiredo/Barbosa 2011/2012, energy cost & IVV](https://link.springer.com/article/10.1007/s00421-011-2284-6) | primary | Intracycle velocity variation and glide |
| [Companion analysis, IVV lap-by-lap (PMID 22262010)](https://pubmed.ncbi.nlm.nih.gov/22262010/) | primary | Intracycle velocity variation and glide |
| [IVV, elite vs. beginner (PMC4327381)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4327381/) | primary | Intracycle velocity variation and glide |
| [Taylor & Francis, IVV/coordination study](https://www.tandfonline.com/doi/abs/10.1080/14763141.2022.2077815) | unreliable (0 claims survived) | Intracycle velocity variation and glide |
| [Figueiredo et al. 2013, IVV & performance (PMC3613086)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3613086/) | primary | Intracycle velocity variation and glide |
| [IVV stability across a 200m effort](https://link.springer.com/article/10.1007/s00421-012-2468-8) | primary | Intracycle velocity variation and glide |
| [Wiley, muscle metaboreflex review](https://onlinelibrary.wiley.com/doi/10.1111/j.1748-1716.2010.02133.x) | unreliable (0 claims survived) | Exercise pressor response / metaboreflex in swimming |
| [J Appl Physiol, metaboreflex mechanism](https://journals.physiology.org/doi/full/10.1152/jappl.2000.88.2.487) | unreliable (0 claims survived) | Exercise pressor response / metaboreflex in swimming |
| [Grotle et al. 2022, exercise pressor reflex review](https://link.springer.com/article/10.1007/s10286-022-00872-3) | primary | Exercise pressor response / metaboreflex in swimming |
| [Underwater breath-hold HR response](https://www.sciencedirect.com/science/article/pii/0034568787900910) | primary | Exercise pressor response / metaboreflex in swimming |
| [Walsh et al. 2026, breath-holding during land ergometry (PMC13332321)](https://pmc.ncbi.nlm.nih.gov/articles/PMC13332321/) | primary | Breathing rhythm, CO2 retention, and breathlessness |
| [6-week breathing-frequency training adaptation (PMC3873666)](https://pmc.ncbi.nlm.nih.gov/articles/PMC3873666/) | primary | Breathing rhythm, CO2 retention, and breathlessness |
| [16-week monofin fin-swimming, youth national swimmers (PMC4723185)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4723185/) | primary | Breathing rhythm, CO2 retention, and breathlessness |
| [Adv Physiol Educ, CO2/ventilatory drive](https://journals.physiology.org/doi/full/10.1152/advan.00030.2015) | primary | Breathing rhythm, CO2 retention, and breathlessness |
| [Frontiers 2025, SR/SL kernel density estimation](https://www.frontiersin.org/journals/sports-and-active-living/articles/10.3389/fspor.2025.1656633/full) | primary | Elite stroke-per-length (SPL) race-pace data |
| [100m front crawl lap-to-lap SR/SL (PMC10250633)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10250633/) | primary | Elite stroke-per-length (SPL) race-pace data |
| [Incremental front crawl test, stroke & physiological outcomes (PMC10460968)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10460968/) | primary | Field-testable protocol for optimal stroke count |
| [PMC13454069](https://pmc.ncbi.nlm.nih.gov/articles/PMC13454069/) | primary | Field-testable protocol for optimal stroke count |
