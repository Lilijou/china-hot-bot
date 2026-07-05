import os
import requests
import feedparser
from datetime import datetime

TG_TOKEN = os.getenv("TG_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")


# =========================
# 1. HOT FEED
# =========================

def fetch_hn():
    url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    ids = requests.get(url, timeout=10).json()[:10]

    items = []
    for i in ids:
        item = requests.get(
            f"https://hacker-news.firebaseio.com/v0/item/{i}.json"
        ).json()

        if item and "title" in item:
            items.append({
                "title": item["title"],
                "source": "HackerNews"
            })
    return items


def fetch_reddit():
    url = "https://www.reddit.com/r/worldnews/hot.json?limit=10"
    headers = {"User-Agent": "Mozilla/5.0"}

    data = requests.get(url, headers=headers, timeout=10).json()

    items = []
    for p in data["data"]["children"]:
        d = p["data"]
        items.append({
            "title": d["title"],
            "source": "Reddit"
        })

    return items


def fetch_rss():
    feeds = [
        ("https://news.google.com/rss", "GoogleNews"),
        ("https://feeds.bbci.co.uk/news/rss.xml", "BBC"),
        ("https://techcrunch.com/feed/", "TechCrunch")
    ]

    items = []

    for url, source in feeds:
        feed = feedparser.parse(url)
        for e in feed.entries[:5]:
            items.append({
                "title": e.title,
                "source": source
            })

    return items


# =========================
# 2. CONTENT ENGINE
# =========================

def generate_content(title, source):
    """
    核心：爆款内容生成器
    """

    # 简单但有效的“爆点结构”
    hook = f"🔥 {title}"

    angle = f"""
📌 来源：{source}

📌 为什么这条重要：
这类信息往往代表行业趋势 / 社会议题 / 技术变化。

📌 可传播角度：
👉 普通人怎么看这件事？
👉 对未来有什么影响？

📌 抖音标题建议：
{title[:30]}...

📌 15秒口播脚本：
这条新闻其实很关键……
很多人还没意识到它的影响……
"""

    return hook + "\n" + angle


# =========================
# 3. BUILD REPORT
# =========================

def build_report(items):
    date = datetime.now().strftime("%Y-%m-%d")

    text = f"🌍 GLOBAL VIRAL CONTENT ENGINE\n📅 {date}\n\n"

    for i, item in enumerate(items[:20], 1):
        content = generate_content(item["title"], item["source"])

        text += f"\n【{i}】\n{content}\n\n"

    return text


# =========================
# 4. SAVE
# =========================

def save_file(text):
    name = f"viral_content_{datetime.now().strftime('%Y-%m-%d')}.txt"
    with open(name, "w", encoding="utf-8") as f:
        f.write(text)
    return name


# =========================
# 5. TELEGRAM
# =========================

def send_telegram(text):
    if not TG_TOKEN or not TG_CHAT_ID:
        return

    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": TG_CHAT_ID,
        "text": text[:4000]
    })


# =========================
# MAIN
# =========================

def main():
    items = []

    items += fetch_hn()
    items += fetch_reddit()
    items += fetch_rss()

    # 去重（简单版）
    seen = set()
    unique = []
    for i in items:
        if i["title"] not in seen:
            seen.add(i["title"])
            unique.append(i)

    report = build_report(unique)

    save_file(report)
    send_telegram(report)

    print("V11 DONE")


if __name__ == "__main__":
    main()
