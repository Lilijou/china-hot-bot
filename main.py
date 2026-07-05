import requests
from datetime import datetime

# =========================
# HackerNews
# =========================
def fetch_hackernews():
    try:
        ids = requests.get(
            "https://hacker-news.firebaseio.com/v0/topstories.json",
            timeout=10
        ).json()[:40]

        results = []

        for i in ids:
            item = requests.get(
                f"https://hacker-news.firebaseio.com/v0/item/{i}.json",
                timeout=10
            ).json()

            if not item:
                continue

            score = item.get("score", 0)

            # 热点过滤
            if score < 60:
                continue

            results.append({
                "title": item.get("title", ""),
                "score": score,
                "comments": item.get("descendants", 0),
                "url": item.get("url", ""),
                "source": "HackerNews"
            })

        return results
    except:
        return []


# =========================
# Reddit
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
    except:
        return []


# =========================
# 🔥 V6核心：热点理解层
# =========================
def analyze_item(item):
    title = item["title"].lower()

    # 分类系统
    if any(k in title for k in ["ai", "gpt", "openai", "model", "claude"]):
        category = "🔥 AI / 大模型"
    elif any(k in title for k in ["google", "apple", "microsoft", "meta"]):
        category = "📈 大厂动态"
    elif any(k in title for k in ["security", "leak", "hack", "vulnerability"]):
        category = "⚠️ 安全/漏洞"
    elif item["score"] > 1000:
        category = "🔥 爆点热点"
    else:
        category = "🧠 技术趋势"

    # 人话解释（关键升级）
    explanation = generate_explanation(item["title"])

    item["category"] = category
    item["explanation"] = explanation

    return item


def generate_explanation(title):
    # 简化版“热点理解层”（V6核心）
    if "AI" in title or "GPT" in title:
        return "这个话题涉及AI技术进展或模型能力变化，容易引发开发者和行业讨论。"
    elif "Google" in title or "Apple" in title:
        return "大厂动态，通常意味着产品或战略变化，会影响行业方向。"
    elif "leak" in title or "hack" in title:
        return "涉及安全或数据泄露，容易引发争议和关注。"
    else:
        return "这是当前技术社区或互联网用户正在讨论的热门内容。"


# =========================
# 排序
# =========================
def rank(items):
    return sorted(
        items,
        key=lambda x: x["score"] * 2 + x["comments"],
        reverse=True
    )


# =========================
# 主程序（V6）
# =========================
def main():
    print("START V6 HOT INTELLIGENCE BOT")

    items = []
    items += fetch_hackernews()
    items += fetch_reddit()

    # 🔥 加理解层
    items = [analyze_item(i) for i in items]

    # 排序
    items = rank(items)

    # 控制 30 条以内
    items = items[:30]

    if not items:
        content = "⚠️ 无热点数据"
    else:
        content = "🌍 GLOBAL HOT REPORT V6（热点理解版）\n"
        content += f"📅 {datetime.now().strftime('%Y-%m-%d')}\n\n"

        for i, item in enumerate(items, 1):
            content += f"{i}. {item['title']}\n"
            content += f"   {item['category']}\n"
            content += f"   🔥 热度: {item['score']} | 💬 {item['comments']}\n"
            content += f"   🧠 解读: {item['explanation']}\n"
            content += f"   🌐 {item['source']}\n"
            content += f"   🔗 {item['url']}\n\n"

    filename = f"global_hot_v6_{datetime.now().strftime('%Y-%m-%d')}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

    print("DONE:", filename)


if __name__ == "__main__":
    main()
