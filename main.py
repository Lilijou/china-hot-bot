import requests
from datetime import datetime

# ========= 数据源 =========

def fetch_hackernews():
    try:
        url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        ids = requests.get(url, timeout=10).json()[:5]

        results = []
        for i in ids:
            item = requests.get(
                f"https://hacker-news.firebaseio.com/v0/item/{i}.json",
                timeout=10
            ).json()

            results.append({
                "title": item.get("title", ""),
                "source": "HackerNews"
            })

        return results
    except Exception as e:
        print("HN error:", e)
        return []


def fetch_reddit():
    try:
        url = "https://www.reddit.com/r/all/hot.json?limit=5"
        headers = {"User-Agent": "Mozilla/5.0"}

        data = requests.get(url, headers=headers, timeout=10).json()

        results = []
        for post in data["data"]["children"]:
            d = post["data"]
            results.append({
                "title": d.get("title", ""),
                "source": "Reddit"
            })

        return results
    except Exception as e:
        print("Reddit error:", e)
        return []


def fetch_producthunt():
    try:
        url = "https://www.producthunt.com/frontend/graphql"
        # fallback：简单RSS替代
        rss = requests.get("https://www.producthunt.com/feed", timeout=10)

        return [{
            "title": "ProductHunt Daily Trending (RSS)",
            "source": "ProductHunt"
        }]
    except Exception as e:
        print("PH error:", e)
        return []


# ========= 主程序 =========

def main():
    print("START GLOBAL HOT BOT")

    items = []
    items += fetch_hackernews()
    items += fetch_reddit()
    items += fetch_producthunt()

    # 如果全失败
    if not items:
        content = "⚠️ 无数据（所有海外源失败）"
    else:
        content = "🌍 GLOBAL HOT DAILY REPORT\n\n"

        for i, item in enumerate(items, 1):
            content += f"{i}. {item['title']}\n"
            content += f"   来源: {item['source']}\n\n"

    filename = f"global_hot_{datetime.now().strftime('%Y-%m-%d')}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

    print("DONE:", filename)


if __name__ == "__main__":
    main()
