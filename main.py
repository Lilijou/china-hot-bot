import requests
import feedparser
from datetime import datetime


# =========================
# SAFE REQUEST
# =========================

def get_json(url, headers=None):
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code != 200:
            return None
        if not r.text.strip():
            return None
        return r.json()
    except:
        return None


# =========================
# REDDIT (PRIMARY SOURCE)
# =========================

def fetch_reddit():
    url = "https://www.reddit.com/r/worldnews/hot.json?limit=10"
    headers = {"User-Agent": "Mozilla/5.0"}

    data = get_json(url, headers)
    if not data:
        return []

    items = []

    for post in data["data"]["children"]:
        d = post["data"]

        items.append({
            "title": d.get("title"),
            "source": "Reddit",
            "url": "https://reddit.com" + d.get("permalink"),
            "text": d.get("selftext", ""),
            "score": d.get("ups", 0)
        })

    return items


# =========================
# HACKER NEWS (PRIMARY SOURCE)
# =========================

def fetch_hn():
    ids = get_json("https://hacker-news.firebaseio.com/v0/topstories.json")
    if not ids:
        return []

    items = []

    for i in ids[:10]:
        item = get_json(
            f"https://hacker-news.firebaseio.com/v0/item/{i}.json"
        )

        if not item:
            continue

        items.append({
            "title": item.get("title"),
            "source": "HackerNews",
            "url": item.get("url"),
            "text": item.get("text", ""),
            "score": item.get("score", 0)
        })

    return items


# =========================
# STOCKS (Yahoo Finance Lite)
# =========================

def fetch_market():
    url = "https://query1.finance.yahoo.com/v7/finance/quote?symbols=SPY,BTC-USD,QQQ"
    data = get_json(url)

    items = []

    if data and "quoteResponse" in data:
        for q in data["quoteResponse"]["result"]:
            items.append({
                "title": f"{q.get('symbol')} price update",
                "source": "Market",
                "url": "",
                "text": f"Price: {q.get('regularMarketPrice')}",
                "score": q.get("regularMarketChangePercent", 0)
            })

    return items


# =========================
# RSS NEWS (PRIMARY GLOBAL NEWS)
# =========================

def fetch_rss():
    feeds = [
        ("https://feeds.bbci.co.uk/news/rss.xml", "BBC"),
        ("https://www.reutersagency.com/feed/?best-topics=business-finance", "Reuters")
    ]

    items = []

    for url, source in feeds:
        feed = feedparser.parse(url)

        for e in feed.entries[:5]:
            items.append({
                "title": e.title,
                "source": source,
                "url": e.link,
                "text": e.get("summary", ""),
                "score": 1
            })

    return items


# =========================
# CLASSIFY
# =========================

def classify(item):
    t = item["title"].lower()

    if any(k in t for k in ["bitcoin", "btc", "crypto"]):
        return "Crypto"

    if any(k in t for k in ["stock", "market", "spy", "qqq"]):
        return "Stocks"

    if any(k in t for k in ["ai", "openai", "google", "meta"]):
        return "AI"

    return "Tech"


# =========================
# REPORT
# =========================

def build(items):

    date = datetime.now().strftime("%Y-%m-%d")

    report = f"""
🌍 GLOBAL INFO RADAR v1
📅 {date}

========================
"""

    for i, item in enumerate(items, 1):

        report += f"""
【{i}】
📌 {item['title']}
🏷 分类：{classify(item)}
📡 来源：{item['source']}
🔗 链接：{item['url']}

🧠 原文信息：
{item['text'][:300] if item['text'] else '无正文'}

------------------------
"""

    return report


# =========================
# MAIN
# =========================

def main():

    items = []

    items += fetch_reddit()
    items += fetch_hn()
    items += fetch_rss()
    items += fetch_market()

    # 去空
    items = [i for i in items if i.get("title")]

    report = build(items)

    filename = f"info_radar_{datetime.now().strftime('%Y-%m-%d')}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(report)

    print("DONE:", filename)


if __name__ == "__main__":
    main()
