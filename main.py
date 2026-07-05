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

            # 🔥 过滤冷内容（V7升级重点）
            if score < 80:
                continue

            results.append({
                "title": item.get("title", ""),
                "score": score,
                "comments": item.get("descendants", 0),
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

            if score < 300 and comments < 30:
                continue

            results.append({
                "title": d.get("title", ""),
                "score": score,
                "comments": comments,
                "source": "Reddit"
            })

        return results
    except:
        return []


# =========================
# 🔥 V7核心：内容生成器
# =========================
def generate_content(item):
    title = item["title"]

    # 分类（升级版）
    if any(k in title.lower() for k in ["ai", "gpt", "openai", "model"]):
        t = "🔥 AI爆点"
    elif any(k in title.lower() for k in ["google", "apple", "microsoft"]):
        t = "📈 大厂动态"
    elif item["score"] > 1000:
        t = "🔥 全球爆点"
    else:
        t = "🧠 技术趋势"

    # 🧠 发生了什么（结构化解释）
    happened = f"社区正在讨论：{title}"

    # 💥 为什么火（核心升级）
    why_hot = generate_why_hot(title)

    # ⚡ 争议点
    debate = generate_debate(title)

    # 📢 可传播角度
    angle = generate_angle(title)

    return {
        "title": title,
        "type": t,
        "happened": happened,
        "why": why_hot,
        "debate": debate,
        "angle": angle,
        "score": item["score"],
        "comments": item["comments"],
        "source": item["source"]
    }


def generate_why_hot(title):
    t = title.lower()

    if "ai" in t or "gpt" in t:
        return "AI能力变化引发开发者与行业关注"
    if "hack" in t or "leak" in t:
        return "涉及安全或隐私问题，容易引发传播"
    if "google" in t or "apple" in t:
        return "大厂动作影响行业预期"
    return "该话题在技术社区或社交平台出现集中讨论"


def generate_debate(title):
    return "真实性 / 影响范围 / 技术可行性存在讨论空间"


def generate_angle(title):
    return "可以从普通人影响 + 行业变化角度进行内容化表达"


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
# 主程序（V7）
# =========================
def main():

    print("START V7 CONTENT ENGINE")

    items = []
    items += fetch_hackernews()
    items += fetch_reddit()

    # 👉 内容生成层（核心升级）
    items = [generate_content(i) for i in items]

    # 排序
    items = rank(items)

    # 控制数量
    items = items[:30]

    date = datetime.now().strftime("%Y-%m-%d")

    content = []
    content.append("🌍 GLOBAL HOT REPORT V7（内容生成版）")
    content.append(f"📅 {date}")
    content.append("")

    for i, item in enumerate(items, 1):
        content.append(f"{i}. {item['title']}")
        content.append(f"   {item['type']}")
        content.append(f"   🧠 发生：{item['happened']}")
        content.append(f"   💥 为什么火：{item['why']}")
        content.append(f"   ⚡ 争议点：{item['debate']}")
        content.append(f"   📢 可传播角度：{item['angle']}")
        content.append(f"   🔥 热度: {item['score']} | 💬 {item['comments']}")
        content.append(f"   🌐 来源: {item['source']}")
        content.append("")

    filename = f"global_hot_v7_{date}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(content))

    print("DONE:", filename)


if __name__ == "__main__":
    main()
