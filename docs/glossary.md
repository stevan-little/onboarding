# Glossary

Terms you will hit in the first week. Grouped by domain. "≈" gives an analogy to familiar tech.

## Airline domain

| Term | Meaning |
|---|---|
| **SSIM** | IATA *Standard Schedules Information Manual* — the fixed-width text file format airlines use to exchange schedules. What users upload. |
| **Leg** | One takeoff-to-landing flight segment (SEA→ANC). The atomic unit of a schedule. |
| **Segment** | What a passenger books under one flight number; may be one or more legs. |
| **Itinerary** | A passenger's whole trip: one or more segments, possibly with connections. |
| **O&D** (origin & destination) | The passenger's true start and end, regardless of connections. SEA→HNL via PDX is one O&D, two legs. "True O&D" in the code means exactly this. |
| **PNR** | Passenger Name Record — a booking. "Bookings" tables are PNR data. |
| **MCT** | Minimum Connecting Time — the shortest legal/practical layover at an airport. Decides whether two legs form a valid connection. |
| **Period** | A date range a schedule applies to (schedules are seasonal). Many API routes are `/{schedule}/{period}/…`. |
| **Disruption** | A booked passenger whose itinerary no longer works under a new schedule (flight removed, retimed past MCT…). |
| **RASM** | Revenue per Available Seat Mile — core airline profitability metric. |
| **RPM / ASM** | Revenue Passenger Miles / Available Seat Miles. |
| **Load factor** | Fraction of seats filled. |
| **Gauge / fleet gauge** | Aircraft size on a route. The gauge optimizer chooses which aircraft type flies what. |
| **Frequency plan** | How many times per day/week a route is flown. |
| **Carrier code** | Two-letter IATA airline code: AS = Alaska, QX = Horizon, OO = SkyWest, HA = Hawaiian. |
| **ARC / DDS** | Airlines Reporting Corporation, which settles ticket sales across the industry; DDS is its Direct Data Solutions sales dataset. Used for competitor and industry demand views. |
| **Mileage Plan** | Alaska's loyalty program — appears in revenue valuation rules. |

## Data platform

| Term | Meaning |
|---|---|
| **Databricks** | Hosted Spark platform: notebooks, scheduled jobs, SQL warehouses, all over files in cloud storage. |
| **Spark / PySpark** | Distributed data-processing engine; PySpark is its Python API. ≈ a SQL engine where the query plan runs across many machines. |
| **Delta table** | Parquet files + a transaction log in S3, giving ACID, MERGE, time travel. ≈ an InnoDB table whose storage is a directory of files. |
| **Unity Catalog (UC)** | Databricks' namespace + permissions layer: `catalog.schema.table`. ≈ MySQL `database.table` with one extra level on top, plus GRANTs. |
| **Volume** | A UC-governed directory of plain files (where uploaded SSIM files land). |
| **Medallion (bronze/silver/gold)** | Layering convention: bronze = raw as received, silver = cleaned/typed/deduped, gold = business logic and aggregates. |
| **SCD Type 1 / Type 2** | Slowly Changing Dimension: Type 1 overwrites the row; Type 2 keeps history with valid-from/valid-to rows. |
| **DLT (Delta Live Tables)** | Declarative pipeline framework (`@dlt.table`). Used heavily in the warehouse; the new data-platform deliberately avoids it (its adr/00004). |
| **Job / workflow** | A scheduled or triggered DAG of tasks in Databricks. ≈ cron + a dependency graph. |
| **Asset Bundle (DAB)** | `databricks.yml` — Databricks' deploy-as-code format (optimizers use it; warehouse uses Terraform instead). |
| **Lakebase** | Databricks-managed PostgreSQL. Gold tables are *synced* into it so the API gets fast row lookups. ≈ an ETL-fed read replica. |
| **SQL warehouse** | A Databricks compute endpoint that answers SQL over Delta tables. Slower to start, built for scans, not point lookups. |
| **Service principal** | A non-human identity (≈ a MySQL user for an application). Jobs run *as* a per-client principal for isolation. |
| **Delta Sharing** | Protocol for sharing tables across organisations — how airline data arrives ("alaska_share", "DAP share"). |
| **Tenant** | One client airline, with its own catalog `<tenant>_<env>`. |
| **Contract** | A versioned schema for a published table (`odysee-data-platform/contracts/`). Breaking change = new major version side by side. |

## AWS (for someone who has never used it)

| Term | Meaning |
|---|---|
| **Account** | Hard isolation boundary with its own billing and permissions. Here: one per environment. |
| **Organization / OU / Control Tower** | Grouping and guardrails over many accounts. |
| **IAM role** | A set of permissions an identity can assume. |
| **S3** | Object storage — where all Delta files physically live. |
| **KMS** | Encryption key service; one key per client here. |
| **ECS Fargate** | Runs Docker containers without managing servers — where schedule-service runs. |
| **RDS** | Hosted Postgres/MySQL — schedule-service's own database. |
| **ElastiCache / Valkey** | Hosted Redis-compatible cache. |
| **SSO** | `aws sso login` — how humans get temporary credentials. |

## Tooling / org

| Term | Meaning |
|---|---|
| **Sierra** | Internal codename for the product; Jira project key `SIERRA`. |
| **Terraform Cloud (TFC)** | Stores Terraform state and locks; org `Odysee`. |
| **ADR** | Architecture Decision Record — numbered markdown files in `adr/`; index is in `adr/README.md`. |
| **Clerk** | Hosted authentication (login, JWTs) for frontend and API. |
| **Novu** | Notification service used by schedule-service. |
| **CP-SAT** | Google OR-Tools' constraint solver used by the optimizers. |
