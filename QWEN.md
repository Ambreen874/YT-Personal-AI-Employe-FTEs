# Personal AI Employee (Digital FTE) Project

## Project Overview

This is a **hackathon project** for building a "Personal AI Employee" or "Digital FTE" (Full-Time Equivalent) - an autonomous AI agent that manages personal and business affairs 24/7. The project uses **Claude Code** as the reasoning engine and **Obsidian** (local Markdown) as the knowledge base/dashboard.

**Tagline:** *Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.*

### Core Architecture

The architecture follows a **Perception → Reasoning → Action** pattern:

| Layer | Component | Purpose |
|-------|-----------|---------|
| **Perception (Watchers)** | Python Sentinel Scripts | Monitor Gmail, WhatsApp, filesystems to trigger AI |
| **Reasoning (Brain)** | Claude Code | Reads tasks, creates plans, makes decisions |
| **Action (Hands)** | MCP Servers | Execute external actions (email, browser, payments) |
| **Memory/GUI** | Obsidian Vault | Dashboard, long-term memory, human interface |

### Key Concepts

- **Watchers:** Lightweight Python scripts that run continuously, monitoring inputs and creating actionable `.md` files in `/Needs_Action` folder
- **Ralph Wiggum Loop:** A Stop hook pattern that keeps Claude iterating until multi-step tasks are complete
- **Human-in-the-Loop:** Sensitive actions require approval via file movement (`/Pending_Approval` → `/Approved`)
- **MCP (Model Context Protocol):** Servers that expose capabilities for Claude to interact with external systems

## Directory Structure

```
YT-Personal-AI-Employe-FTEs/
├── .qwen/skills/           # Qwen Agent Skills
│   └── browsing-with-playwright/
├── .gitattributes          # Git text file normalization
├── skills-lock.json        # Skill dependencies lock file
├── QWEN.md                 # This file - project context
└── Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md
                            # Main hackathon documentation
```

### Expected Obsidian Vault Structure (to be created)

```
Vault/
├── Dashboard.md            # Real-time summary
├── Company_Handbook.md     # Rules of engagement
├── Business_Goals.md       # Q1/Q2 objectives
├── Plans/                  # Task plans
├── Needs_Action/           # Pending items from watchers
├── In_Progress/            # Currently being processed
├── Pending_Approval/       # Awaiting human approval
├── Approved/               # Approved actions
├── Done/                   # Completed tasks
├── Accounting/             # Bank transactions
└── Briefings/              # CEO briefing reports
```

## Technologies & Dependencies

| Component | Technology | Purpose |
|-----------|------------|---------|
| **AI Engine** | Claude Code | Primary reasoning engine |
| **Dashboard** | Obsidian v1.10.6+ | Knowledge base & GUI |
| **Automation** | Python 3.13+ | Watcher scripts, orchestration |
| **MCP Servers** | Node.js v24+ LTS | External system integration |
| **Browser Automation** | Playwright MCP | Web interaction |
| **Version Control** | GitHub Desktop | Vault synchronization |

## Building and Running

### Prerequisites Setup

1. **Install required software:**
   - Claude Code (Pro subscription or use Free Gemini API with Claude Code Router)
   - Obsidian v1.10.6+
   - Python 3.13+
   - Node.js v24+ LTS
   - GitHub Desktop

2. **Create Obsidian vault:**
   ```bash
   mkdir AI_Employee_Vault
   cd AI_Employee_Vault
   # Create folder structure
   mkdir Inbox Needs_Action Done Plans Pending_Approval Approved Accounting Briefings
   ```

3. **Verify Claude Code:**
   ```bash
   claude --version
   ```

### Running Watcher Scripts

**Gmail Watcher** (monitors for new emails):
```bash
python gmail_watcher.py
```

**WhatsApp Watcher** (monitors WhatsApp Web):
```bash
python whatsapp_watcher.py
```

**Filesystem Watcher** (monitors drop folder):
```bash
python filesystem_watcher.py
```

### Running Playwright MCP Server

**Start Server:**
```bash
# Using helper script (recommended)
bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh

# Or manually
npx @playwright/mcp@latest --port 8808 --shared-browser-context &
```

**Stop Server:**
```bash
# Using helper script (closes browser first)
bash .qwen/skills/browsing-with-playwright/scripts/stop-server.sh
```

**Verify Server:**
```bash
python .qwen/skills/browsing-with-playwright/scripts/verify.py
```

### Starting Claude Code with Ralph Wiggum Loop

```bash
# Start a Ralph loop for autonomous task completion
/ralph-loop "Process all files in /Needs_Action, move to /Done when complete" \
  --completion-promise "TASK_COMPLETE" \
  --max-iterations 10
```

### Scheduled Operations

**Daily Briefing (8:00 AM):**
```bash
# cron (Mac/Linux) or Task Scheduler (Windows)
claude "Check /Needs_Action and /Accounting, generate Monday Morning CEO Briefing"
```

## Development Conventions

### Coding Style

- **Python Watchers:** Follow the `BaseWatcher` abstract class pattern
- **Markdown Files:** Use YAML frontmatter for metadata
- **File Naming:** `TYPE_Description_YYYY-MM-DD.md` for action files

### Watcher Pattern Template

```python
from base_watcher import BaseWatcher
from pathlib import Path
from abc import abstractmethod

class CustomWatcher(BaseWatcher):
    def check_for_updates(self) -> list:
        '''Return list of new items to process'''
        pass

    def create_action_file(self, item) -> Path:
        '''Create .md file in Needs_Action folder'''
        pass
```

### Action File Schema

```markdown
---
type: email|whatsapp|file_drop|approval_request|subscription
from: Sender Name
subject: Subject Line
received: 2026-01-07T10:30:00Z
priority: high|medium|low
status: pending|in_progress|done
---

## Content/Description

## Suggested Actions
- [ ] Action item 1
- [ ] Action item 2
```

### Human-in-the-Loop Pattern

For sensitive actions (payments, sending emails):

1. Claude creates approval request file in `/Pending_Approval`
2. User reviews and moves file to `/Approved`
3. Orchestrator triggers MCP action
4. Result logged in `/Done`

### MCP Server Configuration

Configure in `~/.config/claude-code/mcp.json`:

```json
{
  "servers": [
    {
      "name": "email",
      "command": "node",
      "args": ["/path/to/email-mcp/index.js"],
      "env": {
        "GMAIL_CREDENTIALS": "/path/to/credentials.json"
      }
    },
    {
      "name": "browser",
      "command": "npx",
      "args": ["@anthropic/browser-mcp"],
      "env": {
        "HEADLESS": "true"
      }
    }
  ]
}
```

## Available Agent Skills

### browsing-with-playwright

Browser automation using Playwright MCP server. Use for:
- Web browsing and navigation
- Form submission
- Web scraping/data extraction
- UI testing
- Taking screenshots

**Key Tools:**
- `browser_navigate` - Navigate to URL
- `browser_snapshot` - Capture accessibility snapshot
- `browser_click` - Click element
- `browser_type` - Type text into fields
- `browser_fill_form` - Fill multiple form fields
- `browser_take_screenshot` - Capture screenshot
- `browser_run_code` - Execute Playwright code

**Usage Example:**
```bash
# Navigate and interact
python scripts/mcp-client.py call -u http://localhost:8808 \
  -t browser_navigate -p '{"url": "https://example.com"}'

# Get snapshot to find elements
python scripts/mcp-client.py call -u http://localhost:8808 \
  -t browser_snapshot -p '{}'

# Click element using ref from snapshot
python scripts/mcp-client.py call -u http://localhost:8808 \
  -t browser_click -p '{"element": "Submit button", "ref": "e42"}'
```

## Hackathon Tiers

| Tier | Requirements | Estimated Time |
|------|--------------|----------------|
| **Bronze** | Obsidian dashboard, one watcher, Claude reading/writing | 8-12 hours |
| **Silver** | Multiple watchers, MCP server, approval workflow, scheduling | 20-30 hours |
| **Gold** | Full integration, Odoo accounting, social media, Ralph Wiggum loop | 40+ hours |
| **Platinum** | 24/7 cloud deployment, Cloud/Local split, A2A upgrade | 60+ hours |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Playwright server not responding | Run `bash scripts/stop-server.sh && bash scripts/start-server.sh` |
| Element not found | Run `browser_snapshot` first to get current refs |
| Claude exits prematurely | Use Ralph Wiggum Stop hook pattern |
| Watcher not detecting items | Check credentials/API permissions |
| MCP action fails | Check server configuration and environment variables |

## Resources

- **Main Documentation:** `Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md`
- **Playwright Tools Reference:** `.qwen/skills/browsing-with-playwright/references/playwright-tools.md`
- **Ralph Wiggum Pattern:** https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum
- **MCP Servers:** https://github.com/modelcontextprotocol/servers

## Meeting Schedule

**Research and Showcase Meeting:** Every Wednesday at 10:00 PM on Zoom

- **Zoom:** https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1
- **Meeting ID:** 871 8870 7642
- **Passcode:** 744832
- **YouTube Archive:** https://www.youtube.com/@panaversity
