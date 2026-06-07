#!/usr/bin/env python3
"""
抖音采集存储脚本
从浏览器 snapshot 数据中提取摩旅视频信息，追加到 export 文件
"""
import json, os, sys, io, re
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

OUTPUT_DIR = r"D:\moto\data\raw"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "openclaw_export.json")
SEEN_FILE = os.path.join(OUTPUT_DIR, "douyin_seen_titles.txt")

# 辽宁摩旅内容关键词
MOTO_KEYWORDS = [
    "摩旅", "摩友", "骑行", "跑山", "摩托车", "机车",
    "路线", "攻略", "沈阳周边", "本溪", "丹东",
    "关门山", "大伙房", "滨海", "摩旅路线",
]

def is_moto_related(title: str) -> bool:
    title_lower = title.lower()
    for kw in MOTO_KEYWORDS:
        if kw in title_lower:
            return True
    return False

def load_seen() -> set:
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def save_seen(titles: set):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        for t in sorted(titles):
            f.write(t + "\n")

def load_export() -> dict:
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"exported_at": "", "source": "douyin-browser", "total": 0, "items": []}

def save_export(data: dict):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    data["exported_at"] = datetime.now().isoformat()
    data["total"] = len(data["items"])
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_from_browser_snapshot(snapshot_text: str) -> int:
    """
    从浏览器 snapshot 文本中提取视频卡片数据
    格式来自抖音搜索结果页 snapshot
    """
    export = load_export()
    seen = load_seen()
    existing_names = {i.get("name", "") for i in export["items"]}
    
    new_count = 0
    lines = snapshot_text.split('\n')
    
    i = 0
    current_author = ""
    current_title = ""
    
    while i < len(lines):
        line = lines[i].strip()
        
        # 提取作者: @xxx
        if line.startswith('"@') or line.startswith('@'):
            current_author = line.strip('"')
        
        # 提取标题/描述（长的文本行）
        if len(line) > 30 and not line.startswith('<') and not line.startswith('-') and not line.startswith('/'):
            # 检查是否包含摩旅关键词
            if is_moto_related(line):
                # 提取标题（取前80字符）
                title = line.strip()[:100]
                if title not in seen and title not in existing_names:
                    # 尝试提取作者（从前面几行找）
                    author = ""
                    for j in range(max(0, i-5), i):
                        prev = lines[j].strip()
                        if prev.startswith('"@') or prev.startswith('@'):
                            author = prev.strip('"')
                            break
                    
                    item = {
                        "platform": "douyin",
                        "poiId": f"douyin-{hash(title) & 0xFFFFFFFF}",
                        "name": title,
                        "sourceUrl": f"https://www.douyin.com/search/{title[:20]}",
                        "owner": author or "抖音用户",
                        "provider": "douyin-scraper",
                        "location": {"city": "", "region": "辽宁"},
                        "poiType": "video-note",
                        "keywords": ["摩旅", "骑行", "辽宁"],
                        "excerpt": title[:200],
                        "source_platform": "抖音",
                        "collected_at": datetime.now().isoformat(),
                    }
                    export["items"].append(item)
                    seen.add(title)
                    existing_names.add(title)
                    new_count += 1
                    print(f"  + [{new_count}] {author} - {title[:50]}...")
        
        i += 1
    
    if new_count > 0:
        save_seen(seen)
        save_export(export)
        print(f"\n新增 {new_count} 条抖音数据，总计 {export['total']} 条")
    
    return new_count


def add_douyin_video_card(author: str, title: str, likes: str = "", date: str = "") -> int:
    """手动添加一条抖音视频卡片数据"""
    export = load_export()
    seen = load_seen()
    existing_names = {i.get("name", "") for i in export["items"]}
    
    name = title[:100]
    if name in seen or name in existing_names:
        return 0
    
    item = {
        "platform": "douyin",
        "poiId": f"douyin-{hash(name) & 0xFFFFFFFF}",
        "name": name,
        "author": author,
        "likes": likes,
        "date": date,
        "owner": author,
        "provider": "douyin-scraper",
        "location": {"city": "", "region": "辽宁"},
        "poiType": "video-note",
        "keywords": ["摩旅", "辽宁"],
        "excerpt": name[:200],
        "source_platform": "抖音",
        "collected_at": datetime.now().isoformat(),
    }
    export["items"].append(item)
    seen.add(name)
    
    save_seen(seen)
    save_export(export)
    
    print(f"  + {author} - {name[:50]}...")
    return 1


# 从当前 snapshot 批量添加
def batch_add(cards: list[dict]) -> int:
    """批量添加抖音卡片数据"""
    export = load_export()
    seen = load_seen()
    existing_names = {i.get("name", "") for i in export["items"]}
    
    count = 0
    for card in cards:
        name = card.get("title", "")[:100]
        if name and name not in seen and name not in existing_names:
            item = {
                "platform": "douyin",
                "poiId": f"douyin-{hash(name) & 0xFFFFFFFF}",
                "name": name,
                "author": card.get("author", ""),
                "likes": card.get("likes", ""),
                "date": card.get("date", ""),
                "location": {"city": "", "region": "辽宁"},
                "poiType": "video-note",
                "keywords": card.get("keywords", ["摩旅"]),
                "excerpt": name[:200],
                "source_platform": "抖音",
                "collected_at": datetime.now().isoformat(),
            }
            export["items"].append(item)
            seen.add(name)
            count += 1
            print(f"  + [{count}] {card.get('author','?')} - {name[:50]}")
    
    if count > 0:
        save_seen(seen)
        save_export(export)
        print(f"\n✅ 新增 {count} 条，总计 {export['total']} 条")
    return count

if __name__ == "__main__":
    print(f"抖音采集存储脚本 v1")
    print(f"输出: {OUTPUT_FILE}")
