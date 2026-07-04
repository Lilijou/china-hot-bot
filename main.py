from datetime import datetime

# =========================
# 模拟热点数据（后面可升级真实抓取）
# =========================
def fetch_baidu():
    return [
        "AI行业迎来重大技术突破",
        "某地召开经济发展相关会议",
        "明星突发事件引发全网讨论"
    ]

def fetch_weibo():
    return [
        "娱乐圈爆料持续发酵引热议",
        "某科技公司发布新AI模型",
        "社会热点事件引发关注"
    ]

# =========================
# 过滤层（简化版）
# =========================
def is_useful_hot(title):
    bad_keywords = ["会议", "通知", "调研", "部署", "政府"]

    for kw in bad_keywords:
        if kw in title:
            return False

    return True

# =========================
# 生成中文日报
# =========================
def main():
    baidu = fetch_baidu()
    weibo = fetch_weibo()

    items = baidu + weibo

    # 过滤
    items = [i for i in items if is_useful_hot(i)]

    date = datetime.now().strftime("%Y年%m月%d日")

    report = []
    report.append("🔥 中国每日热点日报")
    report.append(f"📅 {date}")
    report.append("")
    report.append("——————————————")

    for i, title in enumerate(items, 1):
        report.append(f"{i}. {title}")

    report.append("")
    report.append("📊 数据来源：百度热榜 / 微博热搜（模拟版）")

    final_text = "\n".join(report)

    # 输出到 GitHub Actions 日志
    print(final_text)

    # 保存成文件（关键）
    filename = f"每日热点日报_{date}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(final_text)


if __name__ == "__main__":
    main()
