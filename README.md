# Multi.AI-agent-content-generation

Multi-Agent collaboration system for short-video content production — human decides, AI executes, data drives creativity.

Five independent AI agents work together through a shared data protocol — no database, no API, just files and conventions.

**How it works:** The human (creator) makes creative decisions — what stories to tell, which scripts to approve, when to publish. The agents handle the rest: collecting raw material, writing scripts, packaging titles and covers, tracking data and trends.

The result is a closed loop: life experiences → structured material → data-informed scripts → competitive titles → performance feedback → better decisions next round.

Not a fully automated pipeline — a human-in-the-loop system that scales creativity without sacrificing authenticity.

---

## Architecture Overview

```
👤 Human Layer
  Creator ──→ decides, provides material, reviews output

🤖 Agent Layer (4+1 independent agents)
  ┌────────────────────────────────────────────────┐
  │  Manager (dispatcher)                          │
  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────┐│
  │  │Material  │ │Script    │ │Title&    │ │Intel││
  │  │Manager   │ │Writer    │ │Cover     │ │ligence│
  │  └──────────┘ └──────────┘ └──────────┘ └────┘│
  └────────────────────────────────────────────────┘

📁 Shared Data Layer (file-based, zero dependency)
  data.json  /  materials/  /  scripts/  /  benchmarking/  /  events.json

🌐 External Layer
  Douyin.com  ←  Chromium  ←  Intelligence Agent scraping
  Ollama qwen2.5:7b ─→  Local analysis for benchmarking
```

> See `docs/architecture.html` for interactive diagram.

---

## Core Design Philosophy

### Human-in-the-loop
The system never creates without human direction. Agents do the heavy lifting — collecting, organizing, drafting, analyzing — but every creative decision (which story to tell, which script to publish, which title to use) is made by the human. This keeps the content authentic and the human in control.

### File-based shared state
Why no database? Because JSON files are Git-friendly, zero-dependency, and trivially debuggable. Every change is tracked in version control. Any AI agent can read and write the shared data layer without HTTP calls, connection pools, or schema migrations.

### Dual material storage
Every story is saved twice: as raw markdown (the human's exact words, preserving tone and detail) and as structured JSON (machine-readable for agent consumption). Structured data loses the "how it was said" — raw archives fill that gap.

### Local model for analysis, cloud model for creativity
Analysis tasks (trend spotting, benchmarking, self-review) run on a local 7B model via Ollama — free, fast, doesn't burn API credits. Creative tasks (script writing, title generation) use the main cloud model, where creativity matters most.

---

## Agents

| Agent | Role | Guide |
|:------|:-----|:------|
| **Manager** | Understands intent, dispatches to the right agent | [`agents/manager.md`](agents/manager.md) |
| **Material Manager** | Receives stories from human, archives raw + structured | [`skills/douyin-素材管家/agents/sucai-guanjia.md`](skills/douyin-素材管家/agents/sucai-guanjia.md) |
| **Script Writer** | Writes scripts based on materials + benchmarking data | [`skills/douyin-脚本生成器/agents/script-writer.md`](skills/douyin-脚本生成器/agents/script-writer.md) |
| **Title & Cover Designer** | Generates 3+ title/cover/tag schemes per script | [`skills/douyin-标题封面官/agents/title-cover.md`](skills/douyin-标题封面官/agents/title-cover.md) |
| **Intelligence** | Scrapes account data, benchmarks competitors, daily check | [`skills/douyin-情报站/agents/qingbaozhan.md`](skills/douyin-情报站/agents/qingbaozhan.md) |

---

## Collaboration Flows

### Material Intake (human triggered)
```
Human: "I have a story..."
  → Material Manager archives raw text
  → Extracts core emotion, key phrase, angles
  → Saves to shared data layer
  → "Material received, ready when you are"
```

### Script Creation (human triggered)
```
Human: "Time to write a script"
  → Script Writer reads:
      ├─ Unused materials from pool
      ├─ Trending titles from benchmarking
      └─ Performance data from past videos
  → Writes script → saves to shared/scripts/
  → Human reviews and approves
```

### Title & Cover Packaging (human triggered)
```
Human: "Create title options"
  → Title & Cover Designer reads script + benchmarking data
  → Outputs 3+ title/cover/tag schemes
  → Human picks one and publishes
```

### Data Intelligence (can run automatically)
```
Intelligence Agent daily check:
  → Scrapes account page (followers, likes, views)
  → Compares with yesterday, records changes
  → Updates shared data
  → Flags significant fluctuations to human
```

---

## Data Protocol

```
shared/
├── data.json              # Master data: account info, rankings, materials, templates, benchmarking
├── events.json            # Event queue for pipeline mode
├── materials/             # Raw material archives (Material Manager)
├── scripts/               # Finished scripts (Script Writer)
└── benchmarking/          # Competitor analysis (Intelligence)

agents/
├── manager.md             # Manager guide
└── ...                    # Other agent guides in their respective skill directories
```

### Read/Write Matrix

| Agent | Read | Write |
|-------|------|-------|
| Manager | events.json, data.json | read-only |
| Material Manager | data.json.materials | data.json.materials, shared/materials/, events.json |
| Script Writer | data.json (all) | shared/scripts/, events.json |
| Title & Cover Designer | shared/scripts/, data.json | data.json (templates), events.json |
| Intelligence | data.json (all) | data.json (rankings/benchmarking), events.json |

---

## Tech Stack

| Component | Description |
|:----------|:------------|
| AI Framework | OpenClaw (main model: deepseek-chat) |
| Agent Protocol | File system + event queue |
| Local Model | Ollama + qwen2.5:7b (analysis tasks) |
| Data Collection | Chromium browser automation |
| Data Storage | JSON files (Git-friendly) |
| Runtime | Windows + remote macOS node (standby) |

---

## Getting Started

If you take over this system:

1. Read this README to understand the full picture
2. Read each agent's guide in `agents/` or `skills/*/agents/`
3. Check `shared/events.json` for pending events
4. Review `shared/data.json` for current account state
5. Say "I'm online" to the human

---

## Roadmap

- [x] Agent boundary definitions and independent guides
- [x] Shared data protocol
- [x] Raw material archiving mechanism
- [x] Daily intelligence check (auto-capable)
- [ ] **Pipeline mode** — Manager auto-polls events.json
- [ ] **Self-review module** — Analyze published video performance
- [ ] **Multi-platform** — Reuse architecture for Xiaohongshu, etc.
- [ ] **Dashboard** — Visual account data trends

---

## Related Resources

- [Architecture Diagram (HTML)](docs/architecture.html)
- [Manager Guide](agents/manager.md)
- [Shared Data README](shared/README.md) (Chinese)

---

*Built for [@sunlifengandsunzinan](https://github.com/sunlifengandsunzinan)*
