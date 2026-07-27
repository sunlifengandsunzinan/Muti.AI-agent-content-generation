import subprocess
import os

d = r'D:\小红书素材'
for v in ['VID_20260608_183422.mp4', 'VID_20260608_184055.mp4', 'VID_20260608_185000.mp4', 'wx_camera_1750503011375.mp4', 'petal_hdr_20250503_164048.mp4']:
    fp = os.path.join(d, v)
    if not os.path.exists(fp):
        print(f'{v}: NOT FOUND')
        continue
    dur = subprocess.run(['ffprobe','-v','quiet','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',fp],capture_output=True,text=True).stdout.strip()
    w = subprocess.run(['ffprobe','-v','quiet','-show_entries','stream=width,height','-of','default=noprint_wrappers=1:nokey=1',fp],capture_output=True,text=True).stdout.strip()
    print(f'{v}: {float(dur):.1f}s  {w}')
