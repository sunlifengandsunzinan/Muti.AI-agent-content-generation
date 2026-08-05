---
name: "douyin-git-commit-rules"
description: "抖音项目git提交规范：大文件(素材/工具)禁入仓库、push被拒的排查、历史清理安全顺序防止误删未跟踪文件"
---

# douyin-git-commit-rules

抖音内容运营项目（仓库：sunlifengandsunzinan/Muti.AI-agent-content-generation.git）的 git 提交规范。
**核心目的：防止再次踩「大文件混入 git → GitHub push 被拒 → 清理时误删未跟踪文件」这一整条坑。**

---

## 一、铁律：哪些文件绝对不进 git

以下内容**必须**在 .gitignore 里，若已 track 要立刻排除：

| 类别 | 路径 | 原因 |
|------|------|------|
| 大体积素材 | `shared/video-library/` | 视频素材 B_001 曾 170MB，超 GitHub 100MB 上限 |
| 剪辑工具 | `shared/capcut-mate/` | 含 ffprobe(75MB)/sticker.json(58MB)/zip |
| 图片 | `*.png *.jpg *.jpeg *.gif` | 已有规则 |
| 私有文档 | `TOOLS.md MEMORY.md SOUL.md USER.md` | 敏感 |

**判断标准：** 任何 >20MB 的文件，或者运行时素材/依赖/工具，默认不进 git。
**提交前自查：** `git ls-files | ForEach-Object { $s = git cat-file -s "HEAD:$_" 2>$null; if($s -and [long]$s -gt 10MB){"$_  $([math]::Round([long]$s/1MB,1))MB"} }`

---

## 二、push 被拒 `GH001: Large files detected` 的排查

**现象：**
```
remote: error: File shared/video-library/B_001/clip.mp4 is 170.50 MB; this exceeds GitHub's file size limit
remote: error: GH001: Large files detected.
! [remote rejected] master -> master (pre-receive hook declined)
```

**原因：** 仓库**历史**里（不止工作区）有 >100MB 的 blob。只要在历史里，所有 push 都被拒。
即使当前工作区删了也没用，必须从历史清掉。

**排查步骤：**
```powershell
cd C:\Users\Administrator\.openclaw\workspace
# 1. 找出所有被track的大文件
git ls-files | ForEach-Object { $p=$_; $s = git cat-file -s "HEAD:$p" 2>$null; if($s -and [long]$s -gt 10MB){ "$p  $([math]::Round([long]$s/1MB,1))MB" } }
# 2. 找这些文件进了哪些commit
git log --oneline --all -- "shared/video-library/B_001/clip.mp4"
```

---

## 三、历史清理安全流程（血的教训，顺序绝不能错！）

> ⚠️ **2026-08-05 案例：** 我在 filter-branch 前用 `git stash push --include-untracked` 暂存工作区，
> 结果 **filter-branch 重写了 refs/stash，pop 不能完整还原未跟踪文件**；
> 更致命的是我在 pop 之前先跑了 `git gc --prune=now`，把 stash 里未跟踪的 blob 当垃圾清了，
> 导致 video-index.json、封面方案、diagnosis/plans/reports/TODO、material-24 素材源文档全部丢失且无法从 git 恢复。

### 安全做法（两选一）

**方案A（推荐，最简单）：不动工作区，直接 filter-branch**
filter-branch 只改 git 历史，不需要先 stash 工作区。会报 "You have unstaged changes" 的错误——**不要用 stash 解决**，改用下面方法：
```powershell
# 1. 只提交/忽略当前改动，保证 index 干净（不要 --include-untracked stash！）
git add -A
git commit -m "wip: 临时提交以清理历史"   # 或把改动先正常提交

# 2. 执行历史清理
$env:FILTER_BRANCH_SQUELCH_WARNING=1
git filter-branch --force --index-filter "git rm --cached --ignore-unmatch -r shared/video-library shared/capcut-mate shared/capcut-mate-main.zip" --prune-empty -- --all

# 3. 清理 backup refs + 过期对象（⚠️ 确认工作区已无未跟踪重要文件后再 gc）
git for-each-ref --format="%(refname)" refs/original/ | ForEach-Object { git update-ref -d $_ }
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 4. force push（历史重写必须 -f）
git push -f origin master
```

**方案B：如果必须保留未跟踪文件，先备份到 .gitignore 之外的安全目录**
```powershell
# 把重要未跟踪文件先拷出工作区（不是 stash！）
New-Item -ItemType Directory -Force C:\backup_pre_rewrite
Copy-Item shared\video-index.json C:\backup_pre_rewrite\ 2>$null
Copy-Item "shared\covers\douyin-马拉松类比-过客-20260804.md" C:\backup_pre_rewrite\ 2>$null
# ... 所有不想丢的未跟踪文件都拷走
# 再做方案A的 filter-branch 流程
```

### ⚠️ 绝对禁止
1. **不要**用 `git stash push --include-untracked` 处理 filter-branch 的 unstaged 提示（会重写 stash 且 pop 丢未跟踪文件）
2. **不要**在 stash pop 之前跑 `git gc --prune=now`（会把 stash 里未跟踪的 blob 当垃圾清掉）
3. **不要**在重写历史前不确认工作区未跟踪文件是否安全

---

## 四、历史清理后验证

```powershell
# 确认历史无大文件
git ls-tree -r HEAD --name-only | Select-String "clip.mp4|video-library|capcut-mate"
# 确认 pack 变小（应 <2MB）
git count-objects -vH   # size-pack 应很小
# 确认远程同步
git status -sb          # 应显示 ahead/behind 无
git rev-parse HEAD      # 与 git ls-remote origin master 一致
```

---

## 五、子Agent（情报站等）写入文件的保护

情报站等子Agent 会写 `shared/video-index.json`、`shared/publish-log.json`、`shared/data.json`。
**这些是子Agent 正在用的活数据，不要擅自 stash/移动/gc。**
- 做任何 git 破坏性操作（filter-branch / gc / stash include-untracked）前，先确认没有正在运行的子Agent 写这些文件
- 子Agent 写入的未跟踪文件，要么用方案B先拷到安全目录，要么等子Agent 跑完再操作
