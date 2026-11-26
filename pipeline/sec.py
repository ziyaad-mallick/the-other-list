"""Pull annual figures from SEC XBRL (companyfacts) for every SEC filer, tied to the latest annual filing.

Writes data/raw/sec/<KEY>.json. Each value carries the concept it came from, the period and the filing URL.
Also caches the annual report and proxy text so `explore.py` can show the headcount / median-pay / ownership passages.
"""
from datetime import date

from common import CACHE, DATA, fetch, html_to_text, sec_json, write_json
from universe import COMPANIES

# First concept found wins. Flows are taken for the fiscal year of the latest annual filing.
CONCEPTS = {
    "revenue": ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet", "Revenue"],
    "operating_income": ["OperatingIncomeLoss", "ProfitLossFromOperatingActivities"],
    "d_and_a": ["DepreciationDepletionAndAmortization", "DepreciationAmortizationAndAccretionNet", "DepreciationAndAmortization",
                "DepreciationAndAmortisationExpense", "AdjustmentsForDepreciationAndAmortisationExpense",
                "DepreciationAmortisationAndImpairmentLossReversalOfImpairmentLossRecognisedInProfitOrLoss"],
    "cash_taxes_paid": ["IncomeTaxesPaidNet", "IncomeTaxesPaid", "IncomeTaxesPaidRefundClassifiedAsOperatingActivities"],
    "rd": ["ResearchAndDevelopmentExpense", "ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost", "ResearchAndDevelopmentExpenseSoftwareExcludingAcquiredInProcessCost"],
    "personnel_cost": ["EmployeeBenefitsExpense", "LaborAndRelatedExpense"],
    "pretax_income": ["IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
                      "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments",
                      "ProfitLossBeforeTax"],
    # cash-flow statement; stored as positive magnitudes in build.py
    "stock_based_comp": ["ShareBasedCompensation", "AllocatedShareBasedCompensationExpense", "AdjustmentsForSharebasedPayments"],
    "capex": ["PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets",
              "PurchaseOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities"],
    "dividends_paid": ["PaymentsOfDividendsCommonStock", "PaymentsOfDividends", "DividendsPaidClassifiedAsFinancingActivities",
                       "DividendsPaidToEquityHoldersOfParentClassifiedAsFinancingActivities"],
}


def tickers():
    rows = sec_json("https://www.sec.gov/files/company_tickers.json").values()
    return {r["ticker"]: r["cik_str"] for r in rows}


def latest(subs, forms):
    r = subs["filings"]["recent"]
    for i, f in enumerate(r["form"]):
        if f in forms:
            return {"form": f, "accn": r["accessionNumber"][i], "filed": r["filingDate"][i],
                    "period": r["reportDate"][i], "doc": r["primaryDocument"][i]}
    return None


def doc_url(cik, f):
    return f"https://www.sec.gov/Archives/edgar/data/{cik}/{f['accn'].replace('-', '')}/{f['doc']}"


def pick(facts, names, accn, period):
    """The one-year value for the fiscal year ending `period`, as reported in filing `accn`."""
    for taxonomy in ("us-gaap", "ifrs-full"):
        for name in names:
            concept = facts.get("facts", {}).get(taxonomy, {}).get(name)
            if not concept:
                continue
            for unit, vals in concept["units"].items():
                hits = []
                for v in vals:
                    if v.get("accn") != accn or v.get("end") != period or "start" not in v:
                        continue
                    days = (date.fromisoformat(v["end"]) - date.fromisoformat(v["start"])).days
                    if 350 <= days <= 380:
                        hits.append(v)
                if hits:
                    v = hits[0]
                    return {"value": v["val"], "unit": unit, "concept": f"{taxonomy}:{name}", "start": v["start"], "end": v["end"]}
    return None


def run():
    cik_of = tickers()
    for key, c in COMPANIES.items():
        if c["filer"] not in ("sec10k", "sec20f"):
            continue
        cik = cik_of[c["sec"]]
        subs = sec_json(f"https://data.sec.gov/submissions/CIK{cik:010d}.json")
        annual = latest(subs, ("10-K", "20-F"))
        proxy = latest(subs, ("DEF 14A",))
        facts = sec_json(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json")
        out = {"key": key, "cik": cik, "entity": facts.get("entityName"),
               "annual": {**annual, "url": doc_url(cik, annual)},
               "proxy": {**proxy, "url": doc_url(cik, proxy)} if proxy else None,
               "values": {}}
        for field, names in CONCEPTS.items():
            out["values"][field] = pick(facts, names, annual["accn"], annual["period"])
        if out["values"]["d_and_a"] is None:
            # No combined D&A tag: depreciation + amortisation of intangibles, both from the same filing.
            dep = pick(facts, ["Depreciation", "AdjustmentsForDepreciationExpense"], annual["accn"], annual["period"])
            amo = pick(facts, ["AmortizationOfIntangibleAssets", "AdjustmentsForAmortisationExpense"], annual["accn"], annual["period"])
            if dep:
                out["values"]["d_and_a"] = {**dep, "value": dep["value"] + (amo["value"] if amo else 0),
                                            "concept": dep["concept"] + (" + " + amo["concept"] if amo else "")}
        # cache the documents' text for explore.py
        for f in (annual, proxy):
            if f:
                (CACHE / "text").mkdir(parents=True, exist_ok=True)
                (CACHE / "text" / f"{key}-{f['form'].replace(' ', '')}.txt").write_text(
                    html_to_text(fetch(doc_url(cik, f), ua="pie-index research bot admin@pie-index.invalid")), encoding="utf-8")
        write_json(DATA / "raw" / "sec" / f"{key}.json", out)
        v = out["values"]
        show = {k: (round(x["value"] / 1e9, 2), x["unit"]) if x else None for k, x in v.items()}
        print(key, annual["form"], annual["period"], "proxy:", proxy["filed"] if proxy else None, show)


if __name__ == "__main__":
    run()
