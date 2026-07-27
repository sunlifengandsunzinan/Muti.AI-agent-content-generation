#!/usr/bin/env python3
"""
Keep 七年跑步 · 情绪短片 v3
镜头设计（按你一步一步说好的）:
  [0-3s]   开场：用VID_20260608_183422.mp4真实跑步视频做开头
           "坚持跑步七年，到底能改变一个人多少？"
  [3-6s]   反差：image_1780734672485 (胖橙色衣服) → 49b5e14b (接力棒瘦照)
           "7年前的我，迷茫又懒散，对生活提不起热情。"
  [6-10s]  7600km：展示总里程截图 + 数字翻牌
           "如今跑完7600公里，翻看Keep里数千条轨迹，心里满是感慨。"
  [10-14s] Keep数据回放：轨迹截图逐条划过
           "一路走来，从抗拒到热爱，从浮躁到平静，跑步..."
  [14-17s] 数据高潮：7378km/7年/766次
           "...不仅练了身体，更治愈了内心。普通人最好的翻盘..."
  [17-20s] 收尾：回到IMG_20240701 (跑渣照) + 脚步视频无正脸
           "干货持续更新，普通人跑步自律，我帮你少走弯路"
"""

import os, re, shutil, subprocess, glob, math
from collections import defaultdict
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

# ========== 配置 ==========
KEEP_DIR = r'D:\Keep轨迹素材'
XHS_DIR = r'D:\小红书素材'
OUTPUT_DIR = r'C:\Users\Administrator\Desktop\Keep跑步七年'
OUTPUT_VIDEO = os.path.join(OUTPUT_DIR, 'Keep_七年跑步_20s_v3.mp4')
TMP_DIR = os.path.join(OUTPUT_DIR, '_frames_v3')

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

# ========== 素材文件 ==========
OPENING_VIDEO = os.path.join(XHS_DIR, 'VID_20260608_183422.mp4')       # 开场真实跑步视频
FAT_PHOTO = os.path.join(XHS_DIR, 'image_1780734672485.jpg')            # 橙色衣服胖照
RUNNER_PHOTO = os.path.join(XHS_DIR, '49b5e14b-30e5-4049-99fb-71046a8a802b.png')  # 接力棒瘦照
END_PHOTO = os.path.join(XHS_DIR, 'IMG_20240701_214942.jpg')            # 结尾跑渣照
TOTAL_KM_SCREEN = os.path.join(XHS_DIR, 'screenshot_20260607_181201_com.gotokeep.hm.keep.jpg') # 总里程截图
FOOTSTEP_VIDEO = os.path.join(XHS_DIR, 'VID_20260608_185000.mp4')       # 脚步视频(结尾用)

# Keep轨迹截图
all_tracks = sorted(glob.glob(os.path.join(KEEP_DIR, '*', '*.jpg')))

# 解析轨迹
def parse_track(fp):
    fn = os.path.basename(fp)
    m = re.search(r'(\d{4})-(\d{2})-(\d{2})_([\d.]+)km_([\d.]+)min', fn)
    if m:
        return {'year': m.group(1), 'date': f"{m.group(1)}-{m.group(2)}-{m.group(3)}",
                'km': float(m.group(4)), 'min': float(m.group(5))}
    return None

year_tracks = defaultdict(list)
for fp in all_tracks:
    info = parse_track(fp)
    if info:
        year_tracks[info['year']].append((fp, info))

total_km = sum(sum(info['km'] for _, info in items) for items in year_tracks.values())
print(f"总里程: {total_km:.0f}km  年份: {sorted(year_tracks.keys())}  轨迹: {len(all_tracks)}张")

# ========== 工具函数 ==========
def make_bg_blur(track_path=None, dark_factor=0.3):
    canvas = Image.new('RGB', (W, H), (8, 8, 25))
    if track_path and os.path.exists(track_path):
        try:
            bg = Image.open(track_path).convert('RGB')
            bg = bg.resize((W, H), Image.LANCZOS)
            bg = bg.filter(ImageFilter.GaussianBlur(radius=35))
            bg = bg.point(lambda p: int(p * dark_factor))
            canvas.paste(bg, (0, 0))
        except:
            pass
    return canvas

def load_still_frame(video_path, seek_time):
    """从视频抽一帧"""
    out = os.path.join(TMP_DIR, f'_vf_{os.path.basename(video_path)}_{int(seek_time*100)}.jpg')
    if not os.path.exists(out):
        subprocess.run(['ffmpeg','-y','-ss',str(seek_time),'-i',video_path,
                       '-vframes','1','-q:v','2','-f','image2',out],
                      capture_output=True, timeout=10)
    if os.path.exists(out):
        return Image.open(out).convert('RGB')
    return None

def resize_fill(img, target_w, target_h):
    """等比例裁剪填充到目标尺寸"""
    w, h = img.size
    src_ratio = w / h
    dst_ratio = target_w / target_h
    if src_ratio > dst_ratio:
        new_w = int(h * dst_ratio)
        x = (w - new_w) // 2
        img = img.crop((x, 0, x + new_w, h))
    else:
        new_h = int(w / dst_ratio)
        y = (h - new_h) // 2
        img = img.crop((0, y, w, y + new_h))
    return img.resize((target_w, target_h), Image.LANCZOS)

# ========== 镜头1: 开场真实视频 [0-3s] ==========
def scene_opening(frame_idx, total_frames, out_path):
    progress = frame_idx / total_frames
    
    # 从开场视频里截取自然跑步画面
    seek_start = 0.5  # 从0.5秒开始取，避免黑场
    seek_end = 14.0    # 最多取到14秒
    seek_t = seek_start + progress * min(seek_end - seek_start, total_frames/FPS * 1.5)
    
    frame = load_still_frame(OPENING_VIDEO, seek_t)
    
    if frame:
        # 视频是1920x1080横向，裁剪成竖屏
        frame = resize_fill(frame, W, H)
        # 自然色调，不做过度处理
        img = frame
    else:
        img = make_bg_blur()
    
    draw = ImageDraw.Draw(img)
    
    # 底部半透明遮罩
    for i in range(300):
        alpha = int(180 * (1 - i/300))
        draw.rectangle([0, H-300+i, W, H-300+i+1], fill=(0,0,0,alpha))
    
    try:
        ft = ImageFont.truetype(FONT, 48)
    except:
        return
    
    # 打字效果
    line1 = "坚持跑步七年，"
    line2 = "到底能改变一个人多少？"
    
    n1 = min(len(line1), int(len(line1) * progress * 2.8))
    n2 = max(0, min(len(line2), int(len(line2) * max(0, progress - 0.35) * 2.8)))
    
    for shown, text, color, y_base in [
        (n1, line1, (255,255,255), H-250),
        (n2, line2, (0,200,255), H-170)
    ]:
        if shown > 0:
            txt = text[:shown]
            bbox = draw.textbbox((0,0), txt, font=ft)
            dx = (W - (bbox[2]-bbox[0])) // 2
            draw.text((dx+2, y_base+2), txt, font=ft, fill=(0,0,0,180))
            draw.text((dx, y_base), txt, font=ft, fill=color)
    
    img.save(out_path)

# ========== 镜头2: 胖照→瘦照 反差 [3-6s] ==========
def scene_contrast(frame_idx, total_frames, out_path):
    progress = frame_idx / total_frames
    
    img = Image.new('RGB', (W, H), (10, 10, 20))
    draw = ImageDraw.Draw(img)
    
    # 第一步：先显示胖照（0-0.5进度）
    # 第二步：过渡到瘦照（0.5-0.7进度）
    # 第三步：保持瘦照（0.7-1.0进度）
    
    if progress < 0.5:
        # 显示胖照
        if os.path.exists(FAT_PHOTO):
            try:
                photo = Image.open(FAT_PHOTO).convert('RGB')
                photo = resize_fill(photo, W, H)
                # 去饱和、暗调，增加怀旧感
                photo = photo.convert('L').convert('RGB')
                photo = photo.point(lambda p: int(p * 0.7 + 30))
                img.paste(photo, (0, 0))
            except:
                pass
        
        # 文字
        try:
            ft = ImageFont.truetype(FONT, 36)
            lines = ["7年前的我，", "迷茫又懒散，", "对生活提不起热情。"]
            for i, line in enumerate(lines):
                show_at = i * 0.3
                a = max(0, min(1, (progress - show_at) * 3))
                if a > 0:
                    c = int(255 * a)
                    bbox = draw.textbbox((0,0), line, font=ft)
                    dx = (W - (bbox[2]-bbox[0])) // 2
                    draw.text((dx+2, 350+i*70+2), line, font=ft, fill=(0,0,0,c))
                    draw.text((dx, 350+i*70), line, font=ft, fill=(255,255,255,c))
        except:
            pass
    
    elif progress < 0.65:
        # 过渡：胖照渐出 + 瘦照渐入
        t = (progress - 0.5) / 0.15  # 0→1
        
        # 先贴胖照底层
        if os.path.exists(FAT_PHOTO):
            try:
                photo = Image.open(FAT_PHOTO).convert('RGB')
                photo = resize_fill(photo, W, H)
                photo = photo.convert('L').convert('RGB')
                photo = photo.point(lambda p: int(p * 0.7 + 30))
                img.paste(photo, (0, 0))
            except:
                pass
        
        # 再叠瘦照（渐入）
        if os.path.exists(RUNNER_PHOTO):
            try:
                runner = Image.open(RUNNER_PHOTO).convert('RGB')
                runner = resize_fill(runner, W, H)
                runner = runner.point(lambda p: int(p * min(1, t * 1.3)))
                # 透明度混合
                blend = Image.blend(img, runner, t)
                img.paste(blend, (0, 0))
            except:
                pass
    
    else:
        # 完全显示瘦照
        if os.path.exists(RUNNER_PHOTO):
            try:
                runner = Image.open(RUNNER_PHOTO).convert('RGB')
                runner = resize_fill(runner, W, H)
                runner = runner.point(lambda p: int(p * 0.85 + 15))
                img.paste(runner, (0, 0))
            except:
                pass
        
        # "蜕变" 文字
        try:
            ft = ImageFont.truetype(FONT, 48)
            label = "蜕变"
            bbox = draw.textbbox((0,0), label, font=ft)
            dx = (W - (bbox[2]-bbox[0])) // 2
            draw.text((dx, H//2-50), label, font=ft, fill=(0,200,255,180))
        except:
            pass
    
    # 顶部暗角
    for i in range(200):
        alpha = int(100 * (1 - i/200))
        draw.rectangle([0, i, W, i+1], fill=(0,0,0,alpha))
    
    img.save(out_path)

# ========== 镜头3: 7600km截屏 + 数字翻牌 [6-10s] ==========
def scene_km_showcase(frame_idx, total_frames, out_path):
    progress = frame_idx / total_frames
    
    img = Image.new('RGB', (W, H), (5, 5, 15))
    
    if os.path.exists(TOTAL_KM_SCREEN):
        try:
            screen = Image.open(TOTAL_KM_SCREEN).convert('RGB')
            # 全屏展示截屏，但做半透明处理+模糊
            screen = resize_fill(screen, W, H)
            screen = screen.filter(ImageFilter.GaussianBlur(radius=8))
            screen = screen.point(lambda p: int(p * 0.3))
            img.paste(screen, (0, 0))
        except:
            pass
    
    draw = ImageDraw.Draw(img)
    
    # 在截屏中央突出显示7600数字
    target = int(total_km)
    target_str = str(target)
    
    try:
        fnum = ImageFont.truetype(FONT, 140)
        fcom = ImageFont.truetype(FONT, 70)
        ftext = ImageFont.truetype(FONT, 32)
    except:
        return
    
    # 逐位翻牌
    digits_shown = []
    for i, ch in enumerate(target_str):
        dp = progress * 2 - i * 0.12
        dp = max(0, min(1, dp))
        digits_shown.append(str(int(int(ch) * dp)))
    
    shown = ''.join(digits_shown)
    
    bbox = draw.textbbox((0,0), shown, font=fnum)
    dx = (W - (bbox[2]-bbox[0])) // 2
    dy = 450
    
    # 发光
    for lw in range(8):
        alpha = 60 - lw * 7
        if alpha > 0:
            draw.text((dx+lw, dy), shown, font=fnum, fill=(0,150,255,max(0,alpha)))
            draw.text((dx-lw, dy), shown, font=fnum, fill=(0,150,255,max(0,alpha)))
    draw.text((dx, dy), shown, font=fnum, fill=(0,200,255))
    
    # km 单位
    draw.text((dx + (bbox[2]-bbox[0]) + 15, dy+40), "km", font=fcom, fill=(255,255,255))
    
    # 截屏缩略图小窗（右下角）
    if os.path.exists(TOTAL_KM_SCREEN):
        try:
            thumb = Image.open(TOTAL_KM_SCREEN).convert('RGB')
            thumb = resize_fill(thumb, 400, 700)
            img.paste(thumb, (W-440, H-750))
            draw.rectangle([W-440, H-750, W-40, H-50], outline=(255,255,255,80), width=2)
        except:
            pass
    
    # 文字
    if progress > 0.4:
        lines = ["如今跑完7600公里，", "翻看Keep里数千条轨迹，", "心里满是感慨。"]
        for i, line in enumerate(lines):
            a = max(0, min(1, (progress - 0.4 - i*0.2) * 2.5))
            if a > 0:
                c = int(255 * a)
                bbox = draw.textbbox((0,0), line, font=ftext)
                dx2 = (W - (bbox[2]-bbox[0])) // 2
                draw.text((dx2+2, 820+i*50+2), line, font=ftext, fill=(0,0,0,c))
                draw.text((dx2, 820+i*50), line, font=ftext, fill=(255,255,255,c))
    
    img.save(out_path)

# ========== 镜头4: Keep数据回放 [10-15s] ==========
def scene_data_replay(frame_idx, total_frames, out_path):
    progress = frame_idx / total_frames
    
    img = Image.new('RGB', (W, H), (5, 5, 20))
    draw = ImageDraw.Draw(img)
    
    # 按照年份组织轨迹回放
    years = sorted(year_tracks.keys())
    
    # 收集所有轨迹
    all_items = []
    for year in years:
        for item in year_tracks.get(year, []):
            all_items.append((year, item))
    
    count = len(all_items)
    
    if count == 0:
        img.save(out_path)
        return
    
    # 用第一张轨迹图做底
    bg_track = all_items[0][1][0]
    bg = make_bg_blur(bg_track)
    draw = ImageDraw.Draw(bg)
    img = bg
    
    # 当前显示哪条
    current_idx = min(int(progress * count), count - 1)
    year, (fp, info) = all_items[current_idx]
    
    try:
        ft_yr = ImageFont.truetype(FONT, 72)
        ft_info = ImageFont.truetype(FONT, 30)
        ft_sub = ImageFont.truetype(FONT, 28)
    except:
        return
    
    # 大年份
    draw.text((60, 80), year, font=ft_yr, fill=(0,200,255))
    
    # 缩略图底部显示
    thumb_w = 500
    thumb_h = 500
    try:
        thumb = Image.open(fp).convert('RGB')
        tw, th = thumb.size
        tr = tw / th
        if tr > 1:
            thumb_h_new = int(thumb_w / tr)
            thumb = thumb.resize((thumb_w, thumb_h_new), Image.LANCZOS)
        else:
            thumb_w_new = int(thumb_h * tr)
            thumb = thumb.resize((thumb_w_new, thumb_h), Image.LANCZOS)
        tx = (W - thumb.width) // 2
        ty = 200
        # 圆角背景
        draw.rounded_rectangle([tx-8, ty-8, tx+thumb.width+8, ty+thumb.height+8],
                              radius=12, fill=(0,0,0,100))
        bg.paste(thumb, (tx, ty))
        
        # 信息标签
        label = f"{info['date']}  {info['km']:.1f}km  {info['min']:.0f}min"
        draw.text((tx, ty-35), label, font=ft_info, fill=(0,200,255,200))
    except:
        pass
    
    # 底部进度条
    prog_y = H - 60
    bar_w = 800
    bar_h = 4
    bar_x = (W - bar_w) // 2
    draw.rounded_rectangle([bar_x, prog_y, bar_x+bar_w, prog_y+bar_h],
                          radius=2, fill=(50,50,50))
    fill_w = int(bar_w * progress)
    draw.rounded_rectangle([bar_x, prog_y, bar_x+fill_w, prog_y+bar_h],
                          radius=2, fill=(0,200,255))
    
    # 进度计数
    draw.text((bar_x+bar_w+20, prog_y-10), f"{current_idx+1}/{count}",
             font=ft_sub, fill=(150,150,150))
    
    # 口播文字
    if progress > 0.2:
        lines = [
            "一路走来，从抗拒到热爱，",
            "从浮躁到平静，",
            "跑步不仅练了身体，",
            "更治愈了内心。",
            "",
            "普通人最好的翻盘，",
            "就是日复一日的坚持。"
        ]
        # 取与当前进度匹配的某段文字展示
        line_idx = int((progress - 0.2) / 0.1)  # 每0.1秒换一行
        if line_idx < len(lines) and lines[line_idx]:
            try:
                ft_now = ImageFont.truetype(FONT, 34)
                line = lines[line_idx]
                bbox = draw.textbbox((0,0), line, font=ft_now)
                dx = (W - (bbox[2]-bbox[0])) // 2
                draw.text((dx, H-130), line, font=ft_now, fill=(255,255,255))
            except:
                pass
    
    img.save(out_path)

# ========== 镜头5: 数据高潮 [15-17s] ==========
scene5_total = 2 * FPS  # 缩短到2秒

def scene_data_highlights(frame_idx, total_frames, out_path):
    progress = frame_idx / total_frames
    
    # 用一张最大轨迹做底
    biggest = None
    max_km = 0
    for fp in all_tracks:
        info = parse_track(fp)
        if info and info['km'] > max_km:
            max_km = info['km']
            biggest = fp
    
    img = make_bg_blur(biggest, dark_factor=0.25)
    draw = ImageDraw.Draw(img)
    
    try:
        ft_num = ImageFont.truetype(FONT, 80)
        ft_unit = ImageFont.truetype(FONT, 36)
        ft_text = ImageFont.truetype(FONT, 32)
    except:
        return
    
    # 3x2 布局
    items = [
        (f"{total_km:.0f}", "km", "总里程"),
        ("9", "年", "2018-2026"),
        ("766", "次", "奔跑"),
        (f"{int(total_km/766*1000/60):.0f}", "km/次", "平均"),
    ]
    
    for i, (num, unit, label) in enumerate(items):
        col = i % 2
        row = i // 2
        a = max(0, min(1, (progress - i*0.08) * 3))
        if a > 0:
            c = int(255 * a)
            x = 120 + col * 400
            y = 350 + row * 220
            # 数字
            bbox = draw.textbbox((0,0), num, font=ft_num)
            draw.text((x, y), num, font=ft_num, fill=(0, 200, 255, c))
            # 单位
            draw.text((x + (bbox[2]-bbox[0]) + 10, y+20), unit, font=ft_unit, fill=(255,255,255,c))
            # 标签
            draw.text((x, y+90), label, font=ft_text, fill=(150,150,150,c))
            # 底线
            draw.rectangle([x, y+75, x+120, y+77], fill=(255,255,255,max(0,c-120)))
    
    # 金句
    if progress > 0.5:
        line = "日复一日的坚持，就是普通人最好的翻盘"
        a = max(0, min(1, (progress - 0.5) * 3))
        if a > 0:
            c = int(255 * a)
            try:
                ft = ImageFont.truetype(FONT, 42)
                bbox = draw.textbbox((0,0), line, font=ft)
                dx = (W - (bbox[2]-bbox[0])) // 2
                draw.text((dx+2, 1100+2), line, font=ft, fill=(0,0,0,c))
                draw.text((dx, 1100), line, font=ft, fill=(255,255,255,c))
            except:
                pass
    
    img.save(out_path)

# ========== 镜头6: 收尾 [17-20s] ==========
def scene_ending(frame_idx, total_frames, out_path):
    progress = frame_idx / total_frames
    
    img = Image.new('RGB', (W, H), (5, 5, 15))
    draw = ImageDraw.Draw(img)
    
    # 底部用脚步视频（不露脸，只取脚部）
    if os.path.exists(FOOTSTEP_VIDEO):
        seek_t = 2.0 + progress * 10.0  # 视频2-12秒区间
        frame_jpg = os.path.join(TMP_DIR, f'_foot_{frame_idx}.jpg')
        subprocess.run(['ffmpeg','-y','-ss',str(seek_t),'-i',FOOTSTEP_VIDEO,
                       '-vframes','1','-q:v','2','-f','image2',frame_jpg],
                      capture_output=True, timeout=10)
        if os.path.exists(frame_jpg):
            try:
                foot = Image.open(frame_jpg).convert('RGB')
                # 只取下半部分画面（脚步区域）
                fw, fh = foot.size
                foot = foot.crop((0, int(fh*0.45), fw, fh))  # 下半部分
                foot = foot.resize((W, int(H*0.65)), Image.LANCZOS)
                foot = foot.point(lambda p: int(p * 0.4))
                img.paste(foot, (0, int(H*0.35)))
            except:
                pass
            try:
                os.remove(frame_jpg)
            except:
                pass
    
    # 顶部显示胖照（跑渣照）
    if os.path.exists(END_PHOTO):
        try:
            photo = Image.open(END_PHOTO).convert('RGB')
            photo = resize_fill(photo, W, int(H*0.45))
            photo = photo.point(lambda p: int(p * 0.6))
            img.paste(photo, (0, 0))
            
            # 过渡渐变
            for i in range(100):
                a = int(150 * (1 - i/100))
                draw.rectangle([0, int(H*0.45)-i, W, int(H*0.45)-i+1], fill=(0,0,0,a))
        except:
            pass
    
    # 灰色遮罩
    for i in range(H):
        a = int(40 * (1 - abs(i-H*0.5)/(H*0.5)))
        draw.rectangle([0, i, W, i+1], fill=(0,0,0,max(0,a)))
    
    try:
        ft = ImageFont.truetype(FONT, 40)
        fs = ImageFont.truetype(FONT, 32)
        fsm = ImageFont.truetype(FONT, 24)
    except:
        return
    
    # 文字
    line1 = "干货持续更新，普通人跑步自律"
    line2 = "我帮你少走弯路"
    
    a1 = max(0, min(1, progress * 2.5))
    if a1 > 0:
        c = int(255 * a1)
        bbox = draw.textbbox((0,0), line1, font=ft)
        dx = (W - (bbox[2]-bbox[0])) // 2
        draw.text((dx+2, int(H*0.42)+2), line1, font=ft, fill=(0,0,0,c))
        draw.text((dx, int(H*0.42)), line1, font=ft, fill=(255,255,255,c))
    
    a2 = max(0, min(1, (progress - 0.25) * 2.5))
    if a2 > 0:
        c = int(255 * a2)
        bbox = draw.textbbox((0,0), line2, font=fs)
        dx = (W - (bbox[2]-bbox[0])) // 2
        draw.text((dx+2, int(H*0.42)+60+2), line2, font=fs, fill=(0,0,0,c))
        draw.text((dx, int(H*0.42)+60), line2, font=fs, fill=(0,200,255,c))
    
    # 底部数据信息
    if progress > 0.5:
        draw.text(((W-280)//2, H-180), "Keep 2018-2026", font=fsm, fill=(100,100,100))
        draw.text(((W-300)//2, H-145), f"{total_km:.0f}km · 766次", font=fsm, fill=(100,100,100))
        
        # 关注按钮
        btn_w, btn_h = 260, 50
        bx = (W - btn_w) // 2
        by = H - 100
        draw.rounded_rectangle([bx, by, bx+btn_w, by+btn_h], radius=25, fill=(0,200,255,200))
        draw.text((bx+btn_w//2-45, by+8), "关 注", font=fs, fill=(0,0,0))
    
    img.save(out_path)

# ========== 主循环 ==========
scenes = [
    ('opening',     scene_opening,         3*FPS),     # 0-3s: 开场真实视频
    ('contrast',    scene_contrast,         3*FPS),     # 3-6s: 胖瘦反差
    ('km_showcase', scene_km_showcase,      4*FPS),     # 6-10s: 7600km展示
    ('data_replay', scene_data_replay,      5*FPS),     # 10-15s: Keep数据回放
    ('data_high',   scene_data_highlights,  2*FPS),     # 15-17s: 数据高潮
    ('ending',      scene_ending,           3*FPS),     # 17-20s: 收尾
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

with open(os.path.join(TMP_DIR, 'frames.txt'), 'w') as f:
    f.write('\n'.join(frame_lines))

print("合成视频...")
raw = os.path.join(TMP_DIR, 'raw.mp4')
subprocess.run(['ffmpeg','-y','-f','concat','-safe','0',
               '-i',os.path.join(TMP_DIR, 'frames.txt'),
               '-c:v','libx264','-pix_fmt','yuv420p',
               '-preset','fast','-crf','20','-r',str(FPS),raw],
              check=True, capture_output=True)

subprocess.run(['ffmpeg','-y','-i',raw,
               '-f','lavfi','-t',str(global_idx/FPS),
               '-i','anullsrc=r=44100:cl=mono',
               '-c:v','copy','-c:a','aac','-shortest',OUTPUT_VIDEO],
              check=True, capture_output=True)

shutil.rmtree(TMP_DIR, ignore_errors=True)

size = os.path.getsize(OUTPUT_VIDEO) / 1024 / 1024
print(f"\n[OK] 视频生成完成!")
print(f"  File: {OUTPUT_VIDEO}")
print(f"  {global_idx/FPS:.1f}s | {W}x{H} | {size:.1f}MB")
