"""Latest Form 4 holdings for an insider: python pipeline/form4.py OWNER_CIK ISSUER_CIK [n]

Prints, for the newest n Form 4s filed for that issuer, every holding line's post-transaction amount by security,
so the stake can be read off (and cross-checked against the proxy).
"""
import json
import re
import sys

from common import SEC_UA, fetch, sec_json

owner, issuer = int(sys.argv[1]), int(sys.argv[2])
n = int(sys.argv[3]) if len(sys.argv) > 3 else 3
r = sec_json(f"https://data.sec.gov/submissions/CIK{owner:010d}.json")["filings"]["recent"]
seen = 0
for form, filed, acc in zip(r["form"], r["filingDate"], r["accessionNumber"]):
    if form != "4":
        continue
    base = f"https://www.sec.gov/Archives/edgar/data/{owner}/{acc.replace('-', '')}"
    idx = json.loads(fetch(f"{base}/index.json", SEC_UA))
    xml = next(i["name"] for i in idx["directory"]["item"] if i["name"].endswith(".xml"))
    x = fetch(f"{base}/{xml}", SEC_UA)
    if f"<issuerCik>{issuer:010d}</issuerCik>" not in x and f"<issuerCik>{issuer}</issuerCik>" not in x:
        continue
    last = {}
    for _, row in re.findall(r"<(nonDerivativeTransaction|nonDerivativeHolding)>(.*?)</\1>", x, re.S):
        title = re.search(r"<securityTitle>\s*<value>(.*?)</value>", row, re.S).group(1).strip()
        post = re.search(r"<sharesOwnedFollowingTransaction>\s*<value>(.*?)</value>", row, re.S)
        nat = re.search(r"<natureOfOwnership>\s*<value>(.*?)</value>", row, re.S)
        if post:
            last[(title, nat.group(1).strip()[:60] if nat else "direct")] = float(post.group(1))
    period = re.search(r"<periodOfReport>(.*?)<", x).group(1)
    print(f"== filed {filed} period {period} {base}/{acc}-index.htm")
    for (title, nat), v in last.items():
        print(f"   {title} | {nat} | {v:,.0f}")
    print(f"   TOTAL {sum(last.values()):,.0f}")
    seen += 1
    if seen >= n:
        break
