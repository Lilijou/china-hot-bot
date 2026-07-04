import requests
from datetime import datetime
import re

# =========================
# 请求
# =========================
def get_html(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        r.encoding = "utf-8"
        return r.text
    except Exception as e:
        print("request error:", e)
        return ""

# =========================
# 从HTML中粗暴提取标题（不依赖bs4）
# =========================
def extract_titles(html):
    # 用正则抓 title / a 标签文本（极简稳定）
    titles = re.findall(r'title="(.*?)"', html)
    clean = []

    for t in titles:
        t = t.strip()
        if 4 < len(t) < 60:
            clean.append(t)

    return clean[:30]


# =========================
# 百度
# =========================
def fetch_baidu():
    html = get_html("https://top.baidu.com/board")
    return extract_titles(html)


# =========================
# 微博
# =========================
def fetch_weibo():
    html = get_html("https://s.weibo.com/top/summary")
    return extract_titles(html)


# =========================
# 过滤
# =========================
def is_bad(title):
    bad = ["会议", "讲话", "部署", "通报", "政府", "学习"]
    for b in bad:
        if b in title:
            return True
    return False


# =========================
# 主程序
# =========================
def main():

    print("🔥 START HOT REPORT")

    baidu = fetch_baidu()
    weibo = fetch_weibo()

    items = baidu + weibo

    print("raw:", len(items))

    items = [i for i in items if not is_bad(i)]

    items = list(dict.fromkeys(items))[:20]

    date = datetime.now().strftime("%Y-%m-%d")

    report = []
    report.append("🔥 中国真实热点日报（稳定版）")
    report.append(f"📅 {date}")
    report.append("")

    for i, t in enumerate(items, 1):
        report.append(f"{i}. {t}")

    final = "\n".join(report)

    print(final)

    with open(f"hot_report_{date}.txt", "w", encoding="utf-8") as f:
        f.write(final)


if __name__ == "__main__":
    main()
