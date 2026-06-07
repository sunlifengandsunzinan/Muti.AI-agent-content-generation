#!/usr/bin/env python3
"""
通过 OpenClaw browser 工具采集抖音辽宁摩旅数据
被 cron 调用，每10分钟跑一个关键词
"""
import json, os, sys, re, time, random
from datetime import datetime
from pathlib import Path

DATA_DIR = r"D:\moto\data\raw"
EXPORT_FILE = os.path.join(DATA_DIR, "openclaw_export.json")
CANDIDATES_FILE = os.path.join(DATA_DIR, "openclaw_candidates.json")
NORMALIZED_FILE = r"D:\moto\data\normalized\candidate_spots.json"
STATUS_FILE = os.path.join(DATA_DIR, "local_collection_status.json")

# 辽宁摩旅关键词池
KEYWORDS = [
    "辽宁摩旅路线推荐",
    "沈阳周边骑行",
    "本溪摩旅攻略",
    "丹东骑行",
    "大连摩旅",
    "辽宁滨海公路骑行",
    "锦州摩旅",
    "G331辽宁段",
    "辽宁摩旅打卡",
    "鞍山骑行路线",
]

seen_file = os.path.join(DATA_DIR, "douyin_seen_titles.txt")

def load_export():
    if not os.path.exists(EXPORT_FILE):
        return {"total": 0, "items": []}
    try:
        with open(EXPORT_FILE, "r", encoding="utf-8") as f:
            d = json.load(f)
        return d
    except:
        return {"total": 0, "items": []}

def save_export(data):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(EXPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_seen():
    if not os.path.exists(seen_file):
        return set()
    try:
        with open(seen_file, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    except:
        return set()

def save_seen(seen):
    with open(seen_file, "w", encoding="utf-8") as f:
        f.write("\n".join(sorted(seen)))

def update_status(payload):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

def parse_card_text(text: str) -> dict:
    """解析抖音搜索卡片文本"""
    result = {"author": "", "title": "", "likes": "0", "date": ""}
    if not text:
        return result
    
    # 找点赞数 @作者 日期
    m = re.search(r'(\d[\d\.]*[万kK]?)\s+(.*?)(?:\s*@(\S+))?\s*·\s*(\d{4}年\d{1,2}月\d{1,2}日|\d{1,2}月\d{1,2}日|\d{1,2}天前|\d+周前)', text)
    if m:
        result["likes"] = m.group(1).strip()
        result["author"] = "@" + (m.group(3) or "").strip()
        result["date"] = m.group(4).strip()
        # title 在likes前面
        # 需要上下文提取，这里简化
        return result
    
    # 简单fallback：截取前40字符做title
    result["title"] = text.strip()[:60]
    return result

def main():
    # 用文件标记当前关键词索引
    idx_file = os.path.join(DATA_DIR, "keyword_index.txt")
    try:
        with open(idx_file, "r") as f:
            idx = int(f.read().strip())
    except:
        idx = 0
    
    keyword = KEYWORDS[idx % len(KEYWORDS)]
    
    # 更新下一轮索引
    next_idx = (idx + 1) % len(KEYWORDS)
    with open(idx_file, "w") as f:
        f.write(str(next_idx))
    
    start_time = datetime.now()
    
    # 输出状态信息给 cron log
    print(f"本轮关键词: [{idx+1}/{len(KEYWORDS)}] {keyword}")
    
    # 实际采集由 OpenClaw agent 的 browser 工具完成
    # 这里输出关键词供 agent 使用
    cycle_info = {
        "keyword": keyword,
        "keyword_index": idx,
        "cycle_start": start_time.isoformat(),
        "status": "pending",
    }
    
    # 更新状态文件
    status = {
        "collector_name": "douyin-browser-collector",
        "state": "running",
        "cycle": idx + 1,
        "current_keyword": keyword,
        "current_stage": "等待浏览器采集",
        "last_heartbeat": start_time.isoformat(),
        "cycle_start": start_time.isoformat(),
    }
    update_status(status)
    
    # 写入 cycle_info 供 OpenClaw 读取
    info_path = os.path.join(DATA_DIR, "current_cycle.json")
    with open(info_path, "w", encoding="utf-8") as f:
        json.dump(cycle_info, f, ensure_ascii=False, indent=2)
    
    print(f"KEYWORD:{keyword}")
    print(f"READY_TO_COLLECT")

if __name__ == "__main__":
    main()
