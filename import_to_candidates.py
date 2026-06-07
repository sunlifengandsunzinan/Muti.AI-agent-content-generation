#!/usr/bin/env python3
"""
将 openclaw_export.json 中的抖音数据导入审批候选队列
输出到 openclaw_candidates.json
"""
import json, os, sys, io, re
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DATA_DIR = r"D:\moto\data\raw"
EXPORT_FILE = os.path.join(DATA_DIR, "openclaw_export.json")
CANDIDATE_FILE = os.path.join(DATA_DIR, "openclaw_candidates.json")
NORMALIZED_FILE = r"D:\moto\data\normalized\candidate_spots.json"
REVIEWED_DIR = r"D:\moto\data\reviewed"
APPROVED_FILE = os.path.join(REVIEWED_DIR, "approved_spots.json")
REJECTED_FILE = os.path.join(REVIEWED_DIR, "rejected_spots.json")

def slugify(name: str) -> str:
    s = re.sub(r'[^\w\u4e00-\u9fff]', '-', name)
    s = re.sub(r'-+', '-', s).strip('-')
    if not s:
        s = f"spot-{hash(name) & 0xFFFFFFFF}"
    return s[:40]

def extract_city(name: str, author: str, kw: str) -> str:
    cities = ["沈阳", "大连", "鞍山", "抚顺", "本溪", "丹东", "锦州",
              "营口", "阜新", "辽阳", "盘锦", "铁岭", "朝阳", "葫芦岛"]
    for city in cities:
        if city in (name or "") or city in (kw or "") or city in (author or ""):
            return city
    return "辽宁"

def extract_route_type(name: str, kw: str) -> str:
    txt = (name or "") + " " + (kw or "")
    if re.search(r'滨海|沿海|海岸|海', txt):
        return "coast"
    if re.search(r'山|岭|峰|峡谷|十八盘', txt):
        return "mountain"
    if re.search(r'水库|湖|河|江|水洞|温泉', txt):
        return "scenic-water"
    if re.search(r'环城|城内|市区|市郊', txt):
        return "city-riverside"
    return "mountain"

def main():
    # 读取 export 数据
    if not os.path.exists(EXPORT_FILE):
        print(f"找不到 {EXPORT_FILE}")
        return
    
    with open(EXPORT_FILE, "r", encoding="utf-8") as f:
        export = json.load(f)
    items = export.get("items", [])
    print(f"export 中共 {len(items)} 条数据")
    
    # 读取已有候选（如存在）
    existing_candidates = []
    if os.path.exists(CANDIDATE_FILE):
        try:
            with open(CANDIDATE_FILE, "r", encoding="utf-8") as f:
                existing_candidates = json.load(f)
        except:
            pass
    existing_slugs = {s.get("slug", "") for s in existing_candidates}
    print(f"已有候选: {len(existing_candidates)} 条")
    
    new_candidates = []
    count = 0
    for item in items:
        name = item.get("name", "")
        if not name:
            continue
        slug = slugify(name)
        if slug in existing_slugs:
            continue
        
        author = item.get("owner", item.get("author", ""))
        city = item.get("location", {}).get("city", "")
        if not city:
            city = extract_city(name, author, item.get("keywords", [""])[0] if item.get("keywords") else "")
        
        candidate = {
            "slug": slug,
            "raw_name": name[:80],
            "city": city,
            "region": "辽宁",
            "source_name": "抖音",
            "source_author": author,
            "description": name[:200],
            "tags": item.get("keywords", ["摩旅"]),
            "reference_url": item.get("sourceUrl", ""),
            "collected_at": item.get("collected_at", ""),
            "route_type": extract_route_type(name, ""),
            "source_platform": "douyin",
            "platform_slug": item.get("poiId", ""),
        }
        new_candidates.append(candidate)
        existing_slugs.add(slug)
        count += 1
    
    if count == 0:
        print("没有新数据需要导入")
        return
    
    # 合并写入
    all_candidates = existing_candidates + new_candidates
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(CANDIDATE_FILE, "w", encoding="utf-8") as f:
        json.dump(all_candidates, f, ensure_ascii=False, indent=2)
    
    print(f"\n导入完成: 新增 {count} 条候选数据")
    print(f"候选队列总计: {len(all_candidates)} 条")
    print(f"文件: {CANDIDATE_FILE}")
    
    # 同时清理 git 冲突的 normalized 文件
    normalized_path = NORMALIZED_FILE
    if os.path.exists(normalized_path):
        content = open(normalized_path, encoding="utf-8").read()
        if "<<<<<<" in content:
            # 修复 git conflict - 取 ours (stash pop 后的版本)
            clean = re.sub(r'<<<<<<<.*?\n=======\n.*?\n>>>>>>>.*?\n', '', content, flags=re.DOTALL)
            with open(normalized_path, "w", encoding="utf-8") as f:
                f.write(clean)
            print(f"修复了 {normalized_path} 的 git conflict")
    
    # 清理 reviewed 目录
    os.makedirs(REVIEWED_DIR, exist_ok=True)
    for f in [APPROVED_FILE, REJECTED_FILE]:
        if not os.path.exists(f):
            with open(f, "w", encoding="utf-8") as f2:
                json.dump([], f2)
    
    print("准备就绪，可以去审批页面审核了！")

if __name__ == "__main__":
    main()
