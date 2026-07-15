---
name: "douyin-对标采集"
description: "Windows浏览器搜索赛道爆款，采集标题/播放/封面特征，写入data.json benchmarking"
---

# douyin-对标采集

## 任务目标
搜索指定关键词的抖音视频，采集标题、播放量、作者、封面特征等数据，结构化写入 `data.json -> benchmarking`。

## 操作设备
**Windows（本机）** -- 浏览器 target="host"（默认）

**绝对不要登录峰峰账号。**

---

## 核心采集方案（浏览器JS注入）

不再手动滚动+截图。用JS一次性提取可见DOM数据，省token省时间。

## 标准操作流程

### 步骤A：搜索关键词

选3个关键词，打开抖音搜索页：
```
https://www.douyin.com/search/{关键词}?type=general
```

### 步骤B：用JS注入提取数据

用浏览器 act kind=evaluate 执行以下JS，提取搜索结果页所有可见视频：

```javascript
// 从抖音搜索结果页提取视频列表
(function() {
  const items = document.querySelectorAll('[class*="search"] [class*="item"], [class*="video-card"], article');
  const results = [];
  
  // 方法1: 从搜索结果容器取
  items.forEach(el => {
    const text = el.textContent || '';
    const links = el.querySelectorAll('a');
    const title = el.querySelector('[class*="title"]')?.textContent 
      || el.querySelector('p')?.textContent || '';
    
    // 提取播放量
    let plays = 0;
    const playMatch = text.match(/(\d+\.?\d*)\s*[万亿]?[次播放]/);
    if (playMatch) {
      const num = parseFloat(playMatch[1]);
      if (text.includes('\u4e07')) plays = num * 10000;
      else plays = num;
    }
    
    // 提取作者
    const author = el.querySelector('[class*="author"], [class*="nickname"]')?.textContent 
      || text.match(/@(\S+)/)?.[1] || '';
    
    // 提取头像/封面是否有真人的特征
    const imgs = el.querySelectorAll('img');
    const hasImg = imgs.length > 0;

    if (title) {
      results.push({
        title: title.trim(),
        author: author.trim() || '\u672a\u77e5',
        plays: plays,
        coverType: hasImg ? '\u67e5\u770b\u5c01\u9762' : '\u65e0\u56fe',
        raw: text.slice(0, 100),
      });
    }
  });
  
  // 如果方法1没结果，用方法2：取页面正文
  if (results.length < 3) {
    const lines = document.body.innerText.split('\n').filter(l => l.trim().length > 3);
    lines.forEach(line => {
      // 按关键词特征筛选
      if (line.includes('\u8dd1\u6b65') || line.includes('\u8fd0\u52a8') 
        || line.includes('\u8f6c\u53d1') || line.includes('\u89c2\u770b')) {
        results.push({raw: line.slice(0, 150)});
      }
    });
  }

  return JSON.stringify({
    keyword: location.href.match(/search\/([^?]+)/)?.[1] || '',
    count: results.length,
    items: results.slice(0, 30),
  }, null, 2);
})();
```

### 步骤C：特征标注

对提取到的每条视频，浏览器snapshot看一眼封面，手工标注：
- **coverStyle** -- 封面类型
- **hasPerson** -- 是否有真人出镜
- **titleType** -- 标题类型

### 步骤D：去重合并

读 `data.json -> benchmarking` 去重合并，按标题去重。

### 步骤E：更新对标账号库

提取播放>5000的新作者，去重后追加。

### 步骤F：更新封面策略分析

统计本批数据的封面特征写入 `benchmarking.coverStrategyStats`：
```json
{
  "realPersonRate": "真人出镜率%",
  "titleOnCoverRate": "封面有标题率%",
  "commonLayouts": ["常用布局1", "常用布局2"],
  "benchmarkingSample": "本批xxx条",
}
```

### 步骤G：更新标题模板

提取TOP3视频的标题公式。

### 步骤H：更新采集时间

```
benchmarking.lastCollection = "当前时间ISO"
benchmarking.source = "抖音搜索：关键词1 / 关键词2"
```

---

## 常见问题

### Q: JS提取到0条？
A: 说明DOM结构变了。跑 browser snapshot，手动看搜索结果区域的class/aria标签，更新JS选择器。

### Q: 播放量没显示？
A: 记录"播放: 无显示"，图文笔记不分析。

### Q: 验证码/空白页？
A: 跳过该关键词，换下一个。

### Q: 某个作者出现多次？
A: 每条都采集，标题去重在写入时做。
