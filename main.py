import os
import requests
import feedparser
from datetime import datetime

TG_TOKEN = os.getenv("TG_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")


# =========================
# SAFE REQUEST CORE
# =========================

def safe_get_json(url, headers=None):
    try:
        r = requests.get(url, headers=headers, timeout=10)

        if r.status_code != 200:
            print(f"[WARN] HTTP {r.status_code} -> {url}")
            return None

        # 防止 HTML / 空内容炸 json
        if not r.text or r.text.strip() == "":
            print(f"[WARN] EMPTY RESPONSE -> {url}")
            return None

        return r.json()

    except Exception as e:
        print(f"[ERROR] JSON FAIL -> {url} | {e}")
        return None


# =========================
# 1. HACKER NEWS
# =========================

def fetch_hn():
    url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    ids = safe_get_json(url)

    if not ids:
        return []

    items = []
    for i in ids[:10]:
        item = safe_get_json(
            f"https://hacker-news.firebaseio.com/v0/item/{i}.json"
        )

        if item and "title" in item:
            items.append({
                "title": item["title"],
                "source": "HackerNews"
            })

    return items


# =========================
# 2. REDDIT（关键修复点）
# =========================

def fetch_reddit():
    url = "https://www.reddit.com/r/worldnews/hot.json?limit=10"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    data = safe_get_json(url, headers)

    if not data:
        return []

    items = []
    try:
        for p in data["data"]["children"]:
            d = p["data"]
            items.append({
                "title": d["title"],
                "source": "Reddit"
            })
    except:
        pass

    return items


# =========================
# 3. RSS（容错版）
# =========================

def fetch_rss():
    feeds = [
        ("https://feeds.bbci.co.uk/news/rss.xml", "BBC"),
        ("https://techcrunch.com/feed/", "TechCrunch"),
    ]

    items = []

    for url, source in feeds:
        try:
            feed = feedparser.parse(url)

            for e in feed.entries[:5]:
                if hasattr(e, "title"):
                    items.append({
                        "title": e.title,
                        "source": source
                    })
        except:
            continue

    return items


# =========================
# 4. CONTENT ENGINE（不变）
# =========================

def generate_content(title, source):

    return f"""
🔥 {title}

📌 来源：{source}

📌 爆点解读：
这类信息通常代表趋势变化 / 行业信号 / 技术拐点

📌 内容角度：
- 普通人怎么看？
- 对未来有什么影响？

📌 抖音标题：
{title[:30]}...

📌 15秒口播：
这条信息其实很关键……
很多人还没意识到它的影响……
"""


# =========================
# 5. REPORT
# =========================

def build_report(items):
    date = datetime.now().strftime("%Y-%m-%d")

    text = f"🌍 GLOBAL HOT REPORT (V11.1)\n📅 {date}\n\n"

    if not items:
        return text + "\n⚠️ 无数据（所有源失败，但系统已稳定运行）"

    for i, item in enumerate(items[:20], 1):
        text += f"\n【{i}】{generate_content(item['title'], item['source'])}\n"

    return text


# =========================
# 6. SAVE
# =========================

def save_file(text):
    name = f"hot_report_{datetime.now().strftime('%Y-%m-%d')}.txt"
    with open(name, "w", encoding="utf-8") as f:
        f.write(text)
    return name


# =========================
# 7. TELEGRAM
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

    print("[INFO] fetching hn...")
    items += fetch_hn()

    print("[INFO] fetching reddit...")
    items += fetch_reddit()

    print("[INFO] fetching rss...")
    items += fetch_rss()

    # 去重
    seen = set()
    unique = []

    for i in items:
        if i["title"] not in seen:
            seen.add(i["title"])
            unique.append(i)

    report = build_report(unique)

    save_file(report)
    send_telegram(report)

    print("DONE V11.1")


if __name__ == "__main__":
    main()
