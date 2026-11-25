import { describe, expect, it } from "vitest";
import people from "../data/people.json";
import companies from "../data/companies.json";
import * as m from "./metrics";

type C = (typeof companies)[keyof typeof companies];
const co = (k: string) => (companies as Record<string, C>)[k];
const rows = people.map((p) => ({ id: p.id, ranked: p.ranked, forbesRank: p.forbes.rank, heldByOthers: p.value_held_by_others_usd }));

describe("parity with the Python pipeline", () => {
  it.each(people.map((p) => [p.id, p] as const))("%s share kept and held by others", (_, p) => {
    const cap = co(p.company).market_cap_usd.value;
    expect(m.shareKeptPct(p.stake_usd.value, cap)).toBeCloseTo(p.share_kept_pct, 6);
    expect(m.heldByOthers(p.stake_usd.value, cap)).toBeCloseTo(p.value_held_by_others_usd, -3);
  });
  it.each(Object.keys(companies))("%s GDP contribution", (k) => {
    const c = co(k);
    const e = c.ebitda_usd ? c.ebitda_usd.value : null;
    const g = m.gdpContribution(e, c.payroll_usd ? c.payroll_usd.value : null);
    expect(g == null ? null : Math.round(g)).toBe(c.gdp_contribution_usd ? Math.round(c.gdp_contribution_usd.value) : null);
  });
  it("value rank matches the pipeline", () => {
    m.valueOrder(rows).filter((r) => r.ranked).forEach((r, i) => {
      expect(people.find((p) => p.id === r.id)!.value_rank).toBe(i + 1);
    });
  });
});

describe("rank deltas", () => {
  const d = m.rankDeltas(rows);
  it("are bounded by the list size, never global Forbes rank", () => {
    for (const v of d.values()) if (v != null) expect(Math.abs(v)).toBeLessThan(people.length);
  });
  it("are null for the 5 unranked rows", () => {
    expect([...d.values()].filter((v) => v == null)).toHaveLength(5);
  });
  it("Hastings: 24th in Forbes order, 9th in value order", () => {
    expect(d.get("reed-hastings")).toBe(24 - 9);
  });
});

describe("edge cases", () => {
  it("bounds share kept", () => {
    expect(m.shareKeptPct(2, 1)).toBe(100);
    expect(m.shareKeptPct(-1, 1)).toBe(0);
  });
  it("401(k) exposure is null outside the S&P 500", () => {
    expect(m.indexExposure(50000, null)).toBeNull();
    expect(m.indexExposure(50000, 4)).toBe(2000);
  });
});
