# onboarding

Stevan's working notes and tools for learning the Odysee / Sierra system.
Not production code. Nothing here is deployed.

## Read in this order

1. [docs/01-system-overview.md](docs/01-system-overview.md) — the whole system on one page:
   who uses it, the repositories, how a request flows, where data lives.
2. [docs/glossary.md](docs/glossary.md) — airline and Databricks vocabulary you will hit immediately.
3. [docs/open-questions.md](docs/open-questions.md) — things the code doesn't answer; ask a human.

## Layout

```
docs/    numbered explainers, built up in layers (overview first, then deep dives)
tools/   scripts we write to explore the repos (each one documents its own usage)
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
