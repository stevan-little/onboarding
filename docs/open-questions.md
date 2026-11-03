# Open questions

Things the code doesn't answer. Ask a human; record the answer and who gave it.

A prioritised one-pager of these, for discussing with a manager, is a shared doc: [Onboarding: open questions, prioritised](https://claude.ai/artifact/4HP4HUsRtsDamkzK3zocxr).

| # | Question | Why it's unclear | Answer |
|---|---|---|---|
| 1 | Who created the four AWS Databricks workspaces the warehouse deploys to? | `odysee-infra/README.md` says it has created none; `odysee-data-warehouse/resources/environments/*.tfvars` points at four. | **Probably answered (see 04):** `odysee-infra/stacks/environment` has tfvars for all of them; the README status block is stale. Confirm. |
| 2 | Is the Azure workspace still serving anything in production, or is it only an export source now? | `migration-export` stack expires 2026-11-18; schedule-service egress still lists `login.microsoftonline.com` (`schedule-service/infra/README.md`). | |
| 3 | Where is `odysee-mlops`, and do I need access? | Referenced by infra ADR 00021 and data-platform README as the owner of models; not in my repo list. | |
| 4 | What is the full chain of jobs after an SSIM upload? | Only the first job ID is in `schedule-service/settings.py`; the rest is in warehouse Terraform. | **Answered (see 03):** `bronze_ssim_flight_job` → `silver_schedule_flights_v2_job`, the master DAG; traced in 03 Layer 3. |
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
| 23 | What is the production revenue model's test WAPE, on which period, and is there a forward-in-time backtest? | No metrics in git (outputs stripped); validation is later than test, and the correction boosters are fitted on validation (see 06). | |
| 24 | Who moves the `@champion` alias for `…champion_ml_internal_…_full_network_…` in staging/prod, and how? | The promotion notebooks in `odysee-ds/deployment` name a different model with a hard-coded version. | |
| 25 | Is there a plan to share feature code between training (odysee-ds) and inference (`gold.schedule_revenue.py`)? | Functions are duplicated with no parity check; the JSX pipeline has `test_feature_parity.py`. | |
| 26 | Why is `model_drift_monitor` paused in staging and prod? | `resources/environments/*.tfvars`. | |
| 27 | Should the unused `ml_disrupted_leg_model_name` Terraform variable drive `silver.disrupted_revenue_prediction_leg.py`, which hard-codes the model name? | Declared in every tfvars, passed to no job. | |
| 28 | Is environment-wide serialization of schedule processing (one upload at a time, forced by the shared `connectivity_temp_connections` scratch table) a known throughput limit? | `jobs/connectivity_v2.py:1155-1162`; `max_concurrent_runs = 1` on the master DAG. | |
| 29 | Should "valid connection" (max connection time, max stops) be the same in Connectivity, Guest Disruptions and the optimizers? | 6 h flat vs 6 h/12 h vs carrier data (see 07). | |
| 30 | Should Connectivity opportunity values use the same hour-smoothing as the optimizers? | Warehouse scoring has none (see 07, finding 2). | |
| 31 | Are the Stations section and the Network Overview page (v1 routes) dead code? | No backend routes for either. | |
| 32 | Under `catalog_override` (staging/prod/demo), the Alaska adapter's tables resolve to the same names the warehouse's DLT pipelines write (e.g. `alaska_sierra_staging_catalog.bronze.dap_current_bookings`). How is a collision avoided when adapter jobs run there? | `odysee-data-platform/src/odysee_data/core/naming.py:117-143`, `config/tenants/alaska.yaml`. | |
| 33 | Who runs the data-platform jobs while every schedule is paused, and how do 24-hour freshness SLAs hold? | `schedules_paused: true` in every environment. | |
| 34 | Have data-platform staging/prod ever been released? | No tags in this clone. | |
| 35 | What is BA's source format, and who writes its adapter? | BA is provisioned in infra but has no config or adapter. | |
| 36 | schedule-service has no customer/organization scoping: every user sees every schedule in the environment. Is "one real customer per environment" a deliberate rule, and what changes before two customers share one? | No org column, filter or auth check anywhere; `XE → jsx` mapping is a default (see 09). | |
| 37 | Is the daily attribution refresh (`gold_preserved_itineraries_refresh_job`, hard-coded `PAUSED`) run by hand, and how fresh must the Impact Dashboard be? | Cancellations and incremental bookings only update when it runs. | |
| 38 | Who maintains the curated Before/After CSV that defines attribution pairs, and how are the choices reviewed? | `jobs/reprocess_attribution_pairs_loop.py`; the headline ROI depends on it. | |
| 39 | Is preserved/incremental revenue presented to customers as an upper bound? | Full booked fares count, with no counterfactual for rebooking or for passengers who'd have booked another flight (see 09). | |
