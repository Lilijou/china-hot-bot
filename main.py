import requests
import feedparser
from datetime import datetime

# =========================
# DATA SOURCES
# =========================

def fetch_hn():
    try:
        ids = requests.get(
            "https://hacker-news.firebaseio.com/v0/topstories.json",
            timeout=10
        ).json()

        items = []

        for i in ids[:20]:
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

        return items

    except:
        return []


def fetch_rss():

    feeds = [
        ("https://www.reuters.com/rssFeed/businessNews", "Reuters"),
        ("https://feeds.bbci.co.uk/news/rss.xml", "BBC"),
        ("https://cointelegraph.com/rss", "CoinTelegraph"),
        ("https://techcrunch.com/feed/", "TechCrunch")
    ]

    items = []

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
# SIGNAL DETECTOR CORE
# =========================

def detect_signal(item):

    t = (item.get("title") or "").lower()
    text = (item.get("text") or "").lower()

    score = 0
    tags = []

    # 💰 money signal
    if any(k in t for k in ["fed", "rate", "inflation", "btc", "bitcoin", "stock", "market"]):
        score += 4
        tags.append("MARKET_SIGNAL")

    # 🧠 AI signal
    if any(k in t for k in ["openai", "gpt", "google", "meta", "ai", "model"]):
        score += 4
        tags.append("AI_SIGNAL")

    # 🌍 macro signal
    if any(k in t for k in ["war", "china", "us", "policy", "sec", "regulation"]):
        score += 3
        tags.append("MACRO_SIGNAL")

    # 🚨 strong wording detection
    if any(k in t for k in ["ban", "launch", "collapse", "crash", "breakthrough"]):
        score += 2
        tags.append("EVENT_SPIKE")

    # 🧊 noise filter
    if any(k in t for k in ["sports", "celebrity", "movie"]):
        score -= 5
        tags.append("NOISE")

    return score, tags


# =========================
# FILTER SIGNALS
# =========================

def filter_signals(items):

    signals = []

    for i in items:
        score, tags = detect_signal(i)

        if score >= 5:
            i["score"] = score
            i["tags"] = tags
            signals.append(i)

    return sorted(signals, key=lambda x: x["score"], reverse=True)


# =========================
# OUTPUT
# =========================

def build(signals):

    date = datetime.now().strftime("%Y-%m-%d")

    if not signals:
        return f"""
🌍 SIGNAL DETECTION v1
📅 {date}

⚠️ No strong signals detected today
"""

    text = f"""
🚨 SIGNAL DETECTION v1
📅 {date}

========================
"""

    for i, s in enumerate(signals, 1):

        text += f"""
【{i}】
📌 {s['title']}
🏷 {s['source']}
⭐ Signal Score: {s['score']}
🏷 Tags: {', '.join(s.get('tags', []))}

🧠 Context:
{s.get('text','')[:400]}

------------------------
"""

    return text


# =========================
# MAIN
# =========================

def main():

    items = []

    items += fetch_hn()
    items += fetch_rss()

    signals = filter_signals(items)

    report = build(signals)

    filename = f"signal_report_{datetime.now().strftime('%Y-%m-%d')}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(report)

    print("DONE SIGNAL SYSTEM:", filename)


if __name__ == "__main__":
    main()
