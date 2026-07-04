import requests
from datetime import datetime

def fetch_zhihu():
    try:
        url = "https://tenapi.cn/v2/zhihuhot"

        r = requests.get(url, timeout=10)

        print("ZH status:", r.status_code)
        print("ZH text:", r.text[:200])

        data = r.json().get("data", [])

        items = []
        for i in data[:10]:
            items.append({
                "title": i.get("title", "no-title"),
                "hot": i.get("hot", 0),
                "source": "zhihu"
            })
        return items

    except Exception as e:
        print("ZH error:", e)
        return []

def fetch_baidu():
    try:
        url = "https://tenapi.cn/v2/baiduhot"

        r = requests.get(url, timeout=10)

        print("BD status:", r.status_code)
        print("BD text:", r.text[:200])

        data = r.json().get("data", [])

        items = []
        for i in data[:10]:
            items.append({
                "title": i.get("name", "no-title"),
                "hot": i.get("hot", 0),
                "source": "baidu"
            })
        return items

    except Exception as e:
        print("BD error:", e)
        return []

def main():

    zhihu = fetch_zhihu()
    baidu = fetch_baidu()

    items = zhihu + baidu

    date = datetime.now().strftime("%Y-%m-%d")
    filename = f"hot_report_{date}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write("🔥 中国真实热点日报（调试版）\n")
        f.write(f"📅 {date}\n\n")

        if not items:
            f.write("❌ 数据源全部失败（请看日志）\n")
            return

        for i, item in enumerate(items, 1):
            f.write(f"{i}. {item['title']}\n")
            f.write(f"   来源: {item['source']}\n")
            f.write(f"   热度: {item['hot']}\n\n")

if __name__ == "__main__":
    main()
