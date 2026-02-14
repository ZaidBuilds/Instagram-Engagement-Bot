import time
import random
import os
from instagrapi import Client
import sqlite3
from src.database import get_connection
from src.utils import setup_logger, random_sleep
from src.ai_generator import AICommentGenerator
from src.notifications import send_telegram_alert
from datetime import datetime, timedelta

class InstagramBot:
    def __init__(self, account_id, username, password, proxy=None, settings=None):
        self.account_id = account_id
        self.username = username
        self.password = password
        self.proxy = proxy
        self.settings = settings or {}
        self.cl = Client()
        self.logger = setup_logger(f"bot_{username}")
        self.ai = AICommentGenerator()
        self.is_logged_in = False
        
        # Ensure sessions directory exists
        self.session_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sessions', f"{self.username}.json")
        os.makedirs(os.path.dirname(self.session_file), exist_ok=True)
        
        # Load daily counters from DB or reset if new day
        self.daily_likes = 0
        self.daily_comments = 0
        self.daily_follows = 0
        self.daily_unfollows = 0

    def login(self):
        try:
            if self.proxy:
                self.cl.set_proxy(self.proxy)
            
            self.logger.info(f"Attempting to login as {self.username}...")
            
            # Try to load session first
            if os.path.exists(self.session_file):
                self.logger.info("Loading session from file...")
                try:
                    self.cl.load_settings(self.session_file)
                except Exception as e:
                    self.logger.warning(f"Could not load session: {e}")

            # active valid session check could be done here, but login() handles it usually
            # if self.cl.login(self.username, self.password): # This re-logs in if session invalid
            # But instagrapi login() automatically checks session validity if settings loaded?
            # Actually best practice with instagrapi:
            # 1. load settings
            # 2. if not logged in, login
            
            self.cl.login(self.username, self.password)
            self.cl.dump_settings(self.session_file) # Save session
            
            self.is_logged_in = True
            self.logger.info("Login successful!")
            self._update_status("active")
            return True
        except Exception as e:
            self.logger.error(f"Login failed: {e}")
            self._update_status("login_failed")
            send_telegram_alert(f"Login failed for {self.username}: {e}")
            return False

    def get_warmup_multiplier(self):
        """
        Calculate scale factor based on account age in the system.
        If account added < 7 days ago, reduce limits.
        """
        conn = get_connection()
        row = conn.execute("SELECT created_at FROM accounts WHERE id = ?", (self.account_id,)).fetchone()
        conn.close()
        
        if row and row['created_at']:
            try:
                # Handle timestamp format 'YYYY-MM-DD HH:MM:SS'
                created_dt = datetime.strptime(row['created_at'], "%Y-%m-%d %H:%M:%S")
                days_active = (datetime.now() - created_dt).days
                if days_active < 7:
                    self.logger.info(f"Warm-up active: Account age {days_active} days. Scaling limits by 50%.")
                    return 0.5
            except:
                pass 
        return 1.0

    def _update_status(self, status):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE accounts SET status = ?, last_action_time = CURRENT_TIMESTAMP WHERE id = ?", 
                       (status, self.account_id))
        conn.commit()
        conn.close()

    def _log_action(self, action_type, target_user, details=""):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO actions_log (account_id, action_type, target_user, details)
            VALUES (?, ?, ?, ?)
        ''', (self.account_id, action_type, target_user, details))
        conn.commit()
        conn.close()
        self.logger.info(f"Action logged: {action_type} on {target_user}")

    def check_limits(self):
        """Check if daily limits are reached"""
        settings = self.settings
        multiplier = self.get_warmup_multiplier()
        
        limit_likes = int(settings.get('max_likes_per_day', 150) * multiplier)
        limit_comments = int(settings.get('max_comments_per_day', 40) * multiplier)
        limit_follows = int(settings.get('max_follows_per_day', 50) * multiplier)
        
        if self.daily_likes >= limit_likes:
            return False
        if self.daily_comments >= limit_comments:
            return False
        if self.daily_follows >= limit_follows:
            return False
        # Add more checks as needed
        return True

    def process_targets(self, targets):
        """Interact with posts from specific targets (hashtags or locations)"""
        if not self.is_logged_in: return
        
        for target in targets:
            target_type = target['type']
            target_value = target['value']
            
            if not self.check_limits(): 
                self.logger.info("Daily limits reached. Stopping.")
                break
                
            self.logger.info(f"Scanning {target_type}: {target_value}")
            
            try:
                medias = []
                if target_type == 'hashtag':
                    # target_value should be the tag name (without #)
                    tag = target_value.replace('#', '')
                    medias = self.cl.hashtag_medias_recent(tag, amount=20)
                elif target_type == 'location':
                    # Search for location ID
                    locs = self.cl.location_search(target_value)
                    if locs:
                        loc = locs[0]
                        self.logger.info(f"Found location ID {loc.pk} for {target_value}")
                        medias = self.cl.location_medias_recent(loc.pk, amount=20)
                    else:
                        self.logger.warning(f"Location {target_value} not found.")
                        continue
                
                for media in medias:
                    if not self.check_limits(): break
                    
                    user_info = media.user
                    
                    # Skip if own account
                    if user_info.username == self.username: continue
                    
                    # SAFETY FILTER: Skip verified accounts (usually influencers/brands with low follow-back)
                    if getattr(user_info, 'is_verified', False):
                        self.logger.info(f"Skipping verified user: {user_info.username}")
                        continue
                        
                    # 1. Like
                    if self.daily_likes < self.settings.get('max_likes_per_day', 150):
                        self.logger.info(f"Liking post {media.pk} by {user_info.username}")
                        try:
                            self.cl.media_like(media.pk)
                            self.daily_likes += 1
                            self._log_action('like', user_info.username, f"Media: {media.pk}")
                            random_sleep(30, 60, "Post-like delay")
                        except Exception as e:
                            self.logger.error(f"Failed to like media {media.pk}: {e}")

                    # Helper to check business account (expensive call, so use sparingly)
                    def is_business_account(user_pk):
                        try:
                            full_info = self.cl.user_info(user_pk)
                            return full_info.is_business or full_info.account_type != 1 # 1 is usually personal
                        except:
                            return False # specific logic dependent on instagrapi version, assume false on error to be safe or true to be safe

                    # 2. Comment (random chance, e.g., 30%)
                    if random.random() < 0.3 and self.daily_comments < self.settings.get('max_comments_per_day', 40):
                        # Optional: Check if business account before commenting (to save API calls, maybe allow simple comments)
                        # if is_business_account(user_info.pk): 
                        #     self.logger.info(f"Skipping comment on business account: {user_info.username}")
                        # else:
                        
                        comment_text = self.ai.generate_comment(media.caption_text)
                        if comment_text:
                            self.logger.info(f"Commenting on post {media.pk}: {comment_text}")
                            try:
                                self.cl.media_comment(media.pk, comment_text)
                                self.daily_comments += 1
                                self._log_action('comment', user_info.username, f"Comment: {comment_text}")
                                random_sleep(60, 120, "Post-comment delay")
                            except Exception as e:
                                self.logger.error(f"Failed to comment on {media.pk}: {e}")
                    
                    # 3. Follow (random chance, e.g., 20%)
                    if random.random() < 0.2 and self.daily_follows < self.settings.get('max_follows_per_day', 50):
                         # For follows, we definitely want to avoid business accounts if possible
                        if is_business_account(user_info.pk):
                            self.logger.info(f"Skipping follow of business account: {user_info.username}")
                        else:
                            self.logger.info(f"Following user {user_info.username}")
                            try:
                                self.cl.user_follow(user_info.pk)
                                self.daily_follows += 1
                                self._log_action('follow', user_info.username)
                                
                                # Track for unfollow later
                                conn = get_connection()
                                conn.execute("INSERT INTO followers_tracking (account_id, username, source_target) VALUES (?, ?, ?)",
                                             (self.account_id, user_info.username, f"{target_type}:{target_value}"))
                                conn.commit()
                                conn.close()
                                
                                random_sleep(40, 80, "Post-follow delay")
                            except Exception as e:
                                self.logger.error(f"Failed to follow {user_info.username}: {e}")

            except Exception as e:
                self.logger.error(f"Error processing target {target_value}: {e}")
                send_telegram_alert(f"Error processing target {target_value} for {self.username}: {e}")
                random_sleep(120, 300, "Error cooldown")

    def run_unfollow_routine(self):
        """Unfollow users followed > 3 days ago"""
        if not self.is_logged_in: return
        
        conn = get_connection()
        # Find users followed more than 3 days ago who haven't been unfollowed
        three_days_ago = datetime.now() - timedelta(days=3)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT username FROM followers_tracking 
            WHERE account_id = ? AND is_unfollowed = 0 AND followed_date < ?
            LIMIT ?
        ''', (self.account_id, three_days_ago, self.settings.get('max_unfollows_per_day', 50)))
        
        users_to_unfollow = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        for username in users_to_unfollow:
            try:
                self.logger.info(f"Unfollowing {username}...")
                user_id = self.cl.user_id_from_username(username)
                self.cl.user_unfollow(user_id)
                self.daily_unfollows += 1
                
                # Update DB
                conn = get_connection()
                conn.execute("UPDATE followers_tracking SET is_unfollowed = 1, unfollowed_date = CURRENT_TIMESTAMP WHERE account_id = ? AND username = ?", 
                             (self.account_id, username))
                conn.commit()
                conn.close()
                self._log_action('unfollow', username)
                random_sleep(30, 60, "Post-unfollow delay")
                
            except Exception as e:
                self.logger.error(f"Failed to unfollow {username}: {e}")

