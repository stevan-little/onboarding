# onboarding

Stevan's working notes and tools for learning the Odysee / Sierra system.
Not production code. Nothing here is deployed.

## Read in this order

1. [docs/01-system-overview.md](docs/01-system-overview.md) — the whole system on one page:
   who uses it, the repositories, how a request flows, where data lives.
2. [docs/02-domain-data-model.md](docs/02-domain-data-model.md) — the entities (schedule, band,
   flight, leg, booking, itinerary, O&D, coupon), how they relate, and how products join them.
3. [docs/03-guest-disruptions.md](docs/03-guest-disruptions.md) — one product traced from the
   React page through the API and SQL to the Databricks job DAG and its algorithms.
4. [docs/04-aws-infrastructure.md](docs/04-aws-infrastructure.md) — AWS and Databricks from first
   principles: accounts, IAM roles, VPCs, how one client's data is walled off, how Terraform applies.
5. [docs/05-optimizers.md](docs/05-optimizers.md) — the three CP-SAT optimizers: constraint
   programming from first principles, the study lifecycle, the models, and how to run the tests.
6. [docs/06-revenue-models.md](docs/06-revenue-models.md) — the ML revenue model behind every dollar
   figure: ML basics, what's predicted, the model stack, how it reaches production, how far to trust it.
7. [docs/07-connectivity-intelligence.md](docs/07-connectivity-intelligence.md) — served markets and
   near-miss connection opportunities: the binary-search engine, ranking, impacts and valuation.
8. [docs/08-data-platform-adapters.md](docs/08-data-platform-adapters.md) — the multi-tenant data
   platform: adapters, the standard layer, contracts and gates, and where the migration really stands.
9. [docs/09-attribution.md](docs/09-attribution.md) — Load Review / Impact Dashboard: how "preserved"
   and "incremental" booked revenue are defined, produced and should be read.
10. [docs/10-how-code-ships.md](docs/10-how-code-ships.md) — branches, deploys, approvals, local checks
    and commit/AI rules for every repo, side by side. Read before a first PR.
11. [docs/glossary.md](docs/glossary.md) — airline and Databricks vocabulary you will hit immediately.
12. [docs/open-questions.md](docs/open-questions.md) — things the code doesn't answer; ask a human.
   Prioritised one-pager (shared doc): [Onboarding: open questions, prioritised](https://claude.ai/artifact/4HP4HUsRtsDamkzK3zocxr).

## Layout

```
docs/    numbered explainers, built up in layers (overview first, then deep dives)
tools/   scripts we write to explore the repos (each one documents its own usage)
         nbcode.py  print notebook source as text, never outputs (they may hold client data)
```

## The repositories being studied

All are siblings of this checkout (e.g. `../schedule-service`).

| Repo | One line |
|---|---|
| odysee-frontend | Next.js web app the airline users see |
| schedule-service | FastAPI backend; the frontend's only API; triggers Databricks jobs |
| odysee-data-warehouse | Legacy Databricks pipelines (Alaska-specific) + product modules + Lakebase serving |
| odysee-data-platform | New multi-tenant ingestion/platform layer, being migrated into from the warehouse |
| odysee-optimizers | CP-SAT schedule optimizers, run as Databricks jobs |
| odysee-infra | Terraform: AWS accounts, Databricks/Unity Catalog, client isolation |
| odysee-ds | Data-science notebooks: analysis, feature engineering, model training/promotion |
