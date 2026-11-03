# CLAUDE.md

This repository holds onboarding notes and exploration tools for a new engineer (Stevan)
learning the Odysee system. The real code lives in sibling checkouts under `..`
(odysee-frontend, schedule-service, odysee-data-warehouse, odysee-data-platform,
odysee-optimizers, odysee-infra, odysee-ds).

## How to help here

- **Explain top-down, in layers.** Start with the big picture and a diagram, then go one level
  deeper. Stevan thinks visually/spatially: prefer Mermaid diagrams and tables over long prose.
- **Assume strong general engineering background** (25 yrs, Perl/JS/TS, MySQL at scale, system
  design) but **no AWS, no PostgreSQL-specific features, no hands-on ML, weak Python.** Explain
  AWS, Databricks, Postgres and ML concepts by analogy to things they already know (MySQL, Unix, Perl/JS).
- **Be honest.** Distinguish what the code shows from what docs claim from what you infer.
  Mark inference explicitly. Point out stale docs and contradictions between repos.
- **Cite sources** as `repo/path/file:line` so claims can be checked.
- Docs go in `docs/` as numbered files (`02-…`, `03-…`). Update the README index when adding one.
  Unresolved questions go in `docs/open-questions.md`.
- Tools go in `tools/`, are read-only against the sibling repos, and must never need credentials
  unless that is their stated purpose.
- Never put secrets, account credentials or client data in this repo.
