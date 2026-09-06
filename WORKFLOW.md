# Workflow

A step-by-step reference for how this project actually runs — usable by a future Claude Code session or by hand.

## 1. How the research is organized

`research/research_findings.md` is the single source of truth. Every claim in it is tagged **confirmed** (survived adversarial verification) or **refuted** (tested and killed) — never treat a refuted claim as true again, even if it sounds plausible. New research passes get appended as a new `## Pass N` section; they don't overwrite earlier passes.

## 2. How a practice session gets generated

1. Start from the framework in `guides/garpar-training-audit.html` — it defines three session archetypes (technique + aerobic base / speed-bridge / race-distance-endurance) and the principles behind them (polarized effort distribution, technique-fresh-before-fatigue, real recovery for max effort, etc.).
2. Apply whatever the user specifies for that day: which archetype, time cap, distance cap, any equipment notes.
3. Write the session using this section order and style (see `practices/2026-09-05.md` or `practices/2026-09-07.md` for real examples):
   - `# YYYY-MM-DD — <session name>`, then total time/distance
   - `## Warmup`, `## Technique`, `## Bridge` (if applicable), `## Main set`, `## Cooldown` — each with its own meterage
   - `## Notes` — equipment choices and why, tied back to `research_findings.md` where relevant
4. Save as `practices/YYYY-MM-DD.md`.
5. **Add a link to the new file at the top of `practices/index.md`** (newest first) — this is not automatic; GitHub Pages 404s on `practices/` without it.
6. After the session is actually swum, if anything changed from the plan (distance, sets, results like stroke counts held), edit the same file: mark the changed line `(as swum — planned Xm)`, update the total, and add a `## Session log` section at the bottom noting what happened and what it means.

## 3. How to publish (git + GitHub Pages)

This repo's commits use a **local identity**, already set — don't use `--global`:
```
git config --local user.name   # → peturgordon
git config --local user.email  # → 325747432+peturgordon@users.noreply.github.com
```

Authentication is via a dedicated SSH key (`~/.ssh/id_ed25519_github_peturgordon`, configured in `~/.ssh/config` for `Host github.com` — separate from the existing GitLab key, no interaction needed).

To publish a change:
```bash
cd "<local clone of this repo>"
git add <changed files>
git commit -m "short description"
git push
```

Live site: **https://peturgordon.github.io/swim-training/** (root and `practices/` both need their own `index.md` — GitHub Pages has no automatic directory listing, so any new top-level section needs one too).

Repo: **https://github.com/peturgordon/swim-training**
