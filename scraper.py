"""Henter koncerter fra TRAIN, VoxHall, Musikhuset og Tivoli Friheden (Hermans) og skriver data.json.

Ingen AI i kørslen. Kun offentlige kalendersider på stedernes egne domæner.
Billetsider (Ticketmaster, billetten.dk, billetlugen.dk, Tixly) hentes ikke.
Hvis et sted fejler, beholdes sidste kendte data for det sted.
"""
import datetime
import html
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "data.json"
UA = "Mozilla/5.0 (koncert-oplaeg; personlig brug; kontakt: ejer af repo)"
WINDOW_DAYS = 120
TODAY = datetime.date.today()
END = TODAY + datetime.timedelta(days=WINDOW_DAYS)

MONTHS = {
    "januar": 1, "februar": 2, "marts": 3, "april": 4, "maj": 5, "juni": 6,
    "juli": 7, "august": 8, "september": 9, "oktober": 10, "november": 11, "december": 12,
}
STATUS_WORDS = ("Udsolgt", "Få tilbage", "Venteliste")
VENUES = {
    "t": {"name": "TRAIN", "base": "https://train.dk"},
    "v": {"name": "VoxHall", "base": "https://voxhall.dk"},
    "m": {"name": "Musikhuset", "base": "https://www.musikhuset.dk"},
    "f": {"name": "Friheden", "base": "https://friheden.dk"},
}
SOURCE_PAGES = {
    "t": "https://train.dk/kalender",
    "v": "https://voxhall.dk/koncerter/",
    "m": "https://www.musikhuset.dk/kalender",
    "f": "https://friheden.dk/hermans/arrangementer",
}


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")


def anchors(page):
    """Yder (href, tekst, rå indhold) for hvert <a>-element."""
    for m in re.finditer(r'<a\s[^>]*?href="([^"]+)"[^>]*>(.*?)</a>', page, re.S):
        inner = m.group(2)
        text = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", inner))).strip()
        yield m.group(1), text, inner


def split_status(text):
    for w in STATUS_WORDS:
        if text.startswith(w + " "):
            return w, text[len(w) + 1:].strip()
        if text.startswith(w):
            return w, text[len(w):].strip()
    return "", text


def parse_train(page):
    out, seen = [], set()
    pat = re.compile(
        r"^(.*?)\s*(Mandag|Tirsdag|Onsdag|Torsdag|Fredag|Lørdag|Søndag)\s*/\s*(\d{2})\.(\d{2})\.(\d{2})"
    )
    for href, text, _ in anchors(page):
        if not href.startswith("/kalender/") or href in seen:
            continue
        m = pat.match(text)
        if not m:
            continue
        seen.add(href)
        status, name = split_status(m.group(1).strip())
        d, mo, y = int(m.group(3)), int(m.group(4)), 2000 + int(m.group(5))
        out.append({
            "date": f"{y:04d}-{mo:02d}-{d:02d}", "artist": name, "venue": "t",
            "status": status, "note": "", "url": VENUES["t"]["base"] + href,
        })
    return out


def parse_voxhall(page):
    out, seen = [], set()
    pat = re.compile(r"^(\d{2})\.(\d{2})\.(\d{2})\s+(.*)$")
    for href, text, _ in anchors(page):
        if not href.startswith("https://voxhall.dk/koncerter/") or href in seen:
            continue
        if href.rstrip("/") == "https://voxhall.dk/koncerter":
            continue
        m = pat.match(text)
        if not m:
            continue
        seen.add(href)
        d, mo, y = int(m.group(1)), int(m.group(2)), 2000 + int(m.group(3))
        out.append({
            "date": f"{y:04d}-{mo:02d}-{d:02d}", "artist": m.group(4).strip(), "venue": "v",
            "status": "", "note": "", "url": href,
        })
    return out


def parse_musikhuset(page):
    """Siden er grupperet: måned (h3) → dag (aria-label 'onsdag 14. oktober') → begivenheder (a.event).
    Dato og år tages fra overskrifterne, titel og genre fra aria-label på begivenheden."""
    out, seen = [], set()
    tokens = re.compile(
        r"<h3[^>]*>\s*([a-zæøå]+ \d{4})\s*</h3>"
        r'|aria-label="(?:mandag|tirsdag|onsdag|torsdag|fredag|lørdag|søndag) (\d{1,2})\. ([a-zæøå]+)"'
        r"|<a\b([^>]*)>(.*?)</a>",
        re.S | re.I,
    )
    year, day = TODAY.year, None
    for m in tokens.finditer(page):
        if m.group(1):
            name, yr = m.group(1).split()
            if name.lower() in MONTHS:
                year = int(yr)
            continue
        if m.group(2):
            mo = MONTHS.get(m.group(3).lower())
            day = (int(m.group(2)), mo) if mo else None
            continue
        attrs, inner = m.group(4), m.group(5)
        cls = re.search(r'class="([^"]*)"', attrs)
        href = re.search(r'href="(/kalender/[^"]+)"', attrs)
        aria_m = re.search(r'aria-label="([^"]*)"', attrs)
        if not (cls and "event" in cls.group(1).split() and href and aria_m):
            continue
        href, aria = href.group(1), html.unescape(aria_m.group(1))
        if not day or (href, day) in seen:
            continue
        seen.add((href, day))
        body = re.sub(r"^Kl\. [\d.]+:\s*", "", aria)
        artist, _, _ = body.partition(" - ")
        artist = re.sub(r",\s*(Udsolgt|Få tilbage|Venteliste)$", "", artist)
        for genre in ("Familie/Børn", "Klassisk", "Pop/Rock", "Jazz", "Teater", "Comedy", "Dans", "Foredrag/Talk", "Show", "Gratis"):
            artist = re.sub(r",\s*" + re.escape(genre) + r"(?=,|$)", "", artist)
        genres = body.lower()
        status = ""
        for w in STATUS_WORDS:
            if w in html.unescape(re.sub(r"<[^>]+>", " ", inner)):
                status = w
                break
        d, mo = day
        out.append({
            "date": f"{year:04d}-{mo:02d}-{d:02d}", "artist": artist.strip(), "venue": "m",
            "status": status, "note": "", "url": VENUES["m"]["base"] + href,
            "_tags": [g for g in ("pop-rock", "klassisk", "jazz") if g in genres.replace("/", "-")],
        })
    return out


def parse_friheden(page):
    """Hver begivenhed er en <article>. Linket om billedet er tomt, så teksten tages fra hele artiklen."""
    out, seen = [], set()
    pat = re.compile(r"(\d{1,2})\. (\w+) (\d{4}) - \d{2}\.\d{2}")
    for art in re.findall(r'<article class="event-item">(.*?)</article>', page, re.S):
        href_m = re.search(r'href="(/arrangementer/hermans/[^"]+)"', art)
        date_m = re.search(r'class="event-item__date">([^<]+)<', art)
        title_m = re.search(r'class="event-item__headline">([^<]+)<', art)
        if not (href_m and date_m and title_m):
            continue
        href = href_m.group(1)
        if href in seen:
            continue
        m = pat.search(html.unescape(date_m.group(1)))
        mo = MONTHS.get(m.group(2).lower()) if m else None
        if not mo:
            continue
        seen.add(href)
        out.append({
            "date": f"{int(m.group(3)):04d}-{mo:02d}-{int(m.group(1)):02d}",
            "artist": html.unescape(title_m.group(1)).strip(), "venue": "f", "status": "", "note": "",
            "url": VENUES["f"]["base"] + href,
        })
    return out


def keep(ev):
    """Filtrer ikke-koncerter fra og sæt faste notater."""
    d = datetime.date.fromisoformat(ev["date"])
    if not (TODAY <= d <= END):
        return False
    name = ev["artist"]
    if ev["venue"] == "v":
        if re.search(r"wrestling", name, re.I):
            return False
        if name.lower().startswith("next gen"):
            ev["note"] = "Tjek type: ikke angivet på siden"
    if ev["venue"] == "m":
        tags = set(ev.pop("_tags", []))
        if not (tags & {"pop-rock", "klassisk", "jazz"}) and not re.search(r"koncert", name, re.I):
            return False
        if name.lower().startswith("vampyren"):
            ev["note"] = "Tjek type: klassisk på siden"
    if ev["venue"] == "t" and name.lower().startswith("trolds magiske"):
        ev["note"] = "Tjek type: ser ud til at være en forestilling"
    if ev["venue"] == "f":
        if not re.search(
            r"Xperience|Koppel|Bootleg|Policeman|Kvinde Min|MammaMia|1991|Krøller|HIGH KINGS|Copenhagen Drummers|Nytårskoncert|Forårskoncert|Bowie|Jazz",
            name, re.I,
        ):
            return False
    ev.pop("_tags", None)
    return True


PARSERS = {"t": parse_train, "v": parse_voxhall, "m": parse_musikhuset, "f": parse_friheden}


SOLD_PATTERNS = [
    re.compile(r">\s*Udsolgt\s*<"),           # knap på koncertsiden (TRAIN)
    re.compile(r"Koncerten er udsolgt", re.I),  # besked på koncertsiden (TRAIN)
]


OG_IMAGE = re.compile(r'<meta[^>]+property="og:image"[^>]+content="([^"]+)"|<meta[^>]+content="([^"]+)"[^>]+property="og:image"')


def enrich_details(events):
    """Hent hver koncerts egen side for udsolgt og billede (og:image).
    Friheden springes over for billede, fordi deres og:image er et generelt billede for stedet.
    Fejl på én side stopper ikke de andre."""
    for e in events:
        if not e["url"]:
            continue
        try:
            page = fetch(e["url"])
        except Exception:
            continue
        if not e["status"] and any(p.search(page) for p in SOLD_PATTERNS):
            e["status"] = "Udsolgt"
        if e["venue"] != "f":
            m = OG_IMAGE.search(page)
            if m:
                e["image"] = html.unescape(m.group(1) or m.group(2))
        time.sleep(0.3)
    return events


def fetch_and_parse(key, parse, attempts=4):
    """Musikhuset har set svar uden kalenderdata (en anden side-variant, sandsynligvis fra cache).
    Prøv igen med cache-bypass før det tæller som fejl; ved fejl beholdes sidste kendte data."""
    for n in range(attempts):
        url = f"{SOURCE_PAGES[key]}?v={int(time.time())}{n}"
        found = [e for e in parse(fetch(url)) if keep(e)]
        if found:
            return enrich_details(found)
        if n < attempts - 1:
            time.sleep(10)
    raise RuntimeError("0 koncerter fundet efter flere forsøg — siden kan have ændret sig")


def load_previous():
    if not OUT.exists():
        return {"events": [], "venues": {}}
    try:
        return json.loads(OUT.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return {"events": [], "venues": {}}


def main():
    prev = load_previous()
    prev_by_venue = {k: [e for e in prev.get("events", []) if e["venue"] == k] for k in VENUES}
    status = {}
    events = []
    for key, parse in PARSERS.items():
        try:
            found = fetch_and_parse(key, parse)
            events.extend(found)
            status[key] = {"ok": True, "count": len(found), "hentet": TODAY.isoformat()}
        except Exception as exc:  # ét sted må ikke slette de andre
            kept = [e for e in prev_by_venue[key] if e["date"] >= TODAY.isoformat()]
            events.extend(kept)
            status[key] = {"ok": False, "fejl": str(exc)[:200], "beholdt": len(kept)}
            print(f"[{VENUES[key]['name']}] fejl: {exc}", file=sys.stderr)

    events.sort(key=lambda e: (e["date"], e["artist"]))
    data = {
        "opdateret": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "vindue": [TODAY.isoformat(), END.isoformat()],
        "kilder": {k: SOURCE_PAGES[k] for k in SOURCE_PAGES},
        "status": status,
        "events": events,
    }
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for k, s in status.items():
        print(f"{VENUES[k]['name']}: {'ok' if s['ok'] else 'FEJL'} {s.get('count', s.get('beholdt'))}")
    print(f"I alt: {len(events)} koncerter -> {OUT.name}")


if __name__ == "__main__":
    main()
