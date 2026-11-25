"""Print the spot-check table (markdown) from data/people.json + data/companies.json."""
import json

from common import DATA

P = json.loads((DATA / "people.json").read_text(encoding="utf-8"))
C = json.loads((DATA / "companies.json").read_text(encoding="utf-8"))
ROLE = {"founder": "Founder", "cofounder": "Co-founder", "acquirer": "Acquirer", "heir": "Heir", "hired": "Hired CEO"}


def b(v):
    return f"${v / 1e9:,.1f}B" if v is not None else "—"


def t(v):
    return f"${v / 1e12:,.2f}T" if v >= 1e12 else f"${v / 1e9:,.0f}B"


print("| Forbes # | Value # | Person | Co. | Role | Net worth | Stake (share kept) | Held by others | Jobs | Median pay | GDP contrib. | Cash taxes | S&P wt |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for p in sorted(P, key=lambda p: p["forbes"]["rank"]):
    c, s = C[p["company"]], p["stake_usd"]
    flag = ("≤" if s["upper_bound"] else "~" if s["estimate"] else "") + ("family " if s["family"] else "")
    g = c["gdp_contribution_usd"]
    gt = f"{b(g['value'])} {'floor' if g['method'] == 'floor' else 'reported'}" if g else "n/a"
    j = c["jobs"]
    jt = (">" if j["more_than"] else "") + f"{j['value']:,}" + (" (avg)" if "average" in j["basis"] else "")
    m, w = c["median_pay_usd"], c["sp500_weight_pct"]
    print(f"| {p['forbes']['rank']} | {p.get('value_rank', '—')} | {p['name']} | {c['ticker']} | {ROLE[p['role']]} | "
          f"{b(p['forbes']['net_worth_usd'])} | {flag}{b(s['value'])} ({p['share_kept_pct']:.1f}%) | {t(p['value_held_by_others_usd'])} | "
          f"{jt} | {'$' + format(m['value'], ',') if m else 'n/d'} | {gt} | {b(c['cash_taxes_paid_usd']['value'])} | "
          f"{format(w['value'], '.2f') + '%' if w else '—'} |")
