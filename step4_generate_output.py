# -*- coding: utf-8 -*-
"""
Step 4: 生成最终输出文件
1. 辽宁摩旅路线_精选排名.json
2. 辽宁摩旅路线_精华摘要.md
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import json, re, datetime

with open(r'D:\摩旅数据采集\辽宁摩旅路线_去重评分.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

routes = data['routes']

# Clean up ollama reviews (remove terminal escape codes)
def clean_review(text):
    if not text:
        return ""
    # Remove [K sequences and other control chars
    text = re.sub(r'\[\d*[KABCD]', '', text)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text)
    return text.strip()

for r in routes:
    r['ollama_review'] = clean_review(r['ollama_review'])

# ---------- 1. Save精选排名 JSON ----------
with open(r'D:\摩旅数据采集\辽宁摩旅路线_精选排名.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("已保存: 辽宁摩旅路线_精选排名.json ({} 条路线)".format(len(routes)))

# ---------- 2. Generate精华摘要 MD ----------
# Also reload original data for stats
with open(r'D:\摩旅数据采集\辽宁摩旅路线_全量分析.json', 'r', encoding='utf-8') as f:
    raw_data = json.load(f)

total_raw = len(raw_data)
liaoning_count = sum(1 for d in raw_data if d['qualification_assessment']['is_liaoning_related'])
has_route_count = sum(1 for d in raw_data if d['route_analysis']['has_route_info'])
qualified = len(routes)

# Parse ollama review for display
def parse_review(text):
    """Split ollama review into [评语] and [建议] sections"""
    if not text or text == '[Ollama分析失败]':
        return "暂无AI点评", "暂无骑行建议"
    
    rating = ""
    advice = ""
    
    if '【评语】' in text:
        parts = text.split('【评语】')
        after = parts[1]
        if '【建议】' in after:
            rating = after.split('【建议】')[0].strip()
            advice = after.split('【建议】')[1].strip()
        else:
            rating = after.strip()
    elif '【建议】' in text:
        parts = text.split('【建议】')
        rating = parts[0].strip()
        advice = parts[1].strip() if len(parts) > 1 else ""
    else:
        rating = text[:100]
    
    # Clean up trailing garbage
    rating = re.sub(r'\[\w+', '', rating).strip()
    advice = re.sub(r'\[\w+', '', advice).strip()
    
    return rating or "适合摩旅路线", advice or "建议根据实际路线情况准备"

# Build markdown
md_lines = []
md_lines.append("# 🏍️ 辽宁摩旅路线精选分析报告\n")
md_lines.append("生成时间：{} | 数据来源：小红书 | 分析引擎：Qwen2.5-7B (Ollama)".format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M')))
md_lines.append("")

# Stats
md_lines.append("## 📊 总览")
md_lines.append("| 指标 | 数量 |")
md_lines.append("| --- | ---: |")
md_lines.append("| 原始采集笔记 | {} 条 |".format(total_raw))
md_lines.append("| 辽宁省内相关 | {} 条 |".format(liaoning_count))
md_lines.append("| 含路线信息 | {} 条 |".format(has_route_count))
md_lines.append("| 精选推荐路线 | {} 条 |".format(qualified))
md_lines.append("")

# Category distribution
route_types = {}
for r in routes:
    rt = r['route_analysis'].get('route_type', '未分类')
    route_types[rt] = route_types.get(rt, 0) + 1

md_lines.append("### 路线类型分布")
for rt, cnt in sorted(route_types.items(), key=lambda x: -x[1]):
    md_lines.append("- **{}**：{} 条".format(rt, cnt))
md_lines.append("")

# Top 5 routes
md_lines.append("## 🥇 TOP 5 摩旅路线\n")

for i, r in enumerate(routes[:5]):
    bi = r['basic_info']
    ra = r['route_analysis']
    eng = r['engagement']
    rating, advice = parse_review(r['ollama_review'])
    
    rank_badges = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    badge = rank_badges[i] if i < 5 else "#{}".format(i+1)
    
    wp_list = " → ".join(ra['waypoint_names']) if ra['waypoint_names'] else "未标注"
    moto_km = ra.get('estimated_motorcycle_km', 0)
    
    md_lines.append("### {}. {}  ({}/10)".format(badge, bi['title'], r['score']))
    md_lines.append("")
    md_lines.append("| 项目 | 内容 |")
    md_lines.append("| --- | --- |")
    md_lines.append("| **作者** | {} |".format(bi.get('author', '未知')))
    md_lines.append("| **里程** | {} km（预估骑行 {} km）|".format(ra['distance_km'], moto_km))
    md_lines.append("| **途经路线** | {} |".format(wp_list))
    md_lines.append("| **互动数据** | 👍 {} 赞 · ⭐ {} 收藏 · 💬 {} 评论 |".format(eng['likes'], eng['collects'], eng['comments']))
    md_lines.append("| **路线类型** | {} |".format(ra.get('route_type', '未分类')))
    md_lines.append("| **AI评分** | **{} / 10** |".format(r['score']))
    md_lines.append("")
    md_lines.append("**💡 AI 专业点评**：{}".format(rating))
    md_lines.append("")
    md_lines.append("**🛵 骑行建议**：{}".format(advice))
    md_lines.append("")

    # Show segments if available
    if ra.get('segments') and len(ra['segments']) > 0:
        md_lines.append("**🗺️ 路线分段**：")
        for seg in ra['segments']:
            md_lines.append("- {}".format(seg))
        md_lines.append("")

    # Show key comment insights
    ci = r.get('key_comment_insights', '')
    if ci and len(ci) > 20:
        md_lines.append("**💬 评论区洞察**：{}".format(ci[:200]))
        md_lines.append("")

    # Show sample comments
    comments = r.get('sample_comments', [])[:3]
    if comments:
        md_lines.append("**🗣️ 热门评论**：")
        for c in comments:
            content = c.get('content', '')[:80]
            likes = c.get('likes', 0)
            user = c.get('user', '匿名')
            md_lines.append("> \"{}\" — {} (👍 {})".format(content, user, likes))
        md_lines.append("")

    md_lines.append("---")
    md_lines.append("")

# Remaining top routes (6-15)
md_lines.append("## 🏆 更多精选路线 (排名 6-15)\n")

for r in routes[5:15]:
    bi = r['basic_info']
    ra = r['route_analysis']
    eng = r['engagement']
    rating, advice = parse_review(r['ollama_review'])
    
    wp_list = " → ".join(ra['waypoint_names'][:5]) if ra['waypoint_names'] else "未标注"
    if len(ra['waypoint_names']) > 5:
        wp_list += "…"
    
    md_lines.append("### #{} [{}分] {}".format(r['rank'], r['score'], bi['title']))
    md_lines.append("- **里程**：{} km | **途经点**：{}".format(ra['distance_km'], wp_list))
    md_lines.append("- **互动**：👍{} ⭐{} 💬{}".format(eng['likes'], eng['collects'], eng['comments']))
    md_lines.append("- **AI点评**：{}".format(rating[:120]))
    md_lines.append("- **骑行建议**：{}".format(advice[:120]))
    md_lines.append("")

# Full list
md_lines.append("## 📋 全部精选路线列表 ({}条)\n".format(len(routes)))
md_lines.append("| # | 标题 | 里程 | 途经点 | 热度 | 评分 |")
md_lines.append("| --- | --- | ---: | --- | ---: | ---: |")
for r in routes:
    rt = r['route_analysis']
    wp_names = rt['waypoint_names'] if rt['waypoint_names'] else []
    wp = "→".join(wp_names[:3]) if wp_names else "-"
    if len(wp_names) > 3:
        wp += "…"
    eng = r['engagement']
    total_eng = sum([eng['likes'], eng['collects'], eng['comments']])
    title_clean = r['basic_info']['title'].replace("|", "｜")[:25]
    md_lines.append("| {} | {} | {}km | {} | {} | {}/10 |".format(
        r['rank'], title_clean, rt['distance_km'], wp, total_eng, r['score']))

md_lines.append("")

with open(r'D:\摩旅数据采集\辽宁摩旅路线_精华摘要.md', 'w', encoding='utf-8') as f:
    f.write("\n".join(md_lines))

print("已保存: 辽宁摩旅路线_精华摘要.md")
print("\n摘要预览:")
# Print first few lines
preview = "\n".join(md_lines[:20])
print(preview)
