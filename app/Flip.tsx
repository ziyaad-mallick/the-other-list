"use client";

import { LayoutGroup, motion } from "framer-motion";
import { Fragment, useMemo, useState } from "react";
import { companies, drawerNotes, isWalton, money, people, ROLE, sharedName, type Person, type Src } from "@/lib/data";
import { forbesOrder, indexExposure, minorityOfNetWorth, rankDeltas, valueOrder } from "@/lib/metrics";

type SortKey = "jobs" | "median" | "gdp";
type Mode = { view: "forbes" | "value"; sort?: { key: SortKey; dir: 1 | -1 } };

const rows = people.map((p) => ({ ...p, forbesRank: p.forbes.rank, heldByOthers: p.value_held_by_others_usd }));
type Row = (typeof rows)[number];
const deltas = rankDeltas(rows);
const rankedCount = rows.filter((r) => r.ranked).length;

const sortVal = (r: Row, k: SortKey) => {
  const c = companies[r.company];
  if (k === "jobs") return c.jobs.value;
  if (k === "median") return c.median_pay_usd?.value ?? null;
  return c.gdp_contribution_usd?.value ?? null;
};

const initials = (n: string) => n.replace(/&.*$/, "").split(/\s+/).filter(Boolean).map((w) => w[0]).slice(0, 2).join("");

function SrcLink({ src, children }: { src: Src; children: React.ReactNode }) {
  const t = [src.label, src.as_of && `as of ${src.as_of}`, src.page && `p. ${src.page}`, src.quote && `"${src.quote}"`].filter(Boolean).join(" · ");
  return (
    <a href={src.url} target="_blank" rel="noreferrer" title={t} className="src" onClick={(e) => e.stopPropagation()}>
      {children}
    </a>
  );
}

function Stake({ p }: { p: Person }) {
  const s = p.stake_usd;
  const pct = `${p.share_kept_pct.toFixed(1)}%`;
  if (isWalton(p.id)) return <span>family {pct}</span>;
  const pre = s.upper_bound ? "≤" : s.estimate ? "~" : "";
  return (
    <span>
      {pre}{s.family ? "family " : ""}{pct}
    </span>
  );
}

export default function Flip() {
  const [mode, setMode] = useState<Mode>({ view: "forbes" });
  const [open, setOpen] = useState<string | null>(null);
  const [balance, setBalance] = useState(50000);

  const ordered = useMemo(() => {
    if (mode.sort) {
      const { key, dir } = mode.sort;
      return [...rows].sort((a, b) => {
        const x = sortVal(a, key), y = sortVal(b, key);
        if (x == null) return 1;
        if (y == null) return -1;
        return (y - x) * dir;
      });
    }
    return mode.view === "forbes" ? forbesOrder(rows) : valueOrder(rows);
  }, [mode]);

  const isValue = mode.view === "value" && !mode.sort;
  const firstUnranked = isValue ? ordered.findIndex((r) => !r.ranked) : -1;

  const sortBy = (key: SortKey) =>
    setMode((m) => ({ view: m.view, sort: m.sort?.key === key ? (m.sort.dir === 1 ? { key, dir: -1 } : undefined) : { key, dir: 1 } }));
  const arrow = (k: SortKey) => (mode.sort?.key === k ? (mode.sort.dir === 1 ? " ▼" : " ▲") : "");

  return (
    <section aria-label="The list" className="flip">
      <div className="toggle" role="tablist">
        <button role="tab" aria-selected={mode.view === "forbes" && !mode.sort} onClick={() => setMode({ view: "forbes" })}>
          What they kept <span className="sub">Forbes order</span>
        </button>
        <button role="tab" aria-selected={isValue} onClick={() => setMode({ view: "value" })}>
          What others hold <span className="sub">value held by others</span>
        </button>
      </div>
      {mode.sort?.key === "gdp" && (
        <p className="floor-note">Floor rows (US companies that don&apos;t report payroll) are understated: payroll is counted as jobs × median pay.</p>
      )}

      <div className="grid head" role="row">
        <span>#</span>
        <span>Person · company</span>
        <span className="num">Net worth</span>
        <span className="num">Share kept</span>
        <span className="num strong">Held by others</span>
        <button className="num hide-sm" onClick={() => sortBy("jobs")}>Jobs{arrow("jobs")}</button>
        <button className="num hide-md" onClick={() => sortBy("median")}>Median pay{arrow("median")}</button>
        <button className="num hide-md" onClick={() => sortBy("gdp")}>GDP contrib.{arrow("gdp")}</button>
      </div>

      <LayoutGroup>
        {ordered.map((r, i) => {
          const c = companies[r.company];
          const d = deltas.get(r.id);
          const nw = r.forbes.net_worth_usd;
          const minority = minorityOfNetWorth(r.stake_usd.value, nw);
          const shared = r.shares_company_with.length > 0;
          const rankLabel = isValue ? (r.ranked ? r.value_rank : "–") : mode.sort ? i + 1 : r.forbes.rank;
          return (
            <Fragment key={r.id}>
              {i === firstUnranked && (
                <motion.div layout className="group-label">Not ranked: inherited or hired. Their companies&apos; numbers still show.</motion.div>
              )}
              <motion.div
                layout="position"
                transition={{ type: "spring", stiffness: 380, damping: 38 }}
                className={`grid row ${open === r.id ? "is-open" : ""} ${r.ranked ? "" : "unranked"}`}
                role="row"
                tabIndex={0}
                aria-expanded={open === r.id}
                onClick={() => setOpen(open === r.id ? null : r.id)}
                onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && (e.preventDefault(), setOpen(open === r.id ? null : r.id))}
              >
                <span className="rank">
                  {rankLabel}
                  {isValue && d != null && d !== 0 && <span className={d > 0 ? "up" : "down"}>{d > 0 ? `▲${d}` : `▼${-d}`}</span>}
                </span>
                <span className="who">
                  <span className="avatar" aria-hidden>{initials(r.name)}</span>
                  <span>
                    <span className="name">{r.name}</span>
                    <span className="meta">
                      {c.name} · <span className={`role role-${r.role}`}>{ROLE[r.role]}</span>
                      {shared && <span className="pill">shared {sharedName[r.company] ?? c.name} figure</span>}
                      {r.badge && <span className="pill accent">{r.badge}</span>}
                    </span>
                  </span>
                </span>
                <span className="num">
                  {money(nw)}
                  {(r.id === "elon-musk" || minority) && (
                    <sup className="mark" title={`The listed ${c.name} stake is under half of this net worth; share kept and held by others describe ${c.name} only.`}>
                      *
                    </sup>
                  )}
                  {r.id === "elon-musk" && <span className="subtext">incl. private SpaceX/xAI; other columns are Tesla only</span>}
                </span>
                <span className="num"><Stake p={r} /></span>
                <span className="num strong">{money(r.value_held_by_others_usd)}</span>
                <span className="num hide-sm">{c.jobs.more_than ? ">" : ""}{c.jobs.value.toLocaleString("en-US")}</span>
                <span className="num hide-md">{c.median_pay_usd ? money(c.median_pay_usd.value) : <span className="na">not disclosed</span>}</span>
                <span className="num hide-md">
                  {c.gdp_contribution_usd ? (
                    <>
                      {money(c.gdp_contribution_usd.value)}
                      <span className={`tag ${c.gdp_contribution_usd.method}`}>{c.gdp_contribution_usd.method === "floor" ? "floor" : "reported"}</span>
                    </>
                  ) : (
                    <span className="na">n/a</span>
                  )}
                </span>
              </motion.div>
              {open === r.id && <Detail p={r} balance={balance} setBalance={setBalance} />}
            </Fragment>
          );
        })}
      </LayoutGroup>
      <p className="table-foot">
        Rows don&apos;t add up: co-founders each show their whole company. ▲▼ count places moved between the two views within this list of {rows.length}; {rankedCount} are ranked.
        <sup className="mark">*</sup> marks a stake under half of net worth.
      </p>
    </section>
  );
}

function Detail({ p, balance, setBalance }: { p: Row; balance: number; setBalance: (n: number) => void }) {
  const c = companies[p.company];
  const kept = p.share_kept_pct;
  const inst = c.institutional_pct ? Math.min(c.institutional_pct.value, 100 - kept) : null;
  const rest = 100 - kept - (inst ?? 0);
  const exp = indexExposure(balance, c.sp500_weight_pct?.value ?? null);
  const v = deltas.get(p.id);
  const fin: [string, { value: number; src: Src } | null | undefined, string?][] = [
    ["Revenue", c.revenue_usd],
    ["EBITDA", c.ebitda_usd, "operating income + depreciation & amortisation"],
    ["Payroll", c.payroll_usd, c.payroll_usd?.method === "floor" ? "at least: jobs × median pay" : "reported"],
    ["Cash taxes paid", c.cash_taxes_paid_usd],
    ["R&D", c.rd_usd],
  ];
  return (
    <motion.div className="detail" initial={{ opacity: 0, y: -4 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.18 }}>
      <div className="d-col">
        <h4>Who owns the rest of {c.name}</h4>
        <div className="bar" aria-label="ownership split">
          <span style={{ width: `${kept}%` }} className="b-kept" />
          {inst != null && <span style={{ width: `${inst}%` }} className="b-inst" />}
          <span style={{ width: `${rest}%` }} className="b-rest" />
        </div>
        <ul className="legend">
          <li><i className="b-kept" />{isWalton(p.id) || p.stake_usd.family ? "Family" : p.name.split(" ")[0]} {kept.toFixed(1)}%{" "}
            {!isWalton(p.id) && <SrcLink src={p.stake_usd.src as Src}>({money(p.stake_usd.value)})</SrcLink>}
            {isWalton(p.id) && <SrcLink src={p.stake_usd.src as Src}>(source)</SrcLink>}
          </li>
          {inst != null && c.institutional_pct && <li><i className="b-inst" />Institutions {inst.toFixed(0)}% <SrcLink src={c.institutional_pct.src}>(source)</SrcLink></li>}
          <li><i className="b-rest" />Everyone else {rest.toFixed(0)}%</li>
        </ul>
        {p.stake_usd.note && <p className="small">{p.stake_usd.note}</p>}
        {drawerNotes[p.id] && <p className="note">{drawerNotes[p.id]}</p>}
        {p.ranked && v != null && (
          <p className="small">
            Forbes #{p.forbes.rank} worldwide → #{p.value_rank} of {rankedCount} ranked here by value held by others.
          </p>
        )}
        {p.note && <p className="small">{p.note}</p>}
        {c.cofounders.length > 1 && <p className="small">Co-founders: {c.cofounders.join(", ")}.</p>}
      </div>

      <div className="d-col">
        <h4>Company footprint <span className="fy">FY ending {c.fiscal_year_end}</span></h4>
        <dl className="fin">
          <dt>Jobs</dt>
          <dd><SrcLink src={c.jobs.src}>{c.jobs.more_than ? ">" : ""}{c.jobs.value.toLocaleString("en-US")}</SrcLink> <span className="small">{c.jobs.basis}</span></dd>
          <dt>Median pay</dt>
          <dd>{c.median_pay_usd ? <SrcLink src={c.median_pay_usd.src}>{money(c.median_pay_usd.value)}</SrcLink> : <span className="na">not disclosed</span>}</dd>
          {fin.map(([k, n, hint]) => (
            <Fragment key={k}>
              <dt>{k}</dt>
              <dd>{n ? <SrcLink src={n.src}>{money(n.value)}</SrcLink> : <span className="na">n/a</span>} {n && hint && <span className="small">{hint}</span>}</dd>
            </Fragment>
          ))}
          <dt>GDP contribution</dt>
          <dd>{c.gdp_contribution_usd ? <>{money(c.gdp_contribution_usd.value)} <span className="small">EBITDA + payroll, {c.gdp_contribution_usd.method}</span></> : <span className="na">n/a</span>}</dd>
        </dl>
        {c.notes.map((n) => <p key={n} className="small">{n}</p>)}
      </div>

      <div className="d-col">
        <h4>In your 401(k)</h4>
        {exp != null && c.sp500_weight_pct ? (
          <>
            <label className="small">
              If your 401(k) holds an S&amp;P 500 index fund with $
              <input type="number" min={0} step={1000} value={balance} onChange={(e) => setBalance(Math.max(0, Number(e.target.value) || 0))} />
            </label>
            <p className="big">{money(exp)}</p>
            <p className="small">of it is {c.name} ({c.sp500_weight_pct.value.toFixed(2)}% of the index, <SrcLink src={c.sp500_weight_pct.src}>SPY holdings</SrcLink>).</p>
          </>
        ) : (
          <p className="small">{c.name} is not in the S&amp;P 500.</p>
        )}
        <p className="small">But most stock is held by few: the top 1% of US households hold 50.9% of it, the bottom 90% hold 12.0%.</p>
      </div>
    </motion.div>
  );
}
