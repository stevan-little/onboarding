# Open questions

Things the code doesn't answer. Ask a human; record the answer and who gave it.

| # | Question | Why it's unclear | Answer |
|---|---|---|---|
| 1 | Who created the four AWS Databricks workspaces the warehouse deploys to? | `odysee-infra/README.md` says it has created none; `odysee-data-warehouse/resources/environments/*.tfvars` points at four. | **Probably answered (see 04):** `odysee-infra/stacks/environment` has tfvars for all of them; the README status block is stale. Confirm. |
| 2 | Is the Azure workspace still serving anything in production, or is it only an export source now? | `migration-export` stack expires 2026-11-18; schedule-service egress still lists `login.microsoftonline.com` (`schedule-service/infra/README.md`). | |
| 3 | Where is `odysee-mlops`, and do I need access? | Referenced by infra ADR 00021 and data-platform README as the owner of models; not in my repo list. | |
| 4 | What is the full chain of jobs after an SSIM upload? | Only the first job ID is in `schedule-service/settings.py`; the rest is in warehouse Terraform. | |
| 5 | How far along is the warehouse → data-platform migration in practice? | `MIGRATION.md` lists P0–P3 moves; some marked "not yet published or reconciled". | |
| 6 | Which customers are live vs. demo/prospect? (Alaska, JSX, New Zealand) | Inferred from catalog names and notebook folders only. | |
| 7 | What's the relationship between `odysee-ds` notebooks and production models? | Notebooks include `promote_model_prod`, but no CI/packaging. | |
| 8 | Is excluding zero-revenue itineraries from disruption analysis intended? Which passengers does it drop (award tickets, staff travel)? | `gold.disrupted_itineraries_v2.py`: `FILTER_ZERO_REVENUE = True`, but its comment says "off by default". | |
| 9 | Does anything persist legacy flight IDs across reprocessing of a schedule? | Legacy `expand_flights` uses `uuid()`, which changes on every run; the new contract requires stable IDs. | |
| 10 | Is the `flight` table in schedule-service's Postgres still populated or read by anything? | The ORM model exists in `database/models.py:194`, but nothing in the service uses it. | |
| 11 | Who owns the design of the draft product contracts (`itinerary_schedule_match`, `schedule_revenue`, `connectivity_core`)? | They're placeholders with no columns; that logic only exists in the warehouse today. | |
| 12 | Is "N moved" on the Guest Disruptions table meant to count distinct shift *sizes*? "Not found" can only ever be 0 or 1. | The API counts `DISTINCT disruption_reason`, and that text embeds the minutes (`services/disruption.py`, `gold.guest_disruptions_v2.py`). | |
| 13 | Do disruption alternatives deliberately ignore seat availability? | `disruption_alternatives_v2.py` filters on time, connections, MCT and carrier, but not on free seats. | |
| 14 | Should the "not found" thresholds be unified? (`9999` in the pipeline and API, `< 1440` in the reason text) | Two repos depend on the same magic numbers. | |
| 15 | Is someone handling the `migration-export` stack's expiry on 2026-11-18, and its hand-made static AWS key? | `odysee-infra/stacks/migration-export/README.md`. | |
| 16 | Can schedule-service's `temporary-network` VPC be deleted now that the real dev VPC exists? Its range `10.95.96.0/20` is also demo's. | `schedule-service/infra/stacks/temporary-network/README.md` vs `odysee-infra/stacks/environment/README.md`. | |
| 17 | Which region will `odysee-ml-prod` use? | `adr/00016` lists us-west-2; `adr/00022` says eu-central-1, pending CTO/legal. | |
| 18 | How do I get AWS and Databricks access, and who owns the Google Workspace groups? | `adr/00017`. | |
| 19 | Does any deployed environment set `NEXT_PUBLIC_ENABLE_MOCKS=true`, i.e. show mocked optimizer results? The frontend's optimisation `results`/`rotations`/`decision` mocks look stale now that the backend implements them. | `odysee-frontend/apps/web/src/mocks/config.ts` vs `schedule-service/.../services/optimizer_studies.py`; the Vercel env isn't in the repo. | |
| 20 | Should odysee-optimizers pin Python (`.python-version` or `<3.13`)? `uv sync` fails on 3.13 because the pinned ortools has no wheel. | Reproduced in this session. | |
| 21 | When will the revenue models score continuous time, so `core/revenue_smoothing.py` can be removed? | It's labelled a temporary stopgap; the retiming optimizers' recommendations depend on it. | |
| 22 | When does the optimizer API move from `alaska_sierra_<env>_catalog` to the tenant catalogs? | `schedule-service/settings.py:100`. | |
