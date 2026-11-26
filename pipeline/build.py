"""Merge raw pulls + curated values into the two files the site reads: data/companies.json and data/people.json.

Every number is stored as {"value": ..., "src": {"label", "url", "as_of", "page"?, "quote"?}} so the page can link it.
"""
import json

from common import DATA, write_json
from curated import COMPANY, STAKES
from universe import COMPANIES, PEOPLE

RANKED_ROLES = {"founder", "cofounder", "acquirer"}
CASH_FLOW = ("stock_based_comp", "capex", "dividends_paid")  # stored as positive magnitudes
FILER_LABEL = {"10-K": "annual report (10-K)", "20-F": "annual report (20-F)", "DEF 14A": "proxy statement (DEF 14A)"}


def load(path):
    return json.loads((DATA / "raw" / path).read_text(encoding="utf-8"))


def sec_src(key, which, sec):
    f = sec[key][which]
    return {"label": f"{COMPANIES[key]['name']} {FILER_LABEL[f['form']]}, filed {f['filed']}", "url": f["url"], "as_of": f["filed"]}


def resolve(src, key, sec, as_of=None, page=None, quote=None, label=None):
    if src.startswith("sec:"):
        s = sec_src(key, src[4:], sec)
    else:
        s = {"label": label or src, "url": src, "as_of": as_of}
    if as_of:
        s["as_of"] = as_of
    if page:
        s["page"] = page
    if quote:
        s["quote"] = quote
    return s


def num(value, src):
    return {"value": value, "src": src}


def build_companies(sec, market):
    fx = market["fx_to_usd"]
    out = {}
    for key, c in COMPANIES.items():
        m = market["companies"][key]
        cur = COMPANY.get(key, {})
        rec = {"key": key, "name": c["name"], "ticker": c["yahoo"], "cofounders": c["cofounders"],
               "financial_holding": c.get("financial_holding", False), "notes": []}
        mkt_src = {"label": f"Yahoo Finance quote, {c['yahoo']}", "url": m["quote_url"], "as_of": market["fetched_at"][:10]}
        rec["market_cap_usd"] = num(m["market_cap_usd"], mkt_src)
        if cur.get("unvested_award_shares"):
            # Yahoo's share count includes unvested, performance-contingent award shares that the proxy's
            # ownership percentages leave out; count them on neither side so share-kept matches the filing.
            rec["market_cap_usd"]["value"] -= cur["unvested_award_shares"] * m["price"]
            rec["notes"].append(f"Market cap excludes {cur['unvested_award_shares']:,} unvested 2025 performance-award shares, matching the proxy's ownership basis.")
        rec["price"] = {"value": m["price"], "currency": m["currency"], "src": mkt_src}
        rec["institutional_pct"] = num(m["institutional_pct"], {"label": f"Yahoo Finance holders, {c['yahoo']}", "url": m["holders_url"],
                                                                "as_of": market["fetched_at"][:10]}) if m["institutional_pct"] is not None else None
        rec["sp500_weight_pct"] = num(m["sp500_weight_pct"], {
            "label": "SPDR S&P 500 ETF (SPY) daily holdings", "as_of": market["spy_holdings_as_of"],
            "url": "https://www.ssga.com/us/en/intermediary/etfs/spdr-sp-500-etf-trust-spy"}) if m["sp500_weight_pct"] else None

        if c["filer"] in ("sec10k", "sec20f") and key in sec and key != "AMX":
            v = sec[key]["values"]
            fin_src = sec_src(key, "annual", sec)
            rate = fx[v["revenue"]["unit"]] if v["revenue"] else 1.0
            rec["fiscal_year_end"] = sec[key]["annual"]["period"]
            rec["reporting_currency"] = v["revenue"]["unit"]

            def x(field):
                d = v.get(field)
                return num(d["value"] * rate, {**fin_src, "concept": d["concept"]}) if d else None

            rec["revenue_usd"], rec["operating_income_usd"] = x("revenue"), x("operating_income")
            rec["d_and_a_usd"], rec["cash_taxes_paid_usd"], rec["rd_usd"] = x("d_and_a"), x("cash_taxes_paid"), x("rd")
            for f in CASH_FLOW:
                d = x(f)
                rec[f"{f}_usd"] = {**d, "value": abs(d["value"])} if d else None
            if cur.get("payroll_from_xbrl"):
                p = x(cur["payroll_from_xbrl"])
                rec["payroll_usd"] = {**p, "method": "reported", "src": {**p["src"], "quote": cur["payroll_quote"]}}
        else:
            src_url = cur["src"]
            rate = fx[cur["currency"]]
            rec["fiscal_year_end"] = cur["fy_end"]
            rec["reporting_currency"] = cur["currency"]

            def h(field, quote_key=None):
                if field not in cur:
                    return None
                qk = quote_key or f"{field}_quote"
                s = resolve(cur.get(f"{field}_src", src_url), key, sec, as_of=cur.get("doc_date"), page=cur.get(f"{field}_page") or cur.get(f"{field.split('_')[0]}_page"), quote=cur.get(qk),
                            label=f"{c['name']} FY{cur['fy_end'][:4]} report")
                return num(cur[field] * rate, s)

            rec["revenue_usd"], rec["operating_income_usd"], rec["d_and_a_usd"] = h("revenue"), h("operating_income"), h("d_and_a")
            rec["cash_taxes_paid_usd"] = h("cash_taxes_paid", "cash_taxes_quote")
            if rec["cash_taxes_paid_usd"] and cur.get("cash_taxes_page"):
                rec["cash_taxes_paid_usd"]["src"]["page"] = cur["cash_taxes_page"]
            rec["rd_usd"] = h("rd")
            for f in CASH_FLOW:
                rec[f"{f}_usd"] = h(f)
            if "payroll" in cur:
                pdate = cur.get("urd_date") if cur.get("payroll_src", src_url) != src_url and cur.get("urd_date") else cur.get("doc_date")
                ps = resolve(cur.get("payroll_src", src_url), key, sec, as_of=pdate, page=cur.get("payroll_page"), quote=cur.get("payroll_quote"),
                             label=f"{c['name']} FY{cur['fy_end'][:4]} report")
                rec["payroll_usd"] = {**num(cur["payroll"] * rate, ps), "method": "reported"}
            if cur.get("fx_note"):
                rec["notes"].append(cur["fx_note"])
        if rec["reporting_currency"] != "USD" and key != "AMX":
            rec["notes"].append(f"Converted from {rec['reporting_currency']} at the snapshot rate ({fx[rec['reporting_currency']]:.4f} USD).")

        if cur.get("no_dividends"):
            assert not rec.get("dividends_paid_usd"), key
            rec["dividends_paid_usd"] = num(0, {**sec_src(key, "annual", sec), "quote": "No dividend payments in the cash-flow statement"})

        # jobs and median pay
        jdate = cur.get("urd_date") or cur.get("doc_date")
        jsrc = resolve(cur.get("jobs_src", "sec:annual" if c["filer"] != "report" else cur["src"]), key, sec, as_of=jdate,
                       page=cur.get("jobs_page"), quote=cur.get("jobs_quote"), label=f"{c['name']} annual report")
        rec["jobs"] = {**num(cur["jobs"], jsrc), "basis": cur.get("jobs_basis", "employees at fiscal year-end"),
                       "more_than": cur.get("jobs_more_than", False)}
        if "median_pay" in cur:
            rec["median_pay_usd"] = num(cur["median_pay"], resolve("sec:proxy", key, sec, quote=cur["median_quote"]))
        else:
            rec["median_pay_usd"] = None
        if "average_pay_eur" in cur:
            rec["average_pay_usd"] = num(cur["average_pay_eur"] * fx["EUR"], resolve(ITX_PEOPLE_URL(), key, sec, as_of=cur.get("doc_date"), quote=cur["average_pay_quote"],
                                                                               label="Inditex Annual Report 2025, Our drivers"))
        if "rd_note" in cur:
            rec["notes"].append(cur["rd_note"])

        # payroll floor, EBITDA, GDP contribution (value added = EBITDA + payroll)
        if "payroll_usd" not in rec:
            if rec["median_pay_usd"]:
                rec["payroll_usd"] = {"value": rec["jobs"]["value"] * rec["median_pay_usd"]["value"], "method": "floor",
                                      "src": {"label": "jobs x median pay (both cited above)", "url": rec["median_pay_usd"]["src"]["url"],
                                              "as_of": rec["median_pay_usd"]["src"]["as_of"]}}
            else:
                rec["payroll_usd"] = None
        oi, da = rec.get("operating_income_usd"), rec.get("d_and_a_usd")
        rec["ebitda_usd"] = {"value": oi["value"] + da["value"], "src": {"label": "operating income + depreciation & amortisation",
                                                                         "url": oi["src"]["url"], "as_of": oi["src"]["as_of"]}} if oi and da else None
        if rec["financial_holding"]:
            rec["ebitda_usd"] = None
            rec["notes"].append("Berkshire's reported income mixes insurance and investment gains with operating results, so EBITDA and GDP contribution are not shown.")
        if rec["ebitda_usd"] and rec["payroll_usd"]:
            rec["gdp_contribution_usd"] = {"value": rec["ebitda_usd"]["value"] + rec["payroll_usd"]["value"], "method": rec["payroll_usd"]["method"]}
        else:
            rec["gdp_contribution_usd"] = None
        out[key] = rec
    return out


def ITX_PEOPLE_URL():
    from curated import ITX_PEOPLE
    return ITX_PEOPLE


def build_people(companies, sec, forbes, market):
    prices = {m["yahoo"]: m["price"] for m in market["companies"].values()} | market["prices"]
    people = []
    for p in PEOPLE:
        c = companies[p["company"]]
        st = STAKES[p["id"]]
        st = {**STAKES[st["same_as"]]} if "same_as" in st else st
        mcap = c["market_cap_usd"]["value"]
        if "shares" in st:
            stake = sum(n * prices[sym] for sym, n in st["shares"].items())
        else:
            stake = st["pct"] / 100 * mcap
        src = resolve(st["src"], p["company"], sec, as_of=st["as_of"], page=st.get("page"), quote=st["quote"],
                      label=("Forbes profile" if "forbes.com" in st["src"] else None))
        if st.get("src2"):
            src["also"] = st["src2"]
        kept = min(100.0, max(0.0, stake / mcap * 100))
        people.append({
            "id": p["id"], "name": p["name"], "company": p["company"], "role": p["role"], "ranked": p["role"] in RANKED_ROLES,
            "featured": p.get("featured", False), "badge": p.get("badge"), "note": p.get("note"),
            "forbes": forbes[p["id"]],
            "stake_usd": {"value": stake, "src": src, "shares": st.get("shares"), "pct_basis": st.get("pct"),
                          "estimate": st.get("estimate", False), "upper_bound": st.get("upper_bound", False),
                          "family": st.get("family", False), "note": st.get("note")},
            "share_kept_pct": kept,
            "value_held_by_others_usd": max(0.0, mcap - stake),
        })
    # rows that share a company figure, and the value-view rank (ranked people only; ties break on Forbes rank)
    for p in people:
        p["shares_company_with"] = [q["id"] for q in people if q["company"] == p["company"] and q["id"] != p["id"]]
    ranked = sorted((p for p in people if p["ranked"]), key=lambda p: (-p["value_held_by_others_usd"], p["forbes"]["rank"]))
    for i, p in enumerate(ranked, 1):
        p["value_rank"] = i
    by_forbes = sorted(people, key=lambda p: p["forbes"]["rank"])
    for i, p in enumerate(by_forbes, 1):
        p["forbes_order"] = i
    return people


def run():
    sec = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in (DATA / "raw" / "sec").glob("*.json")}
    market, forbes = load("market.json"), load("forbes.json")
    companies = build_companies(sec, market)
    people = build_people(companies, sec, forbes, market)
    write_json(DATA / "companies.json", companies)
    write_json(DATA / "people.json", people)
    write_json(DATA / "meta.json", {"snapshot_date": market["fetched_at"][:10], "market_fetched_at": market["fetched_at"],
                                    "forbes_as_of": next(iter(forbes.values()))["as_of"], "fx_to_usd": market["fx_to_usd"],
                                    "spy_holdings_as_of": market["spy_holdings_as_of"]})
    print(f"wrote {len(companies)} companies, {len(people)} people")


if __name__ == "__main__":
    run()
