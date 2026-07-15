---
name: "douyin-情报站"
description: "导航调度：根据任务性质分派到3个独立子技能执行（对标采集/创作者中心/每日简报）"
---

# douyin-情报站

⚠️ **本文件从2026-07-15起不再包含具体操作指令。**

具体任务已拆分为3个独立子技能，通过 **子Agent模式** 或 **主会话→subagent** 方式执行。此文件只做任务分派。

---

## 任务分派表

| 你要做什么 | 应该读哪个SKILL | 操作机器 |
|:----------|:---------------|:--------|
| 搜赛道爆款、采集对标数据 | `skills/douyin-对标采集/SKILL.md` | 🖥️ Windows |
| 采集自己账号的作品深度数据 | `skills/douyin-创作者中心/SKILL.md` | 🍎 Mac |
| 出每日简报、对比数据变化 | `skills/douyin-每日简报/SKILL.md` | 当前会话 |
| 发后追踪（采集数据+出简报） | 先读`创作者中心`采集数据，再用`每日简报`出报告 | 🍎 Mac + 会话 |

---

## 数据枢纽

所有子技能读写同一个 `shared/data.json`，不存在多份数据副本。

```
对标采集 → 写入 benchmarking
创作者中心 → 写入 creatorCenter
每日简报 → 读取 benchmarking + creatorCenter + postPublishTracking
发后追踪 → 写入 postPublishTracking
```
