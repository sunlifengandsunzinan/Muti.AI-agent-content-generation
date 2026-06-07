#!/usr/bin/env python3
"""Screenshot using Chrome DevTools Protocol"""
import io, sys, json, base64, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import http.client
import time

def cdp_send(method, params=None, session_id=None):
    body = json.dumps({"id": 1, "method": method, "params": params or {}})
    conn = http.client.HTTPConnection("127.0.0.1", 9223, timeout=30)
    conn.request("POST", "/json/execute", body, {"Content-Type": "application/json"})
    resp = conn.getresponse()
    return json.loads(resp.read().decode())

def cdp_get_tabs():
    conn = http.client.HTTPConnection("127.0.0.1", 9223, timeout=30)
    conn.request("GET", "/json")
    resp = conn.getresponse()
    return json.loads(resp.read().decode())

try:
    tabs = cdp_get_tabs()
    for t in tabs:
        if "collector" in t.get("url", "") or "6001" in t.get("url", ""):
            target_id = t["id"]
            print(f"Found tab: {t['url']}")
            break
    else:
        print("No target tab found, creating one")
        conn = http.client.HTTPConnection("127.0.0.1", 9223, timeout=30)
        conn.request("PUT", f"/json/new?http://127.0.0.1:6001/moto/collector/monitor")
        resp = conn.getresponse()
        new_tab = json.loads(resp.read().decode())
        print(new_tab)
        target_id = new_tab["id"]
    
    time.sleep(3)
    
    # Screenshot
    result = cdp_send("Page.captureScreenshot", {"format": "png", "fromSurface": True})
    
    if "result" in result:
        b64 = result["result"]["data"]
        output = r"C:\Users\Administrator\.openclaw\workspace\collector_monitor.png"
        with open(output, "wb") as f:
            f.write(base64.b64decode(b64))
        print(f"Screenshot saved: {output} ({os.path.getsize(output)} bytes)")
    else:
        print(f"FAILED: {result}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
