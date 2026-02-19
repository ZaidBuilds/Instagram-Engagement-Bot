import os
import sys

print("Checking system setup...")

# 1. Check Python version
print(f"Python Version: {sys.version}")

# 2. Check imports
required_packages = [
    "instagrapi",
    "streamlit",
    "pandas",
    "groq",
    "dotenv",
    "schedule",
    "plotly",
]

missing = []
for pkg in required_packages:
    try:
        __import__(pkg)
    except ImportError:
        missing.append(pkg)

if missing:
    print("Missing packages: " + ", ".join(missing))
    print("Run: pip install -r requirements.txt")
else:
    print("[OK] All required packages are installed.")

# 3. Check database
try:
    import sqlite3

    db_path = os.path.join("database", "instagram_bot.db")
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table'")
        count = cursor.fetchone()[0]
        conn.close()
        print(f"[OK] Database found at {db_path} with {count} tables.")
    else:
        print(f"[MISSING] Database not found at {db_path}. Run: python src/database.py")
except Exception as e:
    print(f"[ERROR] Database check failed: {e}")

# 4. Check env
if os.path.exists(".env"):
    print("[OK] .env file found.")
else:
    print("[WARN] .env file missing. Copy .env.example to .env and configure it.")

print("\nSetup check complete.")
