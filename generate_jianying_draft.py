#!/usr/bin/env python3
"""
生成剪映草稿 - 辽宁摩旅路线视频草稿生成器
读取 D:\摩旅数据采集目录\routes_v8_new_LN.json 中的路线数据，
自动生成剪映草稿包（draft package）到桌面。
"""

import json
import os
import uuid
import base64
import shutil
from datetime import datetime

# ======================== 配置 ========================
DATA_FILE = r"D:\摩旅数据采集目录\routes_v8_new_LN.json"
OUTPUT_DIR = os.path.expanduser(r"~\Desktop\摩旅剪映草稿")
ROUTE_NAME = "辽宁摩旅路线精选"  # 草稿名称

# ======================== 加载数据 ========================
with open(DATA_FILE, 'r', encoding='utf-8-sig') as f:
    routes = json.load(f)

# 只取前几条路线，包含完整信息
selected_routes = []
for r in routes:
    if r.get('start') and r.get('end') and r.get('waypoints') and r.get('distance'):
        selected_routes.append(r)

print(f"总路线数: {len(routes)}, 有完整信息的: {len(selected_routes)}")

# 按 distance 提取数值排序（粗略）
def extract_distance_km(d):
    import re
    nums = re.findall(r'(\d+)', d.get('distance', ''))
    return int(nums[0]) if nums else 0

selected_routes.sort(key=extract_distance_km, reverse=True)

# 取前15条
ROUTES_TO_USE = selected_routes[:15]

# ======================== 生成草稿 ========================

def make_draft_id():
    return str(uuid.uuid4()).upper()

def make_timeline_id():
    return str(uuid.uuid4()).lower()

def format_duration(ms):
    """Format to 剪映 track format"""
    return ms

def make_segment(material_id, target_duration=3000000, source_duration=3000000, start=0, speed=1.0):
    """Create a track segment"""
    segment = {
        "id": str(uuid.uuid4()).upper(),
        "material_id": material_id,
        "target_timerange": {
            "duration": target_duration,
            "start": 0
        },
        "source_timerange": {
            "duration": source_duration,
            "start": 0
        },
        "speed": speed,
        "transform": {
            "scale": 1.0,
            "rotation": 0,
            "translation_x": 0,
            "translation_y": 0,
            "anchor": 9
        },
        "multi_clip_extra_info": None,
        "canvans_overlay_params": {
            "audio_speed_align": 0
        },
        "realtime_extra_param": None
    }
    return segment

def make_track(track_type, segments):
    """Create a track"""
    track = {
        "id": str(uuid.uuid4()).upper(),
        "type": track_type,
        "flag": 0,
        "segments": segments,
        "attribute": 0
    }
    return track

def make_text_segment(content, start=0, duration=4000000):
    """Create a text overlay segment"""
    return {
        "id": str(uuid.uuid4()).upper(),
        "material_id": f"text_{uuid.uuid4().hex[:12]}",
        "target_timerange": {
            "duration": duration,
            "start": start
        },
        "source_timerange": {
            "duration": duration,
            "start": 0
        },
        "speed": 1.0,
        "transform": {
            "scale": 1.0,
            "rotation": 0,
            "translation_x": 0,
            "translation_y": 0,
            "anchor": 5
        },
        "content": content,
        "style_id": "text_style_1",
        "canvans_overlay_params": {
            "audio_speed_align": 0
        }
    }

# ======================== 生成 draft_content ========================

draft_id = make_draft_id()
timeline_id = make_timeline_id()
now = int(datetime.now().timestamp() * 10000000)
duration_ms = len(ROUTES_TO_USE) * 4000000 + 2000000  # 4秒每条 + 片尾

materials_videos = []
materials_audios = []
materials_texts = []
tracks_video = []
tracks_audio = []
tracks_text = []

# 生成每条路线的素材和轨道
for i, route in enumerate(ROUTES_TO_USE):
    seg_start = i * 4000000
    seg_dur = 4000000
    
    # 视频/图片素材（实际是占位，用户需替换为实际视频）
    vid = f"route_{i}"
    materials_videos.append({
        "id": vid,
        "type": "video",
        "path": "",  # 占位
        "duration": seg_dur,
        "height": 1920,
        "width": 1080
    })
    
    track_vid = make_segment(vid, seg_dur, seg_dur, seg_start)
    tracks_video.append(track_vid)
    
    # 文字素材 - 路线标题
    title_text = route.get('title', '') or f"{route.get('start','')}→{route.get('end','')}"
    route_detail = f"{route.get('start','')}→{route.get('end','')} | {route.get('distance','')} | {route.get('days','')}"
    waypoints = route.get('waypoints', '')
    
    text_content = f"{title_text}\n{route_detail}"
    if waypoints:
        text_content += f"\n途经: {waypoints}"
    
    tracks_text.append(make_text_segment(text_content, seg_start, seg_dur))

# 片尾
end_text = make_text_segment("辽宁摩旅路线精选\n数据来源: 抖音/小红书", len(ROUTES_TO_USE) * 4000000 + 500000, 3000000)
tracks_text.append(end_text)

# 构建 draft_content
draft_content = {
    "version": 1,
    "tracks": [
        make_track("video", tracks_video),
        make_track("text", tracks_text)
    ],
    "materials": {
        "videos": materials_videos,
        "audios": [],
        "texts": [],
        "images": [],
        "transitions": [],
        "effects": []
    },
    "canvas_size": {
        "width": 1080,
        "height": 1920
    },
    "duration": duration_ms
}

# ======================== 写入文件 ========================

os.makedirs(OUTPUT_DIR, exist_ok=True)

# 写入JSON原始格式（未加密，可用于分析/调试）
with open(os.path.join(OUTPUT_DIR, "draft_content_unencrypted.json"), 'w', encoding='utf-8') as f:
    json.dump(draft_content, f, ensure_ascii=False, indent=2)

# 写入路线文稿（直接可用的文案）
script_lines = []
for i, route in enumerate(ROUTES_TO_USE):
    title = route.get('title', '') or f"{route.get('start','')}→{route.get('end','')}"
    summary = route.get('summary', '')
    difficulty = route.get('difficulty', '')
    season = route.get('season', '')
    road_condition = route.get('road_condition', '')
    
    script_lines.append(f"--- 第{i+1}条路线 ---")
    script_lines.append(f"标题: {title}")
    script_lines.append(f"起点→终点: {route.get('start','')} → {route.get('end','')}")
    if route.get('waypoints'): script_lines.append(f"途经: {route.get('waypoints')}")
    if route.get('distance'): script_lines.append(f"距离: {route.get('distance')}")
    if route.get('days'): script_lines.append(f"天数: {route.get('days')}")
    if difficulty: script_lines.append(f"难度: {difficulty}")
    if summary: script_lines.append(f"简介: {summary}")
    script_lines.append("")

script = "\n".join(script_lines)
with open(os.path.join(OUTPUT_DIR, "文案脚本.txt"), 'w', encoding='utf-8') as f:
    f.write(script)

# 写入一条完整markdown路线文档
md_lines = ["# 辽宁摩旅路线精选 - 剪映视频素材", "", "## 视频制作建议", 
            "", "1. 视频尺寸: 1080×1920 (竖屏, 抖音/小红书格式)", 
            "2. 每条路线推荐4秒, BGM用机车/旅行类音乐", 
            "3. 每页包含: 标题、起终点、途经点、距离、天数",
            "4. 建议在路线转弯/关键点用地图标注动画",
            "", "---", "", "## 路线列表", ""]

for i, route in enumerate(ROUTES_TO_USE):
    title = route.get('title', '')
    md_lines.append(f"### {i+1}. {title}")
    md_lines.append(f"- **路线**: {route.get('start','')} → {route.get('end','')}")
    if route.get('waypoints'): md_lines.append(f"- **途经点**: {route.get('waypoints')}")
    if route.get('distance'): md_lines.append(f"- **距离**: {route.get('distance')}")
    if route.get('days'): md_lines.append(f"- **天数**: {route.get('days')}")
    if route.get('difficulty'): md_lines.append(f"- **难度**: {route.get('difficulty')}")
    if route.get('summary'): md_lines.append(f"- **简介**: {route.get('summary')}")
    md_lines.append("")

with open(os.path.join(OUTPUT_DIR, "摩旅路线视频素材.md"), 'w', encoding='utf-8') as f:
    f.write("\n".join(md_lines))

# 生成一个HTML预览文件用于快速查看
html = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>摩旅路线视频预览</title>
<style>
body { font-family: system-ui; max-width: 420px; margin: auto; background: #0a0a0a; color: #fff; padding: 16px; }
.card { background: #1a1a2e; border-radius: 16px; padding: 20px; margin: 12px 0; border-left: 4px solid #e94560; }
h2 { color: #e94560; font-size: 18px; margin: 0 0 8px 0; }
.tag { display: inline-block; background: #16213e; color: #a0a0ff; font-size: 12px; padding: 2px 8px; border-radius: 8px; margin-right: 4px; }
.detail { color: #ccc; font-size: 14px; margin: 4px 0; }
.waypoints { color: #888; font-size: 12px; margin-top: 8px; }
.header { text-align: center; margin-bottom: 20px; }
.header h1 { color: #e94560; font-size: 24px; }
.header p { color: #888; }
.preview-tip { background: #16213e; border-radius: 12px; padding: 12px; font-size: 13px; color: #aaa; margin-bottom: 20px; }
</style></head><body>
<div class="header"><h1>🏍️ 辽宁摩旅路线</h1><p>抖音/小红书视频素材 · 共""" + str(len(ROUTES_TO_USE)) + """条路线</p></div>
<div class="preview-tip">📱 竖屏 1080×1920 · 每条4秒 · 建议配合机车BGM</div>"""

for i, route in enumerate(ROUTES_TO_USE):
    title = route.get('title', '') or f"{route.get('start','')}→{route.get('end','')}"
    html += f'<div class="card">'
    html += f'<h2>{i+1}. {title}</h2>'
    html += f'<div class="detail">📍 {route.get("start","")} → 🏁 {route.get("end","")}</div>'
    if route.get('distance'): html += f'<div class="detail">📏 {route["distance"]}</div>'
    if route.get('days'): html += f'<div class="detail">⏱ {route["days"]}</div>'
    if route.get('difficulty'): html += f'<span class="tag">{route["difficulty"]}</span>'
    if route.get('season'): html += f'<span class="tag">{route["season"]}</span>'
    if route.get('road_condition'): html += f'<span class="tag">{route["road_condition"]}</span>'
    if route.get('waypoints'): html += f'<div class="waypoints">🛣 {route["waypoints"]}</div>'
    if route.get('summary'): html += f'<div class="detail" style="margin-top:8px;color:#999;">{route["summary"]}</div>'
    html += '</div>'

html += '</body></html>'

with open(os.path.join(OUTPUT_DIR, "preview.html"), 'w', encoding='utf-8') as f:
    f.write(html)

# 统计信息
print(f"\n✔ 生成完成!")
print(f"输出目录: {OUTPUT_DIR}")
print(f"路线数: {len(ROUTES_TO_USE)}")
print(f"总时长: {duration_ms / 1000000:.1f}秒 ({len(ROUTES_TO_USE) * 4 + 3}秒)")
print(f"\n生成文件:")
print(f"  1. draft_content_unencrypted.json  - 草稿数据(未加密)")
print(f"  2. 文案脚本.txt                     - 每条路线的文案脚本")
print(f"  3. 摩旅路线视频素材.md              - 完整路线文档")
print(f"  4. preview.html                     - 手机预览HTML")

# 输出到桌面
print(f"\n📂 文件已保存到: {OUTPUT_DIR}")
