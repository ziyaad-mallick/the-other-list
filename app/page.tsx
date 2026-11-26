import Flip from "./Flip";
import { companies, context, meta, money, people } from "@/lib/data";
import { builtTotals } from "@/lib/metrics";

const REPO = "https://github.com/ziyaad-mallick/the-other-list";
const YT = (t: number) => `${context.episode.url}&t=${t}s`;
const q = Object.fromEntries(context.episode.quotes.map((x) => [x.t, x]));
const o = context.ownership;
const nv = context.nvidia;
const t = builtTotals(
  people.map((p) => ({ ranked: p.ranked, company: p.company, stake: p.stake_usd.value })),
  (k) => ({ cap: companies[k].market_cap_usd.value, jobs: companies[k].jobs.value }),
);
const meta_ = companies.META;
const metaFloor = meta_.jobs.value * (meta_.median_pay_usd?.value ?? 0);

function A({ href, children }: { href: string; children: React.ReactNode }) {
  return <a href={href} target="_blank" rel="noreferrer">{children}</a>;
}

export default function Page() {
  return (
    <main>
      <header className="hero">
        <h1>The Other List</h1>
        <p className="subtitle">What the richest founders created for everyone else.</p>
        <div className="thesis" aria-label="The headline">
          <div className="stat big-stat">
            <b>{money(t.others)}</b>
            <span>held by everyone else: pension and index funds, employees, savers</span>
          </div>
          <div className="stat">
            <b>{Math.round(t.keptPct)}%</b>
            <span>kept by the {t.people} founders ranked here ({money(t.kept)})</span>
          </div>
          <div className="stat">
            <b>{(Math.floor(t.jobs / 1e5) / 10).toFixed(1)}M+</b>
            <span>jobs at the {t.companies} companies they built or grew</span>
          </div>
        </div>
        <p className="lede">
          Forbes ranks people by what they kept. Jeff Bezos asked for a list of what they built for everyone else. On 22 Nov,
          David Senra and Tobi Lütke said someone should build it. Here it is, with the case against it.
        </p>
        <p className="byline">
          By <A href="https://github.com/ziyaad-mallick">Ziyaad Mallick</A> · Snapshot {meta.snapshot_date} · <A href={REPO}>Data and code</A>
        </p>
      </header>

      <Flip />

      <section className="prose" id="others">
        <h2>Who are &ldquo;the others&rdquo;?</h2>
        <p>
          Most American adults own some stock: <A href={o.gallup.src.url}>62% in Gallup&apos;s 2025 poll</A>, falling to 28% in
          households under $50,000 a year. But ownership is concentrated. In the{" "}
          <A href={o.fed_dfa.src.url}>Federal Reserve&apos;s accounts for {o.fed_dfa.quarter}</A>, the top 1% of households by wealth
          held {o.fed_dfa.top_1_pct}% of all corporate equities and mutual fund shares; the bottom 90% held {o.fed_dfa.bottom_90_pct}%.
          The <A href={o.scf_2025.src.url}>Fed&apos;s 2025 family survey</A> found {o.scf_2025.bottom_half_income_pct}% of
          bottom-half families held any stock, against {o.scf_2025.top_decile_pct}% of the top decile. Both facts are true at once:
          the others are many people, and they hold very unequal amounts.
        </p>
      </section>

      <div className="cases">
        <section className="prose case">
          <h2>The case for counting this way</h2>
          <p>
            Bezos put the arithmetic plainly in 2024: <q>{context.bezos_dealbook.quote}…</q>{" "}
            (<A href={context.bezos_dealbook.src.url}>Fortune</A>). Senra retold it on his show:{" "}
            <q>{q[1016].text}</q> (<A href={YT(1016)}>16:56</A>). Then: <q>{q[1037].text}</q> (<A href={YT(1037)}>17:17</A>).
          </p>
          <p>
            Lütke agreed and asked the question the usual list skips: <q>{q[1040].text}</q> (<A href={YT(1040)}>17:20</A>). He did
            not wave away the other side: <q>{q[1057].text}</q> (<A href={YT(1057)}>17:37</A>).
          </p>
          <p>
            Markets put a price on founders, too. Jensen Huang resigned as Nvidia CEO on 12 Nov and was reinstated on 23 Nov, after
            the board received input from senior levels of the US government; the shares rose {nv.share_move_pct}% that day, a gain
            CNBC put at {nv.market_value_wording}. Investigations by a board committee, California&apos;s attorney general and
            Congress are still open (<A href={nv.srcs[1].url}>CNBC</A>, <A href={nv.srcs[2].url}>NBC</A>, <A href={nv.srcs[3].url}>Nvidia</A>). That is the market&apos;s
            own estimate, not ours.
          </p>
        </section>

        <section className="prose case" id="against">
          <h2>The case against</h2>
          <ul>
            <li>
              <b>Market value is not social value.</b> A share price counts expected profit, including profit from market power. A
              US court found in 2024 that <q>Google is a monopolist, and it has acted as one to maintain its monopoly</q>{" "}
              (<A href="https://www.npr.org/2024/08/05/nx-s1-5064624/google-justice-department-antitrust-search">NPR</A>). Some of
              Alphabet&apos;s value is that. Prices also leave out costs a company pushes onto others, which no filing records.
            </li>
            <li>
              <b>The others are mostly the already wealthy.</b> The top 1% hold {o.fed_dfa.top_1_pct}% of stock; the bottom half
              hold {o.fed_dfa.bottom_50_pct}% (<A href={o.fed_dfa.src.url}>Fed</A>). Among households earning under $50,000 a year,
              only {o.gallup.under_50k_pct}% own any stock (<A href={o.gallup.src.url}>Gallup</A>).
            </li>
            <li>
              <b>Many people built it.</b> Lütke says so himself: <q>{q[792].text}</q> (<A href={YT(792)}>13:12</A>). Walmart&apos;s
              median worker earned ${companies.WMT.median_pay_usd!.value.toLocaleString("en-US")} in its last fiscal year{" "}
              (<A href={companies.WMT.median_pay_usd!.src.url}>proxy</A>); the work of its 2.1 million employees shows up in the
              company&apos;s value, not in any one person&apos;s stake.
            </li>
            <li>
              <b>Timing and mood move the number.</b> Nvidia&apos;s market value rose by nearly $1 trillion in a day on a CEO&apos;s
              return (<A href={nv.srcs[1].url}>CNBC</A>). Prices carry mood as well as creation.
            </li>
            <li>
              <b>Some fortunes were inherited.</b> Four of the 24 inherited their stake, and one was a hired CEO. They are listed but not
              ranked, because the question is what a person built.
            </li>
          </ul>
        </section>
      </div>

      <section className="prose method" id="method">
        <h2>Method</h2>
        <ul>
          <li><b>Value held by others</b> = market cap − the person&apos;s stake. Bezos&apos;s own arithmetic. Share kept = stake ÷ market cap.</li>
          <li><b>Stakes</b> come from the latest proxy statement, Form 4 or annual report, valued at the {meta.snapshot_date} close. Gates and Ballmer appear in no current filing, so theirs are Forbes estimates and marked ≤ or ~.</li>
          <li><b>No credit splitting.</b> Co-founders each show the whole company, so rows don&apos;t add up. The number is the company&apos;s, not a claim that one person made it.</li>
          <li><b>Ranked</b>: founders, co-founders and people who built a company by acquisition. Heirs and hired CEOs are listed, not ranked. Rank changes count places within this list of 24.</li>
          <li><b>Jobs</b> are from the latest annual filing; <b>median pay</b> from the CEO pay-ratio disclosure in US proxies. Non-US companies don&apos;t disclose it.</li>
          <li>
            <b>GDP contribution</b> = EBITDA + payroll, the income approach to value added. Where a company reports payroll we use it;
            otherwise payroll is jobs × median pay, a floor. The floor is low: Meta&apos;s 10-K lists employee compensation across its two segments of{" "}
            <A href={meta_.payroll_usd!.src.url}>{`$${(meta_.payroll_usd!.value / 1e9).toFixed(1)}B`}</A> in its 10-K, against a floor of $
            {(metaFloor / 1e9).toFixed(1)}B. Berkshire is n/a because its income mixes in investment gains; Shopify and América Movil
            don&apos;t disclose pay.
          </li>
          <li><b>Not done:</b> no scores, weights or multipliers, and no private companies. Non-USD figures convert at the snapshot rate.</li>
          <li>Every number links to its source. The pipeline, data and tests are on <A href={REPO}>GitHub</A>.</li>
        </ul>
      </section>
      <footer>Forbes net worths are Forbes&apos;s real-time figures as of {meta.forbes_as_of}. Not investment advice.</footer>
    </main>
  );
}
