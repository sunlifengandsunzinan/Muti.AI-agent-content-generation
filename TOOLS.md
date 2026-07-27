# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## 抖音双机分工

### 🖥️ Windows（本机 - openclaw gateway）
- **身份：** 外网工具/数据采集机
- **操作内容：** 对标账号采集、爆款分析、数据爬取、浏览器搜同赛道博主、查看他人内容
- **限制：** 绝对不要登录峰峰的抖音账号，不要操作任何与峰峰账号发布/编辑相关的事
- **浏览器：** target="host"

### 🍎 Mac（node: sunlifeng-Mac）
- **身份：** 峰峰专属操作机
- **节点ID：** sunlifeng-Mac (192.168.0.121)
- **操作内容：** 峰峰自己的抖音账号（40了，得干点儿啥了）
  - 账号登录、发布视频、编辑作品、查看创作者中心数据（完播率/2秒播放率）、回复评论、改简介、设置权限
  - 查看/管理抖音创作者中心（creator.douyin.com）
- **访问方式：** 通过 `browser` 工具时指定 `target="node"` + `node="sunlifeng-Mac"`
- **CLI命令：** 通过 `exec` 工具时指定 `host="node"` + `node="sunlifeng-Mac"`

### ⚠️ 硬规则
1. **Windows上绝对不做**任何峰峰账号的操作（登录/发布/编辑/看私信）
2. **Mac上绝对不做**任何对标采集/爬取他人数据/搜索同行爆款（这些会污染账号的推荐和cookie）
3. 如果拿不准某个操作应该在哪个机器上执行 → 先问峰峰
4. 涉及
