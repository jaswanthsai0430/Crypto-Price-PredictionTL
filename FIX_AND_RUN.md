# Run Project Guide

## ⚠️ Error Solution: "Activate.ps1 is not recognized"

This error happens because the virtual environment (`venv`) folder is missing. You need to recreate it.

### Step-by-Step Fix:

1. **Open PowerShell** and navigate to the `backend` folder:
   ```powershell
   cd C:\Users\jaswa\Desktop\final\backend
   ```

2. **Create the virtual environment** (this creates the missing `venv` folder):
   ```powershell
   python -m venv venv
   ```

3. **Activate it** (now this command will work):
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

4. **Install dependencies** (required after recreating venv):
   ```powershell
   pip install -r requirements.txt
   ```
   *Note: This might take a few minutes.*

5. **Run the Server**:
   ```powershell
   python app.py
   ```

---

## 🚀 One-Click Run Script

I have created a script `run_project.ps1` in the `final` folder. You can simply run:

```powershell
cd C:\Users\jaswa\Desktop\final
.\run_project.ps1
```

This script will automatically check for `venv`, create it if missing, install dependencies, and start the server.
