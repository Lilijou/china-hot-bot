import requests
import feedparser
from datetime import datetime


# =========================
# DATA SOURCES
# =========================

def fetch_sources():

    items = []

    # HN
    try:
        hn = requests.get(
            "https://hacker-news.firebaseio.com/v0/topstories.json",
            timeout=10
        ).json()

        for i in hn[:20]:
            item = requests.get(
                f"https://hacker-news.firebaseio.com/v0/item/{i}.json",
                timeout=10
            ).json()

            if item:
                items.append({
                    "title": item.get("title", ""),
                    "text": item.get("text", ""),
                    "source": "HackerNews"
                })
    except:
        pass

    # RSS
    feeds = [
        ("https://feeds.bbci.co.uk/news/rss.xml", "BBC"),
        ("https://techcrunch.com/feed/", "TechCrunch"),
        ("https://cointelegraph.com/rss", "CoinTelegraph")
    ]

    for url, source in feeds:
        try:
            feed = feedparser.parse(url)

            for e in feed.entries[:10]:
                items.append({
                    "title": e.title,
                    "text": e.get("summary", ""),
                    "source": source
                })
        except:
            continue

    return items


# =========================
# SIGNAL GROUPING
# =========================

def group_signals(items):

    groups = {
        "AI": [],
        "MARKET": [],
        "CRYPTO": [],
        "MACRO": []
    }

    for i in items:

        t = (i["title"] + " " + i.get("text", "")).lower()

        if any(k in t for k in ["ai", "openai", "gpt", "model", "google", "meta"]):
            groups["AI"].append(i)

        if any(k in t for k in ["stock", "market", "fed", "inflation", "rate"]):
            groups["MARKET"].append(i)

        if any(k in t for k in ["bitcoin", "btc", "crypto", "eth"]):
            groups["CRYPTO"].append(i)

        if any(k in t for k in ["war", "china", "us", "policy", "regulation"]):
            groups["MACRO"].append(i)

    return groups


# =========================
# INTERPRETATION ENGINE（核心升级）
# =========================

def interpret(name, items):

    count = len(items)

    # === 1. trend strength ===
    if count >= 8:
        strength = "STRONG TREND 🚨"
    elif count >= 4:
        strength = "BUILDING TREND 📈"
    elif count >= 2:
        strength = "WEAK SIGNAL ⚠️"
    else:
        strength = "NOISE / ISOLATED 🧊"

    # === 2. interpretation logic ===
    if name == "AI":
        meaning = "AI industry is showing structural acceleration in model + agent adoption."
        impact = "Impacts: software jobs, automation, enterprise tooling."
    elif name == "MARKET":
        meaning = "Macro liquidity and rate expectations are shifting."
        impact = "Impacts: stocks, risk assets, investment sentiment."
    elif name == "CRYPTO":
        meaning = "Crypto is entering a renewed liquidity + regulatory phase."
        impact = "Impacts: BTC price cycles, institutional adoption."
    else:
        meaning = "Macro geopolitical pressure is changing global risk structure."
        impact = "Impacts: global markets, energy, risk sentiment."

    # === 3. action layer ===
    if count >= 4:
        action = "WATCH CLOSELY → possible regime shift"
    elif count >= 2:
        action = "MONITOR → early signal forming"
    else:
        action = "IGNORE → no actionable signal"

    return {
        "name": name,
        "strength": strength,
        "count": count,
        "meaning": meaning,
        "impact": impact,
        "action": action,
        "samples": items[:3]
    }


# =========================
# OUTPUT ENGINE
# =========================

def build_report(analysis):

    date = datetime.now().strftime("%Y-%m-%d")

    text = f"""
🚨 SIGNAL INTERPRETATION v3
📅 {date}

========================
"""

    for k, v in analysis.items():

        text += f"""
🔥 {k} SIGNAL
{v['strength']}
Event Count: {v['count']}

🧠 MEANING:
{v['meaning']}

💰 IMPACT:
{v['impact']}

🎯 ACTION:
{v['action']}

📌 Examples:
"""

        for s in v["samples"]:
            text += f"- {s['title']}\n"

        text += "\n------------------------\n"

    return text


# =========================
# MAIN
# =========================

def main():

    items = fetch_sources()

    groups = group_signals(items)

    analysis = {}

    for k, v in groups.items():
        analysis[k] = interpret(k, v)

    report = build_report(analysis)

    filename = f"signal_v3_{datetime.now().strftime('%Y-%m-%d')}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(report)

    print("DONE SIGNAL V3:", filename)


if __name__ == "__main__":
    main()
