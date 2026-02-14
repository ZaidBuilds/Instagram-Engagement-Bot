import sys
import os

print("Checking system setup...")

# 1. Check Python Version
print(f"Python Version: {sys.version}")

# 2. Check Imports
try:
    import instagrapi
    import streamlit
    import pandas
    import groq
    import dotenv
    import schedule
    import plotly
    print("✅ All required packages are installed.")
except ImportError as e:
    print(f"❌ Missing package: {e}. Please run 'pip install -r requirements.txt'")

# 3. Check Database
try:
    import sqlite3
    db_path = os.path.join('database', 'instagram_bot.db')
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table'")
        count = cursor.fetchone()[0]
        conn.close()
        print(f"✅ Database found at {db_path} with {count} tables.")
    else:
        print(f"❌ Database not found at {db_path}. Please run 'python src/database.py'")
except Exception as e:
    print(f"❌ Database check failed: {e}")

# 4. Check Env
if os.path.exists('.env'):
    print("✅ .env file found.")
else:
    print("⚠️ .env file missing. Please copy .env.example to .env and configure it.")

print("\nSetup check complete.")
