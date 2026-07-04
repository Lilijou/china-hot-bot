import requests
from datetime import datetime

def fetch_zhihu():
    try:
        url = "https://tenapi.cn/v2/zhihuhot"
        r = requests.get(url, timeout=10)
        data = r.json()["data"]

        items = []
        for i in data[:10]:
            items.append({
                "title": i["title"],
                "hot": i.get("hot", 0),
                "source": "zhihu"
            })
        return items
    except:
        return []

def fetch_toutiao():
    try:
        url = "https://tenapi.cn/v2/baiduhot"
        r = requests.get(url, timeout=10)
        data = r.json()["data"]

        items = []
        for i in data[:10]:
            items.append({
                "title": i["name"],
                "hot": i.get("hot", 0),
                "source": "baidu"
            })
        return items
    except:
        return []

def main():
    items = fetch_zhihu() + fetch_toutiao()

    date = datetime.now().strftime("%Y-%m-%d")

    with open(f"hot_report_{date}.txt", "w", encoding="utf-8") as f:
        f.write("🔥 中国真实热点日报（稳定版）\n")
        f.write(f"📅 {date}\n\n")

        if not items:
            f.write("⚠️ 无数据（接口失败）\n")
            return

        for i, item in enumerate(items, 1):
            f.write(f"{i}. {item['title']}\n")
            f.write(f"   来源: {item['source']}\n")
            f.write(f"   热度: {item['hot']}\n\n")

if __name__ == "__main__":
    main()
