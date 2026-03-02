# AI Employee - Bronze Tier Setup Guide

Your Personal AI Employee that works 24/7 to manage personal and business affairs.

## Quick Start (5 minutes)

### Step 1: Install Python Dependencies

```bash
cd Scripts
pip install watchdog
```

### Step 2: Start the Orchestrator (Recommended)

The orchestrator automatically processes tasks with Qwen Code:

```bash
# From the Scripts folder
python orchestrator.py ..
```

Or run both watcher and orchestrator:
```bash
# Terminal 1: File System Watcher
python filesystem_watcher.py ..

# Terminal 2: Orchestrator  
python orchestrator.py ..
```

### Step 3: Test It Works

1. Keep the orchestrator running in a terminal
2. Drop any file into the `Inbox/` folder
3. Watcher creates action file in `Needs_Action/`
4. Orchestrator processes it and moves to `Done/`

### Step 4: Use with Qwen Code

Open Qwen Code and point it at this vault:

Then ask it to:
```
Check the Needs_Action folder and process any pending items.
Create a plan for each item and move completed tasks to Done.
Update the Dashboard.md with the current status.
```

---

## Project Structure

```
ai-empolyee/
├── Dashboard.md              # Main status dashboard
├── Company_Handbook.md       # Rules of engagement
├── Business_Goals.md         # Q1 2026 objectives
├── QWEN.md                   # Context for AI assistants
├── Inbox/                    # Drop files here for processing
├── Needs_Action/             # Action files created by watchers
├── Done/                     # Completed tasks
├── Plans/                    # Task plans created by Qwen Code
├── Pending_Approval/         # Items awaiting human approval
├── Accounting/               # Financial records
├── Briefings/                # CEO briefings (weekly audits)
└── Scripts/
    ├── base_watcher.py       # Base class for all watchers
    ├── filesystem_watcher.py # File drop watcher (Bronze tier)
    ├── orchestrator.py       # Main orchestrator (auto-processes tasks)
    └── requirements.txt      # Python dependencies
```

---

## How It Works

### The Watcher Pattern

1. **Watcher Script** runs continuously in the background
2. **Monitors** a data source (filesystem, Gmail, WhatsApp, etc.)
3. **Detects** new items requiring attention
4. **Creates** `.md` action files in `Needs_Action/`
5. **Qwen Code** processes these files and takes action

### File Flow

```
[New File] → Inbox/
              ↓
    (Watcher detects)
              ↓
    [Action File] → Needs_Action/
              ↓
    (Qwen Code processes)
              ↓
    [Plan Created] → Plans/
              ↓
    (Task completed)
              ↓
    [Move to] → Done/
```

---

## Bronze Tier Deliverables Checklist

- [x] Obsidian vault with `Dashboard.md` and `Company_Handbook.md`
- [x] One working Watcher script (File System monitoring)
- [x] Qwen Code can read from and write to the vault
- [x] Basic folder structure: `/Inbox`, `/Needs_Action`, `/Done`

---

## Usage Examples

### Example 1: Process a Document

1. Drop `invoice.pdf` into `Inbox/`
2. Watcher creates `Needs_Action/FILE_invoice.pdf.md`
3. Qwen Code reads the action file
4. Qwen Code creates a plan to categorize and record the invoice
5. Move to `Done/` when complete

### Example 2: Daily Check-in

Ask Qwen Code to:
```
1. Check all files in Needs_Action/
2. Create a summary of pending items
3. Update Dashboard.md with current status
4. Suggest priorities for today
```

### Example 3: Weekly Review

Ask Qwen Code to:
```
1. Review all completed tasks in Done/
2. Read Business_Goals.md for targets
3. Generate a weekly progress report
4. Save to Briefings/ folder
```

---

## Running the Orchestrator and Watchers

### Option 1: Orchestrator Only (Recommended for Bronze Tier)

The orchestrator includes task scanning and processing:

```cmd
cd C:\Users\SHARJEELAHMED\Desktop\ai-empolyee\Scripts
python orchestrator.py ..
```

### Option 2: Watcher + Orchestrator (Full Automation)

Run both in separate terminals:

```cmd
REM Terminal 1: File System Watcher
cd C:\Users\SHARJEELAHMED\Desktop\ai-empolyee\Scripts
python filesystem_watcher.py ..

REM Terminal 2: Orchestrator
cd C:\Users\SHARJEELAHMED\Desktop\ai-empolyee\Scripts
python orchestrator.py ..
```

### Run in Background (Windows)

```cmd
start /B python filesystem_watcher.py ..
start /B python orchestrator.py ..
```

### Orchestrator Options

```bash
# Run continuously (default)
python orchestrator.py <vault_path>

# Run with custom check interval (30 seconds)
python orchestrator.py .. --interval 30

# Run once and exit (no continuous monitoring)
python orchestrator.py .. --once
```

### Stop the Watcher/Orchestrator
Press `Ctrl+C` in the terminal where it's running.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Employee System                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Watchers   │───▶│  Orchestrator │───▶│  Qwen Code   │  │
│  │  (Senses)    │    │   (Brain)     │    │   (Action)   │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                   │           │
│         ▼                   ▼                   ▼           │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │ Inbox/       │    │ Needs_Action/│    │ Plans/       │  │
│  │ (File Drop)  │    │ (Task Queue) │    │ (Strategies) │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                              │               │
│                                              ▼               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │ Dashboard.md │◀───│    Done/     │◀───│ Pending_/    │  │
│  │   (Status)   │    │ (Completed)  │    │ Approval/    │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Upgrading to Silver Tier

To add more capabilities:

1. **Gmail Watcher**: Install Google API dependencies and set up OAuth
2. **WhatsApp Watcher**: Install Playwright and set up browser automation
3. **MCP Server**: Set up email-MCP for sending emails
4. **Approval Workflow**: Implement human-in-the-loop for sensitive actions

See the main hackathon document for detailed instructions.

---

## Troubleshooting

### Orchestrator not processing files
- Ensure the orchestrator is running (`python orchestrator.py ..`)
- Check that action files exist in `Needs_Action/` folder
- Verify the `orchestrator.log` file for error details

### Watcher not detecting files
- Ensure the watcher is running (`python filesystem_watcher.py ..`)
- Check that files are being dropped in `Inbox/` (not `Needs_Action/`)
- Verify no permission issues on the folder

### Action files not being created
- Check the terminal for error messages
- Ensure `Needs_Action/` folder exists and is writable
- Verify Python has write permissions

### Qwen Code not processing files
- Make sure Qwen Code is pointed at the correct vault directory
- Check that action files have proper YAML frontmatter
- Verify the file format matches the expected schema

---

## Next Steps

1. **Customize** `Company_Handbook.md` with your specific rules
2. **Update** `Business_Goals.md` with your actual targets
3. **Test** the workflow by dropping files into `Inbox/`
4. **Integrate** with Qwen Code for autonomous processing
5. **Expand** to Silver tier by adding Gmail/WhatsApp watchers

---

## Resources

- **Main Hackathon Document**: `Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md`
- **Qwen Code**: https://github.com/QwenLM/Qwen
- **Agent Skills**: Use modular skills for extended functionality
- **Weekly Research Meeting**: Wednesdays 10:00 PM PKT on Zoom

---

## Support

Join the weekly research meeting for help:
- **Zoom**: https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1
- **YouTube**: https://www.youtube.com/@panaversity
