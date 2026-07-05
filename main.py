import requests
from datetime import datetime

# ---------- 安全请求封装 ----------
def safe_get_json(url, headers=None):
    try:
        r = requests.get(url, headers=headers, timeout=10)

        if r.status_code != 200:
            return None

        if not r.text or len(r.text.strip()) == 0:
            return None

        return r.json()

    except Exception:
        return None


# ---------- HackerNews ----------
def fetch_hn():
    url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    ids = safe_get_json(url)

    if not ids:
        return []

    items = []
    for i in ids[:10]:
        item = safe_get_json(f"https://hacker-news.firebaseio.com/v0/item/{i}.json")
        if item and "title" in item:
            items.append({
                "title": item["title"],
                "source": "HackerNews"
            })

    return items


# ---------- Reddit（稳定UA） ----------
def fetch_reddit():
    url = "https://www.reddit.com/r/worldnews/top.json?limit=10"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    data = safe_get_json(url, headers=headers)

    if not data:
        return []

    items = []
    try:
        children = data["data"]["children"]
        for c in children:
            t = c["data"].get("title")
            if t:
                items.append({
                    "title": t,
                    "source": "Reddit"
                })
    except:
        pass

    return items


# ---------- 生成报告 ----------
def generate_report(items):
    today = datetime.now().strftime("%Y-%m-%d")

    lines = []
    lines.append("🔥 GLOBAL HOT DAILY REPORT (V9 STABLE)")
    lines.append(today)
    lines.append("")

    if not items:
        lines.append("⚠️ No data available (all sources failed, fallback mode)")
        lines.append("System is running in safe mode.")
    else:
        for i, item in enumerate(items[:30], 1):
            lines.append(f"{i}. {item['title']}")
            lines.append(f"来源: {item['source']}")
            lines.append("")

    return "\n".join(lines)


# ---------- 主函数 ----------
def main():
    items = fetch_reddit() + fetch_hn()

    report = generate_report(items)

    filename = f"global_hot_{datetime.now().strftime('%Y-%m-%d')}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(report)

    print("DONE:", filename)


if __name__ == "__main__":
    main()
