# Quick Start Guide - AI Employee with Qwen Code

## ✅ Updated for Qwen Code

All references have been changed from Claude to Qwen.

---

## Commands to Run

### Terminal 1: Start File System Watcher
```bash
cd "C:\Users\Dell i7\Desktop\Batch 67\YT-Personal-AI-Employe-FTEs\scripts"
python filesystem_watcher.py ../AI_Employee_Vault
```
**Keep running** - Watches for new files in `/Inbox`

---

### Terminal 2: Start Orchestrator
```bash
cd "C:\Users\Dell i7\Desktop\Batch 67\YT-Personal-AI-Employe-FTEs\scripts"
python orchestrator.py ../AI_Employee_Vault
```
**Keep running** - Checks for pending items every 60 seconds

---

### Terminal 3: Run Qwen Code (when you have items)
```bash
cd "C:\Users\Dell i7\Desktop\Batch 67\YT-Personal-AI-Employe-FTEs\AI_Employee_Vault"
qwen
```
Then paste this prompt:
```
Check /Needs_Action for pending items. Read Company_Handbook.md for rules. 
Create plans and process items. Update Dashboard when done.
```

---

## Test the System

```bash
# 1. Start watcher and orchestrator (2 terminals above)

# 2. Create a test file
echo "Research CRM software options. Budget: $100/month" > "AI_Employee_Vault/Inbox/task.txt"

# 3. Wait for watcher to detect (Terminal 1 should show detection)

# 4. Wait for orchestrator to update (Terminal 2 should show within 60 seconds)

# 5. Run Qwen Code (Terminal 3)
cd AI_Employee_Vault
qwen "Process items in Needs_Action"
```

---

## What Each Component Does

| Component | Command | Purpose |
|-----------|---------|---------|
| **File System Watcher** | `python filesystem_watcher.py` | Detects new files in `/Inbox` |
| **Orchestrator** | `python orchestrator.py` | Scans `/Needs_Action`, updates Dashboard |
| **Qwen Code** | `qwen` | The AI brain that processes items |

---

## Folder Flow

```
/Inbox          → You drop files here
    ↓ (Watcher detects)
/Needs_Action   → Metadata files created here
    ↓ (Orchestrator detects)
Qwen Code       → Processes and creates plans
    ↓
/Plans          → Action plans stored here
    ↓
/Done           → Completed items moved here
```

---

## Troubleshooting

**"System cannot find the path specified"**
- Make sure you're in the `scripts` folder
- Use `../AI_Employee_Vault` (relative path)

**"qwen: command not found"**
- Verify Qwen Code is installed: `qwen --version`
- Install if needed

**Watcher not detecting files**
- Check if `watchdog` is installed: `pip show watchdog`
- Install: `pip install watchdog`

**Orchestrator shows 0 items**
- Check if files exist in `Needs_Action` folder
- Review logs in `AI_Employee_Vault/Logs/`

---

## Useful Commands

```bash
# Run orchestrator once (test mode)
python orchestrator.py ../AI_Employee_Vault --once

# View logs
type ..\AI_Employee_Vault\Logs\orchestrator_*.log
type ..\AI_Employee_Vault\Logs\watcher_*.log

# Check what's in Needs_Action
dir ..\AI_Employee_Vault\Needs_Action
```

---

*Updated for Qwen Code - Bronze Tier*
