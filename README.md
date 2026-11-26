# Forbes, Flipped

Ranking billionaires by what they created, not what they kept.

Forbes ranks people by what they kept. In 2024 Jeff Bezos asked for a list ranking people by the wealth they created for others. On 22 Nov 2026, David Senra and Tobi Lütke said someone should build it. This is that list: the Forbes top names (plus six founders picked for contrast), flipped to **value held by others = market cap − the person's stake**, with the case against counting this way on the same page.

Every number on the page links to the filing or page it came from. The snapshot is dated, and nothing updates live.

## Method in one table

| Field | How |
|---|---|
| Stake | Shares from the latest proxy, Form 4 or annual report × price at the snapshot close |
| Share kept | stake ÷ market cap |
| Value held by others | market cap − stake |
| Ranked | founders, co-founders, built by acquisition. Heirs and hired CEOs are listed, not ranked |
| GDP contribution | EBITDA + payroll; payroll is reported where disclosed, otherwise jobs × median pay (a floor) |

No credit splitting: co-founders each show their whole company, so the rows don't add up. Full definitions are in [SPEC.md](SPEC.md) §5.

## Re-run the data

Needs Python 3.11.

```
python -m venv .venv
.venv/Scripts/pip install -r pipeline/requirements.txt   # bin/ on macOS/Linux
python pipeline/sec.py && python pipeline/market.py && python pipeline/forbes.py   # fetch
python pipeline/build.py                     # writes data/companies.json, data/people.json
python -m pytest pipeline/test_data.py       # data gates: every number cited, bounds, roles
python pipeline/report.py                    # spot-check table
```

Hand-checked values (stakes, non-US financials, jobs and median pay) live in `pipeline/curated.py`, each with its source URL and the verbatim line it came from.

## Run the site

```
npm install
npm test        # vitest: lib/metrics.ts matches the Python pipeline row by row
npm run dev
```

Next.js App Router, static. `/api/og?id=<person-id>` returns a 1200×630 share card.

## Corrections

If a number is wrong, open an issue with the source. Fixes go into `curated.py` with the new citation.

By Ziyaad Mallick.
