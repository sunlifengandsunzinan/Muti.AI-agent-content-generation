# -*- coding: utf-8 -*-
"""
Step 3: Call Ollama qwen2.5:7b on each qualified route for AI review
Processes in batches of 5 to avoid overwhelming Ollama
"""
import sys, io, json, subprocess, time, re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Load deduplicated routes
with open(r'D:\摩旅数据采集\辽宁摩旅路线_去重评分.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

routes = data['routes']
print("准备用Ollama分析 {} 条路线...".format(len(routes)))

# First check Ollama is working
try:
    result = subprocess.run(
        ["ollama", "run", "qwen2.5:7b", "简单回复ok表示你工作正常。只回复ok。"],
        capture_output=True, text=True, timeout=60, encoding='utf-8', errors='replace'
    )
    print("Ollama响应: {}".format(result.stdout.strip()[:50]))
except Exception as e:
    print("Ollama测试失败: {}".format(e))
    sys.exit(1)

def call_ollama(prompt, max_retries=2):
    """Call Ollama with a prompt and return the response text."""
    for attempt in range(max_retries):
        try:
            result = subprocess.run(
                ["ollama", "run", "qwen2.5:7b", prompt],
                capture_output=True, text=True, timeout=120, encoding='utf-8', errors='replace'
            )
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                print("  Ollama错误 (attempt {}): {}".format(attempt+1, result.stderr[:100]))
        except subprocess.TimeoutExpired:
            print("  Ollama超时 (attempt {})".format(attempt+1))
        except Exception as e:
            print("  Ollama异常 (attempt {}): {}".format(attempt+1, str(e)[:100]))
        time.sleep(2)
    return "[Ollama分析失败]"

BATCH_SIZE = 5
total = len(routes)
completed = 0

for batch_start in range(0, total, BATCH_SIZE):
    batch_end = min(batch_start + BATCH_SIZE, total)
    print("\n===== 批次 {} (路线 {}-{}/{}) =====".format(
        batch_start//BATCH_SIZE + 1, batch_start+1, batch_end, total))
    
    for idx in range(batch_start, batch_end):
        r = routes[idx]
        bi = r['basic_info']
        ra = r['route_analysis']
        eng = r['engagement']
        
        title = bi['title']
        desc = (bi.get('description') or '')[:200]
        waypoints = ", ".join(ra['waypoint_names']) if ra['waypoint_names'] else "未标注"
        dist = ra['distance_km']
        mk = ra.get('estimated_motorcycle_km', 0)
        comments_text = (r.get('key_comment_insights') or '')[:300]
        
        print("  [{}/{}] {} ...".format(idx+1, total, title[:30]))
        
        prompt = """你是一个专业的摩托车旅行路线分析师。请用30-50字分析以下小红书骑行路线数据，给出专业评语和骑行建议。

标题：{title}
描述：{desc}
途经点：{waypoints}
里程：{dist}km
预估骑行里程：{mk}km
评论洞察：{comments}

请按以下格式回复（不要多余内容）：
【评语】一句话评价是否适合摩旅及路线亮点
【建议】车型、季节、耗时等具体骑行建议""".format(
            title=title, desc=desc, waypoints=waypoints, dist=dist,
            mk=mk, comments=comments_text)
        
        response = call_ollama(prompt)
        r['ollama_review'] = response
        completed += 1
        
        # Save intermediate progress every 5
        if completed % 5 == 0:
            with open(r'D:\摩旅数据采集\辽宁摩旅路线_去重评分.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print("  [自动保存进度: {}/{}]".format(completed, total))
    
    # Save after each batch
    with open(r'D:\摩旅数据采集\辽宁摩旅路线_去重评分.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("  批次完成，已保存进度")

print("\n===== 全部完成！=====")
print("已对 {} 条路线完成Ollama分析".format(completed))
