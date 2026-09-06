# Swim Training

An evidence-checked masters swim training project: research on technique, endurance, and sprint training, cross-referenced against a season of real group programming, distilled into two reference guides and an ongoing log of individual practices.

## Guides

- **[Garpar Training Audit](guides/garpar-training-audit.html)** — research findings cross-referenced against a full season's training log, with a gap analysis and a recommended 3-session weekly framework.
- **[The Returning Swimmer](guides/returning-swimmer-guide.html)** — a simpler mental-model guide for a former competitive swimmer returning after a long hiatus: three engines, session/week/season structure, a steady-state protocol, do/avoid lists.

> These are static HTML files — GitHub renders them as source code, not as pages, unless viewed through GitHub Pages. See "Publishing" below.

## Research

- **[research_findings.md](research/research_findings.md)** — the full research corpus behind the guides: every adversarially-verified claim, what was explicitly refuted, sources, and open questions, across multiple research passes (core training science, detraining/decoupling/injury risk, equipment usage).
- **[garpar_sundaefingar_2025-2026.md](research/garpar_sundaefingar_2025-2026.md)** — the source training log analyzed above (66 sessions, Icelandic, Sept 2025–May 2026).

## Practices

Individual session plans, one file per date, in [`practices/`](practices/) — generated from the framework above, with session notes and results logged after the fact.

## Other

- [`research/gemini/`](research/gemini/) — an independent Gemini research export, kept for posterity, alongside [Second Opinion](research/gemini/second-opinion.html), the cross-check of it against this project's own findings.

See [WORKFLOW.md](WORKFLOW.md) for the full step-by-step process — how a practice gets generated, and exactly how to publish a change.

## Publishing

To make the HTML guides render as actual pages instead of source code, enable **GitHub Pages** for this repo (Settings → Pages → deploy from the `main` branch, root folder) once it's pushed. The guides would then be reachable at `https://<username>.github.io/<repo>/guides/garpar-training-audit.html`, etc.
