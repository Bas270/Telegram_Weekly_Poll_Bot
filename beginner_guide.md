# Beginner's Guide: Installing and Running a GitHub Project on Ubuntu 24.04 LTS

This guide will walk you through downloading, installing, and running a project from GitHub on Ubuntu 24.04 LTS. No prior experience required!

---

## Table of Contents

1. [What You'll Need](#what-youll-need)
2. [Step 1: Open the Terminal](#step-1-open-the-terminal)
3. [Step 2: Install Git](#step-2-install-git)
4. [Step 3: Download the Project](#step-3-download-the-project)
5. [Step 4: Navigate to the Project Folder](#step-4-navigate-to-the-project-folder)
6. [Step 5: Install Dependencies](#step-5-install-dependencies)
7. [Step 6: Run the Project](#step-6-run-the-project)
8. [Troubleshooting Common Issues](#troubleshooting-common-issues)
9. [Glossary of Terms](#glossary-of-terms)

---

## What You'll Need

- **Ubuntu 24.04 LTS** installed on your computer
- **Internet connection**
- **Administrator password** (you'll need this to install software)
- **GitHub project URL** (the web address of the project you want to download)

**What is GitHub?**  
GitHub is a website where developers store their code (programs, scripts, etc.). Think of it like a library for computer programs.

**What is a repository?**  
A repository (or "repo") is just a fancy name for a project folder that contains code and files.

---

## Step 1: Open the Terminal

The **Terminal** is a text-based way to control your computer. It's like a command center where you type instructions.

**How to open Terminal:**
1. Press the **Windows key** (or click the Activities button in the top-left corner)
2. Type "Terminal" in the search box
3. Click on the **Terminal** application

You'll see a window with text that looks something like:
```
username@computername:~$
```

This is called the **command prompt** - it's waiting for you to type commands.

---

## Step 2: Install Git

**What is Git?**  
Git is a tool that helps you download projects from GitHub. It's like a special downloader for code.

**Install Git:**
1. In the Terminal, type this command and press **Enter**:
   ```bash
   sudo apt update
   ```
   - You'll be asked for your password (the one you use to log into Ubuntu)
   - Type it and press Enter (you won't see the password as you type - this is normal!)
   - This command updates the list of available software

2. Now install Git by typing:
   ```bash
   sudo apt install git -y
   ```
   - Press Enter
   - Wait for it to finish (you'll see lots of text scrolling by - this is normal!)

3. Verify Git is installed:
   ```bash
   git --version
   ```
   - You should see something like `git version 2.xx.x`
   - If you see an error, go to the Troubleshooting section

**What did we just do?**  
- `sudo` = "super user do" - gives you permission to install software
- `apt` = Advanced Package Tool - Ubuntu's way of installing software
- `install git` = tells the computer to install Git
- `-y` = automatically says "yes" to any questions

---

## Step 3: Download the Project

Now we'll download (or "clone") the project from GitHub.

**Find the GitHub URL:**
1. Go to the GitHub project page in your web browser
2. Click the green **"Code"** button
3. Copy the URL shown (it will look like: `https://github.com/username/project-name.git`)

**Clone the repository:**
1. In Terminal, type:
   ```bash
   git clone https://github.com/username/project-name.git
   ```
   - Replace `https://github.com/username/project-name.git` with the actual URL you copied
   - Press Enter
   - Wait for it to finish (you'll see text showing the download progress)

2. When it's done, you'll see a message like "Cloning into 'project-name'..."

**What did we just do?**  
- `git clone` = downloads the entire project from GitHub
- The project is now saved in a folder on your computer

---

## Step 4: Navigate to the Project Folder

**What is navigating?**  
Navigating means moving into a folder, like double-clicking a folder in a file manager.

**Go into the project folder:**
1. Type this command (replace `project-name` with the actual folder name):
   ```bash
   cd project-name
   ```
   - Press Enter
   - The prompt will change to show you're now inside the folder

2. See what files are in the folder:
   ```bash
   ls
   ```
   - This lists all files and folders
   - Look for files like `README.md`, `requirements.txt`, or `bot.py`

**What did we just do?**  
- `cd` = "change directory" - moves you into a folder
- `ls` = "list" - shows what's in the current folder

**Tip:** If you forget the folder name, type `ls` in your home directory to see all folders.

---

## Step 5: Install Dependencies

**What are dependencies?**  
Dependencies are other programs or libraries that the project needs to work. Think of them as ingredients needed to cook a recipe.

### For Python Projects

If the project uses Python (look for files ending in `.py` or `requirements.txt`):

1. **Install Python** (if not already installed):
   ```bash
   sudo apt install python3 python3-pip python3-venv -y
   ```

2. **Create a virtual environment** (a safe, isolated space for the project):
   ```bash
   python3 -m venv venv
   ```
   - This creates a folder called `venv`

3. **Activate the virtual environment**:
   ```bash
   source venv/bin/activate
   ```
   - Notice your prompt now shows `(venv)` at the beginning
   - This means the virtual environment is active

4. **Install project dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   - This reads the `requirements.txt` file and installs everything listed in it
   - Wait for it to finish (may take a few minutes)

**What did we just do?**  
- `python3 -m venv venv` = creates an isolated Python environment
- `source venv/bin/activate` = activates that environment
- `pip install` = installs Python packages
- `-r requirements.txt` = installs everything listed in that file

### For Node.js Projects

If the project uses Node.js (look for `package.json` file):

1. **Install Node.js**:
   ```bash
   sudo apt install nodejs npm -y
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

### For Other Projects

Check the project's `README.md` file for specific instructions:
```bash
cat README.md
```
- This displays the README file which usually has installation instructions

---

## Step 6: Run the Project

Now let's start the project!

### Check for a README File

First, look for instructions:
```bash
cat README.md
```
- This shows the project's instructions
- Look for a section called "Running" or "Usage"

### Common Ways to Run Projects

**Python projects:**
```bash
python3 bot.py
```
or
```bash
python bot.py
```

**Node.js projects:**
```bash
npm start
```
or
```bash
node app.js
```

**Projects with a run script:**
```bash
./run.sh
```
or
```bash
bash run.sh
```

**What to expect:**
- The program will start running
- You might see output text scrolling
- Some programs run forever until you stop them (press `Ctrl+C` to stop)

---

## Troubleshooting Common Issues

### Problem: "Command not found"

**What it means:** The computer doesn't know what command you're trying to use.

**Solutions:**
- Check for typos in your command
- Make sure you installed the required software (Git, Python, etc.)
- Try the installation steps again

### Problem: "Permission denied"

**What it means:** You don't have permission to do something.

**Solutions:**
- If installing software, make sure you used `sudo`
- If running a script, try: `chmod +x script-name.sh` then run it again
- Check if you're in the correct folder

### Problem: "No such file or directory"

**What it means:** The file or folder doesn't exist where you're looking.

**Solutions:**
- Use `ls` to see what files are actually in the folder
- Check if you're in the right directory with `pwd` (shows current location)
- Make sure you spelled the filename correctly

### Problem: "Could not resolve hostname" or "Connection failed"

**What it means:** Can't connect to GitHub or download files.

**Solutions:**
- Check your internet connection
- Try the GitHub URL in a web browser to make sure it's correct
- Wait a few minutes and try again (GitHub might be busy)

### Problem: "Package not found" or "Unable to locate package"

**What it means:** Ubuntu can't find the software you're trying to install.

**Solutions:**
- Run `sudo apt update` first to refresh the package list
- Check the package name spelling
- The package might have a different name - search online for the correct name

### Problem: Python or pip errors

**Common errors and fixes:**

**"python: command not found"**
```bash
sudo apt install python3 -y
```
Then use `python3` instead of `python`

**"pip: command not found"**
```bash
sudo apt install python3-pip -y
```
Then use `pip3` instead of `pip`

**"ModuleNotFoundError"**
- Make sure you activated the virtual environment (`source venv/bin/activate`)
- Install missing module: `pip install module-name`

### Problem: Project won't start

**Solutions:**
1. Check if all dependencies are installed
2. Read the README.md file for specific instructions
3. Look for error messages - they often tell you what's wrong
4. Make sure configuration files exist (like `vault.json`, `config.json`, etc.)

### Getting Help

**Where to find help:**
1. **README.md file** - Usually has instructions
2. **Project's GitHub page** - Look for "Issues" or "Discussions"
3. **Error messages** - Copy the error and search online
4. **Ubuntu forums** - Ask questions at askubuntu.com

---

## Glossary of Terms

**Terminal/Command Line:** A text-based way to control your computer by typing commands instead of clicking.

**Command:** An instruction you type to tell the computer what to do (like `ls` or `cd`).

**Repository (Repo):** A project folder stored on GitHub containing code and files.

**Clone:** To download a copy of a repository from GitHub to your computer.

**Dependencies:** Other programs or libraries that a project needs to work properly.

**Package Manager:** A tool that installs software for you (like `apt` for Ubuntu).

**Virtual Environment:** An isolated space for a Python project's dependencies, separate from other projects.

**README:** A file that explains what a project is and how to use it.

**sudo:** "Super user do" - gives you administrator privileges to install software.

**Directory/Folder:** A container for files and other folders (same thing, different names).

**Path:** The location of a file or folder (like `/home/username/project`).

**Prompt:** The text that appears in Terminal showing you're ready to type commands (like `username@computer:~$`).

---

## Quick Reference: Common Commands

```bash
# Navigate to home folder
cd ~

# Go up one folder level
cd ..

# See current location
pwd

# List files in current folder
ls

# List files with details
ls -l

# See hidden files
ls -a

# Copy a file
cp file1.txt file2.txt

# Move/rename a file
mv oldname.txt newname.txt

# Delete a file
rm filename.txt

# Delete a folder
rm -r foldername

# View a file's contents
cat filename.txt

# Edit a file (nano editor)
nano filename.txt
# (Press Ctrl+X to exit, Y to save, N to cancel)

# Stop a running program
Ctrl+C

# Clear the terminal screen
clear
```

---

## Example: Complete Walkthrough

Let's say you want to install a project called "telegram-bot" from GitHub:

```bash
# Step 1: Update package list
sudo apt update

# Step 2: Install Git
sudo apt install git -y

# Step 3: Clone the repository
git clone https://github.com/username/telegram-bot.git

# Step 4: Go into the project folder
cd telegram-bot

# Step 5: Install Python tools
sudo apt install python3 python3-pip python3-venv -y

# Step 6: Create virtual environment
python3 -m venv venv

# Step 7: Activate virtual environment
source venv/bin/activate

# Step 8: Install dependencies
pip install -r requirements.txt

# Step 9: Run the project
python3 bot.py
```

---

## Tips for Beginners

1. **Take your time** - Don't rush. Read each step carefully.

2. **Copy commands carefully** - One typo can cause errors. Copy and paste when possible.

3. **Read error messages** - They often tell you exactly what's wrong.

4. **Use Tab key** - In Terminal, pressing Tab will auto-complete file/folder names.

5. **Use arrow keys** - Press the up arrow to repeat previous commands.

6. **Don't panic** - If something goes wrong, you can usually start over.

7. **Keep Terminal open** - Don't close Terminal while programs are running.

8. **Read the README** - Most projects have instructions in README.md.

---

## Next Steps

Once you've successfully installed and run the project:

1. **Learn more** - Read the project's documentation
2. **Customize** - Edit configuration files to suit your needs
3. **Explore** - Try modifying the code (make a backup first!)
4. **Ask questions** - Join the project's community forums

---

## Summary

**The basic process is always the same:**

1. ✅ Install Git
2. ✅ Clone the repository
3. ✅ Go into the project folder
4. ✅ Install dependencies
5. ✅ Run the project

**Remember:**
- Terminal is your friend - it's powerful once you learn it
- Error messages are helpful - they tell you what's wrong
- Take it step by step - don't skip ahead
- Practice makes perfect - the more you use Terminal, the easier it gets

Good luck, and happy coding! 🚀
