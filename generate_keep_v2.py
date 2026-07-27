#!/usr/bin/env python3
"""
Keep 七年跑步 · 情绪短片 (v2)
重新设计镜头:
  [0-3s]   旧照氛围感 — bgm前奏
  [3-6s]   跑步脚步慢动作特写 (真实跑步视频)  
  [6-10s]  7600km数字翻牌动画 (一帧一帧翻)
  [10-14s] 轨迹截图逐条划过 + 路线标注
  [14-17s] 1800天坚持数据 + 情绪高潮
  [17-20s] 脚步特写收尾 + 金句
"""

import json, os, re, shutil, subprocess, glob, math
from collections import defaultdict
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ========== 配置 ==========
KEEP_DIR = r'D:\Keep轨迹素材'
XHS_DIR = r'D:\小红书素材'
OUTPUT_DIR = r'C:\Users\Administrator\Desktop\Keep跑步七年'
OUTPUT_VIDEO = os.path.join(OUTPUT_DIR, 'Keep_七年跑步_20s_v2.mp4')
TMP_DIR = os.path.join(OUTPUT_DIR, '_frames_v2')

FPS = 30
W, H = 1080, 1920

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TMP_DIR, exist_ok=True)

# 字体
FONT = None
for fp in [r'C:\Windows\Fonts\msyhbd.ttc', r'C:\Windows\Fonts\msyh.ttc', r'C:\Windows\Fonts\simhei.ttf']:
    if os.path.exists(fp):
        FONT = fp
        break

# ========== 找素材 ==========
print("搜索素材...")

# 旧照
old_photos = sorted(glob.glob(os.path.join(XHS_DIR, 'IMG_*.jpg')))
# 跑步视频
run_videos = sorted(glob.glob(os.path.join(XHS_DIR, 'VID_2026*.mp4')))
wx_video = os.path.join(XHS_DIR, 'wx_camera_1750503011375.mp4')
petal_video = os.path.join(XHS_DIR, 'petal_hdr_20250503_164048.mp4')
# 轨迹截图
all_tracks = sorted(glob.glob(os.path.join(KEEP_DIR, '*', '*.jpg')))
# keep截图
keep_screens = [os.path.join(XHS_DIR, 'screenshot_20260607_181201_com.gotokeep.hm.keep.jpg'),
                os.path.join(XHS_DIR, 'Screenshot_20241027_192652_co.runner.app.jpg')]

print(f"旧照: {len(old_photos)}  跑步视频: {len(run_videos)}  轨迹图: {len(all_tracks)}")

# 解析所有轨迹文件名
def parse_track(fp):
    fn = os.path.basename(fp)
    m = re.search(r'(\d{4})-(\d{2})-(\d{2})_([\d.]+)km_([\d.]+)min', fn)
    if m:
        return {'year': m.group(1), 'date': f"{m.group(1)}-{m.group(2)}-{m.group(3)}",
                'km': float(m.group(4)), 'min': float(m.group(5))}
    return None

# 按年份收集
year_tracks = defaultdict(list)
for fp in all_tracks:
    info = parse_track(fp)
    if info:
        year_tracks[info['year']].append((fp, info))

# 从轨迹截图里挑每年前几大
year_best = {}
for year, items in year_tracks.items():
    items.sort(key=lambda x: x[1]['km'], reverse=True)
    year_best[year] = items[:8]  # 每年最多8条

# 用所有年份总里程
total_km = sum(sum(info['km'] for _, info in items) for items in year_tracks.values())

print(f"总里程: {total_km:.0f}km  年份: {sorted(year_tracks.keys())}")

# ========== 工具函数 ==========
def make_bg_blur(track_path):
    """生成模糊背景"""
    canvas = Image.new('RGB', (W, H), (8, 8, 25))
    if track_path and os.path.exists(track_path):
        try:
            bg = Image.open(track_path).convert('RGB')
            bg = bg.resize((W, H), Image.LANCZOS)
            bg = bg.filter(ImageFilter.GaussianBlur(radius=35))
            bg = bg.point(lambda p: int(p * 0.3))
            canvas.paste(bg, (0, 0))
        except:
            pass
    return canvas

# ========== 镜头1: 旧照 [0-3s] ==========
def scene_old_photo(frame_idx, total_frames, out_path):
    progress = frame_idx / total_frames
    
    # 淡入效果
    img = make_bg_blur(None)
    draw = ImageDraw.Draw(img)
    
    # 放一张旧照
    if old_photos:
        idx = min(int(progress * len(old_photos)), len(old_photos) - 1)
        try:
            photo = Image.open(old_photos[idx]).convert('RGB')
            pw, ph = photo.size
            s = min(W/pw, H/ph) * 0.9
            nw, nh = int(pw*s), int(ph*s)
            photo = photo.resize((nw, nh), Image.LANCZOS)
            # 裁剪或居中
            if nw > W:
                x = (nw - W) // 2
                photo = photo.crop((x, 0, x+W, nh))
                nh = W * nh // nw
                nw = W
            x = (W - nw) // 2
            y = (H - nh) // 2 - 100
            # 高斯模糊暗角
            photo = photo.filter(ImageFilter.GaussianBlur(radius=1.5))
            photo = photo.point(lambda p: int(p * 0.7 + 20))
            img.paste(photo, (x, y))
        except:
            pass
    
    # 顶部半透明遮罩
    for i in range(250):
        alpha = int(160 * (1 - i/250))
        draw.rectangle([0, i, W, i+1], fill=(0,0,0,alpha))
    
    # 白色边框装饰
    draw.rectangle([30, 450, W-30, 550], fill=None, outline=(255,255,255,40), width=1)
    
    # 文字: 第一句
    try:
        ft = ImageFont.truetype(FONT, 50 if len("坚持跑步七年") < 10 else 42)
        fs = ImageFont.truetype(FONT, 32)
    except:
        return
    
    # 打字效果
    chars1 = "坚持跑步七年，"
    chars2 = "到底能改变一个人多少？"
    
    n1 = min(len(chars1), int(len(chars1) * progress * 2.5))
    n2 = max(0, min(len(chars2), int(len(chars2) * (progress - 0.35) * 2.5)))
    
    shown1 = chars1[:n1]
    shown2 = chars2[:n2]
    
    if shown1:
        bbox = draw.textbbox((0,0), shown1, font=ft)
        dx = (W - (bbox[2]-bbox[0])) // 2
        draw.text((dx+2, 460+2), shown1, font=ft, fill=(0,0,0,180))
        draw.text((dx, 460), shown1, font=ft, fill=(255,255,255))
    
    if shown2:
        bbox = draw.textbbox((0,0), shown2, font=ft)
        dx = (W - (bbox[2]-bbox[0])) // 2
        draw.text((dx+2, 530+2), shown2, font=ft, fill=(0,0,0,180))
        draw.text((dx, 530), shown2, font=ft, fill=(0,200,255))
    
    img.save(out_path)

# ========== 镜头2: 跑步脚步慢动作 [3-6s] ==========
def scene_footstep(frame_idx, total_frames, out_path):
    progress = frame_idx / total_frames
    img = make_bg_blur(None)
    draw = ImageDraw.Draw(img)
    
    # 从跑步视频中截取慢动作帧
    if run_videos:
        vid = run_videos[frame_idx % len(run_videos)]
        # 慢动作: 缓慢推进
        seek_t = (frame_idx / total_frames) * 2.0  # 只取前2秒的视频
        frame_jpg = os.path.join(TMP_DIR, f'_foot_{frame_idx}.jpg')
        subprocess.run(['ffmpeg','-y','-ss',str(seek_t),'-i',vid,
                       '-vframes','1','-q:v','2','-f','image2',frame_jpg],
                      capture_output=True, timeout=10)
        if os.path.exists(frame_jpg):
            try:
                foot = Image.open(frame_jpg).convert('RGB')
                # 裁剪中间区域（脚步位置一般是下半部分）
                fw, fh = foot.size
                foot = foot.crop((0, int(fh*0.3), fw, int(fh*0.85)))
                foot = foot.resize((W, H), Image.LANCZOS)
                # 去色 + 增强对比
                foot = foot.convert('L').convert('RGB')
                foot = foot.point(lambda p: int(p * 1.1 + 10))
                # 暗角
                for i in range(H):
                    dark = max(0, 1 - (min(i, H-i) / (H//2)) * 0.4)
                    layer = Image.new('RGB', (W, 1), tuple(int(c * max(0.4, dark)) for c in (0,0,0)))
                    foot.paste(layer, (0, i))
                img.paste(foot, (0, 0))
            except:
                pass
            try:
                os.remove(frame_jpg)
            except:
                pass
    
    try:
        ft = ImageFont.truetype(FONT, 36)
    except:
        return
    
    lines = ["7年前的我，", "迷茫又懒散，", "对生活提不起热情。"]
    for i, line in enumerate(lines):
        show_at = i * 0.3
        a = max(0, min(1, (progress - show_at) * 2.5))
        if a > 0:
            c = int(255 * a)
            bbox = draw.textbbox((0,0), line, font=ft)
            dx = (W - (bbox[2]-bbox[0])) // 2
            draw.text((dx+2, 400+i*70+2), line, font=ft, fill=(0,0,0,c))
            draw.text((dx, 400+i*70), line, font=ft, fill=(255,255,255,c))
    
    img.save(out_path)

# ========== 镜头3: 7600km数字翻牌 [6-10s] ==========
def scene_km_counter(frame_idx, total_frames, out_path):
    progress = frame_idx / total_frames
    img = make_bg_blur(all_tracks[len(all_tracks)//2] if all_tracks else None)
    draw = ImageDraw.Draw(img)
    
    # 数字翻牌效果: 每一位独立翻转
    target = int(total_km)
    
    # 将数字拆成每一位
    target_str = str(target)
    n_digits = len(target_str)
    
    try:
        fnum = ImageFont.truetype(FONT, 130)
        fcom = ImageFont.truetype(FONT, 80)
        ftext = ImageFont.truetype(FONT, 32)
    except:
        return
    
    # 每个数字位独立滚动
    digits_shown = []
    for i, ch in enumerate(target_str):
        digit_val = int(ch)
        # 每位从0滚到目标值
        digit_progress = progress * 2.5 - i * 0.12  # 每位延迟0.12秒
        digit_progress = max(0, min(1, digit_progress))
        current_digit = int(digit_val * digit_progress)
        digits_shown.append(str(current_digit))
    
    shown = ''.join(digits_shown)
    
    # 发光大数字
    bbox = draw.textbbox((0,0), shown, font=fnum)
    dx = (W - (bbox[2]-bbox[0])) // 2
    dy = 500
    
    # 多层发光
    for lw in range(8):
        alpha = 60 - lw * 7
        if alpha > 0:
            draw.text((dx+lw, dy), shown, font=fnum, fill=(0, 150, 255, max(0, alpha)))
            draw.text((dx-lw, dy), shown, font=fnum, fill=(0, 150, 255, max(0, alpha)))
    draw.text((dx, dy), shown, font=fnum, fill=(0, 200, 255))
    
    # km 单位
    draw.text((dx + (bbox[2]-bbox[0]) + 20, dy + 40), "km", font=fcom, fill=(255,255,255))
    
    if progress > 0.4:
        lines = ["如今跑完7600公里，", "翻看Keep里数千条轨迹，", "心里满是感慨。"]
        for i, line in enumerate(lines):
            a = max(0, min(1, (progress - 0.4 - i*0.25) * 2.5))
            if a > 0:
                c = int(255 * a)
                bbox = draw.textbbox((0,0), line, font=ftext)
                dx2 = (W - (bbox[2]-bbox[0])) // 2
                draw.text((dx2+2, 820+i*50+2), line, font=ftext, fill=(0,0,0,c))
                draw.text((dx2, 820+i*50), line, font=ftext, fill=(255,255,255,c))
    
    img.save(out_path)

# ========== 镜头4: 轨迹截图划过+路线标注 [10-14s] ==========
def scene_tracks_scroll(frame_idx, total_frames, out_path):
    progress = frame_idx / total_frames
    img = Image.new('RGB', (W, H), (5, 5, 20))
    draw = ImageDraw.Draw(img)
    
    # 将所有轨迹按年份排列，横向/竖向滚动
    years = sorted(year_tracks.keys())
    
    try:
        ft_yr = ImageFont.truetype(FONT, 60)
        ft_info = ImageFont.truetype(FONT, 26)
    except:
        return
    
    # 竖向滚动：每条轨迹显示2.5帧
    track_speed = 3.5  # 每条显示帧数
    all_items = []
    for year in years:
        for item in year_tracks.get(year, []):
            all_items.append((year, item))
    
    if not all_items:
        img.save(out_path)
        return
    
    current_idx = int(progress * len(all_items))
    scroll_offset = (progress * len(all_items) * track_speed * 200) % (H + 1000)
    
    # 背景模糊
    bg_track = all_items[current_idx % len(all_items)][1][0]
    canvas = make_bg_blur(bg_track)
    draw = ImageDraw.Draw(canvas)
    
    # 轨迹缩略图竖向排列
    for i in range(current_idx - 1, min(current_idx + 6, len(all_items))):
        if i < 0:
            continue
        year, (fp, info) = all_items[i]
        y_pos = H - ((current_idx - i) * 220 + scroll_offset % 220)
        
        if -200 < y_pos < H + 100:
            x_pos = 100
            try:
                thumb = Image.open(fp).convert('RGB')
                tw, th = thumb.size
                thumb_h = 180
                thumb_w = int(tw * thumb_h / th)
                if thumb_w > W - 2*x_pos:
                    thumb_w = W - 2*x_pos
                    thumb_h = int(th * thumb_w / tw)
                thumb = thumb.resize((thumb_w, thumb_h), Image.LANCZOS)
                
                # 边框背景
                draw.rounded_rectangle([x_pos-5, y_pos-5, x_pos+thumb_w+5, y_pos+thumb_h+5],
                                      radius=8, fill=(0,0,0,120))
                canvas.paste(thumb, (x_pos, y_pos))
                
                # 标签
                label = f"{info['date']}  {info['km']:.1f}km"
                draw.text((x_pos+8, y_pos+8), label, font=ft_info, fill=(0,200,255,220))
                
                # 年份标签(仅第一条)
                if i == current_idx or info['date'].startswith(year) and i == 0:
                    pass
            except:
                pass
    
    # 固定年份(当前)
    if current_idx < len(all_items):
        cy = all_items[current_idx][0]
        draw.text((200, 30), cy, font=ft_yr, fill=(0, 200, 255))
    
    # 底部文字
    if progress > 0.5:
        line = "从抗拒到热爱，从浮躁到平静"
        try:
            font = ImageFont.truetype(FONT, 36)
            bbox = draw.textbbox((0,0), line, font=font)
            dx = (W - (bbox[2]-bbox[0])) // 2
            draw.text((dx, H-200), line, font=font, fill=(255,255,255))
        except:
            pass
    
    canvas.save(out_path)

# ========== 镜头5: 数据高潮+金句 [14-17s] ==========
def scene_highlights(frame_idx, total_frames, out_path):
    progress = frame_idx / total_frames
    img = make_bg_blur(all_tracks[-1] if all_tracks else None)
    draw = ImageDraw.Draw(img)
    
    try:
        ft_num = ImageFont.truetype(FONT, 90)
        ft_unit = ImageFont.truetype(FONT, 40)
        ft_text = ImageFont.truetype(FONT, 36)
    except:
        return
    
    # 四个数据
    data_items = [
        (f"{total_km:.0f}", "公里"),
        ("7", "年"),
        ("766", "次"),
        ("204607", "千卡"),
    ]
    
    # 2x2 网格
    for i, (num, unit) in enumerate(data_items):
        col = i % 2
        row = i // 2
        ap = max(0, min(1, (progress - i * 0.12) * 2.5))
        if ap > 0:
            x = 150 + col * 430
            y = 350 + row * 220
            c = int(255 * ap)
            # 数字
            bbox = draw.textbbox((0,0), num, font=ft_num)
            draw.text((x, y), num, font=ft_num, fill=(0, 200, 255, c))
            # 单位
            draw.text((x + (bbox[2]-bbox[0]) + 15, y + 30), unit, font=ft_unit, fill=(255,255,255,c))
            # 横线
            draw.rectangle([x, y+85, x+160, y+87], fill=(255,255,255,max(0,c-100)))
    
    # 金句
    if progress > 0.45:
        lines = ["跑步不仅练了身体，", "更治愈了内心。", "", "普通人最好的翻盘，", "就是日复一日的坚持。"]
        try:
            ft = ImageFont.truetype(FONT, 38)
            for i, line in enumerate(lines):
                a = max(0, min(1, (progress - 0.45 - i*0.12) * 3))
                if a > 0:
                    c = int(255 * a)
                    bbox = draw.textbbox((0,0), line, font=ft)
                    dx = (W - (bbox[2]-bbox[0])) // 2
                    draw.text((dx+2, 1050+i*55+2), line, font=ft, fill=(0,0,0,c))
                    draw.text((dx, 1050+i*55), line, font=ft, fill=(255,255,255,c))
        except:
            pass
    
    img.save(out_path)

# ========== 镜头6: 收尾 [17-20s] ==========
def scene_ending(frame_idx, total_frames, out_path):
    progress = frame_idx / total_frames
    img = make_bg_blur(None)
    draw = ImageDraw.Draw(img)
    
    # 最后一帧跑步视频
    if run_videos:
        vid = run_videos[-1]
        seek_t = 8.0 + progress * 3.0
        frame_jpg = os.path.join(TMP_DIR, f'_end_{frame_idx}.jpg')
        subprocess.run(['ffmpeg','-y','-ss',str(seek_t),'-i',vid,
                       '-vframes','1','-q:v','2','-f','image2',frame_jpg],
                      capture_output=True, timeout=10)
        if os.path.exists(frame_jpg):
            try:
                foot = Image.open(frame_jpg).convert('RGB')
                foot = foot.resize((W, H), Image.LANCZOS)
                foot = foot.point(lambda p: int(p * 0.45 + 10))
                img.paste(foot, (0, 0))
            except:
                pass
            try:
                os.remove(frame_jpg)
            except:
                pass
    
    try:
        ft = ImageFont.truetype(FONT, 40)
        fs = ImageFont.truetype(FONT, 28)
    except:
        return
    
    # 底部固定
    # 脚步视频帧已经在上面用ffmpeg抽过了，不需要重复
    
    lines = ["干货持续更新，普通人跑步自律", "我帮你少走弯路"]
    for i, line in enumerate(lines):
        a = max(0, min(1, (progress - i*0.25) * 2.5))
        if a > 0:
            c = int(255 * a)
            ft_use = ft if i == 0 else fs
            bbox = draw.textbbox((0,0), line, font=ft_use)
            dx = (W - (bbox[2]-bbox[0])) // 2
            draw.text((dx+2, 600+i*70+2), line, font=ft_use, fill=(0,0,0,c))
            if i == 0:
                draw.text((dx, 600+i*70), line, font=ft_use, fill=(255,255,255,c))
            else:
                draw.text((dx, 600+i*70), line, font=ft_use, fill=(0,200,255,c))
    
    # 关注按钮
    if progress > 0.6:
        btn_w, btn_h = 280, 56
        bx = (W - btn_w) // 2
        by = H - 180
        draw.rounded_rectangle([bx, by, bx+btn_w, by+btn_h], radius=28, fill=(0,200,255))
        draw.text((bx+btn_w//2-45, by+8), "关 注", font=fs, fill=(0,0,0))
    
    img.save(out_path)

# ========== 主循环 ==========
scenes = [
    ('old_photo', scene_old_photo, 3*FPS),
    ('footstep', scene_footstep, 3*FPS),
    ('km_counter', scene_km_counter, 4*FPS),
    ('tracks_scroll', scene_tracks_scroll, 4*FPS),
    ('highlights', scene_highlights, 3*FPS),
    ('ending', scene_ending, 3*FPS),
]

frame_lines = []
global_idx = 0

print("\n生成帧...")

for scene_name, scene_func, n_frames in scenes:
    print(f"  [{scene_name}] {n_frames}帧...")
    for i in range(n_frames):
        fp = os.path.join(TMP_DIR, f'f_{global_idx:06d}.png')
        scene_func(i, n_frames, fp)
        frame_lines.append(f"file 'f_{global_idx:06d}.png'\nduration 0.0333333")
        global_idx += 1
    print(f"    done")

print(f"\n总帧数: {global_idx} ({global_idx/FPS:.1f}s)")

# 写入帧序列
with open(os.path.join(TMP_DIR, 'frames.txt'), 'w') as f:
    f.write('\n'.join(frame_lines))

# 合成视频
print("合成视频...")
raw = os.path.join(TMP_DIR, 'raw.mp4')
subprocess.run(['ffmpeg','-y','-f','concat','-safe','0',
               '-i',os.path.join(TMP_DIR, 'frames.txt'),
               '-c:v','libx264','-pix_fmt','yuv420p',
               '-preset','fast','-crf','20','-r',str(FPS),raw],
              check=True, capture_output=True)

# 加音轨(空白)
subprocess.run(['ffmpeg','-y','-i',raw,
               '-f','lavfi','-t',str(global_idx/FPS),
               '-i','anullsrc=r=44100:cl=mono',
               '-c:v','copy','-c:a','aac','-shortest',OUTPUT_VIDEO],
              check=True, capture_output=True)

# 清临时帧
shutil.rmtree(TMP_DIR, ignore_errors=True)

size = os.path.getsize(OUTPUT_VIDEO) / 1024 / 1024
print(f"\n[OK] 视频生成完成!")
print(f"  File: {OUTPUT_VIDEO}")
print(f"  {global_idx/FPS:.1f}s | {W}x{H} | {size:.1f}MB")
