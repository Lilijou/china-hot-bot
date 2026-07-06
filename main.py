import requests
import feedparser
from datetime import datetime


# =========================
# DATA SOURCES (with URLs)
# =========================

def fetch_reddit():

    url = "https://www.reddit.com/r/worldnews/hot.json?limit=10"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        data = requests.get(url, headers=headers, timeout=10).json()

        items = []

        for p in data["data"]["children"]:
            d = p["data"]

            items.append({
                "title": d.get("title"),
                "source": "Reddit",
                "url": "https://reddit.com" + d.get("permalink"),
                "text": d.get("selftext", "")
            })

        return items

    except:
        return []


def fetch_hn():

    items = []

    try:
        ids = requests.get(
            "https://hacker-news.firebaseio.com/v0/topstories.json",
            timeout=10
        ).json()

        for i in ids[:15]:

            item = requests.get(
                f"https://hacker-news.firebaseio.com/v0/item/{i}.json",
                timeout=10
            ).json()

            if not item:
                continue

            items.append({
                "title": item.get("title"),
                "source": "HackerNews",
                "url": item.get("url", ""),
                "text": item.get("text", "")
            })

        return items

    except:
        return []


def fetch_rss():

    feeds = [
        ("https://feeds.bbci.co.uk/news/rss.xml", "BBC"),
        ("https://techcrunch.com/feed/", "TechCrunch"),
        ("https://cointelegraph.com/rss", "CoinTelegraph")
    ]

    items = []

    for url, source in feeds:

        try:
            feed = feedparser.parse(url)

            for e in feed.entries[:10]:

                items.append({
                    "title": e.title,
                    "source": source,
                    "url": e.link,
                    "text": e.get("summary", "")
                })

        except:
            continue

    return items


# =========================
# SIGNAL DETECTION (REAL + SOURCE BOUND)
# =========================

def detect(item):

    t = (item["title"] or "").lower()
    text = (item.get("text") or "").lower()

    score = 0
    tags = []

    # 💰 market signal
    if any(k in t for k in ["bitcoin", "btc", "market", "fed", "inflation", "stock"]):
        score += 4
        tags.append("MARKET")

    # 🧠 AI signal
    if any(k in t for k in ["ai", "openai", "gpt", "google", "meta", "model"]):
        score += 4
        tags.append("AI")

    # 🌍 macro
    if any(k in t for k in ["war", "china", "us", "policy", "regulation"]):
        score += 3
        tags.append("MACRO")

    # 🚨 strong event
    if any(k in t for k in ["launch", "ban", "crash", "breakthrough", "record"]):
        score += 2
        tags.append("EVENT")

    return score, tags


# =========================
# FILTER SIGNALS
# =========================

def build_signals(items):

    signals = []

    for i in items:

        score, tags = detect(i)

        if score >= 5:

            signals.append({
                "title": i["title"],
                "source": i["source"],
                "url": i["url"],
                "text": i.get("text", ""),
                "score": score,
                "tags": tags
            })

    return sorted(signals, key=lambda x: x["score"], reverse=True)


# =========================
# OUTPUT ENGINE (核心升级)
# =========================

def build_report(signals):

    date = datetime.now().strftime("%Y-%m-%d")

    if not signals:
        return f"""
🌍 SOURCE-BOUND SIGNAL v1
📅 {date}

⚠️ No valid signals found today
"""

    text = f"""
🌍 SOURCE-BOUND SIGNAL v1
📅 {date}

====================================
"""

    for i, s in enumerate(signals, 1):

        text += f"""
【{i}】
📌 TITLE: {s['title']}
🏷 SOURCE: {s['source']}
🔗 URL: {s['url']}
⭐ SCORE: {s['score']}
🏷 TAGS: {', '.join(s['tags'])}

🧠 EXTRACT:
{s['text'][:300]}

------------------------------------
"""

    return text


# =========================
# MAIN
# =========================

def main():

    items = []

    items += fetch_reddit()
    items += fetch_hn()
    items += fetch_rss()

    signals = build_signals(items)

    report = build_report(signals)

    filename = f"source_bound_signal_{datetime.now().strftime('%Y-%m-%d')}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(report)

    print("DONE SOURCE-BOUND v1:", filename)


if __name__ == "__main__":
    main()
