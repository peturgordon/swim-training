# Workflow

A step-by-step reference for how this project actually runs — usable by a future Claude Code session or by hand.

## 1. How the research is organized

[`research/research_findings.md`](research/research_findings.md) is the single source of truth. Every claim in it is tagged **confirmed** (survived adversarial verification) or **refuted** (tested and killed) — never treat a refuted claim as true again, even if it sounds plausible. New research passes get appended as a new `## Pass N` section; they don't overwrite earlier passes.

## 2. How a practice session gets generated

**Weekly rotation:** Monday = Technique + Aerobic Base, Wednesday = Speed Bridge (sprint), Saturday = Race Distance (endurance) — three sessions a week, one hour each, matching the three archetypes below. If asked for "the next practice" without a type specified, work it out rather than asking: check the target date's day-of-week against this rotation, and check [`practices/index.md`](practices/index.md) for what's already logged so the same slot isn't generated twice. (An alternative rotation was considered and deliberately set aside — see [`BACKLOG.md`](BACKLOG.md) — this one stays current unless told otherwise.)

1. Start from the framework in [`guides/training-framework.html`](guides/training-framework.html) — it defines three session archetypes (technique + aerobic base / speed-bridge / race-distance-endurance) and the principles behind them (polarized effort distribution, technique-fresh-before-fatigue, real recovery for max effort, etc.).
2. Apply whatever the user specifies for that day beyond the default: a different archetype, time cap, distance cap, equipment notes.
3. Write the session using this section order and style (see [`practices/2026-09-05.md`](practices/2026-09-05.md) or [`practices/2026-09-07.md`](practices/2026-09-07.md) for real examples):
   - `# YYYY-MM-DD — <session name>`, then total time/distance
   - `## Warmup`, `## Technique`, `## Bridge` (if applicable), `## Main set`, `## Cooldown` — each with its own meterage
   - `## Metrics to capture` — **required in every session, not optional.** What to measure and when (which specific set/rep, not just "sometime") — **not how**: there's no poolside capture method settled yet (open question, see [`BACKLOG.md`](BACKLOG.md)), and figuring that out happens separately, between sessions, not in the water. Don't suggest a capture method inline in a practice file.
     - By archetype: Technique + Aerobic Base → stroke count per 25m at a fixed pace during the aerobic main set. Speed Bridge → RPE or a 10s pulse count immediately after the max-effort reps. Race Distance → stroke count held across the fatiguing main set, start vs. end (the single most evidence-grounded metric in the framework), plus RPE/HR.
   - `## Notes` — equipment choices and why, tied back to [`research_findings.md`](research/research_findings.md) where relevant
4. Save as `practices/YYYY-MM-DD.md`.
5. **Add a link to the new file at the top of [`practices/index.md`](practices/index.md)** (newest first) — this is not automatic; GitHub Pages 404s on [`practices/`](practices/) without it.
6. After the session is actually swum, if anything changed from the plan (distance, sets, results like stroke counts held), edit the same file: mark the changed line `(as swum — planned Xm)`, update the total, and add a `## Session log` section at the bottom noting what happened and what it means.

## 3. How to publish (git + GitHub Pages)

This repo's commits use a **local identity** (deliberately different from the global git config) — check it with `git config --local --list` before committing, and never pass `--global` in this repo.

Authentication is via a dedicated SSH key set up specifically for this GitHub account, configured in `~/.ssh/config` for `Host github.com` — separate from any other key on this machine, no interaction needed.

To publish a change:
```bash
cd <local clone of this repo>
git add <changed files>
git commit -m "short description"
git push
```

**Automated check, after every push:** [`.github/workflows/check-links.yml`](.github/workflows/check-links.yml) runs [`scripts/check-links.sh`](scripts/check-links.sh), which verifies every `practices/*.md` file is linked from `practices/index.md`, and every internal (non-`http`) link across every `.md`/`.html` file in the repo resolves to a real file. It does **not** check external citation links (deliberately — too slow/flaky against third-party sites to run on every push) and it does **not** block the push itself (GitHub Actions run after a push completes) — a failure shows as a red ❌ on the commit at github.com, not a rejected push. Run it locally before pushing with `bash scripts/check-links.sh` from the repo root to catch the same thing immediately instead of waiting to notice the commit status.

Live site: **https://peturgordon.github.io/swim-training/** (root and [`practices/`](practices/) both need their own `index.md` — GitHub Pages has no automatic directory listing, so any new top-level section needs one too).

Repo: **https://github.com/peturgordon/swim-training**

## 4. If something sensitive gets committed and pushed by mistake

Editing the file and committing the fix is **not enough** — the old version is still sitting in an earlier commit, fully recoverable by anyone who checks it out, even after the file looks clean on the latest commit. This happened once already (a name, an email, and a local file path in `WORKFLOW.md`; a coach's name in the training log) and needed a full fix, not just a new commit on top:

1. Search **all of history**, not just the current files, for every term of concern:
   ```bash
   git log --all --source --oneline -S"<exact string>" -- .
   ```
2. Rewrite it out of history:
   - Wrong only in commit author/email → `git filter-branch -f --env-filter '...'`
   - Wrong in a file's actual text → `git filter-branch -f --tree-filter '...'` (small repo, fine for a handful of commits)
3. Clean up what the rewrite leaves behind, or the old data is still locally recoverable:
   ```bash
   rm -rf .git/refs/original
   git reflog expire --expire=now --all
   git gc --prune=now --aggressive
   ```
4. Re-run the same `git log -S` search from step 1 — expect nothing back — before trusting it's fixed.
5. `git push --force origin main` to overwrite what's already public.

**Limit of this fix:** anyone who cloned or forked the repo before the rewrite still has the old data. A force-push only overwrites the copy on GitHub's servers, not copies that already left it.
