import os
import requests
import feedparser
from datetime import datetime

# =========================
# DATA SOURCES
# =========================

def fetch_reddit():
    url = "https://www.reddit.com/r/worldnews/hot.json?limit=15"
    headers = {"User-Agent": "Mozilla/5.0"}

    r = requests.get(url, headers=headers, timeout=10).json()

    items = []
    for p in r["data"]["children"]:
        d = p["data"]
        items.append({
            "title": d["title"],
            "source": "Reddit",
            "text": d.get("selftext", "")
        })

    return items


def fetch_hn():
    ids = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json").json()

    items = []

    for i in ids[:15]:
        item = requests.get(
            f"https://hacker-news.firebaseio.com/v0/item/{i}.json"
        ).json()

        if item:
            items.append({
                "title": item.get("title", ""),
                "source": "HackerNews",
                "text": item.get("text", "")
            })

    return items


def fetch_rss():
    feeds = [
        ("https://feeds.bbci.co.uk/news/rss.xml", "BBC"),
        ("https://techcrunch.com/feed/", "TechCrunch")
    ]

    items = []

    for url, source in feeds:
        feed = feedparser.parse(url)

        for e in feed.entries[:10]:
            items.append({
                "title": e.title,
                "source": source,
                "text": e.get("summary", "")
            })

    return items


# =========================
# IMPACT SCORE ENGINE
# =========================

def score(item):
    t = item["title"].lower()
    text = (item.get("text") or "").lower()

    s = 0

    # 💰 钱相关
    if any(k in t for k in ["bitcoin", "btc", "stock", "market", "fed", "inflation"]):
        s += 4

    # 🧠 AI / Tech
    if any(k in t for k in ["ai", "openai", "google", "meta", "gpu", "chip"]):
        s += 3

    # 🌍 geopolitics
    if any(k in t for k in ["war", "china", "us", "ukraine", "policy", "government"]):
        s += 2

    # 🧊 noise penalty
    if any(k in t for k in ["celebrity", "movie", "sports", "game"]):
        s -= 5

    # 有正文加分
    if len(text) > 200:
        s += 1

    return s


# =========================
# FILTER
# =========================

def filter_items(items):
    scored = []

    for i in items:
        i["score"] = score(i)
        if i["score"] >= 6:
            scored.append(i)

    return sorted(scored, key=lambda x: x["score"], reverse=True)


# =========================
# OUTPUT
# =========================

def build(items):

    date = datetime.now().strftime("%Y-%m-%d")

    text = f"""
🌍 IMPACT NEWS RADAR
📅 {date}

========================
"""

    for i, item in enumerate(items, 1):

        text += f"""
【{i}】
📌 {item['title']}
🏷 来源：{item['source']}
⭐ Impact Score：{item['score']}

🧠 简要说明：
{item.get('text','')[:300]}

------------------------
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

    filtered = filter_items(items)

    report = build(filtered)

    filename = f"impact_news_{datetime.now().strftime('%Y-%m-%d')}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(report)

    print("DONE IMPACT SYSTEM:", filename)


if __name__ == "__main__":
    main()
