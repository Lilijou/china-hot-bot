import requests
import feedparser
from datetime import datetime


# =========================
# DATA SOURCE
# =========================

def fetch_sources():

    items = []

    # HN
    try:
        hn = requests.get(
            "https://hacker-news.firebaseio.com/v0/topstories.json",
            timeout=10
        ).json()

        for i in hn[:15]:
            item = requests.get(
                f"https://hacker-news.firebaseio.com/v0/item/{i}.json",
                timeout=10
            ).json()

            if item:
                items.append({
                    "title": item.get("title", ""),
                    "text": item.get("text", ""),
                    "time": item.get("time", 0),
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
                    "time": 0,
                    "source": source
                })
        except:
            continue

    return items


# =========================
# TREND DETECTION CORE
# =========================

def detect_trend(items):

    trends = {
        "AI": [],
        "MARKET": [],
        "CRYPTO": [],
        "MACRO": []
    }

    for i in items:

        t = (i["title"] + " " + i.get("text", "")).lower()

        # AI trend
        if any(k in t for k in ["ai", "openai", "gpt", "model", "google", "meta"]):
            trends["AI"].append(i)

        # market trend
        if any(k in t for k in ["stock", "market", "fed", "inflation", "rate"]):
            trends["MARKET"].append(i)

        # crypto trend
        if any(k in t for k in ["bitcoin", "btc", "crypto", "eth"]):
            trends["CRYPTO"].append(i)

        # macro
        if any(k in t for k in ["war", "china", "us", "policy", "regulation"]):
            trends["MACRO"].append(i)

    return trends


# =========================
# TREND SCORING (核心升级)
# =========================

def trend_score(group):

    if len(group) >= 5:
        return 10   # 强趋势
    elif len(group) >= 3:
        return 7    # 中趋势
    elif len(group) >= 2:
        return 5    # 弱趋势
    else:
        return 2    # 噪音


# =========================
# BUILD SIGNAL REPORT
# =========================

def build(trends):

    date = datetime.now().strftime("%Y-%m-%d")

    report = f"""
🚨 SIGNAL DETECTION v2 (TREND SYSTEM)
📅 {date}

========================
"""

    for k, v in trends.items():

        score = trend_score(v)

        report += f"""
【{k} TREND】
🔥 Trend Score: {score}
📊 Event Count: {len(v)}

"""

        for i in v[:5]:
            report += f"- {i['title']}\n"

        report += "\n------------------------\n"

    return report


# =========================
# MAIN
# =========================

def main():

    items = fetch_sources()

    trends = detect_trend(items)

    report = build(trends)

    filename = f"signal_v2_{datetime.now().strftime('%Y-%m-%d')}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(report)

    print("DONE SIGNAL V2:", filename)


if __name__ == "__main__":
    main()
