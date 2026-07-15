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

**不再用点击/导航进详情页。** 所有数据通过浏览器 evaluate 执行JavaScript一次性从DOM提取。速度快、token省、不依赖页面改版。

---

## 标准操作流程

### 第一步：打开页面

```
https://creator.douyin.com/creator-micro/content/manage
```

### 第二步：提取作品列表数据

用 browser act kind=evaluate 执行JS，提取所有视频卡片数据：

```javascript
(function(){
  const result = {works: []};
  const bodyText = document.body.innerText;
  
  // 提取账号概览
  const fw = bodyText.match(/粉丝\s*(\d+)/);
  if (fw) result.followers = parseInt(fw[1]);
  
  // 从视频卡片提取列表  
  const cards = document.querySelectorAll('.video-card-zQ02ng');
  cards.forEach(c => {
    const t = c.textContent || '';
    const tm = t.match(/\d{2}:\d{2}\s+(.+?)#/);
    const pm = t.match(/播放\s*(\d+)/);
    const lm = t.match(/点赞\s*(\d+)/);
    const dm = t.match(/(\d{4}年\d{2}月\d{2}日)/);
    if (tm) {
      result.works.push({
        title: tm[1].trim(),
        plays: pm ? parseInt(pm[1]) : 0,
        likes: lm ? parseInt(lm[1]) : 0,
        date: dm ? dm[1] : '',
        status: t.includes('私密') ? '私密' : (t.includes('定时发布') ? '定时发布' : '已发布'),
      });
    }
  });
  
  return JSON.stringify(result);
})();
```

### 第三步：写回data.json

写入 `data.json -> creatorCenter.lastSnapshot`：

```json
{
  "fetchTime": "采集时间ISO",
  "source": "creator.douyin.com DOM提取",
  "overview": {"followers": 53, "totalLikes": 294, "totalWorks": 34},
  "videos": [...]
}
```

### 第四步：写入涨粉分析（强制）

每次写完数据后，必须计算：

```
每千播涨粉率 = 视频涨粉数 / 视频播放数 x 1000
健康值：2-5/千播 | 峰峰现状：0.28/千播
```

写入 `data.json -> creatorCenter.followerAnalysis`。

### 第五步：更新发后追踪简报（强制）

**创作者中心采完数据后，顺手更新发后追踪。**

1. 读 `data.json -> postPublishTracking.videos[]`
2. 找到 status=tracking 的视频
3. 用本次采集到的最新播放量/完播率更新其追踪数据
4. 发布超过7天的标记 status=completed
5. 新增刚发布视频的追踪条目

**这样发后追踪简报不再需要单独启动子Agent。**

### 第六步：检查异常

- 播放量暴增/暴跌 >50% -> 告警
- 完播率波动 >5个百分点 -> 记录
- 粉丝变化 >5 -> 告警
- 连续3天0涨粉 -> 告警

---

## 常见问题

### Q: DOM选择器失效？
A: 用 browser snapshot 看页面实际DOM结构，更新选择器。

### Q: 页面未登录？
A: 标记未登录，结束任务。

### Q: JS提取不到数据？
A: 分两步：先取列表，再用 snapshot 看内容结构调整JS。
