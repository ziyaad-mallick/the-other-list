"""Shared helpers: cached HTTP fetches and HTML-to-text for filings."""
import hashlib
import html
import json
import re
import time
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "pipeline" / ".cache"
DATA = ROOT / "data"
SEC_UA = "pie-index research bot admin@pie-index.invalid"
BROWSER_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"


def fetch(url: str, ua: str = BROWSER_UA, binary: bool = False):
    """GET with an on-disk cache keyed by URL, so re-runs don't re-download."""
    CACHE.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha1(url.encode()).hexdigest()
    path = CACHE / key
    if not path.exists():
        req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept-Encoding": "identity"})
        with urllib.request.urlopen(req, timeout=90) as r:
            path.write_bytes(r.read())
        if "sec.gov" in url:
            time.sleep(0.15)  # SEC fair-access limit is 10 requests/second
    raw = path.read_bytes()
    return raw if binary else raw.decode("utf-8", errors="replace")


def fetch_json(url: str, ua: str = BROWSER_UA):
    return json.loads(fetch(url, ua))


def sec_json(url: str):
    return fetch_json(url, SEC_UA)


class _Text(HTMLParser):
    BLOCK = {"p", "div", "tr", "br", "li", "h1", "h2", "h3", "h4", "table", "td"}

    def __init__(self):
        super().__init__()
        self.out = []

    def handle_starttag(self, tag, attrs):
        if tag in self.BLOCK:
            self.out.append("\n" if tag != "td" else " | ")

    def handle_data(self, data):
        self.out.append(data)


def html_to_text(raw: str) -> str:
    p = _Text()
    p.feed(raw)
    text = html.unescape("".join(p.out)).replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"( \| )+", " | ", text)
    return re.sub(r"\n\s*\n+", "\n", text)


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
