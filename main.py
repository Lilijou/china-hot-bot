import requests
from datetime import datetime

# =========================
# 数据层
# =========================
def fetch_reddit():
    url = "https://www.reddit.com/r/all/hot.json?limit=30"
    headers = {"User-Agent": "Mozilla/5.0"}

    data = requests.get(url, headers=headers, timeout=10).json()

    items = []

    for p in data["data"]["children"]:
        d = p["data"]

        items.append({
            "title": d["title"],
            "score": d["score"],
            "comments": d["num_comments"],
            "url": "https://reddit.com" + d["permalink"],
            "source": "Reddit"
        })

    return items


def fetch_hn():
    ids = requests.get(
        "https://hacker-news.firebaseio.com/v0/topstories.json",
        timeout=10
    ).json()[:30]

    items = []

    for i in ids:
        d = requests.get(
            f"https://hacker-news.firebaseio.com/v0/item/{i}.json",
            timeout=10
        ).json()

        if not d:
            continue

        items.append({
            "title": d.get("title"),
            "score": d.get("score", 0),
            "comments": d.get("descendants", 0),
            "url": d.get("url", ""),
            "source": "HackerNews"
        })

    return items


# =========================
# 爆款评分
# =========================
def score(item):
    text = item["title"].lower()

    s = 0

    if item["score"] > 300:
        s += 2

    if item["comments"] > 50:
        s += 2

    if any(k in text for k in ["ai", "gpt", "openai"]):
        s += 3

    if any(k in text for k in ["leak", "hack", "war", "crash"]):
        s += 3

    return s


# =========================
# 内容生成（可发布）
# =========================
def make_content(item):

    title = item["title"]

    # 抖音脚本
    douyin = f"""
🎬 标题：{title}

🧠 开头3秒：
“你可能没注意，这件事正在发生变化…”

💥 内容：
这条新闻来自 {item['source']}，目前在全球技术社区引发讨论。

⚡ 核心点：
可能影响整个行业的发展方向。

📢 结尾：
你怎么看这件事？
"""

    # 小红书
    xhs = f"""
标题：{title}正在引发全球讨论

👉 发生了什么
全球社区正在关注这个事件

👉 为什么重要
可能影响未来技术和行业趋势

👉 个人看法
这是一个值得持续关注的变化
"""

    return {
        "title": title,
        "douyin": douyin,
        "xhs": xhs,
        "score": item["score"],
        "comments": item["comments"],
        "source": item["source"]
    }


# =========================
# 主程序
# =========================
def main():

    items = fetch_reddit() + fetch_hn()

    # 排序 + 过滤爆点
    items = sorted(items, key=score, reverse=True)

    top = items[:5]   # 🔥 只取爆款

    contents = [make_content(i) for i in top]

    date = datetime.now().strftime("%Y-%m-%d")

    out = []

    out.append("🚀 CONTENT PACK（可发布版本）")
    out.append(f"📅 {date}\n")

    for i, c in enumerate(contents, 1):

        out.append(f"🔥 {i}. {c['title']}")
        out.append("")

        out.append("🎬 抖音脚本：")
        out.append(c["douyin"])

        out.append("📱 小红书：")
        out.append(c["xhs"])

        out.append("────────────────────\n")

    filename = f"content_pack_{date}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(out))

    print("DONE:", filename)


if __name__ == "__main__":
    main()
