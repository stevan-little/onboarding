# Prompt for the next session: make the demo data realistic and re-test the visualizations

Paste the block below to start the session. Edit the priorities first if they have changed.

---

We spent a long session building data visualizations of the synthetic airline ("Odysee Air") in
`odysee-data-warehouse/src/utilities/synthetic_airline`. Read these before doing anything:

- `onboarding/docs/14-data-visualizations.md` — what we built, what the data showed, known problems.
- `onboarding/docs/15-visualization-product-proposal.md` — which views we think belong in the product.
- `onboarding/tools/viz_data.py` — how each page's data is built (one mode per page family).
- `onboarding/CLAUDE.md` — house rules (explain top-down, cite sources, be honest, no client data).

**Goal.** The synthetic airline is too tidy to tell us whether the visualizations would survive a
real user. Build out the demo data so it is realistic enough to stress them, regenerate the pages,
and tell me honestly which ones hold up and which break.

**Why the current data is too tidy** (details in doc 14, "Limits of the synthetic airline"):
one month of schedule; every band flies every day; one seat count per aircraft type and no cabins;
at most two legs per trip; week, seasons and holidays are fixed multipliers; seats are handed out
in the order passengers are invented, not in booking order; no cancellations, overbooking, delays
or rebooking.

**What I want added, in priority order.** Do the first two well before starting the rest.

1. **A realistic schedule.** Bands that differ by weekday and change mid-season; at least two
   seasons so the year calendar is not one schedule repeated; multi-day rotations and overnights;
   more than two fleet types with different seat counts; a few red-eyes and a west-coast time zone;
   ideally a third, smaller hub or focus city. The band-to-flight expansion (sketch 1) should
   finally have something to show.
2. **Realistic booking behaviour.** Seats allocated in booking-time order so a sold-out flight
   turns away late bookers; cancellations and no-shows with overbooking; direction-of-day demand
   (out in the morning, back in the evening) so the mirror views show real imbalance; group
   bookings; events that lift one city for a few days.
3. **Operations.** Actual versus scheduled times: delays, a few cancellations, and what happens to
   connecting passengers (misconnects and rebooking). This is what the Gantt's retiming view is
   pretending to be.
4. **A real optimizer result.** Run one of the optimizers in `odysee-optimizers` on the synthetic
   schedule and load its output into the Fleet Gantt's study diff, replacing the greedy stand-in.
   Report where its rules differ from the ones the page assumes (30-minute turn, 35/60-minute
   connecting time, nobody rebooks).
5. **Scale.** A variant with a few hundred aircraft, to see which pages stop being readable.

**Constraints.**

- The sibling repos are read-only for this work. Do not commit in them. If the simulator itself
  should change, propose the change and wait for my go-ahead; otherwise extend it from
  `onboarding/tools/` the way `viz_data.py --gantt` subclasses `Simulation` to record refused
  requests. If you subclass, prove the unmodified outputs still match a plain run.
- No client data, no credentials. `odysee-optimizers/tests/fixtures/baseline_real_day.parquet` is
  real client data: do not read it into anything that gets published.
- Keep the simulator's tests in mind: `tests/fixtures/odyseeair/warehouse_tables_golden.json` pins
  its random draws, so anything that reorders draws changes every passenger.
- Each page carries its data inline in `<script id="data">`; published pages could not fetch a
  sibling data file. Keep a page under about 16 MB and say when one gets heavy.
- Publish updates to the same file paths so the existing artifact links keep working. The links
  are in doc 14.

**How to work.**

- Start by telling me, in a table, what you can and cannot make realistic and how you would check
  that it is realistic (for example against public sources such as the DOT T-100 file in
  `odysee-ds/Analysis/Past_analysis/`). Then proceed without waiting unless something needs my
  decision.
- After each data change, regenerate the affected pages and look at them. Say what you looked at
  and what you did not.
- Recompute every finding quoted in doc 14 on the new data and say which survive.
- Before you finish, have an independent reviewer check the two or three most important pages for
  bugs, wrong numbers and unsupported claims, as we did for the Gantt.
- Fix the open item from doc 14 while you are there: Hub Clock, Hub Retimer and Hub Waves wrongly
  exclude same-aircraft connections.

**What I want back.**

1. The realistic data, reproducible from `tools/` with one command per page.
2. An updated doc 14 and a short new doc: for each visualization, did it hold up, what broke, and
   what would it need. Be blunt.
3. A revised proposal (doc 15) if the tiers change.
4. Everything committed and pushed on the session's branch.
