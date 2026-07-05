import requests
from datetime import datetime

# ========== CONFIG ==========
TG_TOKEN = None
TG_CHAT_ID = None


def load_secrets():
    import os
    global TG_TOKEN, TG_CHAT_ID
    TG_TOKEN = os.getenv("TG_TOKEN")
    TG_CHAT_ID = os.getenv("TG_CHAT_ID")


# ========== DATA SOURCES (海外稳定源) ==========
def fetch_hackernews():
    url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    ids = requests.get(url, timeout=10).json()[:10]

    items = []
    for i in ids:
        item = requests.get(
            f"https://hacker-news.firebaseio.com/v0/item/{i}.json",
            timeout=10
        ).json()

        if item and "title" in item:
            items.append({
                "title": item["title"],
                "source": "HackerNews",
                "url": item.get("url", "")
            })
    return items


def fetch_reddit_worldnews():
    url = "https://www.reddit.com/r/worldnews/hot.json?limit=10"
    headers = {"User-Agent": "Mozilla/5.0"}

    data = requests.get(url, headers=headers, timeout=10).json()

    items = []
    for post in data["data"]["children"]:
        d = post["data"]
        items.append({
            "title": d["title"],
            "source": "Reddit",
            "url": "https://reddit.com" + d["permalink"]
        })

    return items


def fetch_producthunt():
    url = "https://www.producthunt.com/feed"
    headers = {"User-Agent": "Mozilla/5.0"}

    text = requests.get(url, headers=headers, timeout=10).text

    # 简化抓取（稳定优先，不做复杂解析）
    lines = [l for l in text.split("\n") if "<title>" in l][:10]

    items = []
    for l in lines:
        title = l.replace("<title>", "").replace("</title>", "").strip()
        if "Product Hunt" not in title:
            items.append({
                "title": title,
                "source": "ProductHunt",
                "url": ""
            })

    return items


# ========== FORMAT ==========
def build_report(items):
    date = datetime.now().strftime("%Y-%m-%d")

    text = f"🌍 GLOBAL HOT DAILY REPORT\n📅 {date}\n\n"

    for i, item in enumerate(items[:30], 1):
        text += f"{i}. {item['title']}\n"
        text += f"来源: {item['source']}\n\n"

    return text


# ========== OUTPUT ==========
def save_file(content):
    filename = f"global_hot_{datetime.now().strftime('%Y-%m-%d')}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    return filename


def send_telegram(msg):
    if not TG_TOKEN or not TG_CHAT_ID:
        print("Telegram not configured")
        return

    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": TG_CHAT_ID,
        "text": msg[:4000]
    })


# ========== MAIN ==========
def main():
    load_secrets()

    items = []
    try:
        items += fetch_hackernews()
        items += fetch_reddit_worldnews()
        items += fetch_producthunt()
    except Exception as e:
        items = [{"title": f"数据源失败: {str(e)}", "source": "system", "url": ""}]

    report = build_report(items)
    filename = save_file(report)

    send_telegram(report)

    print("REPORT GENERATED:", filename)


if __name__ == "__main__":
    main()
