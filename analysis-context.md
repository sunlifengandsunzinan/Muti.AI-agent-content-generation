# 抖音数据 → 摩旅路线整合流程文档 (v1.0)
## 适用范围: analysis agent 在下一轮数据处理中复用

---

## 一、全流程概览

```
抖音搜索采集 → JSONL原始数据 → V7正则提取路线 → 合并进 route_templates.json 
→ 补全 days_plan 详情 → 校验字段格式 → 上线
```

## 二、关键步骤详解

### 步骤1: 从 JSONL 中提取路线详情
原始抖音搜索结果存在 `D:\MediaCrawlerResult\douyin\jsonl\search_contents_2026-06-07.jsonl`
每条记录含 `aweme_id`, `aweme_url`, `title`, `desc`, comments 等字段。

**提取途经点的方法：**
- 视频的 `desc`（描述）字段是最有价值的信息源
- 很多摩旅视频的描述里会直接写出完整路线（如："小市县城→清河城镇→岗东村→滴二线翻山→田师付镇→G506国道返程"）
- 用关键词匹配（从 route slug 提取关键词）找到对应视频

### 步骤2: 补全 days_plan 详细字段
`days_plan` 数组中的每一天必须包含以下字段：

```python
{
    "day": 1,                # int，第几天
    "title": "沈阳→灯塔粮仓", # str，当天路线标题
    "ride_time": "5-6小时",  # str，骑行时间
    "distance": 180,         # int/float，当天里程
    "highlights": ["亮点1", "亮点2"],  # list[str]
    "note": "备注信息..."    # str
}
```

**⚠️ 常见坑：** `merge_to_mac.py` 写入的 days_plan 只含有 `day/title/distance_km`（字符串），缺少 `ride_time/highlights/note`，且 `distance` 应为数字而非字符串。必须做格式转换后再写回。

### 步骤3: 字段校验
写入前校验 `route_templates.json` 中每条路线的格式：

```python
校验项:
- days_plan 必须为 list，且 length > 0
- 每个 day 必须含: day(int), title(str), ride_time(str非空), 
  distance(int/float), highlights(list), note(str非空)
- spot_slugs 必须为 list (可为空)
```

校验通过后重新写入 JSON 文件。

### 步骤4: API Serializer 修正
**重要！** Flask 的 API serializer 在 `planner_service.py` 的 `_route_index_card` 函数中。

默认只传了：
```python
"days_plan": [
    {"day": day["day"], "title": day["title"], "distance": day["distance"]}
    for day in route.get("days_plan", [])
]
```

需要手动加 `ride_time`, `highlights`, `note`：
```python
"days_plan": [
    {
        "day": day["day"],
        "title": day["title"],
        "distance": day.get("distance", 0),
        "ride_time": day.get("ride_time", ""),
        "highlights": day.get("highlights", []),
        "note": day.get("note", ""),
    }
    for day in route.get("days_plan", [])
]
```

### 步骤5: 同步与启动
```
1. 更新 Windows 的 route_templates.json
2. scp 到 Mac: ~/Documents/moto/app/services/route_templates.json
3. 重启 Flask (app.py, 端口设为 5000)
4. 验证: curl http://127.0.0.1:5000/api/moto/routes
5. Mac proxy (127.0.0.1:5000 → 192.168.0.112:5000) 无需重启
```

## 三、文件位置

| 文件 | 位置 |
|------|------|
| 抖音原始数据 | `D:\MediaCrawlerResult\douyin\jsonl\search_contents_*.jsonl` |
| 抖音评论数据 | `D:\MediaCrawlerResult\douyin\jsonl\search_comments_*.jsonl` |
| 路线 JSON | `C:\Users\Administrator\temp_moto\app\services\route_templates.json` |
| API builder | `C:\Users\Administrator\temp_moto\app\services\planner_service.py` |
| 字段校验器 | `C:\Users\Administrator\temp_moto\app\services\route_templates_config.py` |
| Mac 同步目标 | `~/Documents/moto/app/services/route_templates.json` |
| 修复脚本示例 | `C:\Users\Administrator\AppData\Local\Temp\enrich_route_details.py` |

## 四、已知问题

1. **Flask 默认端口 6001**: `app.py` 里写死了 `port=6001`，部署需要改为 `flask run --port=5000` 或通过环境变量覆盖
2. **Mac python3 的 xcrun bug**: Mac 上不要用 `python3 -c "..."` 内联验证，用 Node 或写文件到 Mac 再执行
3. **PowerShell 引号地狱**: 含嵌套引号的长命令在 PowerShell 中极其容易崩溃，优先用 Python subprocess 或写 .py 文件执行
4. **emoji ✅ 在 GBK 编码报错**: Windows PowerShell pipe 到文件时用 GBK 编码，含 emoji 的 print 会报 `UnicodeEncodeError`，需要 `sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")`
5. **blueprints 目录恢复**: 之前 `Remove-Item "app/blueprints/*"` 递归删除了 `__init__.py` 等关键文件，可从 Mac scp 恢复

## 途经点质量标准（重要 ⚠️）

**只有城市名的路线 = 低质量数据，不予采用。**

最终地图展示时，纯城市级的途经点在底图上只会画几条城市连线，没有骑行参考价值。

### 可用的途经点格式
- ✅ 具体道路："北叆线思山岭→草河掌露营地"
- ✅ 乡镇级："小市县城→清河城镇→岗东村"
- ✅ 景点+道路："七星山→爱新觉罗皇家博物院→辽河沿岸观花道路"
- ✅ 导航路线："胜利南街→沈营线→灯塔粮仓文创园"
- ❌ 纯城市名："沈阳→辽阳→本溪"
- ❌ 纯区域名："辽东地区"

### 数据清洗规则
1. 从 `search_contents_*.jsonl` 的 `desc` 字段提取
2. 含 "→""导航""路线" 等关键词的最有价值
3. 如果一整批都只有城市级数据，标记低质量，跳过
4. 评论区也经常有详细路线

### 后续提取优先级
1. 描述中有道路/乡镇级途经点 → 保留
2. 描述只有城市 → 看评论
3. 评论也没有 → 跳过
4. 全部低质量 → 放弃该批次

## 六、下一轮数据处理建议

1. 将 `enrich_route_details.py` 中的途经点提取逻辑从**手动编写**改为**自动从 JSONL 描述中解析**
2. 描述中多数格式为"第一站→第二站→第三站"或"导航XXX→XXX→XXX"，可直接用正则提取
3. 新增路线时建议直接从 JSONL 关联视频 ID 后解析 desc，避免写一个空壳 days_plan
4. 注意 `distance_km` vs `distance` 字段名区别：API 中标题栏用 `distance_km`，days_plan 中用 `distance`
