# How to Push Your Project to GitHub

## 🚨 Git Not Installed

Git is not currently installed on your system. Follow these steps to install Git and push your project.

---

## Step 1: Install Git

### Download Git for Windows

1. Go to: https://git-scm.com/download/win
2. Download the latest version (64-bit recommended)
3. Run the installer
4. **Important settings during installation:**
   - ✅ Use Git from the Windows Command Prompt
   - ✅ Use the OpenSSL library
   - ✅ Checkout Windows-style, commit Unix-style line endings
   - ✅ Use MinTTY (default terminal)
   - ✅ Enable Git Credential Manager

5. Click "Install" and wait for completion
6. Restart PowerShell/Terminal after installation

---

## Step 2: Configure Git (First Time Only)

Open PowerShell and run:

```powershell
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

Replace with your actual name and email (use the same email as your GitHub account).

---

## Step 3: Initialize Git Repository

```powershell
cd C:\Users\jaswa\Desktop\final
git init
```

**Expected output:**
```
Initialized empty Git repository in C:/Users/jaswa/Desktop/final/.git/
```

---

## Step 4: Add All Files

```powershell
git add .
```

This stages all files for commit (excluding those in `.gitignore`).

---

## Step 5: Create First Commit

```powershell
git commit -m "Initial commit: Crypto Price Prediction & Sentiment Analysis"
```

**Expected output:**
```
[main (root-commit) abc1234] Initial commit: Crypto Price Prediction & Sentiment Analysis
 XX files changed, XXXX insertions(+)
 create mode 100644 README.md
 ...
```

---

## Step 6: Rename Branch to Main

```powershell
git branch -M main
```

---

## Step 7: Add Remote Repository

```powershell
git remote add origin https://github.com/jaswanthsai0430/Crypto-Price-Predictor.git
```

---

## Step 8: Push to GitHub

```powershell
git push -u origin main
```

**You'll be prompted for GitHub credentials:**

### Option A: Personal Access Token (Recommended)

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a name: "Crypto Predictor"
4. Select scopes: ✅ `repo` (all)
5. Click "Generate token"
6. **Copy the token immediately** (you won't see it again!)
7. When prompted for password, paste the token

### Option B: GitHub CLI

Or use GitHub CLI for easier authentication:
```powershell
winget install GitHub.cli
gh auth login
```

---

## ✅ Verification

After successful push, visit:
https://github.com/jaswanthsai0430/Crypto-Price-Predictor

You should see all your files!

---

## 📋 Quick Reference Commands

### Check status
```powershell
git status
```

### Add specific files
```powershell
git add filename.py
```

### Commit changes
```powershell
git commit -m "Your commit message"
```

### Push changes
```powershell
git push
```

### Pull latest changes
```powershell
git pull
```

### View commit history
```powershell
git log --oneline
```

---

## 🔧 Troubleshooting

### "Git is not recognized"
- Restart PowerShell after installing Git
- Or add Git to PATH manually

### "Permission denied"
- Use Personal Access Token instead of password
- Or set up SSH keys

### "Repository already exists"
If the GitHub repo already has content:
```powershell
git pull origin main --allow-unrelated-histories
git push -u origin main
```

### Large files error
If you get errors about large files:
```powershell
# Remove large files from tracking
git rm --cached backend/models/saved/*.h5
git commit -m "Remove large model files"
git push
```

---

## 📦 What Gets Pushed

### ✅ Included:
- All source code (`.py`, `.js`, `.html`, `.css`)
- Configuration files (`requirements.txt`, `config.json`)
- Documentation (`README.md`)
- Empty directories with `.gitkeep`

### ❌ Excluded (via `.gitignore`):
- Virtual environment (`venv/`)
- Trained models (`*.h5`, `*.pkl`)
- Cache files (`__pycache__/`)
- Environment variables (`.env`)
- IDE settings (`.vscode/`, `.idea/`)

---

## 🎯 After First Push

### To update your code later:

1. Make changes to your files
2. Stage changes:
```powershell
git add .
```

3. Commit:
```powershell
git commit -m "Description of changes"
```

4. Push:
```powershell
git push
```

---

## 📝 Recommended Commit Messages

- `"Add BNB and DOGE support"`
- `"Improve model accuracy with Bi-LSTM"`
- `"Fix sentiment analyzer API integration"`
- `"Update README with installation instructions"`
- `"Add feature engineering module"`

---

## 🔐 Security Reminder

**Never commit:**
- API keys (use `.env` file)
- Passwords
- Personal information
- Large binary files

These are already excluded in `.gitignore`!

---

## ✨ Complete Command Sequence

Here's the full sequence to copy-paste:

```powershell
# Navigate to project
cd C:\Users\jaswa\Desktop\final

# Initialize Git
git init

# Add all files
git add .

# First commit
git commit -m "Initial commit: Crypto Price Prediction & Sentiment Analysis with Bi-LSTM"

# Rename branch
git branch -M main

# Add remote
git remote add origin https://github.com/jaswanthsai0430/Crypto-Price-Predictor.git

# Push to GitHub
git push -u origin main
```

---

## 🎉 Success!

Once pushed, your project will be live at:
**https://github.com/jaswanthsai0430/Crypto-Price-Predictor**

Share it with the world! 🚀
