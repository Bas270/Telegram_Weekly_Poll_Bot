# Quick Reference Card

Print this page and keep it handy!

---

## Essential Commands Cheat Sheet

### Navigation
```bash
cd folder-name          # Go into a folder
cd ..                   # Go up one level
cd ~                    # Go to home folder
pwd                     # Show current location
ls                      # List files
```

### Git Commands
```bash
git clone URL           # Download project from GitHub
git pull                # Update existing project
```

### Installing Software
```bash
sudo apt update                    # Update package list
sudo apt install package-name -y   # Install software
```

### Python Projects
```bash
python3 -m venv venv              # Create virtual environment
source venv/bin/activate          # Activate virtual environment
pip install -r requirements.txt   # Install dependencies
python3 script.py                 # Run Python script
```

### Useful Shortcuts
```
Ctrl+C          # Stop running program
Ctrl+D          # Exit Terminal
Tab             # Auto-complete file/folder names
Up Arrow        # Repeat previous command
clear           # Clear screen
```

---

## Common Installation Steps

### 1. Install Git
```bash
sudo apt update
sudo apt install git -y
```

### 2. Download Project
```bash
git clone https://github.com/username/project-name.git
cd project-name
```

### 3. Install Python Dependencies
```bash
sudo apt install python3 python3-pip python3-venv -y
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Run Project
```bash
python3 main.py
```

---

## Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| "Command not found" | Check spelling, install missing software |
| "Permission denied" | Use `sudo` for installations |
| "No such file" | Check you're in the right folder with `ls` |
| Python errors | Make sure virtual environment is activated |
| Can't connect | Check internet connection |

---

## Getting Help

1. Read `README.md` file
2. Check project's GitHub page
3. Search error message online
4. Ask on Ubuntu forums (askubuntu.com)

---

**Remember:** Take your time, read carefully, and don't be afraid to ask for help!
