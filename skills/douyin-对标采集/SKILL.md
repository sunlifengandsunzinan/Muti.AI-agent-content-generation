---
name: "douyin-对标采集"
description: "Windows浏览器搜索赛道爆款，采集标题/播放/封面特征，写入data.json benchmarking"
---

# douyin-对标采集

## 任务目标
搜索指定关键词的抖音视频，采集标题、播放量、作者、封面特征、色调等数据，结构化写入 `data.json → benchmarking`。

## 操作设备
**🖥️ Windows（本机）** — 浏览器 target="host"（默认）

⚠️ **绝对不要登录峰峰账号**。搜到什么就是什么，不登录不发布。

---

## 标准操作流程

### 步骤A：搜索关键词

每次执行时，从以下关键词库中选 **3个未搜索过或数据较旧的关键词**：
- 中年跑步 感悟
- 40岁 跑步 自律
- 跑步 治愈 人生
- 40岁开始跑步 真实感受
- 跑步 中年男人 心态
- 坚持跑步 变化
- 中年人运动 坚持

用浏览器打开抖音搜索页：
```
https://www.douyin.com/search/{关键词}?type=general
```

### 步骤B：采集视频数据

对搜索结果页，**滚动到第3页**（确保数据量），采集能获取的所有视频：
- 作者名
- 标题（完整标题）
- 播放量
- 发布时间

### 步骤C：记录画面特征

对每个视频记录：
- **coverStyle** — 封面类型：`跑步侧影+大字` / `表情特写+标题` / `风景空镜+文字` / `对比图/文字标题卡` / `文字标题卡` / `其他`
- **hasPerson** — 是否有真人出镜：true/false
- **colorTone** — 色调风格：`自然光` / `暖色调` / `冷色调` / `高对比`
- **titleType** — 标题类型：`设问型` / `宣言型` / `金句型` / `叙事型` / `反差型`

### 步骤D：输出JSON

用 `write` 工具写到 `data.json → benchmarking`：

1. 读现有 `data.json` 的 `benchmarking` 段
2. 去重合并：如果标题已存在，跳过不重复写入
3. 新视频写入 `benchmarking.videos[]`
4. 更新 `benchmarking.visualAnalysis`：
   - `titleTypeDistribution`：重新统计所有视频的标题类型分布
   - `coverTypeDistribution`：重新统计所有视频的封面类型分布
   - `realPersonRate`：真人出镜比例
   - `bestAccounts`：更新最高播放作者TOP5

### 步骤E：更新对标账号库

1. 从本次采集的视频中，提取播放>5000的新作者
2. 检查 `benchmarking.accounts[]` 是否已有，去重后追加
3. 每个新增账号格式：
```json
{
  "name": "作者名",
  "note": "最高播放xxxx | 赛道定位",
  "representativeVideo": "最高播放标题",
  "maxPlays": 最高播放数
}
```

### 步骤F：更新标题模板

根据本次采集的高播放视频（TOP3），提取新的标题公式写入 `benchmarking.titleTemplateInsights.effectiveFormulas[]`。

### 步骤G：更新采集时间

```
benchmarking.lastCollection = "当前时间ISO"
benchmarking.source = "抖音搜索：关键词1 / 关键词2 / 关键词3"
```

---

## 输出示例

```json
{
  "title": "当一个中年人突然开始频繁跑步，意味着什么",
  "author": "严料坊银星",
  "plays": "2.3万",
  "publishDate": "2025年10月1日",
  "titleType": "设问型",
  "coverStyle": "表情特写+标题",
  "hasPerson": true,
  "colorTone": "自然光",
  "keyword": "中年跑步 感悟"
}
```

---

## 常见问题

### Q: 搜索结果中没有播放量显示？
A: 记录 "播放: 无显示" 并备注是图文还是视频。图文笔记不需要封面特征分析。

### Q: 遇到验证码/空白页？
A: 标记`该关键词遇到拦截`，跳过并尝试下一个关键词，不重试不登录。

### Q: 某个作者出现多次怎么办？
A: 每条视频都采集，标题去重只在写入时做，作者可以重复出现。
