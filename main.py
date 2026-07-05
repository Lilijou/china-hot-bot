import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

TG_TOKEN = os.getenv("TG_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")


# =========================
# SAFE REQUEST
# =========================

def get(url, headers=None):
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code != 200:
            return None
        if not r.text.strip():
            return None
        return r
    except:
        return None


# =========================
# EXTRACT WEB CONTENT (核心新增)
# =========================

def extract_text(url):
    r = get(url, headers={"User-Agent": "Mozilla/5.0"})
    if not r:
        return ""

    soup = BeautifulSoup(r.text, "html.parser")

    # 删除无用标签
    for tag in soup(["script", "style", "noscript"]):
        tag.extract()

    text = soup.get_text(separator="\n")

    # 简单清洗
    lines = [l.strip() for l in text.split("\n") if len(l.strip()) > 30]

    return "\n".join(lines[:30])


# =========================
# REDDIT (完整实体版)
# =========================

def fetch_reddit():
    url = "https://www.reddit.com/r/worldnews/hot.json?limit=10"
    headers = {"User-Agent": "Mozilla/5.0"}

    r = get(url, headers)
    if not r:
        return []

    data = r.json()
    results = []

    for post in data["data"]["children"][:10]:
        d = post["data"]

        link = "https://www.reddit.com" + d["permalink"]

        # comments
        comments = []
        try:
            c = get(link + ".json", headers)
            if c:
                cj = c.json()
                if len(cj) > 1:
                    for item in cj[1]["data"]["children"][:5]:
                        body = item["data"].get("body")
                        if body:
                            comments.append(body)
        except:
            pass

        full_text = d.get("selftext", "")

        results.append({
            "title": d.get("title", ""),
            "url": link,
            "source": "Reddit",
            "full_text": full_text,
            "top_comments": comments
        })

    return results


# =========================
# HACKER NEWS (实体增强)
# =========================

def fetch_hn():
    ids = get("https://hacker-news.firebaseio.com/v0/topstories.json")
    if not ids:
        return []

    ids = ids.json()

    items = []

    for i in ids[:10]:
        item = get(f"https://hacker-news.firebaseio.com/v0/item/{i}.json")
        if not item:
            continue

        j = item.json()

        url = j.get("url", "")
        text = j.get("text", "")

        # 如果有外链 → 抓正文
        if url:
            text = extract_text(url)

        items.append({
            "title": j.get("title", ""),
            "url": url,
            "source": "HackerNews",
            "full_text": text,
            "top_comments": []
        })

    return items


# =========================
# SCORE SYSTEM（爆点评分）
# =========================

def score(item):
    s = 0
    if item["full_text"]:
        s += 2
    if len(item["top_comments"]) > 2:
        s += 2
    if "AI" in item["title"] or "Google" in item["title"]:
        s += 1
    return s


# =========================
# CONTENT ENGINE（关键升级）
# =========================

def build(item):

    comments = "\n".join(item["top_comments"][:5]) or "无评论"

    summary = item["full_text"][:200] if item["full_text"] else "无正文（仅标题）"

    return f"""
🔥 标题：{item['title']}
📌 来源：{item['source']}
🔗 原文：{item['url']}

🧠 正文摘要：
{summary}

💬 Top评论：
{comments}

🎯 抖音脚本：
这条海外信息最近在讨论……
核心点其实是……

⚡ 爆点：
- 信息密度：高
- 讨论度：中高
- 可传播性：高
"""


# =========================
# MAIN
# =========================

def main():

    items = []
    items += fetch_reddit()
    items += fetch_hn()

    # 排序（关键）
    items = sorted(items, key=score, reverse=True)

    date = datetime.now().strftime("%Y-%m-%d")

    report = f"🌍 GLOBAL CONTENT ENGINE V12.6\n📅 {date}\n\n"

    for i, item in enumerate(items[:15], 1):
        report += f"\n【{i}】\n{build(item)}\n"

    filename = f"hot_report_{date}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(report)

    print("DONE V12.6:", filename)


if __name__ == "__main__":
    main()
