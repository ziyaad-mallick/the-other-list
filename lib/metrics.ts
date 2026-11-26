// The whole method (SPEC §5) as pure functions. The Python pipeline computes the same numbers;
// lib/metrics.test.ts checks the two agree on every row.

export type Ranked = { id: string; ranked: boolean; forbesRank: number; heldByOthers: number };

export const shareKeptPct = (stake: number, marketCap: number) =>
  Math.min(100, Math.max(0, (stake / marketCap) * 100));

export const heldByOthers = (stake: number, marketCap: number) => Math.max(0, marketCap - stake);

export const ebitda = (operatingIncome: number, dAndA: number) => operatingIncome + dAndA;

export const gdpContribution = (ebitdaUsd: number | null, payrollUsd: number | null) =>
  ebitdaUsd == null || payrollUsd == null ? null : ebitdaUsd + payrollUsd;

export const payrollFloor = (jobs: number, medianPay: number) => jobs * medianPay;

/** Median pay as a multiple of the US all-workers median (BLS OEWS). */
export const vsUsMedian = (medianPay: number | null, usMedian: number) =>
  medianPay == null || usMedian <= 0 ? null : medianPay / usMedian;

/** A company-wide total spread over headcount, e.g. stock-based comp per employee. */
export const perEmployee = (total: number | null, jobs: number) =>
  total == null || jobs <= 0 ? null : total / jobs;

export const indexExposure = (balance: number, weightPct: number | null) =>
  weightPct == null ? null : (balance * weightPct) / 100;

/** Forbes order: positions 1..n within this list (not the global Forbes rank). */
export const forbesOrder = <T extends Ranked>(people: T[]) =>
  [...people].sort((a, b) => a.forbesRank - b.forbesRank);

/** Value order: ranked people by value held by others (ties on Forbes rank), then the unranked group in Forbes order. */
export const valueOrder = <T extends Ranked>(people: T[]) => {
  const ranked = people.filter((p) => p.ranked).sort((a, b) => b.heldByOthers - a.heldByOthers || a.forbesRank - b.forbesRank);
  const rest = forbesOrder(people.filter((p) => !p.ranked));
  return [...ranked, ...rest];
};

/** Places moved between the two views, both counted within this list. Positive = moves up. Null for unranked rows. */
export const rankDeltas = <T extends Ranked>(people: T[]) => {
  const f = new Map(forbesOrder(people).map((p, i) => [p.id, i + 1]));
  const v = new Map(valueOrder(people).map((p, i) => [p.id, i + 1]));
  return new Map(people.map((p) => [p.id, p.ranked ? f.get(p.id)! - v.get(p.id)! : null]));
};

/** The listed stake is under half the person's net worth: share kept describes only the listed company. */
export const minorityOfNetWorth = (stake: number, netWorth: number) => stake < netWorth / 2;

/** Headline totals over the ranked people: each company counted once, stakes summed across its ranked founders. */
export const builtTotals = (
  people: { ranked: boolean; company: string; stake: number }[],
  company: (k: string) => { cap: number; jobs: number },
) => {
  const ranked = people.filter((p) => p.ranked);
  const keys = [...new Set(ranked.map((p) => p.company))];
  const cap = keys.reduce((s, k) => s + company(k).cap, 0);
  const kept = ranked.reduce((s, p) => s + p.stake, 0);
  return { people: ranked.length, companies: keys.length, cap, kept, others: cap - kept, keptPct: (kept / cap) * 100, jobs: keys.reduce((s, k) => s + company(k).jobs, 0) };
};
