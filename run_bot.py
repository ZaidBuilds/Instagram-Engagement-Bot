import threading
import time
import schedule
import sqlite3
from src.database import get_connection
from src.bot_engine import InstagramBot
from src.utils import setup_logger, random_sleep

logger = setup_logger("master_runner")

def run_account_cycle(account_data):
    account_id = account_data['id']
    username = account_data['username']
    password = account_data['password']
    proxy = account_data['proxy']
    
    logger.info(f"Starting thread for {username}")
    
    # Fetch settings
    conn = get_connection()
    settings_row = conn.execute("SELECT * FROM settings WHERE account_id = ?", (account_id,)).fetchone()
    settings = dict(settings_row) if settings_row else {}
    conn.close()
    
    bot = InstagramBot(account_id, username, password, proxy, settings)
    
    if not bot.login():
        logger.error(f"Failed to login {username}. Thread stopping for this cycle.")
        return

    # Main infinite loop for this account
    while True:
        try:
            # 1. Refresh Targets
            conn = get_connection()
            # Fetch hashtags, locations, etc.
            rows = conn.execute("SELECT target_type, target_value FROM targets WHERE account_id = ? AND status='active'", (account_id,)).fetchall()
            conn.close()
            
            targets = [{'type': r['target_type'], 'value': r['target_value']} for r in rows]
            
            if not targets:
                logger.warning(f"No active targets for {username}. Sleeping 10 mins.")
                time.sleep(600)
                continue
                
            # 2. Run Actions
            bot.process_targets(targets)
            
            # 3. Unfollow Routine
            bot.run_unfollow_routine()
            
            # 4. Long Sleep between cycles (e.g., 2-4 hours) to be safe
            logger.info(f"Cycle complete for {username}. Sleeping for ~3 hours.")
            random_sleep(3 * 3600, 4 * 3600, "Cycle Interval")
            
        except Exception as e:
            logger.error(f"Crash in thread for {username}: {e}")
            time.sleep(300) # Sleep 5 mins on error before retrying

def main_loop():
    logger.info("Starting Master Bot Runner...")
    
    active_threads = {}
    
    while True:
        conn = get_connection()
        accounts = conn.execute("SELECT * FROM accounts WHERE status = 'active'").fetchall()
        conn.close()
        
        current_account_ids = []
        
        for acc in accounts:
            acc_id = acc['id']
            current_account_ids.append(acc_id)
            
            if acc_id not in active_threads or not active_threads[acc_id].is_alive():
                logger.info(f"Spawning thread for account {acc['username']}")
                t = threading.Thread(target=run_account_cycle, args=(acc,))
                t.daemon = True
                t.start()
                active_threads[acc_id] = t
        
        # Optional: Clean up threads for accounts no longer active (not implemented for simplicity now)
        
        logger.info(f"Master runner checking in. Active threads: {len(active_threads)}")
        time.sleep(60) # Check for new accounts every minute

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
