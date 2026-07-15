---
name: "douyin-每日简报"
description: "读data.json出结构化简报，对比今日vs昨日变化，汇总关键洞察"
---

# douyin-每日简报

## 任务目标
读 `data.json` 的三块数据（creatorCenter + benchmarking + postPublishTracking），汇总成一份结构化日报。不出外部操作，**纯分析任务**。

## 操作设备
**当前会话** — 不需要浏览器，只读文件。

---

## 简报模板

### 1️⃣ 账号概览（对比昨日）

```
账号：40了，得干点儿啥了
粉丝：xx（昨xx）| 获赞：xx（+x）| 作品数：xx
7日播放：xx 万（+xx vs 前7日）
7日涨粉：+xx
```

### 2️⃣ 新作品表现（最新2-3条）

| 标题 | 日期 | 播放 | 完播率 | 2s跳出 | 涨粉 | 判定 |
|:----|:---:|:---:|:-----:|:------:|:---:|:----|
| 标题 | D+? | xxx | xx% | xx% | +x | ✅/❌ |

### 3️⃣ 播放量变化（对比上次采集）

对每条有历史对比数据的作品：

```
[视频名] xxx → xxx (+x / -x / =)
```

### 4️⃣ 异常标记

如果有以下情况，高亮标记：

**🚀 爆款预警：**
- 单日播放同比涨 >200%
- 7日播放 >5000

**⚠️ 数据下滑：**
- 完播率下降 >5pp
- 2s跳出上升 >10pp

**⛔ 严重不足：**
- D+3 播放 <300
- 点赞 <5

### 5️⃣ 对标洞察（如有新数据）

```
赛道趋势：金句型占比xx%，封面主流是xx
值得关注的作者：xxx（播放xxx，标题策略：xxx）
```

### 6️⃣ 今日建议

```
基于当前数据，建议下一步：
- 方向建议：____（基于涨的趋势）
- 素材建议：____（如果可用素材不匹配）
- 风险提示：____（如果有观点重复或偏离赛道风险）
```

---

## 每次执行前必须做

1. **读 `data.json → creatorCenter`** — 最新作品数据
2. **读 `data.json → benchmarking`** — 最新对标数据
3. **读 `data.json → postPublishTracking`** — 发后追踪状态
4. **读昨天的memory文件** — 看昨日基线

## 输出方式

用 `write` 写到 `skills/douyin-每日简报/shared/daily_briefing_YYYYMMDD.json`，同时在输出结论中直接汇报给峰峰。

```json
{
  "date": "2026-07-15",
  "account": {
    "followers": 54,
    "followersChange": 0,
    "likesReceived": 285,
    "likesChange": 12,
    "plays7d": 15000,
    "plays7dChange": 11600
  },
  "newVideos": [...],
  "anomalies": [
    { "type": "爆款|下滑|不足", "video": "...", "detail": "..." }
  ],
  "benchmarkingInsight": "金句型占比最高32%",
  "recommendation": "方向建议..."
}
```

## 安静模式

- 数据正常时：写文件不主动打扰，等峰峰下次聊天时告知
- 数据异常时：在输出中高亮，峰会问的时候直接说
