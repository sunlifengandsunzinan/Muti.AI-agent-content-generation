---
name: "douyin-创作者中心"
description: "Mac浏览器进入创作者中心，采集作品深度数据（完播率/2s跳出/涨粉/流量来源）并写入video-index.json"
---

# douyin-创作者中心

## 任务目标
通过已登录峰峰账号的Mac电脑，进入抖音创作者中心采集作品深度数据和账号概览数据，以**workId为唯一键**写入 `shared/video-index.json`。

## 操作设备
**Mac（sunlifeng-Mac）** — 浏览器目标：`target="node" node="sunlifeng-Mac"`

**只做峰峰自己账号的操作**，不搜索同行，不采集他人数据。

---

## 核心采集方案（API注入 → JS写文件）

**不要从DOM解析数据，不要逐个点详情页。**
直接调用创作者中心的 `work_list` API 一次性拿全量数据。

---

## 标准操作流程

### 第一步：打开页面
导航到作品管理页，确保已登录且有数据：
```
https://creator.douyin.com/creator-micro/content/manage
```
确认页面出现作品列表后再继续。

### 第二步：滚动加载所有作品
创作者中心默认只渲染可见视口内的作品卡片，需要先滚动到最底部触发虚拟渲染。

用 `browser act kind=evaluate` 执行JS反复滚动：
```javascript
// 滚动到最底部多次，确保懒加载完成
for(let i = 0; i < 10; i++) {
  window.scrollTo(0, document.body.scrollHeight);
  await new Promise(r => setTimeout(r, 1000));
}
```

验证加载完成：检查页面文本中有多少个日期行（或"已发布"标签的数量），与 video-index.json 中的视频数对比。

### 第三步：调用 work_list API 获取全量数据（核心）

JS注入，直接fetch API，分页拉取所有作品：

```javascript
(async function(){
  // 第一页
  const r1 = await fetch(
    'https://creator.douyin.com/janus/douyin/creator/pc/work_list?status=0&count=40&max_cursor=0&scene=star_atlas&device_platform=android&aid=1128',
    { credentials: 'include', headers: {'Content-Type': 'application/json'} }
  );
  const d1 = await r1.json();
  const cursor = d1.max_cursor;
  
  // 第二页（如果 has_more）
  let d2 = {items: []};
  if (d1.has_more) {
    const r2 = await fetch(
      `https://creator.douyin.com/janus/douyin/creator/pc/work_list?status=0&count=40&max_cursor=${cursor}&scene=star_atlas&device_platform=android&aid=1128`,
      { credentials: 'include', headers: {'Content-Type': 'application/json'} }
    );
    d2 = await r2.json();
  }
  
  const allItems = (d1.items || []).concat(d2.items || []);
  return JSON.stringify(allItems.map(item => ({
    workId: String(item.id),           // ⚠️ 重要：id 字段就是 workId
    createTime: item.create_time,      // Unix 时间戳
    title: (item.description || '').split('#')[0].trim(),
    coverUri: item.cover?.uri || '',
    type: item.type,                   // 2=日常口播, 3=图文
    visibility: item.visibility,        // 0=公开, 1=私密
    metrics: item.metrics || {}         // ⚠️ 包含所有深度数据
  })));
})();
```

API返回的metrics结构（重要字段）：
| 字段 | 含义 | 注意 |
|------|------|------|
| view_count | 播放量 | - |
| like_count | 点赞数 | - |
| comment_count | 评论数 | - |
| share_count | 转发数 | - |
| favorite_count | 收藏数 | - |
| completion_rate | 完播率 | 小数，如0.334=33.4% |
| completion_rate_5s | 5秒完播率 | 小数 |
| bounce_rate_2s | 2秒跳出率 | 小数，越低越好 |
| avg_view_second | 平均观看时长 | 秒 |
| avg_view_proportion | 平均观看比例 | 小数，如0.87=87% |
| fan_view_proportion | 粉丝观看占比 | 小数 |
| subscribe_count | 涨粉数 | 这条视频带来的 |
| subscribe_rate | 涨粉率 | - |
| unsubscribe_count | 掉粉数 | - |
| dislike_count | 不感兴趣数 | - |
| download_count | 下载次数 | - |
| cover_show | 封面曝光 | - |
| homepage_visit_count | 主页访问 | - |

**注意：如果某视频 view_count=0 且 metrics 几乎全为0，说明它是私密/审核中视频，可以跳过。**

### 第四步：写入 video-index.json

用 Python 脚本将 fetch 到的 JSON 数据写入 `shared/video-index.json`。

**数据结构：**

```json
{
  "version": 1,
  "lastUpdated": "2026-07-29T13:42:00+08:00",
  "fetchSource": "creator.douyin.com work_list API (Mac)",
  "videos": [
    {
      "workId": "7663757512897826088",
      "canonicalTitle": "老好人是不是都这么傻？我第N次被自己整笑了",
      "publishDate": "2026-07-18",
      "publishTime": "19:40",
      "publishDateTime": "2026-07-18T19:40:00+08:00",
      "duration": "00:10",
      "status": "已发布",
      "materialId": "unknown",
      "angle": "待定",
      "fromPageSnapshot": {
        "plays": 1622,
        "likes": 9,
        "comments": 1,
        "shares": 0,
        "fetchTime": "ISO时间"
      },
      "creatorSnapshot": {
        "viewCount": 1622,
        "likeCount": 9,
        "commentCount": 1,
        "shareCount": 0,
        "favoriteCount": 1,
        "completionRate": 0.334129,
        "completionRate5s": 0.598985,
        "bounceRate2s": 0.155668,
        "avgViewSecond": 8.764241,
        "avgViewProportion": 0.875724,
        "fanViewProportion": 0.003699,
        "subscribeCount": 0,
        "subscribeRate": 0,
        "unsubscribeCount": 0,
        "dislikeCount": 0,
        "downloadCount": 0,
        "coverShow": 16,
        "danmakuCount": 0,
        "homepageVisitCount": 15,
        "fetchTime": "2026-07-29T13:42:21+08:00"
      },
      "checkpoints": [],
      "createdInIndex": "2026-07-29",
      "updatedInIndex": "2026-07-29"
    }
  ],
  "overview": {
    "totalWorks": 32,
    "publicWorks": 32,
    "totalPlays": 37112,
    "totalLikes": 484,
    "totalComments": 183,
    "totalShares": 8,
    "avgPlaysPerWork": 1160,
    "likeRate": "1.30%",
    "followers": 53
  },
  "followerAnalysis": {
    "timestamp": "ISO时间",
    "totalPlaysSinceLastCheck": 0,
    "fansGainedSinceLastCheck": 0,
    "perThousandPlaysFollowerRate": 0,
    "healthRating": "极低",
    "note": "说明"
  },
  "lastUpdated": "2026-07-29T13:42:00+08:00"
}
```

#### 增量更新规则
1. **新视频**（workId不在index中）→ 新增条目
2. **已有视频** → 更新 creatorSnapshot / fromPageSnapshot
3. 同一视频有多个checkpoints → 追加到 checkpoints 数组
4. 标记为已删除的视频 → status: "已删除"

#### 时间戳转换
API返回 `create_time` 是Unix秒级时间戳（UTC），需要转为北京时间：
```python
from datetime import datetime, timezone, timedelta
dt = datetime.fromtimestamp(create_time, tz=timezone(timedelta(hours=8)))
dt.strftime('%Y-%m-%dT%H:%M:%S+08:00')  # publishDateTime
```

### 第五步：写入涨粉分析（强制）

每次写完数据后，必须计算：

```
每千播涨粉率 = 视频涨粉数 / 视频播放数 x 1000
健康值：2-5/千播 | 峰峰现状：接近0
```

写入 `video-index.json -> followerAnalysis`。

### 第六步：更新发后追踪

1. 读 `video-index.json` 中所有视频
2. 找到最近7天内发布的视频 → status标记为 tracking
3. 检查是否需要出简报（D+1/D+3/D+7）
4. 发布超过7天的标记 status=completed
5. 检查异常：
   - 播放量暴增/暴跌 >50% → 记录
   - 完播率波动 >5个百分点 → 记录

### 第七步：低播放视频分析（强制）

检查作品中 **发布已超过24h且播放<300** 的视频（从API返回的view_count判断）。

分析原因写入 `video-index.json` 对应视频的 `analysis.judgement` 字段。

---

## 已知问题与解决方法

### Q: work_list API 找不到？
A: work_list 是创作者中心作品管理页(XHR)调用的API，必须在已登录状态下从页面内fetch。不要在浏览器外直接curl调用（缺少cookie）。

### Q: workId从DOM提取不到？
A: **不要从DOM/卡片提取workId**。创作者中心的卡片DOM没有暴露workId。必须通过API返回的 `id` 字段获取。

### Q: api返回 count 少于总数？
A: 一次最多返回40条，需要翻页。检查 `has_more` 字段，用 `max_cursor` 继续请求。

### Q: 页面未登录？
A: 标记未登录，结束任务。

### Q: video-index.json 不存在？
A: 首次新建。后续每次采集都是增量更新。
