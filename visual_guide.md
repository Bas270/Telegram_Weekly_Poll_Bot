# Visual Step-by-Step Guide

## Installation Flowchart

```
START
  │
  ├─► Open Terminal
  │
  ├─► Install Git?
  │   ├─ Yes ──► sudo apt update
  │   │         sudo apt install git -y
  │   └─ No ────► Continue
  │
  ├─► Download Project
  │   └─► git clone https://github.com/username/project.git
  │
  ├─► Go to Project Folder
  │   └─► cd project-name
  │
  ├─► Check Project Type
  │   │
  │   ├─► Python Project? (has .py files or requirements.txt)
  │   │   ├─► Install Python: sudo apt install python3 python3-pip python3-venv -y
  │   │   ├─► Create venv: python3 -m venv venv
  │   │   ├─► Activate: source venv/bin/activate
  │   │   └─► Install deps: pip install -r requirements.txt
  │   │
  │   ├─► Node.js Project? (has package.json)
  │   │   ├─► Install Node: sudo apt install nodejs npm -y
  │   │   └─► Install deps: npm install
  │   │
  │   └─► Other Project?
  │       └─► Read README.md for instructions
  │
  ├─► Run the Project
  │   ├─► Python: python3 main.py
  │   ├─► Node.js: npm start
  │   └─► Other: Check README.md
  │
  └─► SUCCESS! ✅
```

---

## Decision Tree: What Type of Project Is This?

```
Look at project files (use: ls)

├─► Has requirements.txt?
│   └─► Python Project
│       └─► Follow Python installation steps
│
├─► Has package.json?
│   └─► Node.js Project
│       └─► Follow Node.js installation steps
│
├─► Has README.md?
│   └─► Read it!
│       └─► Follow instructions inside
│
└─► Not sure?
    └─► Check README.md
        └─► Still not sure?
            └─► Ask for help on project's GitHub page
```

---

## Error Resolution Flowchart

```
ERROR OCCURRED
  │
  ├─► Read the error message carefully
  │
  ├─► What does it say?
  │   │
  │   ├─► "Command not found"
  │   │   └─► Check spelling
  │   │   └─► Install missing software
  │   │
  │   ├─► "Permission denied"
  │   │   └─► Add "sudo" before command
  │   │   └─► Or: chmod +x filename
  │   │
  │   ├─► "No such file or directory"
  │   │   └─► Check current location: pwd
  │   │   └─► List files: ls
  │   │   └─► Check spelling
  │   │
  │   ├─► "Could not resolve hostname"
  │   │   └─► Check internet connection
  │   │   └─► Verify GitHub URL is correct
  │   │
  │   ├─► Python/Module errors
  │   │   └─► Activate virtual environment: source venv/bin/activate
  │   │   └─► Install missing module: pip install module-name
  │   │
  │   └─► Something else?
  │       └─► Copy error message
  │       └─► Search online
  │       └─► Ask for help
  │
  └─► Try again!
```

---

## Project Update Flowchart

```
Want to Update Project?
  │
  ├─► Go to project folder
  │   └─► cd project-name
  │
  ├─► Update code from GitHub
  │   └─► git pull
  │
  ├─► Dependencies changed?
  │   ├─ Yes ──► Update dependencies
  │   │         ├─ Python: pip install -r requirements.txt
  │   │         └─ Node.js: npm install
  │   └─ No ───► Continue
  │
  └─► Restart project
      └─► Run it again!
```

---

## First Time Setup Checklist

```
☐ Opened Terminal
☐ Installed Git (sudo apt install git -y)
☐ Cloned repository (git clone URL)
☐ Navigated to project folder (cd project-name)
☐ Checked project type (Python/Node.js/Other)
☐ Installed required tools (Python/Node.js)
☐ Created virtual environment (if Python)
☐ Activated virtual environment (if Python)
☐ Installed dependencies (pip/npm install)
☐ Checked for configuration files
☐ Read README.md for specific instructions
☐ Ran the project successfully
```

---

## Common File Types Reference

| File Extension | What It Means | What To Do |
|----------------|---------------|------------|
| `.py` | Python script | Run with `python3 filename.py` |
| `.js` | JavaScript file | Run with `node filename.js` |
| `.sh` | Shell script | Run with `bash filename.sh` |
| `requirements.txt` | Python dependencies | Install with `pip install -r requirements.txt` |
| `package.json` | Node.js dependencies | Install with `npm install` |
| `README.md` | Instructions | Read with `cat README.md` |
| `.json` | Configuration file | Usually edited, not run directly |
| `.env` | Environment variables | Contains settings (may need to create) |

---

## Terminal Navigation Visual Guide

```
Home Directory (~)
│
├── Documents/
│   └── project-name/          ← You are here after git clone
│       ├── bot.py
│       ├── requirements.txt
│       └── README.md
│
Commands:
  cd Documents/project-name    ← Go into project folder
  cd ..                        ← Go back up
  cd ~                         ← Go to home
  pwd                          ← Show where you are
```

---

## Virtual Environment Visual Guide

```
Before Activation:
username@computer:~$ python3 script.py
  ↑ System Python (shared with everything)

After Activation:
username@computer:~$ source venv/bin/activate
(venv) username@computer:~$ python3 script.py
         ↑ Isolated Python (just for this project)
```

**Why use virtual environment?**
- Keeps project dependencies separate
- Prevents conflicts between projects
- Makes it easier to manage versions

---

## Command Breakdown Examples

### Example 1: Installing Git
```bash
sudo apt install git -y
│    │   │      │   │
│    │   │      │   └─ Automatically say "yes" to prompts
│    │   │      └───── Package name to install
│    │   └──────────── Tool for installing software
│    └──────────────── Administrator permission
└───────────────────── "Super User Do" (admin mode)
```

### Example 2: Cloning Repository
```bash
git clone https://github.com/user/repo.git
│   │     │
│   │     └─ GitHub URL (where to download from)
│   └─────── Command to download repository
└─────────── Git tool
```

### Example 3: Python Virtual Environment
```bash
python3 -m venv venv
│      │  │    │
│      │  │    └─ Folder name (can be anything)
│      │  └────── Module to run (venv = virtual environment)
│      └───────── Python version 3
└──────────────── Python command
```

---

## Time Estimates

| Task | Estimated Time |
|------|----------------|
| Installing Git | 2-5 minutes |
| Cloning repository | 1-3 minutes (depends on size) |
| Installing Python tools | 3-5 minutes |
| Installing dependencies | 2-10 minutes (depends on project) |
| Running project | Instant (if everything is set up) |
| **Total first-time setup** | **10-25 minutes** |

---

## Success Indicators

**✅ Git installed correctly:**
```bash
$ git --version
git version 2.xx.x
```

**✅ Repository cloned successfully:**
```bash
$ ls
project-name/
```

**✅ Virtual environment activated:**
```bash
$ source venv/bin/activate
(venv) $ 
```

**✅ Dependencies installed:**
```bash
$ pip list
Package    Version
---------- -------
package1   1.0.0
package2   2.0.0
```

**✅ Project running:**
- No error messages
- Program output appears
- Program continues running (or completes successfully)

---

## Remember

1. **Terminal is case-sensitive** - `cd` works, but `CD` doesn't
2. **Spaces matter** - `cd folder name` won't work, use quotes: `cd "folder name"`
3. **Read error messages** - They usually tell you exactly what's wrong
4. **Take breaks** - If frustrated, step away and come back
5. **Practice** - The more you use Terminal, the easier it gets!

---

**Need more help?** See `BEGINNER_GUIDE.md` for detailed explanations!
