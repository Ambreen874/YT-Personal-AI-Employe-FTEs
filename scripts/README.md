# AI Employee Scripts

Python scripts for the Personal AI Employee (Bronze Tier).

## Installation

1. **Install Python dependencies:**

```bash
pip install -r requirements.txt
```

2. **Verify installation:**

```bash
python -c "import watchdog; print('watchdog installed:', watchdog.__version__)"
```

## Scripts Overview

### `base_watcher.py`

Abstract base class for all watchers. Provides:
- Logging setup
- Directory management
- File sanitization utilities
- Standard run loop

### `filesystem_watcher.py`

Monitors the `/Inbox` folder for new files. When a file is dropped:
1. Copies it to `/Needs_Action`
2. Creates a metadata `.md` file with file information
3. Tracks processed files to avoid duplicates

**Usage:**
```bash
python filesystem_watcher.py [vault_path]
```

### `orchestrator.py`

Master process that:
1. Monitors `/Needs_Action` for pending items
2. Triggers Claude Code to process items
3. Updates the Dashboard.md
4. Logs all actions

**Usage:**
```bash
# Continuous mode (default, checks every 60 seconds)
python orchestrator.py [vault_path]

# With custom interval (check every 30 seconds)
python orchestrator.py [vault_path] 30

# Single cycle (run once and exit)
python orchestrator.py [vault_path] --once
```

## Quick Start

1. **Start the File System Watcher:**
```bash
cd scripts
python filesystem_watcher.py ../AI_Employee_Vault
```

2. **Start the Orchestrator (in another terminal):**
```bash
cd scripts
python orchestrator.py ../AI_Employee_Vault
```

3. **Test the workflow:**
   - Drop any file into `AI_Employee_Vault/Inbox/`
   - Watcher creates metadata file in `Needs_Action/`
   - Orchestrator detects the new file and triggers Claude

## Running with Claude Code

For Bronze Tier, manually trigger Claude Code:

```bash
cd AI_Employee_Vault
claude "Check /Needs_Action for new items. Read Company_Handbook.md for rules. Create plans and process items."
```

## Logging

All scripts create logs in `AI_Employee_Vault/Logs/`:
- `watcher_FileSystemWatcher_YYYY-MM-DD.log`
- `orchestrator_YYYY-MM-DD.log`

## Troubleshooting

**Watcher not detecting files:**
- Check that the Inbox folder exists
- Verify file permissions
- Check the watcher log for errors

**Orchestrator not triggering Claude:**
- Ensure Claude Code is installed: `claude --version`
- Check that vault path is correct
- Review orchestrator log for details

## Next Steps (Silver Tier)

- Add Gmail watcher with Google API integration
- Add WhatsApp watcher with Playwright
- Implement MCP server for email sending
- Add human-in-the-loop approval workflow
