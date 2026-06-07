#!/usr/bin/env python3
"""
摩旅景點采集任务 - 持久化运行
采集辽宁地区摩旅游记/景點数据
通过浏览器搜索公开信息 + 保存到本地

输出: D:\moto\data\raw\openclaw_export.json
"""

import io
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime

# Fix Windows GBK output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

OUTPUT_DIR = r"D:\moto\data\raw"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "openclaw_export.json")
SEEN_FILE = os.path.join(OUTPUT_DIR, "collected_urls.txt")

# 辽宁摩旅相关搜索关键词
SEARCH_QUERIES = [
    # 抖音热词
    "辽宁摩旅路线",
    "沈阳周边骑行",
    "本溪摩旅攻略",
    "丹东骑行路线",
    "大连滨海骑行",
    "辽东摩旅游记",
    "辽宁摩托车骑行",
    # 小红书/公开内容
    "辽宁景点自驾游",
    "沈阳周边一日游",
    "本溪旅游景点",
    "丹东旅游攻略",
    "大连小众景点",
    # 进一步扩展
    "鞍山千山骑行",
    "抚顺大伙房水库",
    "铁岭冰砬山",
    "岫岩药山",
    "朝阳凤凰山",
]

MAX_RESULTS = 5  # 采集够5条就停


def fetch_baidu_results(keyword: str, max_items: int = 3) -> list[dict]:
    """通过百度搜索获取公开的旅游景点/路线信息"""
    results = []
    url = f"https://www.baidu.com/s?wd={urllib.parse.quote(keyword)}&tn=SE_baiduhome_pg"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="replace")
            # 简单提取
            import re
            # 找标题和摘要模式
            titles = re.findall(r'<h3[^>]*>(.*?)</h3>', html, re.DOTALL)
            for i, raw_title in enumerate(titles[:max_items]):
                # 清理HTML标签
                title = re.sub(r'<[^>]+>', '', raw_title).strip()
                if title and len(title) > 4:
                    results.append({
                        "platform": "web",
                        "name": title[:60],
                        "sourceUrl": f"https://www.baidu.com/s?wd={urllib.parse.quote(keyword)}",
                        "provider": "baidu",
                        "keywords": [keyword],
                        "excerpt": "",
                        "location": {"city": extract_city(keyword), "region": extract_city(keyword)},
                        "poiType": "scenic-spot",
                        "routeType": "mountain",
                        "supportTags": ["viewpoint"],
                        "collected_at": datetime.now().isoformat(),
                    })
    except Exception as e:
        print(f"  [baidu error] {keyword}: {e}")
    return results


def get_douyin_suggestions(keyword: str) -> list[str]:
    """从抖音搜索建议API获取相关关键词（无需登录）"""
    suggestions = []
    url = f"https://www.douyin.com/aweme/v1/web/search/sug/?keyword={urllib.parse.quote(keyword)}&aid=6383"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://www.douyin.com/",
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            for item in data.get("sug_list", []):
                content = item.get("content", "")
                if content and content not in suggestions:
                    suggestions.append(content)
    except Exception as e:
        print(f"  [douyin error] {keyword}: {e}")
    return suggestions


def get_route_type(keyword: str) -> str:
    """根据关键词推断路线类型"""
    kw = keyword.lower()
    if any(x in kw for x in ["滨海", "沿海", "coast", "海"]):
        return "coast"
    if any(x in kw for x in ["山", "本溪", "鞍山", "岫岩"]):
        return "mountain"
    if any(x in kw for x in ["水库", "湖", "河"]):
        return "scenic-water"
    if any(x in kw for x in ["城市", "市内"]):
        return "city-riverside"
    return "mountain"


def extract_city(keyword: str) -> str:
    """从关键词提取城市名"""
    cities = ["沈阳", "大连", "鞍山", "抚顺", "本溪", "丹东", "锦州",
              "营口", "阜新", "辽阳", "盘锦", "铁岭", "朝阳", "葫芦岛", "岫岩"]
    for city in cities:
        if city in keyword:
            return city
    return "辽宁"


def load_collected_urls() -> set:
    """加载已采集的URL集合，避免重复"""
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    return set()


def save_collected_urls(urls: set):
    """保存已采集的URL"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        for url in sorted(urls):
            f.write(url + "\n")


def load_existing_items() -> list[dict]:
    """加载已有数据"""
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and "items" in data:
                return data["items"]
            if isinstance(data, list):
                return data
        except Exception:
            pass
    return []


def save_items(items: list[dict]):
    """保存数据"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output = {
        "exported_at": datetime.now().isoformat(),
        "total": len(items),
        "items": items,
    }
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 已保存 {len(items)} 条数据到 {OUTPUT_FILE}")


def main():
    print("=" * 60)
    print(f"摩旅景点采集任务 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    existing = load_existing_items()
    seen_names = set(item.get("name", "") for item in existing)
    print(f"已有数据: {len(existing)} 条")

    collected_urls = load_collected_urls()
    new_items = []
    new_count = 0

    for query in SEARCH_QUERIES:
        if new_count >= MAX_RESULTS:
            print(f"\n已达到目标 {MAX_RESULTS} 条，停止采集")
            break

        print(f"\n🔍 搜索: {query}")
        
        # 1. 先试抖音建议
        suggestions = get_douyin_suggestions(query)
        if suggestions:
            print(f"  抖音建议: {suggestions[:3]}")

        # 2. 百度搜索采集
        results = fetch_baidu_results(query, max_items=3)
        for item in results:
            name = item["name"]
            if name not in seen_names and name not in [n.get("name") for n in new_items]:
                new_items.append(item)
                new_count += 1
                seen_names.add(name)
                print(f"  ✅ [{new_count}] {name}")
                
                if new_count >= MAX_RESULTS:
                    break

        # 每轮间隔，避免被封
        if new_count < MAX_RESULTS:
            time.sleep(2)

    # 合并保存
    all_items = existing + new_items
    save_items(all_items)
    
    print(f"\n📊 本轮新增: {len(new_items)} 条")
    print(f"📊 总计: {len(all_items)} 条")

    # 如果采集够了，输出通知信息
    if len(all_items) >= MAX_RESULTS:
        print(f"\n🎯 通知: 已采集 {len(all_items)} 条数据，请查收！")


if __name__ == "__main__":
    main()
