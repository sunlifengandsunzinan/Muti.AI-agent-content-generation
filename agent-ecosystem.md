# Agent 协作关系

```
用户/峰峰
  └─ 主 Agent (main) — 统一调度
       ├─ weapp-dev Agent    → 微信小程序开发（Mac SSH + DevTools CLI）
       ├─ crawler Agent      → 数据采集（MediaCrawler 抖音/58moto）
       └─ analysis Agent     → 数据分析（Ollama qwen2.5:7b）
```

## 数据流
1. **crawler** → 采集原始数据 → `D:\MediaCrawlerResult\`
2. **analysis** → 分析原始数据 → `D:\摩旅数据采集目录\`（结构化 JSON）
3. **weapp-dev** → 整合到 Flask 后端 → route_templates.json + 小程序页面
4. **主 agent** → 协调流程 + 通知用户

## 当前项目：摩旅微信小程序
- 小程序 AppID: wxd154f9fe121f3619
- Flask 后端：Windows `192.168.0.112:5000`
- 小程序开发：Mac (sunlifeng, 192.168.0.121)
- 项目路径（Mac）：`~/Documents/moto/`
