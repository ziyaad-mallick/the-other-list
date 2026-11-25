"""Prices, market caps, FX, institutional ownership (Yahoo Finance via yfinance) and S&P 500 weights (SSGA SPY holdings).

Writes data/raw/market.json. Run on the snapshot day; the date is recorded.
"""
import io
from datetime import datetime, timezone

import openpyxl
import yfinance as yf

from common import DATA, fetch, write_json
from universe import COMPANIES

EXTRA_PRICES = ["GOOG", "BRK-A"]  # second share classes priced separately
FX = {"EUR": "EURUSD=X"}
SPY_XLSX = "https://www.ssga.com/us/en/intermediary/library-content/products/fund-data/etfs/us/holdings-daily-us-en-spy.xlsx"


def spy_weights():
    wb = openpyxl.load_workbook(io.BytesIO(fetch(SPY_XLSX, binary=True)), read_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    as_of = next((str(r[1]) for r in rows[:6] if r and r[0] and "Holdings" in str(r[0])), None)
    head = next(i for i, r in enumerate(rows) if r and r[0] == "Name")
    cols = rows[head]
    ti, wi = cols.index("Ticker"), cols.index("Weight")
    w = {r[ti]: float(r[wi]) for r in rows[head + 1:] if r and r[ti] and isinstance(r[wi], (int, float))}
    return as_of, w


def run():
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    fx = {cur: yf.Ticker(sym).fast_info.last_price for cur, sym in FX.items()}
    fx["USD"] = 1.0
    as_of, weights = spy_weights()
    out = {"fetched_at": now, "fx_to_usd": fx, "spy_holdings_as_of": as_of, "companies": {}, "prices": {}}
    for sym in EXTRA_PRICES:
        out["prices"][sym] = yf.Ticker(sym).fast_info.last_price
    for key, c in COMPANIES.items():
        t = yf.Ticker(c["yahoo"])
        fi = t.fast_info
        cur = fi.currency
        try:
            mh = t.major_holders
            inst = float(mh.loc["institutionsPercentHeld", "Value"]) * 100
        except Exception:
            inst = None
        w = sum(weights.get(s, 0.0) for s in c["sp500"]) if c["sp500"] else None
        out["companies"][key] = {
            "yahoo": c["yahoo"], "currency": cur, "price": fi.last_price,
            "market_cap_local": fi.market_cap, "market_cap_usd": fi.market_cap * fx[cur],
            "institutional_pct": inst, "sp500_weight_pct": w,
            "quote_url": f"https://finance.yahoo.com/quote/{c['yahoo']}/",
            "holders_url": f"https://finance.yahoo.com/quote/{c['yahoo']}/holders/",
        }
        print(f"{key:6} {cur} price={fi.last_price:,.2f} mcap_usd={fi.market_cap * fx[cur] / 1e9:,.1f}B inst={inst} sp500={w}")
    write_json(DATA / "raw" / "market.json", out)
    print("SPY as of", as_of, "| EURUSD", fx["EUR"])


if __name__ == "__main__":
    run()
