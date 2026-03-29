"""
Orchestrator Module

Master process that monitors the Needs_Action folder and triggers
Qwen Code to process pending items.

The orchestrator:
1. Watches /Needs_Action for new files
2. Triggers Qwen Code to analyze and create plans
3. Monitors /Approved for human-approved actions
4. Updates the Dashboard with current status
"""

import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict
import logging
import json
import time


class Orchestrator:
    """
    Main orchestrator for the AI Employee system.

    Coordinates between watchers, Qwen Code, and human approval.
    """

    def __init__(self, vault_path: str, qwen_path: str = 'qwen'):
        """
        Initialize the orchestrator.

        Args:
            vault_path: Path to the Obsidian vault root directory
            qwen_path: Command to run Qwen Code (default: 'qwen')
        """
        self.vault_path = Path(vault_path)
        self.qwen_path = qwen_path
        
        # Setup directories
        self.needs_action = self.vault_path / 'Needs_Action'
        self.plans = self.vault_path / 'Plans'
        self.done = self.vault_path / 'Done'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.rejected = self.vault_path / 'Rejected'
        self.logs = self.vault_path / 'Logs'
        self.dashboard = self.vault_path / 'Dashboard.md'
        
        # Ensure directories exist
        for directory in [self.needs_action, self.plans, self.done, 
                          self.pending_approval, self.approved, self.rejected, self.logs]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        log_file = self.logs / f'orchestrator_{datetime.now().strftime("%Y-%m-%d")}.log'
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('Orchestrator')
        
        # Track processed files
        self.processed_files: set = set()
    
    def count_files(self, directory: Path) -> int:
        """Count .md files in a directory."""
        try:
            return len([f for f in directory.iterdir() if f.suffix == '.md'])
        except Exception:
            return 0
    
    def get_pending_items(self) -> List[Path]:
        """
        Get list of pending action files.
        
        Returns:
            List of .md files in Needs_Action folder
        """
        try:
            files = [f for f in self.needs_action.iterdir() 
                    if f.suffix == '.md' and f not in self.processed_files]
            return sorted(files, key=lambda f: f.stat().st_mtime)
        except Exception as e:
            self.logger.error(f'Error scanning Needs_Action: {e}')
            return []
    
    def get_approval_items(self) -> List[Path]:
        """
        Get list of items pending approval.
        
        Returns:
            List of .md files in Pending_Approval folder
        """
        try:
            return [f for f in self.pending_approval.iterdir() if f.suffix == '.md']
        except Exception as e:
            self.logger.error(f'Error scanning Pending_Approval: {e}')
            return []
    
    def get_approved_items(self) -> List[Path]:
        """
        Get list of approved items ready for execution.
        
        Returns:
            List of .md files in Approved folder
        """
        try:
            return [f for f in self.approved.iterdir() if f.suffix == '.md']
        except Exception as e:
            self.logger.error(f'Error scanning Approved: {e}')
            return []
    
    def update_dashboard(self):
        """Update the Dashboard.md with current status."""
        try:
            pending_count = self.count_files(self.needs_action)
            approval_count = self.count_files(self.pending_approval)
            done_today = 0
            
            # Count items completed today
            today = datetime.now().strftime('%Y-%m-%d')
            try:
                for f in self.done.iterdir():
                    if f.suffix == '.md' and today in f.name:
                        done_today += 1
            except Exception:
                pass
            
            # Get recent activity
            recent_activity = []
            try:
                for f in sorted(self.done.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
                    recent_activity.append({
                        'date': f.stat().st_mtime,
                        'name': f.stem,
                        'status': 'completed'
                    })
            except Exception:
                pass
            
            # Build dashboard content
            content = f'''---
last_updated: {datetime.now().isoformat()}
status: active
---

# 📊 AI Employee Dashboard

## Quick Status

| Metric | Value |
|--------|-------|
| **Pending Items** | {pending_count} |
| **In Progress** | 0 |
| **Awaiting Approval** | {approval_count} |
| **Completed Today** | {done_today} |

---

## 📥 Needs Action

'''
            
            # List pending items
            pending_items = self.get_pending_items()
            if pending_items:
                for item in pending_items:
                    content += f"- [ ] `{item.name}`\n"
            else:
                content += "*No pending items*\n"
            
            content += '''
---

## 🔄 In Progress

*No active tasks*

---

## ⏳ Pending Approval

'''
            
            # List approval items
            approval_items = self.get_approval_items()
            if approval_items:
                for item in approval_items:
                    content += f"- [ ] `{item.name}`\n"
            else:
                content += "*No items awaiting approval*\n"
            
            content += '''
---

## ✅ Recent Activity

'''
            
            if recent_activity:
                content += "| Date | Action | Status |\n"
                content += "|------|--------|--------|\n"
                for activity in recent_activity:
                    date_str = datetime.fromtimestamp(activity['date']).strftime('%Y-%m-%d %H:%M')
                    content += f"| {date_str} | {activity['name']} | {activity['status']} |\n"
            else:
                content += "| Date | Action | Status |\n"
                content += "|------|--------|--------|\n"
                content += "| - | - | - |\n"
            
            content += '''
---

## 📈 Business Metrics

### Revenue This Month
- **Target:** $0
- **Actual:** $0
- **Progress:** 0%

### Key Accounts
| Account | Status | Last Contact |
|---------|--------|--------------|
| - | - | - |

---

## 🔔 Alerts

*No active alerts*

---

## 📝 Quick Notes

---

*Last generated by AI Employee v0.1 (Bronze Tier)*
'''
            
            # Write dashboard
            self.dashboard.write_text(content, encoding='utf-8')
            self.logger.info('Dashboard updated')
            
        except Exception as e:
            self.logger.error(f'Error updating dashboard: {e}', exc_info=True)
    
    def trigger_qwen(self, prompt: str) -> bool:
        """
        Trigger Qwen Code to process items.

        Args:
            prompt: The prompt to give Qwen

        Returns:
            True if Qwen was triggered successfully
        """
        try:
            self.logger.info(f'Triggering Qwen Code with prompt: {prompt[:100]}...')

            # Build the command
            cmd = [
                self.qwen_path,
                '--cwd', str(self.vault_path),
                prompt
            ]

            # Run Qwen (non-interactive mode)
            # For Bronze tier, we just log that Qwen should be triggered
            # In practice, user would run Qwen interactively
            self.logger.info(f'Would run: {" ".join(cmd)}')
            self.logger.info('Note: For Bronze tier, run Qwen Code manually with the vault path')

            return True

        except Exception as e:
            self.logger.error(f'Error triggering Qwen: {e}')
            return False
    
    def process_pending_items(self):
        """Process all pending items in Needs_Action."""
        pending = self.get_pending_items()

        if not pending:
            self.logger.debug('No pending items to process')
            return

        self.logger.info(f'Found {len(pending)} pending item(s)')

        # Create a summary prompt for Qwen
        items_summary = '\n'.join([f"- {item.name}" for item in pending])

        prompt = f'''I have {len(pending)} new item(s) in /Needs_Action:

{items_summary}

Please:
1. Read each item carefully
2. Create a Plan.md file for each item with specific action steps
3. If any action requires my approval, create a file in /Pending_Approval
4. Update the Dashboard with the current status
5. When complete, move processed items to /Done

Refer to Company_Handbook.md for rules of engagement.'''

        self.trigger_qwen(prompt)
    
    def log_action(self, action_type: str, details: dict):
        """
        Log an action to the audit log.
        
        Args:
            action_type: Type of action (e.g., 'file_processed', 'approval_requested')
            details: Dictionary of action details
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action_type': action_type,
            'actor': 'orchestrator',
            **details
        }
        
        log_file = self.logs / f'{datetime.now().strftime("%Y-%m-%d")}.json'
        
        try:
            # Append to daily log
            if log_file.exists():
                with open(log_file, 'r') as f:
                    logs = json.load(f)
            else:
                logs = []
            
            logs.append(log_entry)
            
            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=2)
                
            self.logger.debug(f'Logged action: {action_type}')
        except Exception as e:
            self.logger.error(f'Error logging action: {e}')
    
    def move_to_done(self, source: Path):
        """
        Move a file to the Done folder.
        
        Args:
            source: Path to the file to move
        """
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            dest = self.done / f'{today}_{source.name}'
            shutil.move(str(source), str(dest))
            self.logger.info(f'Moved to Done: {source.name}')
            self.log_action('file_completed', {'file': source.name})
        except Exception as e:
            self.logger.error(f'Error moving file to Done: {e}')
    
    def run_cycle(self):
        """Run one complete orchestration cycle."""
        self.logger.info('Starting orchestration cycle')
        
        # Update dashboard
        self.update_dashboard()
        
        # Process pending items
        self.process_pending_items()
        
        # Check for approved items (for future tiers)
        approved = self.get_approved_items()
        if approved:
            self.logger.info(f'Found {len(approved)} approved item(s) ready for execution')
            # For Bronze tier, just log - actual execution in Silver/Gold
        
        self.logger.info('Orchestration cycle complete')
    
    def run(self, interval: int = 60):
        """
        Run the orchestrator in a continuous loop.
        
        Args:
            interval: Time between cycles in seconds
        """
        self.logger.info(f'Starting Orchestrator (interval: {interval}s)')
        self.logger.info(f'Vault path: {self.vault_path}')
        
        try:
            while True:
                self.run_cycle()
                time.sleep(interval)
        except KeyboardInterrupt:
            self.logger.info('Orchestrator stopped by user')
        except Exception as e:
            self.logger.error(f'Fatal error: {e}', exc_info=True)
            raise


def main():
    """Entry point for running the orchestrator."""
    import sys

    # Default vault path
    vault_path = Path(__file__).parent.parent / 'AI_Employee_Vault'
    
    # Default settings
    interval = 60
    run_once = False

    # Parse command line arguments
    args = sys.argv[1:]
    
    for i, arg in enumerate(args):
        if arg == '--once':
            run_once = True
        elif arg.isdigit():
            interval = int(arg)
        elif not arg.startswith('--'):
            # It's a path
            vault_path = Path(arg)

    if not vault_path.exists():
        print(f'Error: Vault path does not exist: {vault_path}')
        print('Usage: python orchestrator.py [vault_path] [--once] [interval_seconds]')
        sys.exit(1)

    orchestrator = Orchestrator(str(vault_path))

    # Run single cycle or continuous?
    if run_once:
        orchestrator.run_cycle()
    else:
        orchestrator.run(interval)


if __name__ == '__main__':
    main()
