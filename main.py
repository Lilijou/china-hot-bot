import os
import requests
from datetime import datetime

TG_TOKEN = os.getenv("TG_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")


# ======================
# SAFE REQUEST
# ======================

def get_json(url, headers=None):
    try:
        r = requests.get(url, headers=headers, timeout=10)

        if r.status_code != 200:
            return None

        if not r.text.strip():
            return None

        return r.json()

    except:
        return None


# ======================
# REDDIT HOT + COMMENTS
# ======================

def fetch_reddit():
    url = "https://www.reddit.com/r/worldnews/hot.json?limit=10"
    headers = {"User-Agent": "Mozilla/5.0"}

    data = get_json(url, headers)

    if not data:
        return []

    results = []

    for post in data["data"]["children"][:10]:
        d = post["data"]

        permalink = "https://www.reddit.com" + d["permalink"]

        # ===== fetch comments =====
        comments_url = permalink + ".json"
        cdata = get_json(comments_url, headers)

        top_comments = []

        try:
            if cdata and len(cdata) > 1:
                comments = cdata[1]["data"]["children"]

                for c in comments[:5]:
                    body = c["data"].get("body", "")
                    if body:
                        top_comments.append(body)
        except:
            pass

        results.append({
            "title": d.get("title", ""),
            "url": permalink,
            "source": "Reddit",
            "content": d.get("selftext", ""),
            "top_comments": top_comments
        })

    return results


# ======================
# HACKER NEWS
# ======================

def fetch_hn():
    ids = get_json("https://hacker-news.firebaseio.com/v0/topstories.json")

    if not ids:
        return []

    items = []

    for i in ids[:10]:
        item = get_json(
            f"https://hacker-news.firebaseio.com/v0/item/{i}.json"
        )

        if not item:
            continue

        items.append({
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "source": "HackerNews",
            "content": item.get("text", ""),
            "top_comments": []
        })

    return items


# ======================
# CONTENT ENGINE
# ======================

def build_script(item):

    comments = "\n".join(
        [f"- {c[:80]}" for c in item["top_comments"]]
    ) if item["top_comments"] else "无评论"

    return f"""
🔥 热点标题：{item['title']}

📌 来源：{item['source']}
🔗 原帖：{item['url']}

🧠 内容摘要：
{item['content'][:200]}

💬 Top 5评论：
{comments}

🎯 抖音口播脚本：
这条信息最近在海外很火……
很多人讨论的点其实是……

⚡ 爆点分析：
- 争议性：高
- 传播性：中高
- 情绪驱动：强
"""


# ======================
# REPORT
# ======================

def main():

    items = []
    items += fetch_reddit()
    items += fetch_hn()

    date = datetime.now().strftime("%Y-%m-%d")

    report = f"🌍 GLOBAL HOT SYSTEM V12\n📅 {date}\n\n"

    for i, item in enumerate(items[:20], 1):
        report += f"\n【{i}】\n{build_script(item)}\n"

    filename = f"hot_report_{date}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(report)

    print("DONE V12:", filename)


if __name__ == "__main__":
    main()
