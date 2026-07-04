import requests
import feedparser
from datetime import datetime

# ========== RSS源（稳定核心） ==========
RSS_SOURCES = [
    {
        "name": "36kr",
        "url": "https://36kr.com/feed"
    },
    {
        "name": "baidu_news",
        "url": "https://rsshub.app/baidu/top"
    },
    {
        "name": "weibo_hot",
        "url": "https://rsshub.app/weibo/search/hot"
    }
]

# ========== API备用源 ==========
API_SOURCES = [
    {
        "name": "zhihu",
        "url": "https://tenapi.cn/v2/zhihuhot",
        "key_title": "title",
        "key_hot": "hot"
    },
    {
        "name": "baidu_api",
        "url": "https://tenapi.cn/v2/baiduhot",
        "key_title": "name",
        "key_hot": "hot"
    }
]


# ========== RSS抓取 ==========
def fetch_rss(source):
    try:
        feed = feedparser.parse(source["url"])

        items = []
        for entry in feed.entries[:10]:
            items.append({
                "title": entry.get("title", "no-title"),
                "source": source["name"],
                "hot": 0
            })

        print(f"[RSS OK] {source['name']} -> {len(items)}")
        return items

    except Exception as e:
        print(f"[RSS ERROR] {source['name']}: {e}")
        return []


# ========== API抓取 ==========
def fetch_api(source):
    try:
        r = requests.get(source["url"], timeout=10)

        print(f"[API STATUS] {source['name']}: {r.status_code}")
        print(f"[API TEXT] {source['name']}: {r.text[:100]}")

        data = r.json().get("data", [])

        items = []
        for i in data[:10]:
            items.append({
                "title": i.get(source["key_title"], "no-title"),
                "source": source["name"],
                "hot": i.get(source["key_hot"], 0)
            })

        return items

    except Exception as e:
        print(f"[API ERROR] {source['name']}: {e}")
        return []


# ========== 主函数 ==========
def main():

    all_items = []

    # 1. RSS（主力）
    for s in RSS_SOURCES:
        all_items += fetch_rss(s)

    # 2. API（备用）
    for s in API_SOURCES:
        all_items += fetch_api(s)

    # 3. 去空
    all_items = [i for i in all_items if i["title"]]

    # 4. 排序
    all_items.sort(key=lambda x: x.get("hot", 0), reverse=True)

    # 5. 输出文件
    date = datetime.now().strftime("%Y-%m-%d")
    filename = f"hot_report_{date}.txt"

    with open(filename, "w", encoding="utf-8") as f:

        f.write("🔥 中国全网热点日报（V2稳定版）\n")
        f.write(f"📅 {date}\n\n")

        if not all_items:
            f.write("❌ 所有数据源失败（RSS/API均不可用）\n")
            return

        # 去重
        seen = set()
        final_items = []

        for item in all_items:
            if item["title"] not in seen:
                seen.add(item["title"])
                final_items.append(item)

        # 输出前20
        for i, item in enumerate(final_items[:20], 1):
            f.write(f"{i}. {item['title']}\n")
            f.write(f"   来源: {item['source']}\n")
            f.write(f"   热度: {item.get('hot', 0)}\n\n")


if __name__ == "__main__":
    main()
