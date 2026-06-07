#!/usr/bin/env python3
"""招商银行黄金活期价格采集 - 纯网页抓取，零费用，不开浏览器"""

import urllib.request
import json
import re
import sys
from datetime import datetime

def fetch_sge_price():
    """从上海黄金交易所官网获取Au99.99实时价格"""
    url = "https://www.sge.com.cn/data/json/v7/public/price/marketQuotation"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Referer": "https://www.sge.com.cn/"
    })
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            # 解析上海金交所数据结构
            return {"source": "sge", "data": data}
    except Exception as e:
        return {"source": "sge", "error": str(e)}

def fetch_au9999_eastmoney():
    """从东方财富获取Au99.99行情"""
    url = "https://push2.eastmoney.com/api/qt/stock/get?secid=100.AU9999&fields=f43,f44,f45,f46,f47,f48,f57,f58,f168,f170,f171,f57,f58"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://quote.eastmoney.com/"
    })
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return {"source": "eastmoney", "data": json.loads(resp.read().decode("utf-8"))}
    except Exception as e:
        return {"source": "eastmoney", "error": str(e)}

def fetch_cmb_gold():
    """从招商银行官网获取黄金价格（通过其API网关）"""
    # 招行黄金积存金API
    url = "https://www.cmbchina.com/CFAPI/Gold/GoldDeal/Quotation"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://www.cmbchina.com/Market/Gold/",
    })
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            text = resp.read().decode("utf-8")
            if text.strip():
                return {"source": "cmb", "data": json.loads(text)}
            return {"source": "cmb", "error": "empty response"}
    except Exception as e:
        return {"source": "cmb", "error": str(e)}

def fetch_gold_api():
    """从gold-api.com获取国际金价并换算"""
    # 人民币金价
    url = "https://api.gold-api.com/price/XAU/CNY"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            price_cny = data.get("price", 0)
            # 盎司转克
            price_per_gram = round(price_cny / 31.1035, 2)
            return {
                "source": "gold-api",
                "price_usd_oz": round(data["price"] / data.get("exchangeRate", 6.8), 2),
                "price_cny_oz": round(data["price"], 2),
                "price_cny_g": price_per_gram,
                "currency": "CNY",
                "updated": data.get("updatedAt", ""),
                "exchange_rate": data.get("exchangeRate", 6.8)
            }
    except Exception as e:
        return {"source": "gold-api", "error": str(e)}

def main():
    results = {}
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"[{timestamp}] ===== 黄金价格采集 =====")
    
    # 优先用 gold-api（国际金价换算，最稳定）
    gold = fetch_gold_api()
    results["gold_api"] = gold
    if "error" not in gold:
        print(f"[金] 国际金价: {gold['price_usd_oz']:.2f} USD/oz")
        print(f"[金] 人民币金价: {gold['price_cny_g']:.2f} 人民币/克")
        print(f"[金] 金衡盎司价: {gold['price_cny_oz']:.2f} 人民币/oz")
        print(f"[金] 汇率: {gold['exchange_rate']}")
        print(f"[金] 更新时间: {gold['updated']}")
    else:
        print(f"[X] gold-api: {gold['error']}")
    
    # 尝试 SGE 国内金价
    sge = fetch_sge_price()
    results["sge"] = sge
    if "error" not in sge:
        print(f"[金] 上海金交所: 数据获取成功")
    else:
        print(f"[i]  SGE: {sge.get('error', 'unknown')}")
    
    # 尝试 CMB 招行
    cmb = fetch_cmb_gold()
    results["cmb"] = cmb
    if "error" not in cmb:
        print(f"[金] 招商银行: 数据获取成功")
    else:
        print(f"[i]  招行API: {cmb.get('error', 'unknown')}")
    
    # 输出JSON到stdout（便于cron捕获）
    print(f"\n--- JSON ---")
    print(json.dumps(results, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
