import requests

def fetch_baidu():
    try:
        r = requests.get("https://top.baidu.com/board", timeout=10)
        return [{"title": "百度热点测试", "source": "baidu"}]
    except Exception as e:
        print("baidu error:", e)
        return []

def fetch_weibo():
    try:
        r = requests.get(
            "https://s.weibo.com/top/summary",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )
        return [{"title": "微博热点测试", "source": "weibo"}]
    except Exception as e:
        print("weibo error:", e)
        return []

def main():
    print("START RUN")

    items = fetch_baidu() + fetch_weibo()

    print("TOTAL ITEMS:", len(items))

    for i, item in enumerate(items, 1):
        print(i, item["title"], item["source"])

if __name__ == "__main__":
    main()
