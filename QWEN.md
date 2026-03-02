# Personal AI Employee Project

## Project Overview

This is a **Personal AI Employee (Digital FTE)** project - an autonomous AI agent system that manages personal and business affairs 24/7. The architecture is local-first, agent-driven, and uses human-in-the-loop patterns for sensitive actions.

### Core Architecture

| Layer | Component | Purpose |
|-------|-----------|---------|
| **Brain** | Qwen Code | Reasoning engine for decision-making |
| **Memory/GUI** | Obsidian (Markdown vault) | Dashboard, knowledge base, state storage |
| **Senses** | Python Watcher scripts | Monitor Gmail, WhatsApp, filesystems |
| **Hands** | MCP Servers | External actions (email, browser, payments) |

### Key Concepts

- **Watchers**: Lightweight Python scripts that run continuously, monitoring inputs and creating actionable `.md` files in `/Needs_Action`
- **Persistence Loop**: A pattern that keeps Qwen Code iterating until tasks are complete
- **Human-in-the-Loop (HITL)**: Sensitive actions require approval via file movement (`/Pending_Approval` → `/Approved`)
- **Monday Morning CEO Briefing**: Autonomous weekly audit generating revenue/bottleneck reports

## Directory Structure

```
ai-empolyee/
├── QWEN.md                    # This context file
├── skills-lock.json           # Skill dependencies (Playwright browsing)
├── Personal AI Employee Hackathon 0_*.md  # Full architectural blueprint
├── .qwen/skills/              # Installed skills
│   └── browsing-with-playwright/
└── [Vault folders - to be created]
    ├── Inbox/
    ├── Needs_Action/
    ├── Pending_Approval/
    ├── Done/
    └── Dashboard.md
```

## Building & Running

### Prerequisites

| Component | Version | Purpose |
|-----------|---------|---------|
| Qwen Code | Active | Primary reasoning engine |
| Python | 3.13+ | Watcher scripts |
| Node.js | v24+ LTS | MCP servers |
| Obsidian | v1.10.6+ | Dashboard/GUI |

### Setup Commands

```bash
# 1. Create Obsidian vault structure
mkdir -p Inbox Needs_Action Pending_Approval Done Plans Updates

# 2. Initialize Python environment for watchers
uv init && uv add playwright watchdog google-api-python-client

# 3. Install Playwright browsers
playwright install

# 4. Verify Qwen Code is working
```

### Running Components

**Watcher Scripts** (run in background):
```bash
python scripts/gmail_watcher.py &
python scripts/whatsapp_watcher.py &
python scripts/filesystem_watcher.py &
```

**Qwen Code with Persistence Loop**:
```bash
# Start autonomous processing
# Process all files in /Needs_Action, move to /Done when complete
```

**Scheduled Tasks** (cron/Task Scheduler):
```bash
# Daily 8 AM briefing
0 8 * * * "Generate Monday Morning CEO Briefing from Business_Goals.md and Transactions"
```

## Development Conventions

### File Naming Patterns

- `WATCHER_<type>_<id>.md` - Files created by watchers
- `PLAN_<task>_<date>.md` - Task plans with checkboxes
- `APPROVAL_<action>_<entity>.md` - Human-in-the-loop requests
- `<date>_<Day>_Briefing.md` - Generated CEO briefings

### Markdown Schema

All action files use YAML frontmatter:
```yaml
---
type: email/whatsapp/payment/file_drop
from: sender
priority: high/medium/low
status: pending/in_progress/done
created: ISO8601_timestamp
---
```

### Agent Skills

All AI functionality should be implemented as modular skills. Use the `browsing-with-playwright` skill for web automation tasks.

### Security Rules

- **Secrets never sync**: `.env`, tokens, WhatsApp sessions stay local
- **Single-writer rule**: Only one agent writes to `Dashboard.md`
- **Claim-by-move**: First agent to move item to `/In_Progress/<agent>/` owns it

## Tiered Achievement Levels

| Tier | Time | Deliverables |
|------|------|--------------|
| **Bronze** | 8-12h | Vault setup, 1 watcher, basic Qwen Code integration |
| **Silver** | 20-30h | Multiple watchers, MCP server, HITL workflow |
| **Gold** | 40+h | Full integration, Odoo accounting, weekly audits |
| **Platinum** | 60+h | Cloud deployment, dual-agent (Cloud/Local), A2A upgrade |

## Key Resources

- **Main Documentation**: `Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md`
- **Playwright References**: `.qwen/skills/browsing-with-playwright/references/`
- **MCP Servers**: https://github.com/AlanOgic/mcp-odoo-adv (Odoo integration)

## Weekly Research Meetings

- **When**: Wednesdays 10:00 PM PKT
- **Zoom**: https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1
- **YouTube**: https://www.youtube.com/@panaversity
