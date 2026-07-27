#!/usr/bin/env python3
"""
Keep历年轨迹合集视频生成器
格式: 抖音竖屏 1080×1920, 20秒
按年份分章节: 片头(2s) + 2018-2026各2s + 片尾(2s)
BGM + 文字叠加（年里程/次数/高光）
"""

import json, os, re, shutil, subprocess, glob, random
from collections import defaultdict
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ========== 配置 ==========
ROOT = r'D:\Keep轨迹素材'
OUTPUT_DIR = r'C:\Users\Administrator\Desktop\Keep历年轨迹合集'
OUTPUT_VIDEO = os.path.join(OUTPUT_DIR, 'Keep历年轨迹合集_20s.mp4')
TMP_DIR = os.path.join(OUTPUT_DIR, '_frames')

# 每段时长(秒)
TOTAL_DURATION = 20
INTRO_DURATION = 2.0      # 片头
CHAPTER_DURATION = 1.8    # 每年1.8秒, 9章=16.2秒
OUTRO_DURATION = 1.8      # 片尾 = 20秒
FPS = 30

W = 1080
H = 1920

BG_COLOR = (10, 10, 30)  # 深蓝黑底

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TMP_DIR, exist_ok=True)

# ========== 解析数据 ==========
print("解析轨迹数据...")
yearly_data = defaultdict(lambda: {'images':[], 'total_km':0.0, 'count':0, 'max_km':0.0, 'max_img':'', 'max_pace':999, 'max_pace_img':'', 'marathons':0, 'halfs':0})

for dirpath, dirnames, filenames in os.walk(ROOT):
    for fn in filenames:
        if not fn.endswith('.jpg'):
            continue
        m = re.search(r'(\d{4})-(\d{2})-\d{2}_([\d.]+)km_([\d.]+)min', fn)
        if not m:
            continue
        year = m.group(1)
        km = float(m.group(3))
        pace = float(m.group(4))
        fp = os.path.join(dirpath, fn)
        
        d = yearly_data[year]
        d['images'].append(fp)
        d['total_km'] += km
        d['count'] += 1
        if km > d['max_km']:
            d['max_km'] = km
            d['max_img'] = fp
        if pace > 0 and pace < d['max_pace']:
            d['max_pace'] = pace
            d['max_pace_img'] = fp
        if km >= 42.195:
            d['marathons'] += 1
        if km >= 21.0975:
            d['halfs'] += 1

years_sorted = sorted(yearly_data.keys())
total_all = sum(yearly_data[y]['total_km'] for y in years_sorted)
total_count = sum(yearly_data[y]['count'] for y in years_sorted)

print(f"总里程: {total_all:.0f}km, 总次数: {total_count}")
print(f"年份: {years_sorted}")

# ========== 生成每一帧画面 ==========

# 尝试加载中文字体
font_paths = [
    r'C:\Windows\Fonts\msyhbd.ttc',   # 微软雅黑粗体
    r'C:\Windows\Fonts\msyh.ttc',     # 微软雅黑
    r'C:\Windows\Fonts\simhei.ttf',   # 黑体
    r'C:\Windows\Fonts\SIMLI.ttf',    # 隶书
]
FONT = None
for fp in font_paths:
    if os.path.exists(fp):
        FONT = fp
        break
if not FONT:
    # fallback: 扫描所有ttf
    for fp in glob.glob(r'C:\Windows\Fonts\*.ttf') + glob.glob(r'C:\Windows\Fonts\*.ttc'):
        try:
            ImageFont.truetype(fp, 20)
            FONT = fp
            break
        except:
            pass

print(f"字体: {FONT}")

def make_text_frame(text, font_size, color=(255,255,255), bold=False, outline=False, out_path=None):
    """生成文字帧"""
    img = Image.new('RGBA', (W, H), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    try:
        if bold and os.path.basename(FONT).startswith('msyhbd'):
            font = ImageFont.truetype(FONT, font_size)
        else:
            font = ImageFont.truetype(FONT, font_size)
    except Exception as e:
        print(f"Font error: {e}")
        return None
    
    # 多行文字
    lines = text.split('\n')
    total_h = len(lines) * (font_size + 10)
    y_start = (H - total_h) // 2
    
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        y = y_start + i * (font_size + 10)
        
        if outline:
            for dx, dy in [(-2,-2),(-2,2),(2,-2),(2,2),(0,-2),(0,2),(-2,0),(2,0)]:
                draw.text((x+dx, y+dy), line, font=font, fill=(0,0,0,220))
        draw.text((x, y), line, font=font, fill=color)
    
    if out_path:
        img.save(out_path)
    return img

def make_frame_with_track(track_img_path, overlay_text, is_highlight=False, out_path=None):
    """
    合成一帧: 深色背景 + 轨迹图(缩放到合适大小+高斯模糊底图) + 文字叠加
    """
    canvas = Image.new('RGB', (W, H), BG_COLOR)
    draw = ImageDraw.Draw(canvas)
    
    try:
        track = Image.open(track_img_path).convert('RGB')
        # 裁剪为竖屏比例
        tw, th = track.size
        # 缩放到合适大小，保持比例
        scale = min(W * 0.85 / tw, H * 0.45 / th)
        new_w = int(tw * scale)
        new_h = int(th * scale)
        track_resized = track.resize((new_w, new_h), Image.LANCZOS)
        
        # 放到底部区域
        x = (W - new_w) // 2
        y = int(H * 0.55) - new_h // 2
        canvas.paste(track_resized, (x, y))
    except Exception as e:
        print(f"Track image error {track_img_path}: {e}")
    
    # 添加文字
    try:
        font_big = ImageFont.truetype(FONT, 48)
        font_small = ImageFont.truetype(FONT, 28)
    except:
        return None
    
    lines = overlay_text.split('\n')
    y_text = int(H * 0.08)
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font_big if len(line) < 20 else font_small)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        # 阴影
        for dx, dy in [(2,2)]:
            draw.text((x+dx, y_text+dy), line, font=font_big if len(line) < 20 else font_small, fill=(0,0,0,180))
        draw.text((x, y_text), line, font=font_big if len(line) < 20 else font_small, fill=(255,255,255))
        y_text += 60 if len(line) < 20 else 40
    
    if out_path:
        canvas.save(out_path)
    return canvas

def make_intro_frame(out_path):
    """片头: Keep 历年轨迹合集"""
    img = Image.new('RGB', (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)
    try:
        font_title = ImageFont.truetype(FONT, 72)
        font_sub = ImageFont.truetype(FONT, 36)
        font_num = ImageFont.truetype(FONT, 96)
    except:
        return None
    
    # 装饰线
    for i in range(0, H, 40):
        draw.rectangle([0, i, W, i+1], fill=(30, 30, 60))
    
    # Title
    draw.text((W//2 - 200, 400), "KEEP", font=font_num, fill=(0, 200, 255))
    draw.text((W//2 - 260, 520), "历年轨迹合集", font=font_title, fill=(255, 255, 255))
    draw.text((W//2 - 240, 650), f"2018 — 2026  •  {total_all:.0f}km  •  {total_count}次", font=font_sub, fill=(150, 200, 255))
    draw.text((W//2 - 180, 1200), "🏃 每一公里 都是故事", font=font_sub, fill=(200, 200, 200))
    
    img.save(out_path)
    print(f"  [Intro] saved")

def make_outro_frame(out_path):
    """片尾"""
    img = Image.new('RGB', (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)
    try:
        font_big = ImageFont.truetype(FONT, 56)
        font_mid = ImageFont.truetype(FONT, 40)
        font_small = ImageFont.truetype(FONT, 30)
    except:
        return None
    
    draw.text((W//2 - 220, 400), f"🏃 {total_count} 次奔跑", font=font_big, fill=(255,255,255))
    draw.text((W//2 - 280, 500), f"📏 {total_all:.0f} 公里累积", font=font_big, fill=(0, 200, 255))
    draw.text((W//2 - 200, 700), "下一段旅程 即将出发", font=font_mid, fill=(200,200,200))
    draw.text((W//2 - 250, 1200), "Made with Keep & OpenClaw", font=font_small, fill=(100,100,100))
    
    img.save(out_path)

def make_chapter_frame(year, data, out_path):
    """
    每年分镜: 当年的最长轨迹图 + 文字数据
    文字: 年份 | 总里程 | 次数 | 高光
    """
    # 优先用当年的最佳轨迹（最长距离）
    track_img = data['max_img'] if data['max_img'] and os.path.exists(data['max_img']) else (data['images'][0] if data['images'] else None)
    
    canvas = Image.new('RGB', (W, H), BG_COLOR)
    draw = ImageDraw.Draw(canvas)
    
    # 背景：用轨迹图模糊放大
    if track_img:
        try:
            bg = Image.open(track_img).convert('RGB')
            bg = bg.resize((W, H), Image.LANCZOS)
            bg = bg.filter(ImageFilter.GaussianBlur(radius=30))
            bg = bg.point(lambda p: p * 0.35)  # 变暗
            canvas.paste(bg, (0, 0))
        except:
            pass
    
    # 主轨迹图缩略（居中偏下）
    if track_img:
        try:
            track = Image.open(track_img).convert('RGB')
            tw, th = track.size
            scale = min(W * 0.7 / tw, H * 0.35 / th)
            new_w = int(tw * scale)
            new_h = int(th * scale)
            track_small = track.resize((new_w, new_h), Image.LANCZOS)
            x = (W - new_w) // 2
            y = H * 3 // 5 - new_h // 2
            # 白边框
            border = 6
            draw.rectangle([x-border, y-border, x+new_w+border, y+new_h+border], fill=(255,255,255,30))
            canvas.paste(track_small, (x, y))
        except:
            pass
    
    # 顶部半透明遮罩
    for i in range(350):
        alpha = int(180 * (1 - i/350))
        draw.rectangle([0, i, W, i+1], fill=(0,0,0,alpha))
    
    # 年份 - 大字
    try:
        font_year = ImageFont.truetype(FONT, 120)
        font_stat = ImageFont.truetype(FONT, 40)
        font_highlight = ImageFont.truetype(FONT, 32)
    except:
        return None
    
    # 年份
    yr_text = str(year)
    bbox = draw.textbbox((0,0), yr_text, font=font_year)
    draw.text(((W - (bbox[2]-bbox[0]))//2, 20), yr_text, font=font_year, fill=(0, 200, 255))
    
    # 统计数据
    stats = f"🏃 {data['count']}次  |  📏 {data['total_km']:.0f}km  |  ⚡ {data['max_pace']:.1f}min/km"
    bbox = draw.textbbox((0,0), stats, font=font_stat)
    draw.text(((W - (bbox[2]-bbox[0]))//2, 150), stats, font=font_stat, fill=(255,255,255))
    
    # 高光标签
    highlights = []
    if data['marathons'] > 0:
        highlights.append(f"🏅 全马×{data['marathons']}")
    if data['halfs'] > 0:
        highlights.append(f"🎯 半马×{data['halfs']}")
    if data['max_km'] >= 30:
        highlights.append(f"🔥 最长{data['max_km']:.1f}km")
    
    if highlights:
        hl_text = '  '.join(highlights)
        bbox = draw.textbbox((0,0), hl_text, font=font_highlight)
        draw.text(((W - (bbox[2]-bbox[0]))//2, 220), hl_text, font=font_highlight, fill=(255, 220, 100))
    
    # 底部分割线
    draw.rectangle([200, 280, W-200, 282], fill=(0, 200, 255, 100))
    
    canvas.save(out_path)
    print(f"  [{year}] saved: {data['count']}次, {data['total_km']:.0f}km")

# ========== 生成所有帧 ==========
print("\n生成画面帧...")

# 1. 片头 - 2秒 = 60帧
intro_frames = []
for i in range(int(INTRO_DURATION * FPS)):
    fp = os.path.join(TMP_DIR, f'intro_{i:04d}.png')
    if i == 0:
        make_intro_frame(fp)
    else:
        # 后面的帧复制（ffmpeg 会处理）
        pass
    intro_frames.append(fp)

# 拷贝片头帧
intro_src = os.path.join(TMP_DIR, 'intro_0000.png')
for i in range(1, int(INTRO_DURATION * FPS)):
    dst = os.path.join(TMP_DIR, f'intro_{i:04d}.png')
    if os.path.exists(intro_src):
        shutil.copy2(intro_src, dst)

# 2. 每年分镜 - 各1.8秒 = 54帧
all_chapter_frames = []
frame_idx = 0
for year in years_sorted:
    data = yearly_data[year]
    # 生成几个不同帧（轻微变化/缩放模拟动效）
    n_frames = int(CHAPTER_DURATION * FPS)
    base_fp = os.path.join(TMP_DIR, f'chapter_{year}_base.png')
    make_chapter_frame(year, data, base_fp)
    
    for i in range(n_frames):
        fp_out = os.path.join(TMP_DIR, f'chapter_{frame_idx:04d}.png')
        shutil.copy2(base_fp, fp_out)
        all_chapter_frames.append(fp_out)
        frame_idx += 1

# 3. 片尾 - 1.8秒 = 54帧
outro_fp = os.path.join(TMP_DIR, 'outro_0000.png')
make_outro_frame(outro_fp)
outro_frames = []
for i in range(int(OUTRO_DURATION * FPS)):
    fp = os.path.join(TMP_DIR, f'outro_{i:04d}.png')
    if i > 0:
        shutil.copy2(outro_fp, fp)
    outro_frames.append(fp)

# ========== 创建帧序列清单（用来给 ffmpeg concat） ==========
print("\n生成帧序列...")
concat_lines = []
all_frames_order = (
    list(range(int(INTRO_DURATION * FPS)))  # intro
)
# Intro frames
for i in range(int(INTRO_DURATION * FPS)):
    concat_lines.append(f"file 'intro_{i:04d}.png'\nduration 0.0333333")

# Chapter frames
for i in range(len(all_chapter_frames)):
    concat_lines.append(f"file 'chapter_{i:04d}.png'\nduration 0.0333333")

# Outro frames
for i in range(int(OUTRO_DURATION * FPS)):
    concat_lines.append(f"file 'outro_{i:04d}.png'\nduration 0.0333333")

with open(os.path.join(TMP_DIR, 'frames.txt'), 'w') as f:
    f.write('\n'.join(concat_lines))

print(f"帧数: 片头{int(INTRO_DURATION*FPS)} + 章节{len(all_chapter_frames)} + 片尾{int(OUTRO_DURATION*FPS)} = {int(INTRO_DURATION*FPS)+len(all_chapter_frames)+int(OUTRO_DURATION*FPS)}")

# ========== 用 ffmpeg 合成 ==========
print("\n合成视频...")

# 先合成为无声音视频
raw_video = os.path.join(TMP_DIR, 'raw_video.mp4')

cmd = [
    'ffmpeg', '-y',
    '-f', 'concat',
    '-safe', '0',
    '-i', os.path.join(TMP_DIR, 'frames.txt'),
    '-c:v', 'libx264',
    '-pix_fmt', 'yuv420p',
    '-preset', 'medium',
    '-crf', '20',
    '-r', str(FPS),
    raw_video
]

subprocess.run(cmd, check=True, capture_output=True)

# 尝试找 BGM - 如果有就用，没有就用纯视频
bgm_path = None
# 先找本地音乐
for p in [
    r'D:\moto\assets\bgm.mp3',
    r'C:\Users\Administrator\Music\bgm.mp3',
]:
    if os.path.exists(p):
        bgm_path = p
        break

if bgm_path:
    final_cmd = [
        'ffmpeg', '-y',
        '-i', raw_video,
        '-i', bgm_path,
        '-c:v', 'copy',
        '-af', f'adelay=0s,apad,atrim=duration={TOTAL_DURATION}',
        '-shortest',
        OUTPUT_VIDEO
    ]
    subprocess.run(final_cmd, check=True, capture_output=True)
else:
    # 纯视频，也可用ffmpeg生成测试音
    # 加一个简单的纯音轨避免有些播放器没声音报错
    final_cmd = [
        'ffmpeg', '-y',
        '-i', raw_video,
        '-f', 'lavfi', '-t', str(TOTAL_DURATION),
        '-i', 'anullsrc=r=44100:cl=mono',
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-shortest',
        OUTPUT_VIDEO
    ]
    subprocess.run(final_cmd, check=True, capture_output=True)

print(f"\n✅ 视频生成完成!")
print(f"📁 {OUTPUT_VIDEO}")
print(f"⏱ {TOTAL_DURATION}秒 | 📐 1080×1920 | 🎞 {FPS}fps")
