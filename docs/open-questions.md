# Open questions

Things the code doesn't answer. Ask a human; record the answer and who gave it.

| # | Question | Why it's unclear | Answer |
|---|---|---|---|
| 1 | Who created the four AWS Databricks workspaces the warehouse deploys to? | `odysee-infra/README.md` says it has created none; `odysee-data-warehouse/resources/environments/*.tfvars` points at four. | |
| 2 | Is the Azure workspace still serving anything in production, or is it only an export source now? | `migration-export` stack expires 2026-11-18; schedule-service egress still lists `login.microsoftonline.com` (`schedule-service/infra/README.md`). | |
| 3 | Where is `odysee-mlops`, and do I need access? | Referenced by infra ADR 00021 and data-platform README as the owner of models; not in my repo list. | |
| 4 | What is the full chain of jobs after an SSIM upload? | Only the first job ID is in `schedule-service/settings.py`; the rest is in warehouse Terraform. | |
| 5 | How far along is the warehouse → data-platform migration in practice? | `MIGRATION.md` lists P0–P3 moves; some marked "not yet published or reconciled". | |
| 6 | Which customers are live vs. demo/prospect? (Alaska, JSX, New Zealand) | Inferred from catalog names and notebook folders only. | |
| 7 | What's the relationship between `odysee-ds` notebooks and production models? | Notebooks include `promote_model_prod`, but no CI/packaging. | |
