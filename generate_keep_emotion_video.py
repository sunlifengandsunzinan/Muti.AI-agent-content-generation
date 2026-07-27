#!/usr/bin/env python3
"""
Keep 七年跑步轨迹 — 情感叙事短视频生成器
镜头设计:
  [0-4s]   旧照氛围感画面 → 口播"坚持跑步七年，到底能改变一个人多少？"
  [4-7s]   脚步慢动作特写 → "7年前的我，迷茫又懒散..."
  [7-10s]  7600km数字动态滚动 → "如今跑完7600公里..."
  [10-14s] Keep总里程+历年合集滚动 → "一路走来，从抗拒到热爱..."
  [14-17s] 轨迹叠加跑者画面 → "更治愈了内心..."
  [17-20s] 脚步特写收尾 → "干货持续更新..."
"""

import json, os, re, shutil, subprocess, glob, random, math
from collections import defaultdict
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

# ========== 配置 ==========
KEEP_DIR = r'D:\Keep轨迹素材'
XHS_DIR = r'D:\小红书素材'
OUTPUT_DIR = r'C:\Users\Administrator\Desktop\Keep跑步七年'
OUTPUT_VIDEO = os.path.join(OUTPUT_DIR, 'Keep_跑步七年_20s.mp4')
TMP_DIR = os.path.join(OUTPUT_DIR, '_frames')

FPS = 30
W, H = 1080, 1920  # 抖音竖屏

# 每段时长(帧)
SCENE_TIMING = {
    'intro_old_photo': 4 * FPS,     # 0-4s 旧照
    'footstep_slowmo': 3 * FPS,     # 4-7s 脚步
    'km_counter':      3 * FPS,     # 7-10s 数字滚动
    'keep_timeline':   4 * FPS,     # 10-14s 合集滚动
    'trail_runner':    3 * FPS,     # 14-17s 轨迹+跑者
    'footstep_end':    3 * FPS,     # 17-20s 收尾
}
TOTAL_FRAMES = sum(SCENE_TIMING.values())

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TMP_DIR, exist_ok=True)

# ========== 字体 ==========
FONT = None
for fp in [r'C:\Windows\Fonts\msyhbd.ttc', r'C:\Windows\Fonts\msyh.ttc', r'C:\Windows\Fonts\simhei.ttf']:
    if os.path.exists(fp):
        FONT = fp
        break

# ========== 找素材 ==========
print("搜索素材...")

# 旧照: IMG_ 开头的可能是旧照
old_photos = sorted([os.path.join(XHS_DIR, f) for f in os.listdir(XHS_DIR) 
                     if f.startswith('IMG_') and f.endswith('.jpg')],
                    key=lambda x: os.path.getsize(x), reverse=True)
# 也找些生活照/小红书素材
life_photos = [os.path.join(XHS_DIR, f) for f in os.listdir(XHS_DIR) 
               if f.endswith('.jpg') and not f.startswith('screenshot') and not f.startswith('Screenshot')]
# Keep截图
keep_screens = [os.path.join(XHS_DIR, f) for f in os.listdir(XHS_DIR) 
                if ('screenshot' in f.lower() or 'Screenshot' in f) and f.endswith('.jpg')]
keep_screens += [os.path.join(KEEP_DIR, f) for f in os.listdir(KEEP_DIR) 
                 if f.endswith('.jpg')]  # Keep轨迹素材

# 跑步视频(脚步特写)
run_videos = sorted([os.path.join(XHS_DIR, f) for f in os.listdir(XHS_DIR) if f.endswith('.mp4') and 'VID' in f])

# 轨迹图片(7600km那年的)
track_imgs = sorted(glob.glob(os.path.join(KEEP_DIR, '*2024*')) + glob.glob(os.path.join(KEEP_DIR, '*2025*')) + glob.glob(os.path.join(KEEP_DIR, '*2026*')))

print(f"  旧照: {len(old_photos)}张")
print(f"  生活照: {len(life_photos)}张")
print(f"  Keep截图: {len(keep_screens)}张")
print(f"  跑步视频: {len(run_videos)}个")
print(f"  轨迹图: {len(track_imgs)}张")

# 从轨迹图文件名解析数据
def parse_track_info(fp):
    fn = os.path.basename(fp)
    m = re.search(r'(\d{4})-(\d{2})-(\d{2})_([\d.]+)km_([\d.]+)min', fn)
    if m:
        return {'year': m.group(1), 'date': f"{m.group(1)}-{m.group(2)}-{m.group(3)}",
                'km': float(m.group(4)), 'min': float(m.group(5))}
    return None

# ========== 镜头1: 旧照氛围感 [0-4s] ==========
def make_scene_old_photo(frame_idx, out_path):
    """旧照+复古色调+口播标题"""
    img = Image.new('RGB', (W, H), (20, 20, 30))
    draw = ImageDraw.Draw(img)
    
    # 选一张旧照 - 稍微随机选
    photo_idx = min(frame_idx // 15, len(old_photos) - 1)
    photo_path = old_photos[photo_idx % max(1, len(old_photos))] if old_photos else None
    
    if photo_path and os.path.exists(photo_path):
        try:
            photo = Image.open(photo_path).convert('RGB')
            # 裁剪为竖屏
            pw, ph = photo.size
            target_ratio = W / H
            src_ratio = pw / ph
            
            if src_ratio > target_ratio:
                # 太宽 → 裁左右
                new_w = int(ph * target_ratio)
                x = (pw - new_w) // 2
                photo = photo.crop((x, 0, x + new_w, ph))
            else:
                # 太高 → 裁上下
                new_h = int(pw / target_ratio)
                y = (ph - new_h) // 2
                photo = photo.crop((0, y, pw, y + new_h))
            
            photo = photo.resize((W, H), Image.LANCZOS)
            
            # 复古色调滤镜: 降低饱和度 + 加暖色
            r, g, b = photo.split()
            r = r.point(lambda p: int(p * 0.95 + 30))
            g = g.point(lambda p: int(p * 0.85 + 20))
            b = b.point(lambda p: int(p * 0.75))
            photo = Image.merge('RGB', (r, g, b))
            
            # 轻微高斯模糊增加氛围感
            photo = photo.filter(ImageFilter.GaussianBlur(radius=2))
            
            # 暗角
            for i in range(H):
                dark = max(0, 1 - (min(i, H-i) / (H//2)) * 0.5)
                dark = min(dark, 0.75)  # 最大暗度
                layer = Image.new('RGB', (W, 1), (0, 0, 0))
                layer = layer.point(lambda p: int(p * (1-dark)))
                photo.paste(layer, (0, i))
            
            img.paste(photo, (0, 0))
        except Exception as e:
            print(f"  photo error: {e}")
    
    # 黑色半透明遮罩(底部文字区)
    for i in range(350):
        alpha = int(180 * (1 - i/350))
        draw.rectangle([0, i, W, i+1], fill=(0,0,0,alpha))
    
    # 文字: 第一句口播
    try:
        font_title = ImageFont.truetype(FONT, 56)
        font_sub = ImageFont.truetype(FONT, 32)
    except:
        return
    
    # 打字机效果 - 根据帧率渐显文字
    progress = frame_idx / SCENE_TIMING['intro_old_photo']
    
    texts = [
        ("坚持跑步七年，", 56, (255, 255, 255)),
        ("到底能改变一个人多少？", 52, (0, 200, 255)),
    ]
    
    y_start = 100
    for i, (text, size, color) in enumerate(texts):
        show_at = i * 0.3  # 每个0.3秒后渐出
        char_progress = max(0, min(1, (progress - show_at) * 2.5))
        char_count = int(len(text) * char_progress)
        if char_count > 0:
            shown = text[:char_count]
            try:
                font = ImageFont.truetype(FONT, size)
                bbox = draw.textbbox((0, 0), shown, font=font)
                x = (W - (bbox[2]-bbox[0])) // 2
                y = y_start + i * 80
                # 阴影
                draw.text((x+2, y+2), shown, font=font, fill=(0,0,0,160))
                draw.text((x, y), shown, font=font, fill=color)
            except:
                pass
    
    # 底部小字
    if progress > 0.5:
        try:
            font = ImageFont.truetype(FONT, 24)
            draw.text((40, H-100), "@峰峰 · Keep 七年跑者", font=font, fill=(150, 150, 150))
        except:
            pass
    
    img.save(out_path)

# ========== 镜头2: 脚步慢动作 [4-7s] ==========
def make_scene_footstep(frame_idx, out_path):
    """跑步脚步慢动作特写 + 文字"""
    img = Image.new('RGB', (W, H), (10, 10, 20))
    draw = ImageDraw.Draw(img)
    
    # 从跑步视频中取一帧做脚步背景
    if run_videos:
        vid = run_videos[0]
        # 用ffmpeg抽一帧作为脚步背景
        frame_img = os.path.join(TMP_DIR, f'_footstep_bg_{frame_idx}.jpg')
        seek_time = frame_idx / FPS  # 不同帧不同位置
        subprocess.run([
            'ffmpeg', '-y', '-ss', str(seek_time * 0.3), '-i', vid,
            '-vframes', '1', '-f', 'image2', frame_img
        ], capture_output=True, timeout=10)
        
        if os.path.exists(frame_img):
            try:
                foot = Image.open(frame_img).convert('RGB')
                foot = foot.resize((W, H), Image.LANCZOS)
                # 抽色 + 运动模糊效果
                foot = foot.filter(ImageFilter.GaussianBlur(radius=min(20, max(10, frame_idx % 15))))
                # 俯视角度加暗角
                img.paste(foot, (0, 0))
            except:
                pass
            try:
                os.remove(frame_img)
            except:
                pass
    
    # 深色叠加
    for i in range(H):
        alpha = int(100 * (1 - i/H * 0.7))
        draw.rectangle([0, i, W, i+1], fill=(0,0,0,alpha))
    
    # 文字渐入
    progress = frame_idx / SCENE_TIMING['footstep_slowmo']
    try:
        font = ImageFont.truetype(FONT, 40)
        font_sub = ImageFont.truetype(FONT, 30)
    except:
        return
    
    lines = [
        "7年前的我，",
        "迷茫又懒散，",
        "对生活提不起热情。"
    ]
    
    for i, line in enumerate(lines):
        show_at = i * 0.4
        alpha_p = max(0, min(1, (progress - show_at) * 2))
        if alpha_p > 0:
            alpha_val = int(255 * alpha_p)
            try:
                bbox = draw.textbbox((0, 0), line, font=font_sub if i == 1 else font)
                tw = bbox[2] - bbox[0]
                x = (W - tw) // 2
                y = 350 + i * 70
                draw.text((x+2, y+2), line, font=font_sub if i == 1 else font, 
                         fill=(0,0,0,alpha_val))
                draw.text((x, y), line, font=font_sub if i == 1 else font, 
                         fill=(255,255,255,alpha_val))
            except:
                pass
    
    img.save(out_path)

# ========== 镜头3: 7600km数字滚动 [7-10s] ==========
def make_scene_km_counter(frame_idx, out_path):
    """7600km数字动态滚动 + Keep轨迹缩略"""
    img = Image.new('RGB', (W, H), (5, 5, 20))
    draw = ImageDraw.Draw(img)
    
    total_frames = SCENE_TIMING['km_counter']
    progress = frame_idx / total_frames
    
    # 数字滚动：0→7600
    target_km = 7378  # 实际总里程
    current_km = int(target_km * min(1, progress * 1.3))
    
    # 背景: 模糊轨迹图
    if track_imgs:
        t_idx = int(progress * len(track_imgs)) % len(track_imgs)
        track_path = track_imgs[t_idx]
        try:
            bg = Image.open(track_path).convert('RGB')
            bg = bg.resize((W, H), Image.LANCZOS)
            bg = bg.filter(ImageFilter.GaussianBlur(radius=25))
            bg = bg.point(lambda p: int(p * 0.3))
            img.paste(bg, (0, 0))
        except:
            pass
    
    try:
        font_num = ImageFont.truetype(FONT, 160)
        font_unit = ImageFont.truetype(FONT, 48)
        font_text = ImageFont.truetype(FONT, 32)
    except:
        return
    
    # 大数字
    num_str = f"{current_km:,}"
    bbox = draw.textbbox((0, 0), num_str, font=font_num)
    x = (W - (bbox[2]-bbox[0])) // 2
    y = 500
    
    # 数字发光效果
    for dx, dy in [(0,0),(0,2),(2,0),(0,-2),(-2,0)]:
        draw.text((x+dx*3, y+dy*3), num_str, font=font_num, fill=(0,150,255,60))
    draw.text((x, y), num_str, font=font_num, fill=(0, 200, 255))
    
    # 单位
    bbox2 = draw.textbbox((0, 0), "km", font=font_unit)
    draw.text(((W - (bbox2[2]-bbox2[0]))//2, y + 170), "km", font=font_unit, fill=(255,255,255))
    
    # 底部文字
    text_lines = [
        "如今跑完7600公里，",
        "翻看Keep里数千条轨迹，",
        "心里满是感慨。"
    ]
    
    for i, line in enumerate(text_lines):
        show_at = i * 0.3
        alpha_p = max(0, min(1, (progress - show_at) * 2))
        if alpha_p > 0:
            alpha_val = int(255 * alpha_p)
            try:
                bbox = draw.textbbox((0, 0), line, font=font_text)
                tw = bbox[2] - bbox[0]
                x_t = (W - tw) // 2
                y_t = 850 + i * 55
                draw.text((x_t+2, y_t+2), line, font=font_text, 
                         fill=(0,0,0,alpha_val))
                draw.text((x_t, y_t), line, font=font_text, 
                         fill=(255,255,255,alpha_val))
            except:
                pass
    
    # 速度感装饰: 从右向左流动的线条
    for i in range(20):
        x_pos = (W + i * 80 - int(progress * 300)) % (W + 200) - 100
        y_pos = 200 + i * 60
        line_h = 1
        draw.rectangle([x_pos, y_pos, x_pos+60, y_pos+line_h], 
                      fill=(0, 200, 255, int(80 - i * 3)))
    
    img.save(out_path)

# ========== 镜头4: Keep历年合集 [10-14s] ==========
def make_scene_keep_timeline(frame_idx, out_path):
    """Keep轨迹截图横向/竖向滚动"""
    img = Image.new('RGB', (W, H), (10, 10, 25))
    draw = ImageDraw.Draw(img)
    
    total_frames = SCENE_TIMING['keep_timeline']
    progress = frame_idx / total_frames
    
    # 挑选各年的代表轨迹
    year_tracks = {}
    for fp in track_imgs:
        info = parse_track_info(fp)
        if info:
            y = info['year']
            if y not in year_tracks:
                year_tracks[y] = []
            year_tracks[y].append(fp)
    
    years = sorted(year_tracks.keys())
    
    # 竖滚动: 从下往上滑每条轨迹
    n_tracks = min(30, len(track_imgs))
    scroll_progress = progress * n_tracks
    
    item_height = 200
    item_gap = 20
    start_y = int(H - scroll_progress * item_height) + 100
    
    for i in range(n_tracks):
        idx = int(i * len(track_imgs) / n_tracks) % len(track_imgs)
        fp = track_imgs[idx]
        y_pos = int(start_y + i * (item_height + item_gap))
        
        if -item_height < y_pos < H + item_height:
            # 显示轨迹缩略图
            if os.path.exists(fp):
                try:
                    thumb = Image.open(fp).convert('RGB')
                    thumb_ratio = thumb.width / thumb.height
                    thumb_h = item_height
                    thumb_w = int(thumb_h * thumb_ratio)
                    if thumb_w > W - 200:
                        thumb_w = W - 200
                        thumb_h = int(thumb_w / thumb_ratio)
                    thumb = thumb.resize((thumb_w, thumb_h), Image.LANCZOS)
                    x = (W - thumb_w) // 2
                    img.paste(thumb, (x, y_pos))
                    
                    # 信息标签
                    info = parse_track_info(fp)
                    if info:
                        try:
                            font_s = ImageFont.truetype(FONT, 18)
                            label = f"{info['date']}  {info['km']:.1f}km"
                            draw.text((x + 10, y_pos + 5), label, font=font_s, fill=(0,200,255,200))
                        except:
                            pass
                except:
                    pass
    
    # 标题(固定)
    try:
        font_title = ImageFont.truetype(FONT, 48)
        font_sub = ImageFont.truetype(FONT, 30)
    except:
        return
    
    draw.text(((W-400)//2, 30), "一路走来", font=font_title, fill=(255,255,255))
    draw.text(((W-500)//2, 100), "从抗拒到热爱，从浮躁到平静", font=font_sub, fill=(0,200,255))
    
    if progress > 0.6:
        draw.text(((W-550)//2, H-200), "跑步不仅练了身体，更治愈了内心", font=font_sub, fill=(255,255,255))
    
    img.save(out_path)

# ========== 镜头5: 轨迹+跑者 [14-17s] ==========
def make_scene_trail_runner(frame_idx, out_path):
    """轨迹地图叠加 + 跑者剪影 + 金句"""
    img = Image.new('RGB', (W, H), (5, 5, 20))
    draw = ImageDraw.Draw(img)
    
    total_frames = SCENE_TIMING['trail_runner']
    progress = frame_idx / total_frames
    
    # 用最大的一张轨迹图做底
    big_track = None
    for fp in track_imgs:
        info = parse_track_info(fp)
        if info and info['km'] > 25:
            big_track = fp
            break
    if not big_track and track_imgs:
        big_track = track_imgs[len(track_imgs)//2]
    
    if big_track:
        try:
            bg = Image.open(big_track).convert('RGB')
            bg = bg.resize((W, H), Image.LANCZOS)
            bg = bg.point(lambda p: int(p * 0.25))
            img.paste(bg, (0, 0))
        except:
            pass
    
    # 网格线装饰 (类似地图)
    for i in range(0, W, 40):
        draw.line([(i, 0), (i, H)], fill=(0, 200, 255, 20))
    for i in range(0, H, 40):
        draw.line([(0, i), (W, i)], fill=(0, 200, 255, 20))
    
    # 速度线动画
    for i in range(15):
        x = int((W/2) - 200 + progress * 400 + i * 30) % W
        draw.line([(x, 500+i*40), (x+80, 500+i*40)], 
                 fill=(0, 200, 255, int(100-i*5)))
    
    try:
        font_main = ImageFont.truetype(FONT, 44)
        font_sub = ImageFont.truetype(FONT, 28)
    except:
        return
    
    # 金句
    texts = [
        ("普通人最好的翻盘，", 44, (255,255,255)),
        ("就是日复一日的坚持。", 44, (0, 200, 255)),
    ]
    
    for i, (text, size, color) in enumerate(texts):
        show_at = i * 0.35
        alpha_p = max(0, min(1, (progress - show_at) * 2))
        if alpha_p > 0:
            try:
                font = ImageFont.truetype(FONT, size)
                bbox = draw.textbbox((0, 0), text, font=font)
                x = (W - (bbox[2]-bbox[0])) // 2
                y = 400 + i * 80
                alpha_v = int(255 * alpha_p)
                draw.text((x+2, y+2), text, font=font, fill=(0,0,0,alpha_v))
                draw.text((x, y), text, font=font, fill=color + (alpha_v,))
            except:
                pass

    # 底部
    if progress > 0.5:
        draw.text(((W-400)//2, H-150), "@峰峰 · Keep", font=font_sub, fill=(150,150,150))
    
    img.save(out_path)

# ========== 镜头6: 收尾 [17-20s] ==========
def make_scene_footstep_end(frame_idx, out_path):
    """脚步特写 + 引导关注"""
    img = Image.new('RGB', (W, H), (10, 10, 20))
    draw = ImageDraw.Draw(img)
    
    total_frames = SCENE_TIMING['footstep_end']
    progress = frame_idx / total_frames
    
    # 用跑步视频的最后一帧
    if run_videos:
        vid = run_videos[-1]
        frame_img = os.path.join(TMP_DIR, f'_foot_end_bg_{frame_idx}.jpg')
        subprocess.run([
            'ffmpeg', '-y', '-ss', str(1.0 + frame_idx/FPS * 0.5), '-i', vid,
            '-vframes', '1', '-f', 'image2', frame_img
        ], capture_output=True, timeout=10)
        
        if os.path.exists(frame_img):
            try:
                foot = Image.open(frame_img).convert('RGB')
                foot = foot.resize((W, H), Image.LANCZOS)
                foot = foot.point(lambda p: int(p * 0.4))
                img.paste(foot, (0, 0))
            except:
                pass
            try:
                os.remove(frame_img)
            except:
                pass
    
    try:
        font_main = ImageFont.truetype(FONT, 40)
        font_sub = ImageFont.truetype(FONT, 28)
    except:
        return
    
    # 渐入文字
    texts = [
        "干货持续更新，普通人跑步自律",
        "我帮你少走弯路 [跑鞋]",
    ]
    
    for i, (text, size2, color) in enumerate([(texts[0], 40, (255,255,255)), (texts[1], 36, (0, 200, 255))]):
        alpha_p = max(0, min(1, (progress - i * 0.3) * 2))
        if alpha_p > 0:
            try:
                font = ImageFont.truetype(FONT, size2)
                bbox = draw.textbbox((0, 0), text, font=font)
                x = (W - (bbox[2]-bbox[0])) // 2
                y = 500 + i * 70
                alpha_v = int(255 * alpha_p)
                draw.text((x+2, y+2), text, font=font, fill=(0,0,0,alpha_v))
                draw.text((x, y), text, font=font, fill=color + (alpha_v,))
            except:
                pass
    
    # log
    draw.text(((W-300)//2, H-300), "Keep 2018-2026", font=font_sub, fill=(100,100,100))
    draw.text(((W-300)//2, H-260), "7,378 km · 766 次", font=font_sub, fill=(100,100,100))
    
    # 关注按钮
    btn_w, btn_h = 300, 60
    bx = (W - btn_w) // 2
    by = H - 150
    draw.rounded_rectangle([bx, by, bx+btn_w, by+btn_h], radius=30, fill=(0, 200, 255, 200))
    draw.text((bx+70, by+10), "  关注 →", font=font_sub, fill=(0,0,0))
    
    img.save(out_path)

# ========== 主循环: 生成所有帧 ==========
print("\n生成帧画面...")
scene_funcs = [
    ('intro_old_photo', make_scene_old_photo),
    ('footstep_slowmo', make_scene_footstep),
    ('km_counter', make_scene_km_counter),
    ('keep_timeline', make_scene_keep_timeline),
    ('trail_runner', make_scene_trail_runner),
    ('footstep_end', make_scene_footstep_end),
]

frame_list_path = os.path.join(TMP_DIR, 'frames.txt')
frame_lines = []
global_idx = 0

for scene_name, scene_func in scene_funcs:
    n_frames = SCENE_TIMING[scene_name]
    print(f"  [{scene_name}] {n_frames}帧...")
    
    for i in range(n_frames):
        fp = os.path.join(TMP_DIR, f'frame_{global_idx:06d}.png')
        # 每10帧做一个不同的画面，其余复用（提速）
        if i % 8 == 0 or scene_name == 'km_counter':  # 数字滚动每帧都需要
            scene_func(i, fp)
        else:
            # 复用最近一帧
            prev_fp = os.path.join(TMP_DIR, f'frame_{global_idx-1:06d}.png')
            if os.path.exists(prev_fp):
                shutil.copy2(prev_fp, fp)
        
        frame_lines.append(f"file 'frame_{global_idx:06d}.png'\nduration 0.0333333")
        global_idx += 1
    
    print(f"  [ok] {scene_name} done")

# 写入帧序列文件
with open(frame_list_path, 'w') as f:
    f.write('\n'.join(frame_lines))

print(f"\n总帧数: {global_idx} ({global_idx/FPS:.1f}秒)")

# ========== 合成视频 ==========
print("\n合成视频...")
raw_video = os.path.join(TMP_DIR, 'raw_video.mp4')

subprocess.run([
    'ffmpeg', '-y',
    '-f', 'concat',
    '-safe', '0',
    '-i', frame_list_path,
    '-c:v', 'libx264',
    '-pix_fmt', 'yuv420p',
    '-preset', 'medium',
    '-crf', '20',
    '-r', str(FPS),
    raw_video
], check=True, capture_output=True)

# 加纯音轨
subprocess.run([
    'ffmpeg', '-y',
    '-i', raw_video,
    '-f', 'lavfi', '-t', str(TOTAL_FRAMES/FPS),
    '-i', 'anullsrc=r=44100:cl=mono',
    '-c:v', 'copy',
    '-c:a', 'aac',
    '-shortest',
    OUTPUT_VIDEO
], check=True, capture_output=True)

# 清理中间帧
shutil.rmtree(TMP_DIR, ignore_errors=True)

# 输出信息
dur = TOTAL_FRAMES / FPS
size_mb = os.path.getsize(OUTPUT_VIDEO) / 1024 / 1024
print(f"\n✅ 视频生成完成!")
print(f"  File: {OUTPUT_VIDEO}")
print(f"  Duration: {dur:.1f}s | {W}x{H} | Size: {size_mb:.1f}MB")
