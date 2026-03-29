# Personal AI Employee - Bronze Tier

A local-first, autonomous AI assistant built with Qwen Code and Obsidian.

## Overview

This is the **Bronze Tier** implementation of the Personal AI Employee Hackathon. It provides the foundational layer for an AI agent that manages personal and business affairs 24/7.

### What's Included

✅ **Obsidian Vault** with:
- `Dashboard.md` - Real-time status overview
- `Company_Handbook.md` - Rules of engagement
- `Business_Goals.md` - Objectives and metrics template

✅ **Folder Structure**:
- `/Inbox` - Drop folder for files to process
- `/Needs_Action` - Pending items
- `/Plans` - Action plans created by Claude
- `/Pending_Approval` - Items awaiting human approval
- `/Approved` - Approved actions ready for execution
- `/Done` - Completed items
- `/Logs` - Audit logs and watcher logs

✅ **Python Scripts**:
- `base_watcher.py` - Abstract base class for all watchers
- `filesystem_watcher.py` - Monitors Inbox for new files
- `orchestrator.py` - Coordinates Claude Code processing

## Quick Start

### 1. Install Dependencies

```bash
cd scripts
pip install -r requirements.txt
```

### 2. Start the File System Watcher

```bash
cd scripts
python filesystem_watcher.py ../AI_Employee_Vault
```

Keep this running in the background. It monitors the `/Inbox` folder.

### 3. Start the Orchestrator (in another terminal)

```bash
cd scripts
python orchestrator.py ../AI_Employee_Vault
```

This runs every 60 seconds, checking for items to process.

### 4. Test the Workflow

1. **Drop a file** into `AI_Employee_Vault/Inbox/`
2. **Watcher** creates a metadata file in `Needs_Action/`
3. **Orchestrator** detects the file and prepares a Qwen prompt
4. **Run Qwen Code** manually (Bronze Tier):

```bash
cd AI_Employee_Vault
qwen "Check /Needs_Action for new items. Read Company_Handbook.md for rules. Create plans and process items."
```

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Gmail         │     │   FileSystem     │     │   WhatsApp      │
│   Watcher       │     │   Watcher        │     │   Watcher       │
│   (future)      │     │   (✓ Bronze)     │     │   (future)      │
└────────┬────────┘     └────────┬─────────┘     └────────┬────────┘
         │                       │                        │
         ▼                       ▼                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    /Needs_Action/                               │
│              (Action files created here)                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Orchestrator                                 │
│         (Monitors, triggers Qwen, updates Dashboard)            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Qwen Code                                    │
│         (Reads, thinks, plans, writes, requests approval)       │
└────────────────────────────┬────────────────────────────────────┘
                             │
              ┌──────────────┴───────────────┐
              ▼                              ▼
┌─────────────────────┐          ┌──────────────────────┐
│  Human Approval     │          │  Auto-approved       │
│  (if required)      │          │  (file, categorize)  │
└─────────────────────┘          └──────────────────────┘
```

## Usage Examples

### Example 1: Process a Document

1. Drop `contract.pdf` into `/Inbox`
2. Watcher creates `FILE_contract.pdf.meta.md` in `/Needs_Action`
3. Orchestrator triggers Qwen
4. Qwen reads the document and:
   - Creates a plan in `/Plans`
   - Summarizes key points
   - Suggests actions
   - Moves to `/Done` when complete

### Example 2: Task Request

1. Create a file `task_request.md` in `/Inbox`:
   ```markdown
   ---
   type: task_request
   priority: high
   ---

   Please research CRM options for our business.
   Budget: $50-200/month
   Requirements: Email integration, mobile app
   ```

2. Qwen processes and:
   - Creates comparison table
   - Lists top 3 options
   - Provides recommendation

## Configuration

### Company Handbook

Edit `Company_Handbook.md` to customize:
- Decision-making rules
- Payment thresholds
- Communication guidelines
- Escalation protocols

### Business Goals

Update `Business_Goals.md` with:
- Revenue targets
- Active projects
- Key metrics to track

## Logs

All activity is logged in `/Logs`:
- `watcher_FileSystemWatcher_YYYY-MM-DD.log` - File detection logs
- `orchestrator_YYYY-MM-DD.log` - Processing logs
- `processed_files.txt` - Track already-processed files
- `YYYY-MM-DD.json` - Audit log (JSON format)

## Troubleshooting

**Watcher not detecting files:**
```bash
# Check if watchdog is installed
pip show watchdog

# Verify Inbox folder exists
dir AI_Employee_Vault\Inbox
```

**Orchestrator not working:**
```bash
# Run a single test cycle
python orchestrator.py ../AI_Employee_Vault 60 --once

# Check logs
type ..\AI_Employee_Vault\Logs\orchestrator_*.log
```

**Qwen Code not responding:**
```bash
# Verify Qwen is installed
qwen --version

# Run interactively
cd AI_Employee_Vault
qwen
```

## Next Steps (Silver Tier)

To upgrade to Silver Tier, add:
- [ ] Gmail Watcher with Google API
- [ ] WhatsApp Watcher with Playwright
- [ ] MCP Server for email sending
- [ ] Human-in-the-loop approval execution
- [ ] Scheduled tasks (cron/Task Scheduler)

## Project Structure

```
YT-Personal-AI-Employe-FTEs/
├── AI_Employee_Vault/          # Obsidian vault
│   ├── Dashboard.md
│   ├── Company_Handbook.md
│   ├── Business_Goals.md
│   ├── Inbox/                  # Drop files here
│   ├── Needs_Action/           # Pending items
│   ├── Plans/                  # Action plans
│   ├── Done/                   # Completed
│   └── Logs/                   # Audit logs
├── scripts/
│   ├── base_watcher.py
│   ├── filesystem_watcher.py
│   ├── orchestrator.py
│   ├── requirements.txt
│   └── README.md
├── test_watcher.py
├── test_orchestrator.py
└── README.md                   # This file
```

## Resources

- **Main Hackathon Doc:** `Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md`
- **Qwen Code Docs:** https://code.qwen.ai
- **Obsidian:** https://obsidian.md
- **Watchdog:** https://pypi.org/project/watchdog/

## Meeting Schedule

**Research and Showcase Meeting:** Every Wednesday at 10:00 PM on Zoom

- **Zoom:** https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1
- **Meeting ID:** 871 8870 7642
- **Passcode:** 744832

---

*Built as part of the Personal AI Employee Hackathon 2026*
