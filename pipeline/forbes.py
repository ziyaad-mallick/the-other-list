"""Snapshot Forbes real-time ranks and net worth for the people in universe.py -> data/raw/forbes.json."""
from datetime import datetime, timezone

from common import DATA, fetch_json, write_json
from universe import PEOPLE

URL = "https://www.forbes.com/forbesapi/person/rtb/0/position/true.json?fields=rank,uri,personName,finalWorth,source,timestamp&limit=3200"


def run():
    rows = fetch_json(URL)["personList"]["personsLists"]
    by_uri = {r["uri"]: r for r in rows}
    out = {}
    for p in PEOPLE:
        r = by_uri[p["forbes_uri"]]  # KeyError here means Forbes changed a profile slug: fix universe.py
        ts = datetime.fromtimestamp(r["timestamp"] / 1000, tz=timezone.utc)
        out[p["id"]] = {"rank": r["rank"], "net_worth_usd": round(r["finalWorth"] * 1e6), "forbes_source": r["source"],
                        "as_of": ts.date().isoformat(), "url": f"https://www.forbes.com/profile/{p['forbes_uri']}/"}
        print(f"{r['rank']:5} {p['name']:40} ${r['finalWorth'] / 1000:,.1f}B")
    write_json(DATA / "raw" / "forbes.json", out)


if __name__ == "__main__":
    run()
