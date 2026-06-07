# -*- coding: utf-8 -*-
"""
Step 2: 筛选合格摩旅路线 + 打分
"""
import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

with open(r'D:\摩旅数据采集\辽宁摩旅路线_全量分析.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# ============ Step 2: 筛选 ============
qualified_routes = []
rejected_reasons = []

for i, d in enumerate(data):
    title = d['basic_info']['title'] + ' ' + d['basic_info'].get('description','')
    ra = d['route_analysis']
    title_short = d['basic_info']['title'][:30]
    
    # 规则1：必须有途经点
    if len(ra['waypoint_names']) < 2:
        continue
    
    # 规则2：里程大于10km
    if ra['distance_km'] < 10:
        continue
    
    # 规则3：必须是辽宁内容
    if not d['qualification_assessment']['is_liaoning_related']:
        continue
    
    # 规则4：排除明显的非路线内容
    exclude_kw = ['咖啡店','探店','奶茶','甜点','婚纱','写真','妆造','美甲']
    if any(kw in title for kw in exclude_kw):
        continue
    
    # 规则5：收藏数 > 100 且 点赞 > 100
    if d['engagement']['collects'] < 100 and d['engagement']['likes'] < 100:
        continue
    
    qualified_routes.append(d)

print(f"=== 筛选结果 ===")
print(f"总原始数据: {len(data)}")
print(f"合格路线数: {len(qualified_routes)}")

# ============ 打分 ============
def score_route(d):
    score = 0.0
    ra = d['route_analysis']
    title = d['basic_info']['title'] + ' ' + d['basic_info'].get('description','')
    wp_count = len(ra['waypoint_names'])
    dist = ra['distance_km']
    likes = d['engagement']['likes']
    collects = d['engagement']['collects']
    comments = d['engagement']['comments']
    
    # 1. 路线相关性 (3分) - 是否真正摩旅/骑行/自驾路线
    motor_kw = ['摩旅','摩托车','骑行','自驾','跑山','压弯','机车','骑车','摩托','旅行','公路']
    route_kw = ['路线','环线','攻略','行程','路书','穿越','沿途','风景']
    text = title + ' ' + str(ra.get('mentions',{}))
    moto_score = 0
    for kw in motor_kw:
        if kw in text:
            moto_score += 0.8
    for kw in route_kw:
        if kw in text:
            moto_score += 0.5
    moto_score = min(moto_score, 3.0)
    # 如果有分段/里程信息加分
    if ra.get('segments') and len(ra['segments']) > 0:
        moto_score += 0.3
    if ra.get('estimated_motorcycle_km',0) > 0:
        moto_score += 0.3
    # 途经点数量适中加分
    if 3 <= wp_count <= 8:
        moto_score += 0.4
    score += min(moto_score, 3.0)
    
    # 2. 里程合理性 (2分)
    if 50 <= dist <= 500:
        score += 1.5
    elif 10 <= dist < 50:
        score += 0.8
    elif 500 < dist <= 800:
        score += 1.0
    else:
        score += 0.3
    # 补充：有motorcycle_km且合理加分
    mk = ra.get('estimated_motorcycle_km', 0)
    if 50 <= mk <= 500:
        score += 0.5
    score = min(score, 2.0 + (2.5 if mk > 0 else 0))  # cap
    
    # 3. 互动热度 (2分)
    total_engagement = likes + collects + comments
    if total_engagement > 5000:
        score += 2.0
    elif total_engagement > 2000:
        score += 1.5
    elif total_engagement > 800:
        score += 1.0
    elif total_engagement > 200:
        score += 0.5
    else:
        score += 0.2
    
    # 4. 评论信息量 (3分) - 是否有路况细节
    ci = d.get('key_comment_insights', '')
    # 评论数加分
    if comments > 50:
        score += 1.0
    elif comments > 20:
        score += 0.6
    elif comments > 5:
        score += 0.3
    else:
        score += 0.1
    
    # 评论insights质量
    if ci:
        insight_len = len(ci)
        if insight_len > 200:
            score += 1.5
        elif insight_len > 80:
            score += 1.0
        elif insight_len > 30:
            score += 0.5
        else:
            score += 0.2
    
    # 有实际路况细节关键词加分
    detail_kw = ['路况','堵','修路','弯道','坡','坡度','山路','碎石','泥土','铺装','隧道','观景台','加油','住宿','吃饭']
    if ci:
        for kw in detail_kw:
            if kw in ci:
                score += 0.2
                break
    
    return min(round(score, 1), 10.0)

# 打分并排序
scored = []
for d in qualified_routes:
    s = score_route(d)
    scored.append((s, d))

scored.sort(key=lambda x: -x[0])

print(f"\n=== 打分排名 ===")
for i, (s, d) in enumerate(scored[:10]):
    print(f"  #{i+1} [{s}/10] {d['basic_info']['title'][:35]} | {d['route_analysis']['distance_km']}km | 点赞{d['engagement']['likes']} 收藏{d['engagement']['collects']}")

# 保存中间结果
output = []
for s, d in scored:
    item = {
        'score': s,
        'rank': len(output) + 1,
        'note_id': d['note_id'],
        'basic_info': d['basic_info'],
        'engagement': d['engagement'],
        'route_analysis': d['route_analysis'],
        'qualification_assessment': d['qualification_assessment'],
        'sample_comments': d.get('sample_comments', []),
        'key_comment_insights': d.get('key_comment_insights', ''),
        'ollama_review': ''
    }
    output.append(item)

with open(r'D:\摩旅数据采集\辽宁摩旅路线_评分中间结果.json', 'w', encoding='utf-8') as f:
    json.dump({'total_raw': len(data), 'liaoning_related': sum(1 for d in data if d['qualification_assessment']['is_liaoning_related']),
               'has_route_info': sum(1 for d in data if d['route_analysis']['has_route_info']),
               'qualified_count': len(scored), 'routes': output}, f, ensure_ascii=False, indent=2)

print(f"\n评分结果已保存，共 {len(scored)} 条合格路线")
