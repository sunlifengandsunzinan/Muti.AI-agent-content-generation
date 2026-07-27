#!/usr/bin/env python3
"""
Keep 七年跑步 · 情绪短片 v4
修复:
  - 3-6s: 胖照→瘦照过渡修复，接力棒不掉
  - 15-17s: 7378km -> 7600+, 平均距离替换为"半马"次数
  - 17-20s: 跑渣照上半+脚步视频下半，强制显示
"""

import os, re, shutil, subprocess, glob, math

FFMPEG = r'C:\Users\Administrator\.openclaw\workspace\skills\video-frames\bin\ffmpeg.exe'
from collections import defaultdict
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ========== 配置 ==========
KEEP_DIR = r'D:\Keep轨迹素材'
XHS_DIR = r'D:\小红书素材'
OUTPUT_DIR = r'C:\Users\Administrator\Desktop\Keep跑步七年'
OUTPUT_VIDEO = os.path.join(OUTPUT_DIR, 'Keep_七年跑步_20s_v4.mp4')
TMP_DIR = os.path.join(OUTPUT_DIR, '_frames_v4')

FPS = 30
W, H = 1080, 1920

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TMP_DIR, exist_ok=True)

FONT = None
for fp in [r'C:\Windows\Fonts\msyhbd.ttc', r'C:\Windows\Fonts\msyh.ttc', r'C:\Windows\Fonts\simhei.ttf']:
    if os.path.exists(fp):
        FONT = fp
        break

# ========== 素材 ==========
OPENING_VIDEO = os.path.join(XHS_DIR, 'VID_20260608_183422.mp4')
FAT_PHOTO = os.path.join(XHS_DIR, 'image_1780734672485.jpg')
RUNNER_PHOTO = os.path.join(XHS_DIR, '49b5e14b-30e5-4049-99fb-71046a8a802b.png')
END_PHOTO = os.path.join(XHS_DIR, 'IMG_20240701_214942.jpg')
TOTAL_KM_SCREEN = os.path.join(XHS_DIR, 'screenshot_20260607_181201_com.gotokeep.hm.keep.jpg')
FOOTSTEP_VIDEO = os.path.join(XHS_DIR, 'VID_20260608_185000.mp4')

all_tracks = sorted(glob.glob(os.path.join(KEEP_DIR, '*', '*.jpg')))

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

# total_km = sum(sum(info['km'] for _, info in items) for items in year_tracks.values())
total_km = 7600.0  # 强制显示7600km
total_runs = sum(len(items) for items in year_tracks.values())
half_marathons = sum(1 for items in year_tracks.values() for _, info in items if info['km'] >= 21.095)
print(f"总里程: {total_km:.0f}km  总次数: {total_runs}  半马次数: {half_marathons}")

# ========== 工具 ==========
def make_bg_blur(track_path=None, dark=0.3):
    canvas = Image.new('RGB', (W, H), (8, 8, 25))
    if track_path and os.path.exists(track_path):
        try:
            bg = Image.open(track_path).convert('RGB')
            bg = bg.resize((W, H), Image.LANCZOS)
            bg = bg.filter(ImageFilter.GaussianBlur(radius=35))
            bg = bg.point(lambda p: int(p * dark))
            canvas.paste(bg, (0, 0))
        except:
            pass
    return canvas

def load_frame(video_path, seek_t):
    out = os.path.join(TMP_DIR, f'_vf{hash(video_path+str(seek_t))}.jpg')
    if not os.path.exists(out):
        subprocess.run([FFMPEG,'-y','-ss',str(seek_t),'-i',video_path,
                       '-vframes','1','-q:v','2','-f','image2',out],
                      capture_output=True, timeout=10)
    if os.path.exists(out):
        return Image.open(out).convert('RGB')
    return None

def letterbox(img, target_w, target_h, bg_color=(0,0,0)):
    """等比例缩放+黑边填充，不裁剪"""
    img.thumbnail((target_w, target_h), Image.LANCZOS)
    canvas = Image.new('RGB', (target_w, target_h), bg_color)
    x = (target_w - img.width) // 2
    y = (target_h - img.height) // 2
    canvas.paste(img, (x, y))
    return canvas

# ========== 镜头1: 开场 [0-3s] ==========
def scene_opening(fi, nf, out):
    p = fi / nf
    seek_t = 0.5 + p * 10
    frame = load_frame(OPENING_VIDEO, seek_t)
    if frame:
        # 视频是1920x1080横屏，裁切中央做竖屏
        fw, fh = frame.size
        crop_w = int(fh * W / H)
        x = (fw - crop_w) // 2
        frame = frame.crop((x, 0, x+crop_w, fh))
        frame = frame.resize((W, H), Image.LANCZOS)
        img = frame
    else:
        img = Image.new('RGB', (W, H), (10,10,20))
    
    draw = ImageDraw.Draw(img)
    for i in range(250):
        a = int(180*(1-i/250))
        draw.rectangle([0,H-250+i,W,H-250+i+1],fill=(0,0,0,a))
    
    try:
        ft = ImageFont.truetype(FONT, 44)
    except:
        img.save(out); return
    
    l1, l2 = "坚持跑步七年，", "到底能改变一个人多少？"
    n1 = min(len(l1), int(len(l1)*p*3))
    n2 = max(0, min(len(l2), int(len(l2)*max(0,p-0.35)*3)))
    for shown, txt, col, y_ in [(n1,l1,(255,255,255),H-200),(n2,l2,(0,200,255),H-125)]:
        if shown>0:
            t=txt[:shown]
            bb=draw.textbbox((0,0),t,font=ft)
            dx=(W-(bb[2]-bb[0]))//2
            draw.text((dx+2,y_+2),t,font=ft,fill=(0,0,0,180))
            draw.text((dx,y_),t,font=ft,fill=col)
    img.save(out)

# ========== 镜头2: 胖瘦反差 [3-6s] ==========
def scene_contrast(fi, nf, out):
    p = fi / nf
    img = Image.new('RGB', (W, H), (10, 10, 20))
    draw = ImageDraw.Draw(img)
    
    try:
        ft = ImageFont.truetype(FONT, 34)
    except:
        pass
    
    # 第一阶段(0-0.45): 胖照全屏
    if p < 0.45:
        if os.path.exists(FAT_PHOTO):
            try:
                photo = Image.open(FAT_PHOTO).convert('RGB')
                photo = letterbox(photo, W, H, (10,10,20))
                photo = photo.convert('L').convert('RGB')
                photo = photo.point(lambda p_: int(p_ * 0.65 + 25))
                img.paste(photo, (0, 0))
            except:
                pass
        
        lines = ["7年前的我，", "迷茫又懒散，", "对生活提不起热情。"]
        for i, l in enumerate(lines):
            a = max(0,min(1,(p-i*0.25)*3))
            if a>0:
                c=int(255*a)
                bb=draw.textbbox((0,0),l,font=ft)
                dx=(W-(bb[2]-bb[0]))//2
                draw.text((dx+2,350+i*65+2),l,font=ft,fill=(0,0,0,c))
                draw.text((dx,350+i*65),l,font=ft,fill=(255,255,255,c))
    
    # 第二阶段(0.45-0.60): 过渡
    elif p < 0.60:
        t = (p - 0.45) / 0.15
        
        # 胖照底层
        bottom = None
        if os.path.exists(FAT_PHOTO):
            photo = Image.open(FAT_PHOTO).convert('RGB')
            photo = letterbox(photo, W, H, (10,10,20)).convert('L').convert('RGB').point(lambda p_: int(p_*0.65+25))
            bottom = photo
        
        # 瘦照上层
        top = None
        if os.path.exists(RUNNER_PHOTO):
            runner = Image.open(RUNNER_PHOTO).convert('RGB')
            runner = letterbox(runner, W, H, (10,10,20))
            runner = runner.point(lambda p_: int(p_*0.85+15))
            top = runner
        
        if bottom and top:
            blend = Image.blend(bottom, top, t)
            img.paste(blend, (0, 0))
        elif bottom:
            img.paste(bottom, (0, 0))
        elif top:
            img.paste(top, (0, 0))
    
    # 第三阶段(0.60-1.0): 瘦照全屏
    else:
        if os.path.exists(RUNNER_PHOTO):
            try:
                runner = Image.open(RUNNER_PHOTO).convert('RGB')
                runner = letterbox(runner, W, H, (10,10,20))
                runner = runner.point(lambda p_: int(p_ * 0.85 + 15))
                img.paste(runner, (0, 0))
            except:
                pass
        
        # "蜕变"大字
        try:
            ft2 = ImageFont.truetype(FONT, 56)
            txt = "蜕变"
            bb = draw.textbbox((0,0), txt, font=ft2)
            dx = (W-(bb[2]-bb[0]))//2
            draw.text((dx, H//2-40), txt, font=ft2, fill=(0,200,255,200))
        except:
            pass
    
    # 顶暗角
    for i in range(150):
        a=int(80*(1-i/150))
        draw.rectangle([0,i,W,i+1],fill=(0,0,0,a))
    
    img.save(out)

# ========== 镜头3: 7600km [6-10s] ==========
def scene_km(fi, nf, out):
    p = fi / nf
    
    if os.path.exists(TOTAL_KM_SCREEN):
        try:
            screen = Image.open(TOTAL_KM_SCREEN).convert('RGB')
            screen = screen.resize((W, H), Image.LANCZOS)
            screen = screen.filter(ImageFilter.GaussianBlur(radius=10))
            screen = screen.point(lambda p_: int(p_ * 0.3))
            img = screen
        except:
            img = Image.new('RGB', (W, H), (5,5,15))
    else:
        img = Image.new('RGB', (W, H), (5,5,15))
    
    draw = ImageDraw.Draw(img)
    
    try:
        fnum = ImageFont.truetype(FONT, 140)
        fcom = ImageFont.truetype(FONT, 70)
        ftext = ImageFont.truetype(FONT, 30)
    except:
        img.save(out); return
    
    target = int(total_km)
    ts = str(target)
    digs = []
    for i, ch in enumerate(ts):
        dp = max(0, min(1, p*2 - i*0.12))
        digs.append(str(int(int(ch)*dp)))
    shown = ''.join(digs)
    
    bb = draw.textbbox((0,0), shown, font=fnum)
    dx = (W-(bb[2]-bb[0]))//2
    dy = 420
    
    for lw in range(8):
        al = 60-lw*7
        if al>0:
            draw.text((dx+lw, dy), shown, font=fnum, fill=(0,150,255,max(0,al)))
            draw.text((dx-lw, dy), shown, font=fnum, fill=(0,150,255,max(0,al)))
    draw.text((dx, dy), shown, font=fnum, fill=(0,200,255))
    draw.text((dx+(bb[2]-bb[0])+15, dy+40), "km", font=fcom, fill=(255,255,255))
    
    # 截图缩略小窗右下
    if os.path.exists(TOTAL_KM_SCREEN):
        try:
            thumb = Image.open(TOTAL_KM_SCREEN).convert('RGB')
            thumb = thumb.resize((360, 640), Image.LANCZOS)
            img.paste(thumb, (W-400, H-720))
            draw.rectangle([W-400, H-720, W-40, H-80], outline=(255,255,255,60), width=2)
        except:
            pass
    
    if p > 0.35:
        lines = ["如今跑完7600公里，", "翻看Keep里数千条轨迹，", "心里满是感慨。"]
        for i, l in enumerate(lines):
            a = max(0,min(1,(p-0.35-i*0.2)*2.5))
            if a>0:
                c=int(255*a)
                bb2=draw.textbbox((0,0),l,font=ftext)
                dx2=(W-(bb2[2]-bb2[0]))//2
                draw.text((dx2+2,820+i*50+2),l,font=ftext,fill=(0,0,0,c))
                draw.text((dx2,820+i*50),l,font=ftext,fill=(255,255,255,c))
    
    img.save(out)

# ========== 镜头4: Keep数据回放 [10-15s] ==========
def scene_replay(fi, nf, out):
    p = fi / nf
    
    all_items = []
    for year in sorted(year_tracks.keys()):
        for item in year_tracks[year]:
            all_items.append((year, item))
    count = len(all_items)
    if count == 0:
        Image.new('RGB', (W, H), (5,5,15)).save(out)
        return
    
    ci = min(int(p * count), count-1)
    cy, (fp, info) = all_items[ci]
    
    img = make_bg_blur(fp, dark=0.25)
    draw = ImageDraw.Draw(img)
    
    try:
        fty = ImageFont.truetype(FONT, 80)
        ftd = ImageFont.truetype(FONT, 28)
    except:
        img.save(out); return
    
    # 大年份 (居左)
    draw.text((50, 60), cy, font=fty, fill=(0,200,255))
    
    # 轨迹缩略图居中
    thumb_w, thumb_h = 550, 550
    try:
        thumb = Image.open(fp).convert('RGB')
        tw, th = thumb.size
        tr = tw / th
        if tr > 1:
            nh = int(thumb_w/tr)
            thumb = thumb.resize((thumb_w, nh), Image.LANCZOS)
            th = nh
            tw = thumb_w
        else:
            nw = int(thumb_h*tr)
            thumb = thumb.resize((nw, thumb_h), Image.LANCZOS)
            tw = nw
            th = thumb_h
        
        tx = (W - tw)//2
        ty = 180
        draw.rounded_rectangle([tx-8,ty-8,tx+tw+8,ty+th+8], radius=10, fill=(0,0,0,80))
        img.paste(thumb, (tx, ty))
        draw.text((tx, ty-32), f"{info['date']}  {info['km']:.1f}km", font=ftd, fill=(0,200,255,200))
    except:
        pass
    
    # 底部进度
    bar_w, bar_h = 700, 3
    bx = (W-bar_w)//2
    draw.rounded_rectangle([bx, H-50, bx+bar_w, H-50+bar_h], radius=2, fill=(50,50,50))
    fill = int(bar_w*p)
    draw.rounded_rectangle([bx, H-50, bx+fill, H-50+bar_h], radius=2, fill=(0,200,255))
    draw.text((bx+bar_w+15, H-55), f"{ci+1}/{count}", font=ftd, fill=(120,120,120))
    
    # 口播轮播
    lines = ["一路走来，从抗拒到热爱，", "从浮躁到平静，", "跑步不仅练了身体，", "更治愈了内心。", "", "普通人最好的翻盘，", "就是日复一日的坚持。"]
    if p > 0.15:
        try:
            ftn = ImageFont.truetype(FONT, 32)
            li = min(int((p-0.15)/0.08), len(lines)-1)
            if li < len(lines) and lines[li]:
                txt = lines[li]
                bb = draw.textbbox((0,0), txt, font=ftn)
                dx = (W-(bb[2]-bb[0]))//2
                draw.text((dx, H-120), txt, font=ftn, fill=(255,255,255))
        except:
            pass
    
    img.save(out)

# ========== 镜头5: 数据高潮 [15-17s] ==========
def scene_high(fi, nf, out):
    p = fi / nf
    
    # 选最大轨迹做底
    biggest = None
    max_km = 0
    for fp in all_tracks:
        info = parse_track(fp)
        if info and info['km'] > max_km:
            max_km = info['km']
            biggest = fp
    
    img = make_bg_blur(biggest, dark=0.2)
    draw = ImageDraw.Draw(img)
    
    try:
        fn = ImageFont.truetype(FONT, 70)
        fu = ImageFont.truetype(FONT, 32)
        ft = ImageFont.truetype(FONT, 28)
        fg = ImageFont.truetype(FONT, 40)
    except:
        img.save(out); return
    
    # 4项: 7600+km, 9年, 766次, 半马次数
    items = [
        ("7600+", "km", "总里程"),
        ("9", "年", "2018-2026"),
        (f"{total_runs}", "次", "奔跑"),
        (f"{half_marathons}", "次", "半马"),
    ]
    
    for i, (num, unit, label) in enumerate(items):
        col = i % 2
        row = i // 2
        a = max(0, min(1, (p - i*0.08) * 3))
        if a > 0:
            c = int(255 * a)
            x = 120 + col * 420
            y = 350 + row * 230
            bb = draw.textbbox((0,0), num, font=fn)
            draw.text((x, y), num, font=fn, fill=(0,200,255,c))
            draw.text((x+(bb[2]-bb[0])+10, y+15), unit, font=fu, fill=(255,255,255,c))
            draw.text((x, y+85), label, font=ft, fill=(140,140,140,c))
            draw.rectangle([x, y+70, x+100, y+72], fill=(255,255,255, max(0,c-120)))
    
    if p > 0.4:
        line = "日复一日的坚持，就是普通人最好的翻盘"
        a = max(0, min(1, (p-0.4)*3))
        if a > 0:
            c = int(255*a)
            bb = draw.textbbox((0,0), line, font=fg)
            dx = (W-(bb[2]-bb[0]))//2
            draw.text((dx+2, 1080+2), line, font=fg, fill=(0,0,0,c))
            draw.text((dx, 1080), line, font=fg, fill=(255,255,255,c))
    
    img.save(out)

# ========== 镜头6: 收尾 [17-20s] ==========
def scene_end(fi, nf, out):
    p = fi / nf
    
    # 创建底图
    img = Image.new('RGB', (W, H), (5, 5, 15))
    
    # 上半部分: IMG_20240701 跑渣照
    if os.path.exists(END_PHOTO):
        try:
            photo = Image.open(END_PHOTO).convert('RGB')
            # 等比例填充到上半区域
            photo_h = int(H * 0.5)
            pw, ph = photo.size
            ratio = ph / pw
            if ratio > (photo_h / W):
                # 太高,裁剪高度
                new_ph = int(W * ratio)
                y = (new_ph - photo_h) // 2
                photo = photo.resize((W, new_ph), Image.LANCZOS)
                photo = photo.crop((0, y, W, y + photo_h))
            else:
                # 太宽
                new_pw = int(photo_h / ratio)
                x = (new_pw - W) // 2
                photo = photo.resize((new_pw, photo_h), Image.LANCZOS)
                photo = photo.crop((x, 0, x + W, photo_h))
            photo = photo.point(lambda px: int(px * 0.55 + 15))
            img.paste(photo, (0, 0))
        except Exception as e:
            print(f"  END_PHOTO error: {e}")
    else:
        print("  END_PHOTO NOT FOUND")
    
    # 中间渐变带(上下分隔)
    for i in range(120):
        a = int(180 * (1 - abs(i-60)/60))
        draw_temp = ImageDraw.Draw(img)
        draw_temp.rectangle([0, int(H*0.5)-60+i, W, int(H*0.5)-60+i+1], fill=(0,0,0,max(0,a)))
    
    # 下半部分: 脚步视频(只取脚,不露脸)
    if os.path.exists(FOOTSTEP_VIDEO):
        seek_t = 2.0 + p * 8.0
        fj = os.path.join(TMP_DIR, f'_ft{fi}.jpg')
        subprocess.run([FFMPEG,'-y','-ss',str(seek_t),'-i',FOOTSTEP_VIDEO,
                       '-vframes','1','-q:v','2','-f','image2',fj],
                      capture_output=True, timeout=10)
        if os.path.exists(fj):
            try:
                foot = Image.open(fj).convert('RGB')
                # 视频是1920x1080横屏,裁下半做脚步
                fw, fh = foot.size
                # 取中间偏下区域
                foot = foot.crop((0, int(fh*0.55), fw, int(fh*0.9)))
                foot = foot.resize((W, int(H*0.5)), Image.LANCZOS)
                foot = foot.point(lambda px: int(px * 0.4))
                img.paste(foot, (0, int(H*0.5)))
            except Exception as e:
                print(f"  FOOTSTEP error: {e}")
            try:
                os.remove(fj)
            except:
                pass
    else:
        print("  FOOTSTEP_VIDEO NOT FOUND")
    
    draw = ImageDraw.Draw(img)
    
    # 全屏暗色遮罩 (仅微暗)
    for i in range(H):
        a = int(30 * (1 - abs(i-H*0.5)/(H*0.5)))
        draw.rectangle([0, i, W, i+1], fill=(0,0,0,max(0,a)))
    
    try:
        ft = ImageFont.truetype(FONT, 38)
        fs = ImageFont.truetype(FONT, 30)
        fsm = ImageFont.truetype(FONT, 22)
    except:
        img.save(out); return
    
    # 文字叠在中间渐变区
    line1 = "干货持续更新，普通人跑步自律"
    line2 = "我帮你少走弯路"
    
    a1 = max(0, min(1, p*2.5))
    if a1 > 0:
        c = int(255*a1)
        bb = draw.textbbox((0,0), line1, font=ft)
        dx = (W-(bb[2]-bb[0]))//2
        draw.text((dx+2, int(H*0.45)+2), line1, font=ft, fill=(0,0,0,c))
        draw.text((dx, int(H*0.45)), line1, font=ft, fill=(255,255,255,c))
    
    a2 = max(0, min(1, (p-0.2)*2.5))
    if a2 > 0:
        c = int(255*a2)
        bb = draw.textbbox((0,0), line2, font=fs)
        dx = (W-(bb[2]-bb[0]))//2
        draw.text((dx+2, int(H*0.45)+55+2), line2, font=fs, fill=(0,0,0,c))
        draw.text((dx, int(H*0.45)+55), line2, font=fs, fill=(0,200,255,c))
    
    if p > 0.5:
        draw.text(((W-260)//2, H-170), "Keep 2018-2026", font=fsm, fill=(100,100,100))
        draw.text(((W-280)//2, H-140), f"{total_km:.0f}km · {total_runs}次", font=fsm, fill=(100,100,100))
        btn_w, btn_h = 240, 46
        bx = (W-btn_w)//2
        by = H-95
        draw.rounded_rectangle([bx, by, bx+btn_w, by+btn_h], radius=23, fill=(0,200,255,200))
        draw.text((bx+btn_w//2-40, by+6), "关 注", font=fs, fill=(0,0,0))
    
    img.save(out)

# ========== 主循环 ==========
scenes = [
    ('opening',   scene_opening,  3*FPS),   # 0-3s
    ('contrast',  scene_contrast, 3*FPS),   # 3-6s
    ('km',        scene_km,       4*FPS),   # 6-10s
    ('replay',    scene_replay,   5*FPS),   # 10-15s
    ('high',      scene_high,     2*FPS),   # 15-17s
    ('end',       scene_end,      3*FPS),   # 17-20s
]

frame_lines = []
gi = 0

print("\n生成帧...")
for name, func, nf in scenes:
    print(f"  [{name}] {nf}帧...")
    for i in range(nf):
        fp = os.path.join(TMP_DIR, f'f_{gi:06d}.png')
        func(i, nf, fp)
        frame_lines.append(f"file 'f_{gi:06d}.png'\nduration 0.0333333")
        gi += 1
    print(f"    done")

print(f"\n总帧数: {gi} ({gi/FPS:.1f}s)")
with open(os.path.join(TMP_DIR, 'frames.txt'), 'w') as f:
    f.write('\n'.join(frame_lines))

print("合成视频...")
raw = os.path.join(TMP_DIR, 'raw.mp4')
subprocess.run([FFMPEG,'-y','-f','concat','-safe','0',
               '-i',os.path.join(TMP_DIR, 'frames.txt'),
               '-c:v','libx264','-pix_fmt','yuv420p',
               '-preset','fast','-crf','20','-r',str(FPS),raw],
              check=True, capture_output=True)
subprocess.run([FFMPEG,'-y','-i',raw,
               '-f','lavfi','-t',str(gi/FPS),
               '-i','anullsrc=r=44100:cl=mono',
               '-c:v','copy','-c:a','aac','-shortest',OUTPUT_VIDEO],
              check=True, capture_output=True)

shutil.rmtree(TMP_DIR, ignore_errors=True)
size = os.path.getsize(OUTPUT_VIDEO)/1024/1024
print(f"\n[OK]")
print(f"  File: {OUTPUT_VIDEO}")
print(f"  {gi/FPS:.1f}s | {W}x{H} | {size:.1f}MB")
