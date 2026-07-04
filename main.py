import requests
from datetime import datetime
from bs4 import BeautifulSoup

# =========================
# 通用请求
# =========================
def get_html(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print("请求失败:", url, e)
        return ""

# =========================
# 百度热榜
# =========================
def fetch_baidu():
    url = "https://top.baidu.com/board"
    html = get_html(url)
    soup = BeautifulSoup(html, "html.parser")

    items = []

    for item in soup.select("div.category-wrap_iQLoo_1iK3h"):
        try:
            title = item.select_one("div.c-single-text-ellipsis").text.strip()
            items.append({
                "title": title,
                "source": "baidu"
            })
        except:
            continue

    return items


# =========================
# 微博热搜（简化版）
# =========================
def fetch_weibo():
    url = "https://s.weibo.com/top/summary"
    html = get_html(url)
    soup = BeautifulSoup(html, "html.parser")

    items = []

    for item in soup.select("td.td-02"):
        a = item.select_one("a")
        if a:
            title = a.text.strip()
            if title:
                items.append({
                    "title": title,
                    "source": "weibo"
                })

    return items


# =========================
# 过滤层（升级版）
# =========================
def is_useful(title):

    bad_words = [
        "会议", "讲话", "部署", "强调", "学习",
        "政府", "通报", "意见", "精神", "调研"
    ]

    for w in bad_words:
        if w in title:
            return False

    return True


# =========================
# 主程序
# =========================
def main():

    print("🔥 开始抓取真实热点...")

    baidu = fetch_baidu()
    weibo = fetch_weibo()

    print("百度数量:", len(baidu))
    print("微博数量:", len(weibo))

    items = baidu + weibo

    # 过滤
    items = [i for i in items if is_useful(i["title"])]

    # 去重
    seen = set()
    final_items = []

    for i in items:
        if i["title"] not in seen:
            seen.add(i["title"])
            final_items.append(i)

    # 取前20
    final_items = final_items[:20]

    # 输出日报
    date = datetime.now().strftime("%Y-%m-%d")

    report = []
    report.append("🔥 中国每日真实热点日报")
    report.append(f"📅 {date}")
    report.append("")
    report.append("——————————————")

    for i, item in enumerate(final_items, 1):
        report.append(f"{i}. {item['title']}")
        report.append(f"来源：{item['source']}")
        report.append("")

    final_text = "\n".join(report)

    print(final_text)

    # 保存文件（GitHub可见）
    with open(f"hot_report_{date}.txt", "w", encoding="utf-8") as f:
        f.write(final_text)


if __name__ == "__main__":
    main()
