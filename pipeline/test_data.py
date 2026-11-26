"""Data gates (SPEC.md section 8). Run: .venv/Scripts/python -m pytest pipeline/test_data.py -q"""
import json
import re
from pathlib import Path

import pytest

DATA = Path(__file__).resolve().parent.parent / "data"
PEOPLE = json.loads((DATA / "people.json").read_text(encoding="utf-8"))
COMPANIES = json.loads((DATA / "companies.json").read_text(encoding="utf-8"))
NUMBER_FIELDS = ["market_cap_usd", "revenue_usd", "operating_income_usd", "d_and_a_usd", "cash_taxes_paid_usd", "rd_usd",
                 "payroll_usd", "ebitda_usd", "jobs", "median_pay_usd", "sp500_weight_pct", "institutional_pct", "average_pay_usd"]


def cited(field):
    s = field["src"]
    return s["url"].startswith("https://") and bool(s.get("as_of")) and bool(s.get("label"))


@pytest.mark.parametrize("key", sorted(COMPANIES))
def test_every_company_number_is_cited(key):
    c = COMPANIES[key]
    for f in NUMBER_FIELDS:
        if c.get(f) is not None:
            assert cited(c[f]), f"{key}.{f} lacks url/as_of/label"


@pytest.mark.parametrize("p", PEOPLE, ids=lambda p: p["id"])
def test_every_person_number_is_cited(p):
    assert cited(p["stake_usd"]), p["id"]
    assert p["forbes"]["url"].startswith("https://www.forbes.com/profile/") and p["forbes"]["as_of"]


@pytest.mark.parametrize("p", PEOPLE, ids=lambda p: p["id"])
def test_stake_is_bounded(p):
    mcap = COMPANIES[p["company"]]["market_cap_usd"]["value"]
    assert 0 < p["stake_usd"]["value"] <= mcap
    assert 0 <= p["share_kept_pct"] <= 100
    assert p["value_held_by_others_usd"] == pytest.approx(mcap - p["stake_usd"]["value"])


def test_ranked_set_and_roles():
    ranked = [p for p in PEOPLE if p["ranked"]]
    assert len(PEOPLE) == 24 and len(ranked) == 19
    for p in PEOPLE:
        assert p["role"] in {"founder", "cofounder", "acquirer", "heir", "hired"}
        assert p["ranked"] == (p["role"] not in {"heir", "hired"})
        assert ("value_rank" in p) == p["ranked"]
    assert sorted(p["value_rank"] for p in ranked) == list(range(1, 20))
    assert {p["id"] for p in PEOPLE if not p["ranked"]} == {"steve-ballmer", "rob-walton", "jim-walton", "alice-walton",
                                                           "francoise-bettencourt-meyers"}


def test_shared_company_pills():
    groups = {"GOOGL": 2, "MSFT": 2, "WMT": 3}
    for p in PEOPLE:
        expect = groups.get(p["company"], 1) - 1
        assert len(p["shares_company_with"]) == expect, p["id"]


@pytest.mark.parametrize("key", sorted(COMPANIES))
def test_real_economy_sanity(key):
    c = COMPANIES[key]
    assert c["jobs"]["value"] > 0
    rev = c["revenue_usd"]["value"]
    if c.get("payroll_usd"):
        assert 0 < c["payroll_usd"]["value"] <= rev, "payroll above revenue: unit bug?"
        assert c["payroll_usd"]["method"] in {"reported", "floor"}
    if c.get("median_pay_usd"):
        assert 15_000 < c["median_pay_usd"]["value"] < 1_000_000
    if c.get("rd_usd"):
        assert 0 <= c["rd_usd"]["value"] <= rev
    if c["gdp_contribution_usd"]:
        assert c["operating_income_usd"]["value"] <= 0 or c["gdp_contribution_usd"]["value"] > 0
        assert c["gdp_contribution_usd"]["value"] <= rev
    assert isinstance(c["cash_taxes_paid_usd"]["value"], (int, float))


def test_sp500_weights():
    w = [c["sp500_weight_pct"]["value"] for c in COMPANIES.values() if c["sp500_weight_pct"]]
    assert all(0 < x < 15 for x in w)
    assert sum(w) < 65
    assert {k for k, c in COMPANIES.items() if not c["sp500_weight_pct"]} == {"ITX", "AMX", "MC", "OR", "SPOT", "SHOP"}


def test_forbes_ranks_unique():
    ranks = [p["forbes"]["rank"] for p in PEOPLE]
    assert len(set(ranks)) == len(ranks)


CASH_FLOW = ["stock_based_comp_usd", "capex_usd", "dividends_paid_usd"]


@pytest.mark.parametrize("key", sorted(COMPANIES))
def test_cash_flow_fields(key):
    c = COMPANIES[key]
    for f in CASH_FLOW:
        if c.get(f) is not None:
            assert c[f]["value"] >= 0, f"{key}.{f} stored negative"
            assert cited(c[f]), f"{key}.{f} lacks url/as_of/label"
    assert c["dividends_paid_usd"] is not None, f"{key}: dividends must be a number (0 if none paid)"
    if c.get("capex_usd"):
        assert c["capex_usd"]["value"] <= c["revenue_usd"]["value"] * 2, f"{key}: capex above 2x revenue, unit bug?"


EVERYDAY = json.loads((DATA / "everyday.json").read_text(encoding="utf-8"))
CONTEXT = json.loads((DATA / "context.json").read_text(encoding="utf-8"))


def test_everyday_covers_every_company():
    assert set(EVERYDAY) == set(COMPANIES)


@pytest.mark.parametrize("key", sorted(EVERYDAY))
def test_everyday_impact_is_cited(key):
    e = EVERYDAY[key]
    assert e["text"] and len(e["text"]) < 300
    assert 1 <= len(e["facts"]) <= 4
    for f in e["facts"]:
        assert f["url"].startswith("https://"), key
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", f["as_of"]), key
        assert f["source_type"] in {"Company-reported", "Federal data", "Third-party estimate"}, key
        assert f["quote"] and f["figure"] and f["publisher"], key


def test_us_median_wage():
    w = CONTEXT["us_median_wage"]
    assert w["value"] == round(w["hourly"] * 2080, -1)
    assert w["src"]["url"].startswith("https://www.bls.gov/") and w["src"]["as_of"]
