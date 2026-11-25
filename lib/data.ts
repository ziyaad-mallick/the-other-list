import peopleJson from "../data/people.json";
import companiesJson from "../data/companies.json";
import metaJson from "../data/meta.json";
import contextJson from "../data/context.json";

export type Src = { label: string; url: string; as_of?: string | null; page?: number | string; quote?: string };
export type Num = { value: number; src: Src } | null;
export type Person = (typeof peopleJson)[number];
export type Company = {
  key: string; name: string; ticker: string; cofounders: string[]; financial_holding: boolean; notes: string[];
  market_cap_usd: { value: number; src: Src }; institutional_pct: Num; sp500_weight_pct: Num;
  fiscal_year_end: string; reporting_currency: string;
  revenue_usd: Num; operating_income_usd: Num; d_and_a_usd: Num; cash_taxes_paid_usd: Num; rd_usd: Num;
  jobs: { value: number; src: Src; basis: string; more_than: boolean };
  median_pay_usd: Num; payroll_usd: { value: number; src: Src; method: string } | null;
  ebitda_usd: Num; gdp_contribution_usd: { value: number; method: string } | null;
};

export const people = peopleJson as Person[];
export const companies = companiesJson as unknown as Record<string, Company>;
export const meta = metaJson;
export const context = contextJson;

export const ROLE: Record<string, string> = {
  founder: "Founder", cofounder: "Co-founder", acquirer: "Built by acquisition", heir: "Heir", hired: "Hired CEO",
};

export const money = (v: number | null | undefined, digits = 1) => {
  if (v == null) return "n/a";
  const a = Math.abs(v);
  if (a >= 1e12) return `$${(v / 1e12).toFixed(2)}T`;
  if (a >= 1e9) return `$${(v / 1e9).toFixed(a >= 1e11 ? 0 : digits)}B`;
  if (a >= 1e6) return `$${(v / 1e6).toFixed(0)}M`;
  return `$${Math.round(v).toLocaleString("en-US")}`;
};

export const sharedName: Record<string, string> = { GOOGL: "Alphabet", MSFT: "Microsoft", WMT: "Walmart" };

const WALTON =
  "The Walton family's holding is pooled in the proxy: 44.3% of Walmart, worth $463.7B at the snapshot. That is more than any one Walton's net worth, so the table shows the percentage only. The same pooled figure sits on all three Walton rows.";

/** Hand-written notes for the detail panel. */
export const drawerNotes: Record<string, string> = {
  "bill-gates":
    "After decades of selling and giving shares away, Forbes puts his stake at under 1% (see source), so his slice is small and the remainder is large. Microsoft's value today also reflects the Ballmer and Nadella eras. The formula is not bent for him: this row is Microsoft's value held by others, not a claim that Gates made all of it.",
  "rob-walton": WALTON,
  "jim-walton": WALTON,
  "alice-walton": WALTON,
  "jensen-huang":
    "Stake from his Form 4 of 16 Sep 2026, valued at the 24 Nov close. Forbes prices its net worth on its own date and counts other assets, so the two can differ by a few percent.",
  "jeff-bezos": "Stake from his Form 4 of 12 Nov 2026, valued at the 24 Nov close.",
  "tobi-lutke":
    "Shopify discloses neither total payroll nor median pay, so GDP contribution is n/a. Its operating profit, cash taxes and research spend are below.",
  "warren-buffett":
    "Berkshire's reported income mixes insurance underwriting and investment gains with its operating businesses, so EBITDA and GDP contribution are left blank rather than estimated.",
};

export const isWalton = (id: string) => id.endsWith("-walton");
