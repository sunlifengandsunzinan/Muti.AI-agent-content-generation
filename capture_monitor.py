#!/usr/bin/env python3
"""Render collector monitor page to screenshot via PIL"""
import io, sys, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import urllib.request

# Get page HTML
r = urllib.request.urlopen('http://127.0.0.1:6001/moto/collector/monitor', timeout=15)
html = r.read().decode('utf-8')

# Also get JSON data
r2 = urllib.request.urlopen('http://127.0.0.1:6001/moto/collector/monitor.json', timeout=15)
data = json.loads(r2.read().decode('utf-8'))

print(f"HTML length: {len(html)}")
print(f"Data keys: {list(data.keys()) if isinstance(data, dict) else 'list'}")
print(f"Monitor health: {json.dumps(data.get('monitor', {}).get('health', {}), ensure_ascii=False)[:200] if isinstance(data, dict) else 'N/A'}")

# Render to simple HTML image using the json data
spots = []
if isinstance(data, dict):
    monitor = data.get('monitor', {})
    spots = monitor.get('recent_spots', data.get('recent_spots', []))
    if not spots:
        spots = monitor.get('spots', data.get('spots', []))

# Build a simple HTML report
report_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>采集监控</title>
<style>
body{{font-family:'Microsoft YaHei',sans-serif;background:#121212;color:#eee;margin:0;padding:20px;}}
h1{{font-size:22px;margin-top:0}}
.container{{max-width:800px;margin:0 auto}}
.card{{background:#1e1e1e;border-radius:12px;padding:20px;margin-bottom:16px}}
.status-row{{display:flex;gap:12px;margin:10px 0}}
.badge{{display:inline-block;padding:4px 12px;border-radius:6px;font-size:13px}}
.badge-green{{background:rgba(46,125,50,0.2);color:#81c784}}
.badge-gray{{background:rgba(158,158,158,0.15);color:#aaa}}
table{{width:100%;border-collapse:collapse;font-size:14px}}
td{{padding:6px 8px;border-bottom:1px solid #333}}
.lbl{{color:#888}}
.val{{color:#eee}}
</style></head>
<body>
<div class="container">
<h1>🔍 采集监控面板</h1>
"""

# Parse data
if isinstance(data, dict):
    mon = data.get('monitor', data.get('page', {}))
    if isinstance(mon, dict):
        health = mon.get('health', {})
        report_html += f"""
<div class="card">
  <div class="status-row">
    <span class="badge badge-green">● 采集已启动</span>
    <span class="badge badge-gray">状态: {mon.get('state_label', 'running')}</span>
  </div>
  <table>
    <tr><td class="lbl">阶段</td><td class="val">{mon.get('current_stage_label', '-')}</td></tr>
    <tr><td class="lbl">管线</td><td class="val">{mon.get('pipeline_status_label', '-')}</td></tr>
    <tr><td class="lbl">上次心跳</td><td class="val">{mon.get('last_heartbeat', '-')}</td></tr>
    <tr><td class="lbl">上次成功</td><td class="val">{mon.get('last_success_at', '-')}</td></tr>
    <tr><td class="lbl">采集进度</td><td class="val">{mon.get('progress_label', '-')}</td></tr>
  </table>
</div>
"""

    # Output file info
    report_html += f"""
<div class="card">
  <table>
    <tr><td class="lbl">输出文件</td><td class="val">{mon.get('output_file', 'data/raw/openclaw_export.json')}</td></tr>
    <tr><td class="lbl">脚本命令</td><td class="val" style="font-size:12px;word-break:break-all">{mon.get('script_command', '-')}</td></tr>
  </table>
</div>
"""

    # Sources
    sources = data.get('source_counts', data.get('sources', {}))
    if sources:
        report_html += '<div class="card"><h2 style="font-size:16px;margin-top:0">数据源</h2><table>'
        for k, v in sources.items():
            report_html += f'<tr><td class="lbl">{k}</td><td class="val">{v} 条</td></tr>'
        report_html += '</table></div>'

    # Recent spots
    if spots:
        report_html += '<div class="card"><h2 style="font-size:16px;margin-top:0">最近采集</h2><table>'
        for s in spots[:10]:
            name = s.get('name', '?')
            city = s.get('location', {}).get('city', '')
            report_html += f'<tr><td class="val">{name}</td><td class="lbl">{city}</td></tr>'
        report_html += '</table></div>'

report_html += '</div></body></html>'

# Save report
report_path = r"C:\Users\Administrator\.openclaw\workspace\collector_monitor.html"
with open(report_path, "w", encoding="utf-8") as f:
    f.write(report_html)
print(f"Report saved: {report_path}")

# Try screenshot via the browser tool by navigating
import time
time.sleep(2)
print("JSON data extracted. Use browser to screenshot the monitor page at http://127.0.0.1:6001/moto/collector/monitor")
