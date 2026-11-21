#!/usr/bin/env python3
"""Build the JSON behind viz/data-shapes.html from the synthetic "Odysee Air" airline.

Read-only against ../odysee-data-warehouse; needs no credentials and touches no client data.
Everything it emits comes from the warehouse repo's own simulator
(src/utilities/synthetic_airline), so every pattern is an assumption of that simulator.

Usage:
    python3 tools/viz_data.py --inject viz/data-shapes.html   # refresh the page's data
    python3 tools/viz_data.py --plan-only --inject viz/hub-waves.html
    python3 tools/viz_data.py --plan-only --inject viz/hub-clock.html
    python3 tools/viz_data.py --plan-only --inject viz/hub-retimer.html
    python3 tools/viz_data.py --journeys --inject viz/journey-flows.html
    python3 tools/viz_data.py --journeys --inject viz/fare-split.html
    python3 tools/viz_data.py --journeys --inject viz/hub-compass.html
    python3 tools/viz_data.py --journeys --inject viz/leg-flows.html
    python3 tools/viz_data.py --year --inject viz/load-calendar.html
    python3 tools/viz_data.py --loads --inject viz/network-treemap.html
    python3 tools/viz_data.py --loads --inject viz/flight-profiles.html
    python3 tools/viz_data.py --loads --inject viz/flight-scatter-matrix.html
    python3 tools/viz_data.py --gantt viz/hub-gantt.html
    python3 tools/viz_data.py > data.json                    # or just print the JSON
"""
from __future__ import annotations

import argparse
import io
import json
import math
import sys
from datetime import date, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

HUB_TZ = ZoneInfo("America/New_York")
UTC = ZoneInfo("UTC")
FOCUS_LEGS = (("BOS", "PIT"), ("PIT", "BOS"))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--warehouse", default=str(Path(__file__).parents[2] / "odysee-data-warehouse"))
    ap.add_argument("--day", default="2027-02-12")
    ap.add_argument("--plan-only", action="store_true",
                    help="schedule and airports only; skips the booking simulation (about 1s)")
    ap.add_argument("--journeys", action="store_true",
                    help="every origin-destination-via combination with its passengers and fares "
                         "for the whole month (runs the booking simulation, about 25s)")
    ap.add_argument("--loads", action="store_true",
                    help="seats sold, connecting passengers and revenue for every flight on every "
                         "day of the month (runs the booking simulation, about 25s)")
    ap.add_argument("--gantt", metavar="PAGE",
                    help="rebuild the data inside viz/hub-gantt.html: every flight on every day "
                         "(seats sold, connecting, revenue, requests refused for lack of seats) and "
                         "the passengers on every pair of connecting flights (about 25s)")
    ap.add_argument("--year", action="store_true",
                    help="passengers and revenue per airport-and-hub pairing for every day of 2027 "
                         "(simulates the whole year on the February schedule, about 5 minutes)")
    ap.add_argument("--inject", help="HTML page whose <script id=data> block gets the JSON")
    args = ap.parse_args()
    sys.path.insert(0, args.warehouse)
    from src.utilities.synthetic_airline.airports import AIRPORTS
    from src.utilities.synthetic_airline.network import Network
    from src.utilities.synthetic_airline.simulate import Simulation
    from src.utilities.synthetic_airline.ssim import read_schedule
    from src.utilities.synthetic_airline.warehouse_tables import coupon_cents

    fixtures = Path(args.warehouse) / "tests/fixtures/odyseeair"
    ssim = fixtures / "OC_FEB27_SSIM_73G_E75_v2.ssim"
    meta = json.loads((fixtures / "warehouse_tables_golden.json").read_text())["meta"]
    schedule = read_schedule(ssim.open())
    network = Network(schedule)
    focus_day = date.fromisoformat(args.day)
    first, last = schedule.carrier_record.validity_from, schedule.carrier_record.validity_to

    def hub_minutes(utc_naive) -> int:
        local = utc_naive.replace(tzinfo=UTC).astimezone(HUB_TZ)
        return (local.date() - focus_day).days * 1440 + local.hour * 60 + local.minute

    # --- 1. the plan: every leg on the focus day, and which aircraft rotation it belongs to
    dated = network.legs_on(focus_day)
    by_number = {d.leg.flight_number: d for d in dated}
    # One id per aircraft-day: follow SSIM's onward-flight pointers, and start a new line when the
    # onward flight leaves before this one lands (it belongs to the next day, so another aircraft
    # is flying it today). The fixture has one two-day cycle like that, via an overnight DEN trip.
    rotation: dict[str, int] = {}
    rid = 0
    for number in by_number:
        if number in rotation:
            continue
        cur, prev = number, None
        while cur and cur in by_number and cur not in rotation:
            if prev is not None and by_number[cur].departure_utc < by_number[prev].arrival_utc:
                rid += 1
            rotation[cur] = rid
            prev, cur = cur, by_number[cur].leg.next_flight_number
        rid += 1
    legs = [
        {
            "id": d.leg_id, "fn": d.leg.flight_number, "o": d.leg.origin, "d": d.leg.destination,
            "dep": hub_minutes(d.departure_utc), "arr": hub_minutes(d.arrival_utc),
            "ac": d.leg.aircraft_type, "seats": d.seats, "rot": rotation[d.leg.flight_number],
            "days": d.leg.days_of_operation,
        }
        for d in dated
    ]
    used = sorted({x for leg in legs for x in (leg["o"], leg["d"])})
    airports = {
        c: {"city": AIRPORTS[c].city, "lat": AIRPORTS[c].latitude, "lon": AIRPORTS[c].longitude,
            "intl": int(AIRPORTS[c].country != "USA"), "region": AIRPORTS[c].region}
        for c in used
    }

    if args.plan_only:
        _emit(args, {"meta": {**meta, "focus_day": focus_day.isoformat(), "first": first.isoformat(),
                              "last": last.isoformat(), "bands": len(schedule.legs)},
                     "airports": airports, "legs": legs})
        return

    if args.year:
        y0, y1 = date(2027, 1, 1), date(2027, 12, 31)
        n, hubs = (y1 - y0).days + 1, ("PIT", "GSO")

        def pairing(leg):  # "BOS-PIT": the airport, then the hub its flights go to and from
            if leg["o"] in hubs and leg["d"] in hubs:
                return "GSO-PIT"
            return f'{leg["d"]}-{leg["o"]}' if leg["o"] in hubs else f'{leg["o"]}-{leg["d"]}'

        key = {leg["id"]: pairing(leg) for leg in legs}
        ser = {}
        for leg in legs:
            ser.setdefault(key[leg["id"]], {"seats": 0, "pax": [0] * n, "rev": [0.0] * n})["seats"] += leg["seats"]
        sim = Simulation(network, meta["seed"], date.fromisoformat(meta["reference_date"]), 1.0)
        for day, _ in sim.run(y0, y1):
            i = (day.day - y0).days
            for booking, di, li in day.coupons:
                direction = booking.directions[di]
                leg_id = direction.path.leg_ids[li]
                cell, party = ser[key[leg_id]], len(booking.passengers)
                cell["pax"][i] += party
                cell["rev"][i] += party * coupon_cents(booking, direction, network.miles(leg_id)) / 100
        _emit(args, {"meta": {**meta, "scale": 1.0, "first": y0.isoformat(), "last": y1.isoformat()},
                     "airports": airports,
                     "series": [{"k": k, "seats": v["seats"], "pax": v["pax"], "rev": [round(x) for x in v["rev"]]}
                                for k, v in sorted(ser.items())]})
        return

    if args.gantt:
        _gantt(args.gantt, Simulation, coupon_cents, network, legs, airports, meta, first, last)
        return

    if args.loads:
        sim = Simulation(network, meta["seed"], date.fromisoformat(meta["reference_date"]), 1.0)
        n_days = (last - first).days + 1
        cells = {leg["id"]: {"pax": [0] * n_days, "flow": [0] * n_days, "rev": [0.0] * n_days} for leg in legs}
        for day, _ in sim.run(first, last):
            i = (day.day - first).days
            for booking, di, li in day.coupons:
                direction = booking.directions[di]
                leg_id = direction.path.leg_ids[li]
                cell, party = cells[leg_id], len(booking.passengers)
                cell["pax"][i] += party
                if not direction.path.nonstop:
                    cell["flow"][i] += party
                cell["rev"][i] += party * coupon_cents(booking, direction, network.miles(leg_id)) / 100
        _emit(args, {"meta": {**meta, "scale": 1.0, "first": first.isoformat(), "last": last.isoformat()},
                     "airports": airports,
                     "flights": [{**{k: leg[k] for k in ("id", "fn", "o", "d", "dep", "arr", "seats", "ac")},
                                  "pax": cells[leg["id"]]["pax"], "flow": cells[leg["id"]]["flow"],
                                  "rev": [round(v) for v in cells[leg["id"]]["rev"]]} for leg in legs]})
        return

    if args.journeys:
        sim = Simulation(network, meta["seed"], date.fromisoformat(meta["reference_date"]), 1.0)
        flows: dict[tuple[str, str, str], list[float]] = {}
        for day, _ in sim.run(first, last):
            for booking, di, li in day.coupons:
                if li:  # count each direction of travel once, on its first leg
                    continue
                direction = booking.directions[di]
                path = direction.path
                via = "" if path.nonstop else network.legs[path.leg_ids[0]].destination
                cell = flows.setdefault((path.origin, path.destination, via), [0, 0.0])
                cell[0] += len(booking.passengers)
                cell[1] += 0.0 if booking.award else direction.fare * len(booking.passengers)
        _emit(args, {"meta": {**meta, "scale": 1.0, "first": first.isoformat(), "last": last.isoformat()},
                     "airports": airports,
                     "journeys": [[o, d, via, n, round(rev)] for (o, d, via), (n, rev) in sorted(flows.items())]})
        return

    # --- 2 & 3. reality: simulate the month, keep the coupons on the focus legs
    focus_ids = {}
    for o, dst in FOCUS_LEGS:
        cands = [d for d in dated if (d.leg.origin, d.leg.destination) == (o, dst)]
        focus_ids[min(cands, key=lambda d: d.departure_utc).leg_id] = f"{o}-{dst}"
    sim = Simulation(network, meta["seed"], date.fromisoformat(meta["reference_date"]), 1.0)
    flights: dict[str, list] = {k: [] for k in focus_ids.values()}
    curves: dict[str, dict[str, list]] = {k: {} for k in focus_ids.values()}
    totals = {"coupons": 0, "bookings": 0, "days": 0}
    for day, started in sim.run(first, last):
        totals["days"] += 1
        totals["bookings"] += len(started)
        totals["coupons"] += sum(len(b.passengers) for b, _, _ in day.coupons)
        for booking, di, li in day.coupons:
            direction = booking.directions[di]
            leg_id = direction.path.leg_ids[li]
            if leg_id not in focus_ids:
                continue
            dep = network.legs[leg_id].departure_time
            dep_at = day.day.toordinal() + int(dep[:2]) / 24
            lead = dep_at - (booking.booked_at.toordinal() + booking.booked_at.hour / 24)
            # Base fare before the advance-purchase ladder: simulate.py Simulation._fare.
            base = (70.0 + 55.0 * math.sqrt(direction.path.miles / 100.0)) * (
                1.0 if direction.path.nonstop else 1.08)
            leg_rev = coupon_cents(booking, direction, network.miles(leg_id)) / 100
            for pi, _ in enumerate(booking.passengers):
                name = focus_ids[leg_id]
                curves[name].setdefault(day.day.isoformat(), []).append(round(lead, 1))
                if day.day != focus_day:
                    continue
                flights[name].append({
                    "o": direction.path.origin, "d": direction.path.destination,
                    "lead": round(lead, 2), "fare": direction.fare, "leg_rev": leg_rev,
                    "mult": round(direction.fare / base, 3),
                    "biz": int(booking.business), "award": int(booking.award),
                    "party": len(booking.passengers), "cls": direction.booking_class,
                    "noshow": int((pi, di, li) in booking.no_shows), "b": booking.sequence,
                })
    payload = {
        "meta": {**meta, "scale": 1.0, "focus_day": focus_day.isoformat(),
                 "first": first.isoformat(), "last": last.isoformat(), "bands": len(schedule.legs),
                 "dated_flights": len(schedule.legs) and sum(
                     1 for leg in schedule.legs
                     for i in range((last - first).days + 1) if leg.operates_on(first + timedelta(days=i))),
                 **totals},
        "airports": airports, "legs": legs,
        "focus": {name: {"leg": next(l for l in legs if l["id"] == lid), "pax": flights[name],
                         "curves": {k: sorted(v, reverse=True) for k, v in curves[name].items()}}
                  for lid, name in focus_ids.items()},
    }
    _emit(args, payload)


def _gantt(out, Simulation, coupon_cents, network, legs, airports, meta, first, last) -> None:
    """One simulation run, recording what the warehouse tables do not keep: refused requests.

    Simulation._take is repeated here unchanged except for the two marked lines, so the random
    draws, and therefore every passenger, stay identical to a plain run. If simulate.py changes,
    re-copy it; the loads this writes must match `--loads` exactly.
    """
    n_days = (last - first).days + 1

    class Recording(Simulation):
        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            self.refused: dict[tuple[int, date], int] = {}
            self.lost: dict[date, int] = {}

        def _take(self, ps, day, party, business):
            available = [p for p in ps if all(self.network.operates(n, day) for n in p.leg_ids)]
            if not available:
                return None
            weights = [(1.0 if p.nonstop else 0.45) * (1.5 if business else 1.0) for p in available]
            order = []
            while available:
                choice = self.rng.choices(range(len(available)), weights)[0]
                order.append(available.pop(choice))
                weights.pop(choice)
            for path in order:
                if all(self._seats(n, day) >= party for n in path.leg_ids):
                    for n in path.leg_ids:
                        self._seats_left[(n, day)] -= party
                    return path
                for n in path.leg_ids:  # added: which flight on this path was short of seats
                    if self._seats(n, day) < party:
                        self.refused[(n, day)] = self.refused.get((n, day), 0) + party
            self.lost[day] = self.lost.get(day, 0) + party  # added: no path had room
            return None

    sim = Recording(network, meta["seed"], date.fromisoformat(meta["reference_date"]), 1.0)
    cells = {leg["id"]: {"pax": [0] * n_days, "flow": [0] * n_days, "rev": [0.0] * n_days} for leg in legs}
    pairs: dict[tuple[int, int], list[int]] = {}
    for day, _ in sim.run(first, last):
        i = (day.day - first).days
        for booking, di, li in day.coupons:
            direction = booking.directions[di]
            ids = direction.path.leg_ids
            cell, party = cells[ids[li]], len(booking.passengers)
            cell["pax"][i] += party
            cell["rev"][i] += party * coupon_cents(booking, direction, network.miles(ids[li])) / 100
            if len(ids) == 2:
                cell["flow"][i] += party
                if li == 0:
                    pairs.setdefault((ids[0], ids[1]), [0] * n_days)[i] += party
    def refused(leg_id):
        return [sim.refused.get((leg_id, first + timedelta(days=i)), 0) for i in range(n_days)]

    keep = ("id", "fn", "o", "d", "dep", "arr", "seats", "ac", "rot")
    dump = lambda v: json.dumps(v, separators=(",", ":"))  # noqa: E731
    with io.StringIO() as f:
        f.write('{"meta":' + dump({**meta, "scale": 1.0, "first": first.isoformat(), "last": last.isoformat()}))
        f.write(',\n"lost":' + dump([sim.lost.get(first + timedelta(days=i), 0) for i in range(n_days)]))
        f.write(',\n"airports":' + dump(airports))
        f.write(',\n"legs":[\n' + ",\n".join(
            dump({**{k: leg[k] for k in keep}, "pax": cells[leg["id"]]["pax"], "flow": cells[leg["id"]]["flow"],
                  "rev": [round(v) for v in cells[leg["id"]]["rev"]], "ref": refused(leg["id"])})
            for leg in legs))
        f.write('\n],\n"pairs":[\n' + ",\n".join(dump([a, b, v]) for (a, b), v in sorted(pairs.items())))
        f.write("\n]}\n")
        text = f.getvalue()
    # Inline, not a file beside the page: the published page could not fetch a sibling data file.
    page = Path(out)
    html = page.read_text()
    start, end = '<script id="data" type="application/json">', "</script>"
    a = html.index(start) + len(start)
    page.write_text(html[:a] + text + html[html.index(end, a):])


def _emit(args: argparse.Namespace, payload: dict) -> None:
    text = json.dumps(payload, separators=(",", ":"))
    if args.inject:
        page = Path(args.inject)
        html = page.read_text()
        start, end = '<script id="data" type="application/json">', "</script>"
        a = html.index(start) + len(start)
        page.write_text(html[:a] + text + html[html.index(end, a):])
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
