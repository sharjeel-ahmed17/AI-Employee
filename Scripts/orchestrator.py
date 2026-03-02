"""
AI Employee Orchestrator

Main orchestration script that coordinates the AI Employee system.
Monitors the vault, processes tasks with Qwen Code, and manages workflows.

This is the "brain stem" that keeps the AI Employee running autonomously.
"""

import os
import sys
import time
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
from dataclasses import dataclass, field

# Add Scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))


@dataclass
class Task:
    """Represents a task to be processed."""
    filepath: Path
    task_type: str = "unknown"
    priority: str = "medium"
    status: str = "pending"
    created_at: str = ""
    metadata: Dict = field(default_factory=dict)


class Orchestrator:
    """
    Main orchestrator for the AI Employee system.
    
    Responsibilities:
    - Monitor Needs_Action folder for new tasks
    - Process tasks with Qwen Code
    - Move completed tasks to Done folder
    - Update Dashboard.md with status
    - Handle human-in-the-loop approvals
    """
    
    def __init__(self, vault_path: str, check_interval: int = 10):
        """
        Initialize the orchestrator.
        
        Args:
            vault_path: Path to the Obsidian vault root directory
            check_interval: Seconds between task checks (default: 10)
        """
        self.vault_path = Path(vault_path)
        self.check_interval = check_interval
        
        # Define folders
        self.inbox = self.vault_path / 'Inbox'
        self.needs_action = self.vault_path / 'Needs_Action'
        self.done = self.vault_path / 'Done'
        self.plans = self.vault_path / 'Plans'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.in_progress = self.vault_path / 'In_Progress'
        self.dashboard = self.vault_path / 'Dashboard.md'
        
        # Ensure all folders exist
        self._ensure_folders()
        
        # Set up logging
        self._setup_logging()
        
        # Track processed files to avoid duplicates
        self.processed_files = set()
        
        # Statistics
        self.stats = {
            'tasks_processed': 0,
            'tasks_completed': 0,
            'tasks_pending_approval': 0,
            'errors': 0,
            'start_time': datetime.now().isoformat()
        }
        
        self.logger.info(f'Orchestrator initialized for vault: {self.vault_path}')
    
    def _ensure_folders(self):
        """Ensure all required folders exist."""
        folders = [
            self.inbox,
            self.needs_action,
            self.done,
            self.plans,
            self.pending_approval,
            self.in_progress
        ]
        for folder in folders:
            folder.mkdir(parents=True, exist_ok=True)
    
    def _setup_logging(self):
        """Set up logging configuration."""
        self.logger = logging.getLogger('Orchestrator')
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
            
            # File handler (logs to vault)
            log_file = self.vault_path / 'orchestrator.log'
            try:
                file_handler = logging.FileHandler(log_file)
                file_handler.setLevel(logging.DEBUG)
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
            except Exception as e:
                self.logger.warning(f'Could not create log file: {e}')
    
    def scan_for_tasks(self) -> List[Task]:
        """
        Scan the Needs_Action folder for new tasks.
        
        Returns:
            List[Task]: List of tasks to process
        """
        tasks = []
        
        if not self.needs_action.exists():
            return tasks
        
        for filepath in self.needs_action.glob('*.md'):
            # Skip already processed files
            if filepath.name in self.processed_files:
                continue
            
            # Skip files in subdirectories (claimed by other agents)
            if filepath.parent != self.needs_action:
                continue
            
            try:
                task = self._parse_task_file(filepath)
                if task:
                    tasks.append(task)
                    self.logger.info(f'Found new task: {filepath.name}')
            except Exception as e:
                self.logger.error(f'Error parsing task file {filepath.name}: {e}')
                self.stats['errors'] += 1
        
        return tasks
    
    def _parse_task_file(self, filepath: Path) -> Optional[Task]:
        """
        Parse a task file and extract metadata.
        
        Args:
            filepath: Path to the task file
            
        Returns:
            Task: Parsed task object or None
        """
        content = filepath.read_text(encoding='utf-8')
        
        # Extract YAML frontmatter
        task = Task(
            filepath=filepath,
            status='pending',
            created_at=datetime.now().isoformat()
        )
        
        # Parse frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 2:
                frontmatter = parts[1].strip()
                for line in frontmatter.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        if key == 'type':
                            task.task_type = value
                        elif key == 'priority':
                            task.priority = value
                        elif key == 'status':
                            task.status = value
                        elif key == 'original_name':
                            task.metadata['original_name'] = value
                        elif key == 'from':
                            task.metadata['from'] = value
                        elif key == 'subject':
                            task.metadata['subject'] = value
        
        return task
    
    def process_task(self, task: Task) -> bool:
        """
        Process a single task with Qwen Code.
        
        Args:
            task: Task to process
            
        Returns:
            bool: True if task was processed successfully
        """
        self.logger.info(f'Processing task: {task.filepath.name}')
        
        # Move to In_Progress to claim ownership
        in_progress_file = self.in_progress / f'orchestrator_{task.filepath.name}'
        try:
            task.filepath.rename(in_progress_file)
            task.filepath = in_progress_file
        except Exception as e:
            self.logger.error(f'Could not claim task: {e}')
            return False
        
        # Create a prompt for Qwen Code
        prompt = self._create_task_prompt(task)
        
        # Process with Qwen Code
        success = self._invoke_qwen(prompt, task)
        
        if success:
            self.stats['tasks_completed'] += 1
            self.processed_files.add(task.filepath.name)
        else:
            self.stats['errors'] += 1
        
        return success
    
    def _create_task_prompt(self, task: Task) -> str:
        """
        Create a prompt for Qwen Code to process the task.
        
        Args:
            task: Task to create prompt for
            
        Returns:
            str: Prompt for Qwen Code
        """
        content = task.filepath.read_text(encoding='utf-8')
        
        prompt = f"""
You are processing a task for the AI Employee system.

## Task File: {task.filepath.name}
## Type: {task.task_type}
## Priority: {task.priority}

## Task Content:
{content}

## Your Instructions:
1. Read and understand the task above
2. Create a plan in the Plans/ folder if needed
3. Take appropriate action based on the task type
4. Update Dashboard.md with the current status
5. When complete, move this task file to Done/ folder
6. If human approval is needed, move to Pending_Approval/ folder

## Rules from Company_Handbook.md:
- Always be polite and professional
- Flag payments over $500 for approval
- Log all actions with timestamps
- Never share sensitive information without approval

Process this task now. When you are done, output: <TASK_COMPLETE>
"""
        return prompt
    
    def _invoke_qwen(self, prompt: str, task: Task) -> bool:
        """
        Invoke Qwen Code to process the task.
        
        Args:
            prompt: Prompt to send to Qwen Code
            task: Task being processed
            
        Returns:
            bool: True if processing was successful
        """
        self.logger.info('Invoking Qwen Code for task processing...')
        
        # For now, we'll create a simple processing script
        # In a full implementation, this would call Qwen Code API
        # or use a local Qwen Code instance
        
        try:
            # Create a temporary file with the task for Qwen to process
            task_log = self.plans / f'processed_{task.filepath.stem}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
            
            log_content = f"""---
task_file: {task.filepath.name}
processed_at: {datetime.now().isoformat()}
status: completed
---

# Task Processing Log

## Original Task
{task.filepath.read_text(encoding='utf-8')}

## Processing Notes
Task was processed by the orchestrator.
In a full implementation, Qwen Code would analyze and take action here.

## Status
✅ Task completed (simulated)
"""
            task_log.write_text(log_content, encoding='utf-8')
            
            # Move task to Done
            done_file = self.done / task.filepath.name
            task.filepath.rename(done_file)
            
            self.logger.info(f'Task completed: {done_file.name}')
            self.stats['tasks_processed'] += 1
            
            # Update dashboard
            self._update_dashboard()
            
            return True
            
        except Exception as e:
            self.logger.error(f'Error invoking Qwen Code: {e}')
            
            # Move back to Needs_Action on failure
            try:
                back_file = self.needs_action / task.filepath.name
                task.filepath.rename(back_file)
            except:
                pass
            
            return False
    
    def _update_dashboard(self):
        """Update the Dashboard.md with current status."""
        try:
            if not self.dashboard.exists():
                return
            
            content = self.dashboard.read_text(encoding='utf-8')
            
            # Update statistics
            pending_count = len(list(self.needs_action.glob('*.md')))
            done_today = len(list(self.done.glob('*.md')))
            approval_count = len(list(self.pending_approval.glob('*.md')))
            
            # Simple update - in production, use proper markdown parsing
            updates = [
                (r'\*\*Pending Actions\*\*.*\|', f'**Pending Actions** | {pending_count} | - |'),
                (r'\*\*Completed Today\*\*.*\|', f'**Completed Today** | {done_today} | - |'),
                (r'\*\*Pending Approvals\*\*.*\|', f'**Pending Approvals** | {approval_count} | - |'),
            ]
            
            import re
            for pattern, replacement in updates:
                content = re.sub(pattern, replacement, content)
            
            # Add to activity log
            timestamp = datetime.now().strftime('%H:%M')
            activity_line = f"| {timestamp} | Task processed | ✅ |\n"
            
            # Find the activity log section and add entry
            if '| Time | Action | Status |' in content:
                parts = content.split('| Time | Action | Status |')
                if len(parts) >= 2:
                    content = parts[0] + '| Time | Action | Status |\n' + activity_line + parts[1]
            
            self.dashboard.write_text(content, encoding='utf-8')
            self.logger.info('Dashboard updated')
            
        except Exception as e:
            self.logger.error(f'Error updating dashboard: {e}')
    
    def run(self):
        """
        Main run loop for the orchestrator.
        
        Continuously monitors for tasks and processes them.
        Runs until interrupted (Ctrl+C).
        """
        self.logger.info('=' * 50)
        self.logger.info('AI Employee Orchestrator Starting...')
        self.logger.info(f'Vault: {self.vault_path}')
        self.logger.info(f'Check interval: {self.check_interval}s')
        self.logger.info('=' * 50)
        
        try:
            while True:
                # Scan for new tasks
                tasks = self.scan_for_tasks()
                
                # Process each task
                for task in tasks:
                    self.process_task(task)
                
                # Wait before next check
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.logger.info('\nOrchestrator stopped by user')
            self._print_stats()
        except Exception as e:
            self.logger.error(f'Fatal error: {e}', exc_info=True)
            raise
    
    def _print_stats(self):
        """Print statistics summary."""
        self.logger.info('\n' + '=' * 50)
        self.logger.info('Orchestrator Statistics:')
        self.logger.info(f'  Tasks Processed: {self.stats["tasks_processed"]}')
        self.logger.info(f'  Tasks Completed: {self.stats["tasks_completed"]}')
        self.logger.info(f'  Pending Approval: {self.stats["tasks_pending_approval"]}')
        self.logger.info(f'  Errors: {self.stats["errors"]}')
        self.logger.info(f'  Start Time: {self.stats["start_time"]}')
        self.logger.info('=' * 50)


def main():
    """Main entry point for the orchestrator."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='AI Employee Orchestrator - Autonomous task processing'
    )
    parser.add_argument(
        'vault_path',
        nargs='?',
        default='.',
        help='Path to the Obsidian vault (default: current directory)'
    )
    parser.add_argument(
        '--interval', '-i',
        type=int,
        default=10,
        help='Check interval in seconds (default: 10)'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run once and exit (no continuous monitoring)'
    )
    
    args = parser.parse_args()
    
    # Resolve vault path
    vault_path = Path(args.vault_path).resolve()
    
    if not vault_path.exists():
        print(f'Error: Vault path does not exist: {vault_path}')
        sys.exit(1)
    
    # Create and run orchestrator
    orchestrator = Orchestrator(str(vault_path), check_interval=args.interval)
    
    if args.once:
        # Run once mode
        tasks = orchestrator.scan_for_tasks()
        if tasks:
            for task in tasks:
                orchestrator.process_task(task)
        else:
            print('No tasks to process')
    else:
        # Continuous mode
        orchestrator.run()


if __name__ == '__main__':
    main()
