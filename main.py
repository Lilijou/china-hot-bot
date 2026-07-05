import requests
import feedparser
from datetime import datetime


# =========================
# SAFE REQUEST LAYER
# =========================

def safe_get_json(url, headers=None):
    try:
        r = requests.get(url, headers=headers, timeout=10)

        if r.status_code != 200:
            return None

        if not r.text.strip():
            return None

        # 🚨 防止 HTML 被当 JSON
        if "html" in r.text[:50].lower():
            return None

        return r.json()

    except:
        return None


# =========================
# REDDIT (ISOLATED)
# =========================

def fetch_reddit():
    url = "https://www.reddit.com/r/worldnews/hot.json?limit=10"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    data = safe_get_json(url, headers)

    if not data:
        return []

    items = []

    try:
        for p in data["data"]["children"]:
            d = p["data"]

            items.append({
                "title": d.get("title", ""),
                "source": "Reddit",
                "text": d.get("selftext", "")
            })

    except:
        return []

    return items


# =========================
# HACKER NEWS (ISOLATED)
# =========================

def fetch_hn():
    data = safe_get_json(
        "https://hacker-news.firebaseio.com/v0/topstories.json"
    )

    if not data:
        return []

    items = []

    for i in data[:10]:
        item = safe_get_json(
            f"https://hacker-news.firebaseio.com/v0/item/{i}.json"
        )

        if not item:
            continue

        items.append({
            "title": item.get("title", ""),
            "source": "HackerNews",
            "text": item.get("text", "")
        })

    return items


# =========================
# RSS (ISOLATED)
# =========================

def fetch_rss():
    feeds = [
        ("https://feeds.bbci.co.uk/news/rss.xml", "BBC"),
        ("https://techcrunch.com/feed/", "TechCrunch")
    ]

    items = []

    for url, source in feeds:
        try:
            feed = feedparser.parse(url)

            for e in feed.entries[:5]:
                items.append({
                    "title": e.title,
                    "source": source,
                    "text": e.get("summary", "")
                })

        except:
            continue

    return items


# =========================
# SAFETY FILTER (NO CRASH)
# =========================

def safe_collect():
    items = []

    try:
        items += fetch_reddit()
    except:
        pass

    try:
        items += fetch_hn()
    except:
        pass

    try:
        items += fetch_rss()
    except:
        pass

    return items


# =========================
# IMPACT FILTER (light version)
# =========================

def score(item):

    t = (item.get("title") or "").lower()

    s = 0

    # 💰 money impact
    if any(k in t for k in ["bitcoin", "btc", "stock", "market", "fed", "inflation"]):
        s += 4

    # 🧠 AI / tech
    if any(k in t for k in ["ai", "openai", "google", "meta", "gpu", "chip"]):
        s += 3

    # 🌍 geopolitics
    if any(k in t for k in ["war", "china", "us", "ukraine", "policy"]):
        s += 2

    # noise filter
    if any(k in t for k in ["sports", "celebrity", "movie"]):
        s -= 5

    return s


def filter_items(items):

    scored = []

    for i in items:
        i["score"] = score(i)
        if i["score"] >= 4:   # ⚠️ 降低门槛（保证不空）
            scored.append(i)

    return sorted(scored, key=lambda x: x["score"], reverse=True)


# =========================
# REPORT BUILDER
# =========================

def build(items):

    date = datetime.now().strftime("%Y-%m-%d")

    if not items:
        return f"""
🌍 STABLE INFO RADAR
📅 {date}

⚠️ 当前没有高质量信息
（数据源可能临时不可用）
"""

    text = f"""
🌍 STABLE INFO RADAR v1
📅 {date}

========================
"""

    for i, item in enumerate(items[:20], 1):

        text += f"""
【{i}】
📌 {item.get('title')}
🏷 来源：{item.get('source')}
⭐ Score：{item.get('score')}

🧠 内容：
{(item.get('text') or '')[:300]}

------------------------
"""

    return text


# =========================
# MAIN
# =========================

def main():

    items = safe_collect()

    filtered = filter_items(items)

    report = build(filtered)

    filename = f"stable_radar_{datetime.now().strftime('%Y-%m-%d')}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(report)

    print("DONE STABLE SYSTEM:", filename)


if __name__ == "__main__":
    main()
