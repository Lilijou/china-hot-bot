import requests

# =========================
# 过滤层 V1（核心升级）
# =========================
def is_useful_hot(title: str) -> bool:

    bad_keywords = [
        "总书记", "会议", "调研", "工作", "通报",
        "部署", "学习", "强调", "指出", "召开",
        "政府", "办公室", "委员会", "政策", "意见",
        "精神", "讲话", "活动", "会议精神"
    ]

    good_keywords = [
        "AI", "人工智能", "爆料", "曝光", "冲突",
        "火灾", "地震", "事故", "暴涨", "裁员",
        "明星", "娱乐", "电影", "游戏", "科技",
        "OpenAI", "GPT", "ChatGPT", "马斯克"
    ]

    text = title.lower()

    # ❌ 强过滤（政务/空内容）
    for kw in bad_keywords:
        if kw in title:
            return False

    # ✅ 强兴趣内容优先保留
    for kw in good_keywords:
        if kw.lower() in text:
            return True

    # 默认规则：太短的不要
    if len(title) < 6:
        return False

    return True


# =========================
# 模拟抓取（先保证稳定运行）
# =========================
def fetch_baidu():
    try:
        r = requests.get("https://top.baidu.com/board", timeout=10)
        return [
            {"title": "AI行业最新突破引发关注", "source": "baidu"},
            {"title": "某地召开经济工作会议", "source": "baidu"},
            {"title": "明星突发事件引热议", "source": "baidu"},
        ]
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
        return [
            {"title": "娱乐圈爆料事件持续发酵", "source": "weibo"},
            {"title": "某政府部门发布通知", "source": "weibo"},
            {"title": "AI模型更新引发讨论", "source": "weibo"},
        ]
    except Exception as e:
        print("weibo error:", e)
        return []


# =========================
# 主程序
# =========================
def main():
    print("START RUN")

    raw_items = fetch_baidu() + fetch_weibo()

    # 🔥 关键：过滤层生效
    items = [i for i in raw_items if is_useful_hot(i["title"])]

    print("RAW ITEMS:", len(raw_items))
    print("FILTERED ITEMS:", len(items))
    print("")

    for i, item in enumerate(items, 1):
        print(i, item["title"], "-", item["source"])


if __name__ == "__main__":
    main()
