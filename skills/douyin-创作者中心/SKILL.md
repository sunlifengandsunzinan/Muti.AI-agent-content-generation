---
name: "douyin-创作者中心"
description: "Mac浏览器进入创作者中心，采集作品深度数据（完播率/2s跳出/涨粉/流量来源）"
---

# douyin-创作者中心

## 任务目标
通过已登录峰峰账号的Mac电脑，进入抖音创作者中心采集作品深度数据和账号概览数据，写入 `data.json → creatorCenter`。

## 操作设备
**🍎 Mac（sunlifeng-Mac）** — 浏览器目标：`target="node" node="sunlifeng-Mac"`

⚠️ **只做峰峰自己账号的操作**，不搜索同行，不采集他人数据。

---

## 标准操作流程

### 步骤A：打开创作者中心

```
https://creator.douyin.com/creator-micro/home
```

### 步骤B：采集账号概览（大盘数据）

从页面上方的数据卡片采集：
- 统计周期（通常是近7日）
- 播放量
- 播放量较前7日变化（+xx）
- 主页访问量
- 主页访问量较前7日变化
- 作品分享数
- 作品评论数
- 粉丝净增数

### 步骤C：采集最新作品列表

在投稿管理/作品列表区域，采集每个视频的基础数据：
- 标题
- 发布时间
- 播放量
- 点赞量
- 评论量
- 分享量
- 收藏量
- 弹幕量（如有）

### 步骤D：逐个视频查看分析（深度数据）

对近期的视频（特别是发布3天内的），点击"查看分析"进入 work-detail 页面，采集：

**总览tab：**
- 完播率（%）
- 2秒跳出率（%）
- 5秒完播率（%）
- 平均播放时长（秒）
- 粉丝播放占比（%）
- 涨粉量 / 脱粉量
- 互动数据：点赞/评论/收藏/分享/弹幕

**流量分析tab：**
- 推荐页来源占比（%）
- 个人主页来源占比（%）
- 搜索来源占比（%）
- 其他来源占比（%）

**对比tab（如有）：**
- 完播率变化（vs往期）
- 2s跳出率变化（vs往期）
- 5s留存变化（vs往期）
- 平均播放时长变化（vs往期）

**用户画像tab（如有）：**
- TOP10地区分布（地区+占比%）
- 兴趣标签分布

### 步骤E：优先关注重点作品

对以下作品优先采集深度数据（标记为 `priority: true`）：
1. 播放量 > 1000 的作品
2. 最近3天内发布的作品
3. 上轮采集遗漏深度的作品（`pendingDepthData` 列表中的）

### 步骤F：输出到 data.json

写入 `data.json → creatorCenter.lastSnapshot`：

```json
{
  "fetchTime": "ISO时间",
  "overview": {
    "followers": 54,
    "likesReceived": 285,
    "videos": 25,
    "plays7d": 15000,
    "homePageViews": 85,
    "likes7d": 151,
    "comments7d": 52,
    "shares7d": 2,
    "netFansGained7d": 45
  },
  "videos": [
    {
      "workId": "抖音视频ID",
      "title": "视频标题",
      "publishDate": "2026-07-14",
      "plays": 305,
      "likes": 10,
      "comments": 1,
      "shares": 0,
      "bookmarks": 2,
      "completionRate": 17.07,
      "exit2sRate": 24.94,
      "followerPlayRatio": 2.3,
      "fansGained": 0,
      "fansLost": 1,
      "duration": 17,
      "trafficSources": { "recommend": 79.8, "profile": 17.3, "search": 0.6, "friend": 1.3 },
      "audience": { "topRegions": [...], "interests": [...] },
      "commentHotWords": ["热词1", "热词2"],
      "priority": false
    }
  ],
  "depthFetched": ["已经采集深度数据的标题列表"],
  "pendingDepthData": ["需要补充深度的标题列表"],
  "videosWithDepth": 10
}
```

### 步骤G：检查异常数据

完成采集后检查：
- 是否有视频播放量暴增/暴跌（>50%变化）
- 完播率异常波动（>5个百分点）
- 粉丝数突变（净增/净减 >5）

异常数据在任务完成时在输出中高亮。

---

## 常见问题

### Q: 页面未登录/跳转到登录页？
A: 标记`未登录`，不重试，直接结束任务。

### Q: 某个视频的深度数据打不开？
A: 跳过后继续采集下一个，把未采集的workId加到 `pendingDepthData`。

### Q: 数据采集了一半浏览器页面崩了？
A: 重新打开创作者中心，从步骤C开始恢复采集。

### Q: 采集到的是自己账号的旧数据怎么办？
A: 对比 `data.json → creatorCenter.lastSnapshot.fetchTime`，确保本次比上次新。如果更旧则跳过不覆盖。
