# SPEC: The Other List

Subtitle: *What the richest founders created for everyone else.*
Byline: Built by Ziyaad Mallick (X link: placeholder until he gives the handle).

Status: APPROVED 24 Nov 2026 with fixes (folded in below). P0 is done; P1 is next, then a pause for his spot-check.
Repo: `Desktop/Mallick/30-work/pie-index` (Next.js 16.4.6, React 19.3.0, Tailwind 4.3.3, framer-motion 14 installed; no app code yet).

---

## 1. What this is, in one paragraph

A single public web page that takes Jeff Bezos's question seriously ("rank people by how much wealth they've created for other people, instead of the Forbes list") and answers it with plain arithmetic from company filings. It also gives the strongest objections the same amount of room. It is neither billionaire PR nor billionaire hate. It shows the numbers, says what they measure and what they don't, and links every figure to its source.

## 2. Why now (verified 24 Nov 2026)

| Fact | Source | Status |
|---|---|---|
All episode quotes below were checked against the YouTube captions of w0oOxs0WKNk (YouTube's English caption track, which looks auto-generated), pulled on 24 Nov. On the page, a quote may cut filler words, marked with "…", but changes no other word. Each quote links to youtube.com/watch?v=w0oOxs0WKNk&t=<seconds>.

| Fact | Source | Status |
|---|---|---|
| David Senra's episode with Tobi Lütke came out on 22 Nov 2026 (1h10m). YouTube title: "There Is No Such Thing as Founder Succession". | davidsenra.com/episode/tobi-lutke-2; Scuttlebutt, 23 Nov | verified (two sources) |
| 16:56, Senra recalling Bezos: "there should be a list of how much wealth the entrepreneur has created… Amazon's worth $2 trillion. I own 200 billion of that 2 trillion, which means I created… or I helped create 1.8 trillion for others." | captions | verified |
| 17:17, Senra: "we can just put things into existence with AI now. We should just build this together and just have a… list… about the wealth created by other people." | captions | verified. **The earlier draft said this wasn't found; that was wrong, it came from summary pages.** |
| 17:20, Lütke: "I completely agree… where does the money come from? It seems a question that a lot of people just are not curious about, but it is the most important question" | captions | verified |
| 13:12, Lütke: "I started Shopify… I'm obviously not responsible for all the value of Shopify. This is a team production… I own very small percentage of the company… like 5, 6%… So like 95% is owned by… the public, by employees, by early people who took bets" | captions | verified |
| 17:37, Lütke: "redistribution of… money is also an incredibly important topic, but clearly it's a secondary topic to creating it" | captions | verified (this is the balanced line for section 6) |
| Bezos at DealBook, 4 Dec 2024: "Somebody needs to make a list where they rank people by how much wealth they've created for other people, instead of the Forbes list that ranks you by your own wealth." He put the figure at about $2.1T. | Fortune, 5 Dec 2024 | one primary report; other search hits repeat Fortune |
| Huang told employees about the affair on 8 Nov and **resigned as CEO on 12 Nov**. Nvidia reinstated him "effective immediately" on 23 Nov. Shares rose 31% that day; CNBC says the stock "gained nearly $1 trillion". The next morning they were about 5% lower in premarket trading. | CNBC 23 and 24 Nov; NBC; Nvidia press release 23 Nov | verified across two outlets. A "$950B" figure suggested in review appears in no source read, so the page uses CNBC's wording. |
| Nvidia's release cites "input from senior levels of the United States government". Trump told CNBC he "personally intervened". Still open: the board committee's investigation, a California DOJ probe, a reported SEC inquiry, and House committee interviews from 1 Dec. | Nvidia release; CNBC 24 Nov; NBC | verified |
| Gallup 2025: 62% of US adults own stock, including through 401(k)s and IRAs. By household income: 28% of those under $50k, 87% of those at $100k or more. | news.gallup.com/poll/266807 | read by a fetch agent; re-open in P5 fact-check |
| **Fed Distributional Financial Accounts, 2026 Q2: share of all corporate equities and mutual fund shares held. Top 1%: 50.9% (top 0.1%: 25.0%, rest of the top 1%: 25.9%). Next 9%: 37.2%. Next 40%: 11.4%. Bottom 50%: 0.6%.** So the bottom 90% hold 12.0%. | federalreserve.gov dfa.zip, dfa-networth-shares.csv | verified (pulled and parsed 24 Nov) |
| Fed 2022 Survey of Consumer Finances: 58% of families own stock directly or indirectly. The 2025 survey was published 9 Oct 2026. | federalreserve.gov | 2022 figure from an extracted summary; **get the 2025 figure in P1** |

Prior art: the Anti-Forbes List by Sakshyam Patro already re-sorts Forbes by market cap minus stake. This site differs in three ways: jobs, pay and GDP contribution sit next to the share maths; heirs and hired CEOs are shown but not credited; and the case against gets equal room.

## 3. Page structure (top to bottom)

1. **Title, subtitle, byline, and the argument in one or two lines.** Draft: *"Forbes ranks people by what they kept. Jeff Bezos asked for a list of what they built for everyone else. On 22 Nov, David Senra and Tobi Lütke said someone should build it. Here it is, with the case against it."* The table starts right below, above the fold at 1440×900. **No news strip at the top.**
2. **The flip (the main thing).**
   - A table of 24 people.
   - The default order is Forbes net worth. One toggle animates the rows into the "value held by others" order.
   - Each row: Forbes rank, name, company, role tag, net worth, share kept, value held by others, jobs, median pay, GDP contribution.
   - In the value view, heirs and the hired CEO drop into a separate "Not ranked: inherited or hired" group at the bottom, with their company numbers still visible.
   - Rank-change pills (▲/▼) appear on every ranked row, computed only from positions within this 24-person list (never global Forbes rank minus value rank). Changed 25 Nov.
   - **Screenshot-proofing:**
     - **Musk:** his net-worth cell reads `$810.8B*`, with inline subtext: "incl. private SpaceX/xAI; share kept and value held by others are Tesla only".
     - **Page and Brin:** both rows carry a small pill, "shared Alphabet figure", so the back-to-back rows don't read as a duplicate.
     - Gates and Ballmer get the same treatment for Microsoft, as do the Waltons for Walmart.
   - **Sorting:** the Jobs, Median pay and GDP contribution headers are clickable, with visible ▲/▼ sort indicators. Sorting by GDP contribution shows a one-line note above the table: "Floor rows (US companies that don't report payroll) are understated."
3. **Detail panel.** Click any row for:
   - **Who owns the rest:** founder versus institutions versus everyone else.
   - **In your 401(k):** for S&P 500 companies, balance × index weight. Labelled "if your 401(k) holds an S&P 500 index fund".
   - **Company footprint:** jobs, median pay, estimated payroll, GDP contribution, **cash taxes paid and R&D spend** (panel only, not the table).
   - **Co-founders named.** Tobi's own "team production" line sits on his card.
   - **The role note** (e.g. "Inherited: Walmart was founded by Sam and Bud Walton").
   - **Sources**, each a link.
4. **Who are "the others"?** The Gallup and Fed numbers: most Americans own some stock (62%), but the top 1% hold 50.9% of it and the bottom 90% hold 12.0%. Both facts appear together, always.
5. **The case for counting this way.** Bezos's arithmetic, and Lütke on creation versus redistribution (including his own "redistribution is also an incredibly important topic" line). Then a two-sentence dated Nvidia note: *"Jensen Huang resigned as Nvidia CEO on 12 Nov and was reinstated on 23 Nov, after the board received input from senior levels of the US government; the shares rose 31% that day, a gain CNBC put at nearly $1 trillion. Investigations by a board committee, California's Justice Department and Congress are still open."* It is framed as the market's own estimate of what one founder is worth, not ours.
6. **The case against.** These are steelmanned and given the same length as section 5:
   - Market value is not social value (externalities, market power).
   - "Others" are mostly already-wealthy shareholders (section 4's numbers).
   - Workers, co-founders and early employees built it too (Lütke says so himself).
   - Timing and luck play a part.
   - Inheritance.
   Each point gets one cited source.
7. **Method and sources.** Every formula in plain words, the snapshot date, and a link to the public GitHub repo (data, pipeline, tests).

## 4. The 24 people (Forbes real-time list, pulled 24 Nov 2026)

Selection rule shown on the page: *"Forbes's 18 largest fortunes that come mainly from a public company, plus six founders we picked to show mid-sized companies, including the podcast guest."* The six are labelled as hand-picked, which answers "why these?" up front.

| Forbes # | Person | Net worth ($B) | Company (ticker) | Role tag | Ranked in value view |
|---|---|---|---|---|---|
| 1 | Elon Musk | 810.8 | Tesla (TSLA) | Co-founder (one of five named in the 2009 settlement); stake counts Tesla only, SpaceX is private | yes |
| 2 | Jeff Bezos | 371.1 | Amazon (AMZN) | Founder | yes |
| 3 | Larry Page | 230.4 | Alphabet (GOOGL) | Co-founder | yes |
| 4 | Sergey Brin | 212.2 | Alphabet (GOOGL) | Co-founder | yes |
| 5 | Mark Zuckerberg | 202.4 | Meta (META) | Co-founder | yes |
| 6 | Michael Dell | 186.2 | Dell (DELL) | Founder | yes |
| 7 | Warren Buffett | 159.1 | Berkshire Hathaway (BRK.B) | Built by acquisition (took control in 1965) | yes |
| 8 | Steve Ballmer | 155.2 | Microsoft (MSFT) | Hired CEO (employee #30) | no |
| 9 | Rob Walton & family | 154.0 | Walmart (WMT) | Inherited | no |
| 10 | Jim Walton & family | 150.8 | Walmart (WMT) | Inherited | no |
| 11 | Amancio Ortega | 146.7 | Inditex (ITX.MC) | Co-founder | yes |
| 12 | Larry Ellison | 146.7 | Oracle (ORCL) | Co-founder | yes |
| 13 | Alice Walton | 140.1 | Walmart (WMT) | Inherited | no |
| 14 | Jensen Huang | 132.2 | Nvidia (NVDA) | Co-founder | yes |
| 15 | Carlos Slim Helú & family | 123.3 | América Movil (AMX) | Built by acquisition (Telmex privatisation, 1990) | yes |
| 16 | Bill Gates | 119.5 | Microsoft (MSFT) | Co-founder | yes |
| 17 | Bernard Arnault & family | 116.7 | LVMH (MC.PA) | Built by acquisition | yes |
| 19 | Françoise Bettencourt Meyers & family | 101.3 | L'Oréal (OR.PA) | Inherited | no |
| 222 | Daniel Ek | 13.5 | Spotify (SPOT) | Co-founder, featured | yes |
| 251 | Brian Chesky | 12.2 | Airbnb (ABNB) | Co-founder, featured | yes |
| 269 | Tobi Lütke | 11.7 | Shopify (SHOP) | Co-founder, featured (podcast guest) | yes |
| 461 | Marc Benioff | 8.2 | Salesforce (CRM) | Co-founder, featured | yes |
| 742 | Brian Armstrong | 5.6 | Coinbase (COIN) | Co-founder, featured | yes |
| 1047 | Reed Hastings | 4.0 | Netflix (NFLX) | Co-founder, featured | yes |

Skipped from Forbes's top 19: #18 Changpeng Zhao (crypto, no corporate filings). The page lists this skip. Ranks and net worth are a dated snapshot, not live.

19 people are ranked and 5 are not, across 20 companies.

## 5. Definitions (exact; these are the whole method)

All money is in USD at the snapshot date, with FX from the same date.

| Field | Formula / source |
|---|---|
| `market_cap` | Shares outstanding × price at the snapshot (Yahoo Finance via `yfinance`). For Alphabet and Berkshire, all share classes together. |
| `stake_usd` | The person's (or family's) shares from the latest proxy statement or annual report × price at the snapshot. The filing and its date are cited. |
| `share_kept_pct` | `stake_usd / market_cap × 100`. Bounded 0 to 100 by construction. |
| `value_held_by_others` | `market_cap − stake_usd`. This is Bezos's own arithmetic. It is the company's value held by everyone except this person. |
| Co-founders | **No credit splitting.** Page's and Brin's rows both show Alphabet. Co-founders are named on each card. The page says plainly that rows don't add up and that the number is the company's, not a claim that one person made all of it. (Tobi's "team production" line backs this up.) |
| Value-view rank | Order by `value_held_by_others`, over ranked people only (founder, co-founder, built by acquisition). Ties break on Forbes rank. |
| `jobs` | Employees as reported in the latest annual filing, with the "as of" date. |
| `median_pay` | Median employee pay from the CEO pay-ratio disclosure in the proxy statement (Item 402(u)). Non-US filers show "not disclosed". |
| `payroll` | Reported personnel or staff cost where the company discloses it (the IFRS filers). Otherwise `jobs × median_pay`, labelled "at least". |
| `gdp_contribution` (est.) | `EBITDA + payroll`, the national-accounts income approach to value added. EBITDA = operating income + depreciation and amortisation, from the same filing. Every row carries a method tag: "reported" or "floor". It is sortable, with a visible note that floor rows are understated. It is **not** part of the flip ranking. |
| Berkshire | EBITDA and GDP contribution are shown as n/a: its reported income mixes insurance underwriting and investment gains with operating results, so no figure fits the same definition. Changed 25 Nov after the spot-check. |
| `sp500_weight` | From SSGA's SPY daily holdings file at the snapshot (GOOGL + GOOG combined). It is null for companies outside the S&P 500 (ITX, MC, OR, AMX, SHOP, SPOT). |
| 401(k) widget | `balance × sp500_weight / 100`. The default balance is $50,000, editable. The section 5 ownership facts always sit right under it. |

What the method deliberately does not do:
- no scores, tiers or weights;
- no credit splits;
- no consumer-surplus or "ecosystem" multipliers in the table;
- no private companies.

## 6. Data pipeline (all offline; the site ships static JSON)

```
pipeline/forbes.py      Forbes real-time JSON -> data/raw/forbes.json (rank, net worth, timestamp)
pipeline/sec.py         SEC companyfacts (revenue, operating income, D&A, taxes, R&D)
                        + 10-K text (headcount) + DEF 14A text (median pay, beneficial ownership)
                        -> data/raw/sec/<ticker>.json, each value with filing URL + accession + date
pipeline/manual.json    Inditex, LVMH, L'Oréal (annual reports), Spotify + América Movil (20-F):
                        each value with the document URL and page number
pipeline/market.py      yfinance prices, shares, FX + SPY holdings -> data/raw/market.json
pipeline/build.py       merges into data/people.json (the one file the site reads) + data/meta.json
pipeline/test_data.py   pytest gates (section 8)
```

Source counts for the 20 companies:
- **US 10-K + proxy (14):** AMZN, GOOGL, META, DELL, BRK, MSFT, WMT, ORCL, NVDA, TSLA, ABNB, NFLX, CRM, COIN.
- **US 10-K, proxy to check (1):** SHOP, which filed a 10-K on 11 Feb 2026.
- **20-F (2):** SPOT, AMX.
- **Annual report only (3):** ITX, MC, OR.
- So median pay will show "not disclosed" for 5 or 6 companies. My earlier "4" was wrong for this set.

## 7. Build

- Next.js App Router, one route (`/`), statically generated. `app/api/og/route.tsx` makes share cards (`next/og`).
- `lib/metrics.ts` holds the pure functions for the section 5 formulas, with `lib/metrics.test.ts` (vitest).
- framer-motion layout animation for the flip. Rows are CSS-grid `div`s, not `<tr>`.
- Initials instead of photos (real photos are copyrighted).
- The design pass runs through `/frontend-zi` before any UI code. The direction carries over from the old spec: editorial, light paper background, ink text, tabular numbers, colour only for rank changes.
- Hosted on Vercel, project `pie-index`.

## 8. Acceptance criteria

1. **Every number is cited.** Each number on the page has a source link that opens the filing or page it came from, and `pytest pipeline/test_data.py` fails if any field lacks a URL and date.
2. **Data integrity.** For every row: `0 ≤ stake_usd ≤ market_cap`, `share_kept_pct` is in [0, 100], `payroll ≤ revenue`, and `gdp_contribution > 0` for profitable companies.
3. **Ranked set and roles.** Exactly 19 people are ranked in the value view and 5 are in the "not ranked" group. The role tag for each matches section 4.
4. **The flip runs cleanly.** It animates without layout shift and with no horizontal scroll at 375 px and 1440 px widths, checked on screenshots.
5. **Verified quotes only.** Every quote on the page matches the YouTube captions or the cited article word for word. No quote rests on a summary site alone.
6. **Fact-check passes.** A cold reviewer (Opus) checks every factual claim on the page against its source and finds no unsupported claims.
7. **Balance.** Sections 5 and 6 are within 15% of each other in word count.
8. **Clean checks.** `npm run build`, `vitest run` and `pytest` all exit 0.
9. **Live.** The live Vercel URL loads, the flip works there, and `/api/og?id=tobi-lutke` returns a 1200×630 PNG.
10. **Screenshot-proofing.** Musk's net-worth cell shows the `*` and its subtext. Every row whose company appears on another row carries the "shared <company> figure" pill (Alphabet ×2, Microsoft ×2, Walmart ×3). The Jobs, Median pay and GDP headers sort on click and show the floor note when sorting by GDP.
11. **Table above the fold.** The table's first row is visible without scrolling at 1440×900.
12. **Public repo.** The GitHub repo is public, with a README explaining how to re-run the pipeline and the tests. It is pushed only after Ziyaad's P1 spot-check, so unchecked numbers are never public.

## 9. Plan and effort

| Phase | Work | CC time | Human team |
|---|---|---|---|
| P0 | Check the quotes against the YouTube captions; open the Nvidia, Bezos and Fed sources | 30 min | 3 h |
| P1 | Data pipeline + `people.json` for 24 people + pytest gates | 2.5 h | 3 days |
| **PAUSE** | **Ziyaad spot-checks a 24-row table of the key numbers** | | |
| P2 | `lib/metrics.ts` + vitest | 30 min | 1 day |
| P3 | `/frontend-zi` design pass: direction plus a prototype of the flip | 45 min | 2 days |
| P4 | Build sections 1 to 8 | 2 h | 4 days |
| P5 | Write the case for and against; cold fact-check review; fixes | 1 h | 1 day |
| P6 | OG cards, mobile, build, deploy, verify live | 45 min | 1 day |
| | **Total** | **~8 h** | **~2.5 weeks** |

Order: data before UI, because the numbers decide what the table can honestly show. The pause after P1 is where wrong figures get caught cheaply.

## 10. Out of scope (v1)

- Scores, tiers or lenses.
- GDP or consumer-surplus multipliers in the table.
- Private companies (SpaceX, Bloomberg LP, Koch), and crypto without corporate filings.
- Live price feeds: the page shows a dated snapshot plus an optional refresh script.
- Photos, accounts and comments.

## 11. Rollback

Static site: roll back with `vercel rollback` or remove the project (`vercel remove` needs Ziyaad's yes). No database and no user data.

## 12. Decisions (answered 24 Nov)

1. **Name:** The Other List. Subtitle: "What the richest founders created for everyone else."
2. **Byline and repo:** Ziyaad's name on the page with an X link (handle still needed). Public GitHub repo with a README, pushed after the P1 spot-check.
3. **Taxes and R&D:** in the detail panel, not the table.
4. **GDP contribution:** per company with a reported/floor tag, sortable, outside the flip ranking.
5. **Nvidia:** no top strip. A two-sentence dated note in section 5 instead.

Still open: his X handle for the byline.
