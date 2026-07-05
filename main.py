import requests
from datetime import datetime

# =========================
# HackerNews（过滤 + 实时）
# =========================
def fetch_hackernews():
    try:
        ids = requests.get(
            "https://hacker-news.firebaseio.com/v0/topstories.json",
            timeout=10
        ).json()[:50]

        results = []

        for i in ids:
            item = requests.get(
                f"https://hacker-news.firebaseio.com/v0/item/{i}.json",
                timeout=10
            ).json()

            if not item:
                continue

            score = item.get("score", 0)

            # 🔥 热点过滤
            if score < 50:
                continue

            results.append({
                "title": item.get("title", ""),
                "score": score,
                "comments": item.get("descendants", 0),
                "url": item.get("url", ""),
                "source": "HackerNews"
            })

        return results

    except Exception as e:
        print("HN error:", e)
        return []


# =========================
# Reddit（严格热点过滤）
# =========================
def fetch_reddit():
    try:
        url = "https://www.reddit.com/r/all/hot.json?limit=50"
        headers = {"User-Agent": "Mozilla/5.0"}

        data = requests.get(url, headers=headers, timeout=10).json()

        results = []

        for post in data["data"]["children"]:
            d = post["data"]

            score = d.get("score", 0)
            comments = d.get("num_comments", 0)

            # 🔥 热点过滤（关键）
            if score < 200 and comments < 20:
                continue

            results.append({
                "title": d.get("title", ""),
                "score": score,
                "comments": comments,
                "url": "https://reddit.com" + d.get("permalink", ""),
                "source": "Reddit"
            })

        return results

    except Exception as e:
        print("Reddit error:", e)
        return []


# =========================
# ProductHunt（弱信号）
# =========================
def fetch_producthunt():
    try:
        return [{
            "title": "ProductHunt Trending (visit site)",
            "score": 0,
            "comments": 0,
            "url": "https://www.producthunt.com",
            "source": "ProductHunt"
        }]
    except:
        return []


# =========================
# 排序引擎（核心）
# =========================
def rank_items(items):
    return sorted(
        items,
        key=lambda x: (x["score"] * 2 + x["comments"]),
        reverse=True
    )


# =========================
# 主程序（V5）
# =========================
def main():
    print("START V5 HOT BOT")

    items = []
    items += fetch_hackernews()
    items += fetch_reddit()
    items += fetch_producthunt()

    # 🔥 排序
    items = rank_items(items)

    # 🔥 限制30条以内
    items = items[:30]

    if not items:
        content = "⚠️ 无实时热点（数据源失败）"
    else:
        content = "🌍 GLOBAL HOT REPORT V5（实时热点版）\n"
        content += f"📅 {datetime.now().strftime('%Y-%m-%d')}\n\n"

        for i, item in enumerate(items, 1):
            content += f"{i}. {item['title']}\n"
            content += f"   🔥 热度: {item['score']} | 💬 {item['comments']}\n"
            content += f"   🌐 {item['source']}\n"
            content += f"   🔗 {item['url']}\n\n"

    filename = f"global_hot_v5_{datetime.now().strftime('%Y-%m-%d')}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

    print("DONE:", filename)


if __name__ == "__main__":
    main()
