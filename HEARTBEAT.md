# 情报站心跳轮询任务

## 每个心跳轮次执行

### 1. 检查 events.json
读 `shared/events.json`，找 `done=false` 的事件：
- 如果是采集类事件 → 启动子Agent干活
- 如果是脚本/标题待处理事件 → 通知Manager处理
- 处理完成后标记 `done=true`

### 2. 检查今天是否已完成数据采集
看 `memory/YYYY-MM-DD.md` 是否已有当天的采集记录：
- 已经采了：跳过
- 还没采且是8:00-18:00之间：执行基础采集（Windows浏览器）
- 还没采且是8:30-18:00之间：执行创作者中心采集（Mac浏览器）

### 3. 检查发后追踪
读 `shared/data.json` → `postPublishTracking.videos`：
- 找 `status != "completed"` 的视频
- 看有没有该出简报还没出的（D+1/D+3/D+7）
- 如有，启动子Agent去采集最新数据并出简报

### 4. 检查新视频
读 `shared/data.json` → `creatorCenter.videos` vs 上次记录：
- 有新增视频 → 标记发后追踪 `tracking`
- 在聊天时通知峰峰"有新视频在追踪了"

### 5. 检查异常数据
读当天采集结果：
- 播放量暴增/暴跌 >50% → 微信推异常
- 完播率波动 >5% → 记录
- 粉丝变化 >5 → 记录

## 安静模式规则
- 23:00-08:00：只检查events.json，不做浏览器采集
- 数据正常：不主动推，写到memory等峰峰回来聊天时告知
- 数据异常：微信推一句话
