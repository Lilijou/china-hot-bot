import os
import requests
import feedparser
from datetime import datetime

TG_TOKEN = os.getenv("TG_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")


# =========================
# SAFE FETCH (核心稳定)
# =========================

def safe_get_json(url, headers=None):
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None


def fetch_hackernews():
    data = safe_get_json("https://hacker-news.firebaseio.com/v0/topstories.json")
    if not data:
        return []

    items = []
    for i in data[:10]:
        item = safe_get_json(
            f"https://hacker-news.firebaseio.com/v0/item/{i}.json"
        )
        if item and "title" in item:
            items.append({
                "title": item["title"],
                "source": "HackerNews",
                "url": item.get("url", "")
            })
    return items


def fetch_reddit():
    url = "https://www.reddit.com/r/worldnews/hot.json?limit=10"
    headers = {"User-Agent": "Mozilla/5.0"}

    data = safe_get_json(url, headers=headers)
    if not data:
        return []

    items = []
    try:
        for post in data["data"]["children"]:
            d = post["data"]
            items.append({
                "title": d["title"],
                "source": "Reddit",
                "url": "https://reddit.com" + d["permalink"]
            })
    except:
        pass

    return items


# =========================
# RSS（核心稳定源）
# =========================

def fetch_rss(url, source):
    try:
        feed = feedparser.parse(url)
        items = []

        for entry in feed.entries[:10]:
            if hasattr(entry, "title"):
                items.append({
                    "title": entry.title,
                    "source": source,
                    "url": entry.link if hasattr(entry, "link") else ""
                })

        return items
    except:
        return []


# =========================
# 去重
# =========================

def deduplicate(items):
    seen = set()
    result = []

    for i in items:
        key = i["title"]
        if key not in seen:
            seen.add(key)
            result.append(i)

    return result


# =========================
# 报告生成
# =========================

def build_report(items):
    date = datetime.now().strftime("%Y-%m-%d")

    text = f"🌍 GLOBAL HOT DAILY REPORT\n📅 {date}\n\n"

    for i, item in enumerate(items[:30], 1):
        text += f"{i}. {item['title']}\n"
        text += f"来源: {item['source']}\n\n"

    return text


# =========================
# 保存文件
# =========================

def save_file(content):
    filename = f"global_hot_{datetime.now().strftime('%Y-%m-%d')}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    return filename


# =========================
# Telegram
# =========================

def send_telegram(msg):
    if not TG_TOKEN or not TG_CHAT_ID:
        print("No Telegram config")
        return

    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    try:
        requests.post(url, data={
            "chat_id": TG_CHAT_ID,
            "text": msg[:4000]
        })
    except:
        pass


# =========================
# MAIN
# =========================

def main():

    items = []

    # ===== 主流稳定源 =====
    items += fetch_hackernews()
    items += fetch_reddit()

    # ===== RSS兜底（关键）=====
    items += fetch_rss("https://news.google.com/rss", "GoogleNews")
    items += fetch_rss("https://feeds.bbci.co.uk/news/rss.xml", "BBC")
    items += fetch_rss("https://techcrunch.com/feed/", "TechCrunch")

    # ===== 清洗 =====
    items = deduplicate(items)

    # ===== 报告 =====
    report = build_report(items)
    filename = save_file(report)

    # ===== 输出 =====
    send_telegram(report)

    print("DONE:", filename)


if __name__ == "__main__":
    main()
