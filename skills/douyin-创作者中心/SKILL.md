---
name: "douyin-创作者中心"
description: "Mac浏览器进入创作者中心，采集作品深度数据（完播率/2s跳出/涨粉/流量来源）"
---

# douyin-创作者中心

## 任务目标
通过已登录峰峰账号的Mac电脑，进入抖音创作者中心采集作品深度数据和账号概览数据，写入 `data.json -> creatorCenter`。

## 操作设备
**Mac（sunlifeng-Mac）** -- 浏览器目标：`target="node" node="sunlifeng-Mac"`

**只做峰峰自己账号的操作**，不搜索同行，不采集他人数据。

---

## 核心采集方案（浏览器JS注入）

**不再用点击/导航进详情页。** 所有数据通过浏览器 evaluate 执行JavaScript一次性从DOM提取。速度快、token省、稳定性高。

## 标准操作流程

### 第一步：打开页面

导航到作品管理页：
```
https://creator.douyin.com/creator-micro/content/manage
```

### 第二步：提取作品列表数据

用 browser act kind=evaluate 执行以下JS，提取所有视频卡片数据：

```javascript
// 从视频卡片DOM提取完整列表
const data = {
  fetchTime: new Date().toISOString(),
  source: 'creator.douyin.com 作品管理页 - DOM提取',
  overview: {},
  works: [],
};

// 提取账号概览（页面顶部可能有数据卡片）
const cards = document.querySelectorAll('.data-card-value, .stat-value, [class*="statistics"]');
// 页面正文文本
const bodyText = document.body.innerText;

// 提取每行播放/点赞数据
// 作品管理页的结构：每个卡片包括视频时长、标题、日期、播放、点赞/评论
const workCards = document.querySelectorAll('.video-card-zQ02ng');
workCards.forEach(card => {
  const text = card.textContent || '';
  const titleMatch = text.match(/\d{2}:\d{2}\s+(.+?)#/);
  const playMatch = text.match(/播放\s*(\d+)/);
  const likeMatch = text.match(/点赞\s*(\d+)/);
  const dateMatch = text.match(/(\d{4}年\d{2}月\d{2}日)/);
  const isPrivate = text.includes('\u79c1\u5bc6'); // 私密
  const isScheduled = text.includes('\u5b9a\u65f6\u53d1\u5e03'); // 定时发布

  data.works.push({
    title: titleMatch ? titleMatch[2].trim() : '',
    publishDate: dateMatch ? dateMatch[1] : '',
    plays: playMatch ? parseInt(playMatch[1]) : 0,
    likes: likeMatch ? parseInt(likeMatch[1]) : 0,
    status: isPrivate ? '\u79c1\u5bc6' : (isScheduled ? '\u5b9a\u65f6\u53d1\u5e03' : '\u5df2\u53d1\u5e03'),
  });
});

// 尝试提取账号总数据（粉丝数、获赞、作品数）
// 从数据中心页面或侧边信息提取
const followersMatch = bodyText.match(/\u7c89\u4e1d\s*(\d+)/); // 粉丝
if (followersMatch) data.overview.followers = parseInt(followersMatch[1]);

// 返回JSON字符串用于复制
JSON.stringify(data, null, 2);
```

### 第三步：写回data.json

将上一步返回的JSON，写入 `data.json -> creatorCenter.lastSnapshot`：

```json
{
  "fetchTime": "2026-07-15T22:27:00+08:00",
  "source": "creator.douyin.com \u4f5c\u54c1\u7ba1\u7406\u9875 - DOM\u63d0\u53d6",
  "overview": {
    "followers": 53,
    "totalLikes": 294,
    "totalWorks": 34
  },
  "videos": [
    {"title": "...", "publishDate": "2026-07-15", "playCount": 414, "likes": 7}
  ],
  "depthFetched": false,
  "followerAnalysis": {
    "currentFollowers": 53,
    "change24h": -1,
    "followerConversionPer1000Plays": 0.28
  }
}
```

### 第四步：获取深度数据（完播率/2s跳出）

深度数据需要进入数据中心页面。导航到：
```
https://creator.douyin.com/creator-micro/data
```

在数据中心页提取每个视频的完播率/2s跳出。如果无法直接从DOM提取，则用截图+视觉方式记录关键数据。

### 第五步：写入涨粉分析

每次写完数据后，必须计算并写入 `followerAnalysis`：

```
每千播涨粉率 = 视频涨粉数 / 视频播放数 x 1000
健康值：2-5/千播
峰峰现状：0.28/千播
```

```json
{
  "currentFollowers": 53,
  "change24h": -1,
  "change7d": 0,
  "followerConversionPer1000Plays": 0.28,
  "videosWithFollowerGain": ["标题1", "标题2"],
  "followerWastingVideos": [
    {"title": "标题", "followerGain": 0, "plays": 800, "reason": "\u5171\u9e23\u578b\u7ed3\u5c3e\u65e0\u951a\u70b9"}
  ],
  "alert": "\u7c89\u4e1d\u63890\u4eba\u4ee5\u4e0b\u4e0d\u544a\u8b66"
}
```

### 第六步：检查异常

- 播放量暴增/暴跌 >50% -> 标记告警
- 完播率波动 >5个百分点 -> 记录
- 粉丝变化 >5 -> 告警
- 连续3天0涨粉 -> 告警

---

## 常见问题

### Q: DOM选择器失效？
A: 用 browser snapshot 查看页面的实际DOM结构，更新选择器。优先用 class 包含 video-card 或 work-card 的元素。

### Q: 页面未登录？
A: 标记`未登录`，结束任务。

### Q: JS执行超时/页面复杂？
A: 分两步：先取列表数据，再取overview数据。不要一次提取太多。

### Q: 数据采集了一半页面崩了？
A: 重新打开创作者中心页面，恢复提取。
