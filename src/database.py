import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'instagram_bot.db')

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Accounts Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        proxy TEXT,
        status TEXT DEFAULT 'active', -- active, paused, banned, checkpoint
        last_action_time TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 2. Targets Table (Hashtags, Locations, Competitors)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS targets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER,
        target_type TEXT NOT NULL, -- hashtag, location, user
        target_value TEXT NOT NULL,
        status TEXT DEFAULT 'active',
        FOREIGN KEY (account_id) REFERENCES accounts (id)
    )
    ''')
    
    # 3. Actions Log Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS actions_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER,
        action_type TEXT NOT NULL, -- like, comment, follow, unfollow
        target_user TEXT,
        details TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (account_id) REFERENCES accounts (id)
    )
    ''')
    
    # 4. Followers Tracking to measure growth and handle unfollows
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS followers_tracking (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER,
        username TEXT NOT NULL,
        followed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_unfollowed BOOLEAN DEFAULT 0,
        unfollowed_date TIMESTAMP,
        source_target TEXT, -- Which hashtag/location led to this follow
        FOREIGN KEY (account_id) REFERENCES accounts (id)
    )
    ''')
    
    # 5. Settings Table (Global or per account - usually per account is better for customization)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER UNIQUE,
        max_likes_per_day INTEGER DEFAULT 150,
        max_comments_per_day INTEGER DEFAULT 40,
        max_follows_per_day INTEGER DEFAULT 50,
        max_unfollows_per_day INTEGER DEFAULT 50,
        speed_multiplier REAL DEFAULT 1.0, -- 1.0 = normal safe speed
        active_hours_start INTEGER DEFAULT 9, -- 9 AM
        active_hours_end INTEGER DEFAULT 22, -- 10 PM
        use_ai_comments BOOLEAN DEFAULT 1,
        FOREIGN KEY (account_id) REFERENCES accounts (id)
    )
    ''')
    
    # 6. Client Billing Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS client_billing (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER UNIQUE,
        client_name TEXT,
        contact_email TEXT,
        monthly_fee REAL DEFAULT 24.0,
        start_date DATE,
        next_payment_due DATE,
        payment_status TEXT DEFAULT 'pending', -- paid, pending, overdue
        notes TEXT,
        FOREIGN KEY (account_id) REFERENCES accounts (id)
    )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

if __name__ == "__main__":
    init_db()
