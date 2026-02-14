import streamlit as st
import pandas as pd
import sqlite3
import os
import sys
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Add project root to path so we can import src
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__))))

from src.database import get_connection

st.set_page_config(
    page_title="Instagram Growth Bot",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #333;
        margin-bottom: 20px;
    }
    .metric-value {
        font-size: 2em;
        font-weight: bold;
        color: #00CC96;
    }
    .metric-label {
        font-size: 1.1em;
        color: #AAAAAA;
    }
</style>
""", unsafe_allow_html=True)

def get_db_connection():
    return get_connection()

def show_home():
    st.title("🚀 Dashboard Overview")
    
    conn = get_db_connection()
    
    # Overview Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_accounts = conn.execute("SELECT count(*) FROM accounts").fetchone()[0]
    active_accounts = conn.execute("SELECT count(*) FROM accounts WHERE status='active'").fetchone()[0]
    total_actions = conn.execute("SELECT count(*) FROM actions_log").fetchone()[0]
    todays_actions = conn.execute("SELECT count(*) FROM actions_log WHERE date(timestamp) = date('now')").fetchone()[0]
    
    with col1:
        st.metric("Total Accounts", total_accounts)
    with col2:
        st.metric("Active Accounts", active_accounts)
    with col3:
        st.metric("Total Actions", total_actions)
    with col4:
        st.metric("Actions Today", todays_actions)
    
    # 2. Daily Activity Chart
    st.markdown("### 📈 Activity Trends")
    
    activity_data = pd.read_sql("""
        SELECT date(timestamp) as date, action_type, count(*) as count 
        FROM actions_log 
        GROUP BY date(timestamp), action_type
        ORDER BY date(timestamp) DESC LIMIT 100
    """, conn)
    
    if not activity_data.empty:
        fig = px.bar(activity_data, x="date", y="count", color="action_type", title="Daily Actions by Type")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No activity data to show yet.")

    col_l, col_r = st.columns(2)
    
    with col_l:
        st.markdown("### 📊 Engagement By Account")
        account_stats = pd.read_sql("""
            SELECT a.username, count(l.id) as total_actions 
            FROM accounts a 
            LEFT JOIN actions_log l ON a.id = l.account_id 
            GROUP BY a.username
        """, conn)
        if not account_stats.empty:
            fig2 = px.pie(account_stats, values='total_actions', names='username', title='Actions Distribution')
            st.plotly_chart(fig2, use_container_width=True)
            
    with col_r:
        st.markdown("### 📋 Recent Logs")
        logs = pd.read_sql("SELECT timestamp, action_type, target_user, details FROM actions_log ORDER BY timestamp DESC LIMIT 10", conn)
        st.dataframe(logs, use_container_width=True)

    conn.close()

def show_accounts():
    st.title("👥 Account Management")
    
    with st.expander("➕ Add New Account"):
        with st.form("add_account"):
            col1, col2 = st.columns(2)
            username = col1.text_input("Username")
            password = col2.text_input("Password", type="password")
            proxy = st.text_input("Proxy (http://user:pass@ip:port)")
            submitted = st.form_submit_button("Add Account")
            
            if submitted and username and password:
                conn = get_db_connection()
                try:
                    conn.execute("INSERT INTO accounts (username, password, proxy) VALUES (?, ?, ?)", 
                                 (username, password, proxy))
                    # Init settings for this account
                    account_id = conn.execute("SELECT seq FROM sqlite_sequence WHERE name='accounts'").fetchone()[0]
                    conn.execute("INSERT INTO settings (account_id) VALUES (?)", (account_id,))
                    conn.commit()
                    st.success(f"Account {username} added!")
                except sqlite3.IntegrityError:
                    st.error("Username already exists!")
                except Exception as e:
                    st.error(f"Error: {e}")
                finally:
                    conn.close()

    st.markdown("### accounts")
    conn = get_db_connection()
    accounts = pd.read_sql("SELECT id, username, status, proxy, last_action_time, created_at FROM accounts", conn)
    
    # Enhanced display with status colors
    def color_status(val):
        color = 'green' if val == 'active' else 'red'
        return f'color: {color}'

    st.dataframe(accounts.style.applymap(color_status, subset=['status']), use_container_width=True)
    conn.close()

def show_targets():
    st.title("🎯 Targets")
    
    conn = get_db_connection()
    accounts = pd.read_sql("SELECT id, username FROM accounts", conn)
    
    if accounts.empty:
        st.warning("Please add an account first.")
        return
        
    option_map = {row['username']: row['id'] for index, row in accounts.iterrows()}
    col1, col2 = st.columns([1, 2])
    
    with col1:
        selected_account = st.selectbox("Select Account", list(option_map.keys()))
        selected_account_id = option_map[selected_account]
    
    with col2:
        with st.form("add_target"):
            col_a, col_b = st.columns(2)
            target_type = col_a.selectbox("Target Type", ["hashtag", "location", "user"])
            target_value = col_b.text_input("Target Value")
            submitted = st.form_submit_button("Add Target")
            
            if submitted and target_value:
                conn.execute("INSERT INTO targets (account_id, target_type, target_value) VALUES (?, ?, ?)",
                             (selected_account_id, target_type, target_value))
                conn.commit()
                st.success(f"Added {target_type}: {target_value}")
                
    st.markdown(f"### Current Targets for {selected_account}")
    targets = pd.read_sql(f"SELECT id, target_type, target_value, status FROM targets WHERE account_id = {selected_account_id}", conn)
    
    # Simple table with delete option (simulated by checking IDs to delete in a real app, here read-only for now)
    st.dataframe(targets, use_container_width=True)
    conn.close()

def show_settings():
    st.title("⚙️ Bot Settings")
    
    conn = get_db_connection()
    accounts = pd.read_sql("SELECT id, username FROM accounts", conn)
    
    if accounts.empty:
        st.warning("No accounts found.")
        return
        
    option_map = {row['username']: row['id'] for index, row in accounts.iterrows()}
    selected_account = st.selectbox("Select Account to Configure", list(option_map.keys()))
    selected_account_id = option_map[selected_account]
    
    # Fetch current settings
    current_settings = pd.read_sql(f"SELECT * FROM settings WHERE account_id = {selected_account_id}", conn)
    
    if current_settings.empty:
        # Should not happen if logic is correct, but safe fallback
        conn.execute("INSERT INTO settings (account_id) VALUES (?)", (selected_account_id,))
        conn.commit()
        current_settings = pd.read_sql(f"SELECT * FROM settings WHERE account_id = {selected_account_id}", conn)
        
    cs = current_settings.iloc[0]
    
    with st.form("update_settings"):
        st.subheader(f"Daily Limits for {selected_account}")
        col1, col2 = st.columns(2)
        max_likes = col1.number_input("Max Likes/Day", value=cs['max_likes_per_day'])
        max_comments = col2.number_input("Max Comments/Day", value=cs['max_comments_per_day'])
        
        col3, col4 = st.columns(2)
        max_follows = col3.number_input("Max Follows/Day", value=cs['max_follows_per_day'])
        max_unfollows = col4.number_input("Max Unfollows/Day", value=cs['max_unfollows_per_day'])
        
        st.subheader("Scheduling & Helpers")
        col5, col6 = st.columns(2)
        active_start = col5.slider("Start Hour (24h)", 0, 23, int(cs['active_hours_start']))
        active_end = col6.slider("End Hour (24h)", 0, 23, int(cs['active_hours_end']))
        
        use_ai = st.checkbox("Use AI for Comments", value=bool(cs['use_ai_comments']))
        
        submitted = st.form_submit_button("Save Settings")
        
        if submitted:
            conn.execute("""
                UPDATE settings SET 
                max_likes_per_day=?, max_comments_per_day=?, max_follows_per_day=?, max_unfollows_per_day=?,
                active_hours_start=?, active_hours_end=?, use_ai_comments=?
                WHERE account_id=?
            """, (max_likes, max_comments, max_follows, max_unfollows, active_start, active_end, use_ai, selected_account_id))
            conn.commit()
            st.success("Settings updated successfully!")
            
    conn.close()

def show_billing():
    st.title("💰 Client Billing Management")
    
    conn = get_db_connection()
    
    # 1. Billing Summary
    total_mrr = conn.execute("SELECT sum(monthly_fee) FROM client_billing WHERE payment_status != 'overdue'").fetchone()[0] or 0
    pending_payments = conn.execute("SELECT count(*) FROM client_billing WHERE payment_status = 'pending'").fetchone()[0]
    
    m1, m2 = st.columns(2)
    m1.metric("Est. Monthly Revenue (MRR)", f"${total_mrr:.2f}")
    m2.metric("Pending Payments (Clients)", pending_payments)
    
    # 2. Manage Client Billing
    st.markdown("### 📝 Manage Subscription")
    accounts = pd.read_sql("SELECT id, username FROM accounts", conn)
    
    if accounts.empty:
        st.warning("No accounts found.")
        conn.close()
        return

    option_map = {row['username']: row['id'] for index, row in accounts.iterrows()}
    
    c1, c2 = st.columns([1, 2])
    with c1:
        selected_account = st.selectbox("Select Client Account", list(option_map.keys()))
        selected_account_id = option_map[selected_account]
        
    # Fetch existing billing info
    existing = pd.read_sql(f"SELECT * FROM client_billing WHERE account_id = {selected_account_id}", conn)
    
    with c2:
        with st.form("billing_form"):
            st.subheader(f"Billing Details for {selected_account}")
            
            # Defaults
            e_name = existing.iloc[0]['client_name'] if not existing.empty else ""
            e_email = existing.iloc[0]['contact_email'] if not existing.empty else ""
            e_fee = existing.iloc[0]['monthly_fee'] if not existing.empty else 24.0
            e_due = pd.to_datetime(existing.iloc[0]['next_payment_due']).date() if not existing.empty and existing.iloc[0]['next_payment_due'] else datetime.now().date()
            e_status = existing.iloc[0]['payment_status'] if not existing.empty else "pending"
            
            c_name = st.text_input("Client Name", value=e_name)
            c_email = st.text_input("Contact Email", value=e_email)
            c_fee = st.number_input("Monthly Fee ($)", value=float(e_fee))
            c_due = st.date_input("Next Payment Due", value=e_due)
            c_status = st.selectbox("Payment Status", ["paid", "pending", "overdue"], index=["paid", "pending", "overdue"].index(e_status))
            
            submitted = st.form_submit_button("Save Billing Info")
            
            if submitted:
                # Upsert
                check = conn.execute("SELECT id FROM client_billing WHERE account_id = ?", (selected_account_id,)).fetchone()
                if check:
                    conn.execute("""
                        UPDATE client_billing 
                        SET client_name=?, contact_email=?, monthly_fee=?, next_payment_due=?, payment_status=?
                        WHERE account_id=?
                    """, (c_name, c_email, c_fee, c_due, c_status, selected_account_id))
                else:
                    conn.execute("""
                        INSERT INTO client_billing (account_id, client_name, contact_email, monthly_fee, next_payment_due, payment_status, start_date)
                        VALUES (?, ?, ?, ?, ?, ?, CURRENT_DATE)
                    """, (selected_account_id, c_name, c_email, c_fee, c_due, c_status))
                conn.commit()
                st.success("Billing info updated!")
                st.experimental_rerun()

    # 3. Billing Table
    st.markdown("### 🧾 All Subscriptions")
    billing_df = pd.read_sql("""
        SELECT a.username, b.client_name, b.monthly_fee, b.next_payment_due, b.payment_status 
        FROM accounts a 
        LEFT JOIN client_billing b ON a.id = b.account_id
    """, conn)
    
    def status_color(val):
        if val == 'paid': return 'color: lightgreen'
        if val == 'overdue': return 'color: red'
        return 'color: orange'

    st.dataframe(billing_df.style.applymap(status_color, subset=['payment_status']), use_container_width=True)
    conn.close()

def main():
    st.sidebar.title("IG Growth Bot 🤖")
    
    # Sidebar stats
    conn = get_db_connection()
    try:
        active = conn.execute("SELECT count(*) FROM accounts WHERE status='active'").fetchone()[0]
        st.sidebar.markdown(f"**Active Bots:** {active}")
    except:
        pass
    conn.close()
    
    page = st.sidebar.radio("Menu", ["Home", "Accounts", "Targets", "Settings", "Billing", "Logs"])
    
    if page == "Home":
        show_home()
    elif page == "Accounts":
        show_accounts()
    elif page == "Targets":
        show_targets()
    elif page == "Settings":
        show_settings()
    elif page == "Billing":
        show_billing()
    elif page == "Logs":
        st.title("📜 Logs")
        conn = get_db_connection()
        logs = pd.read_sql("SELECT * FROM actions_log ORDER BY id DESC LIMIT 500", conn)
        st.dataframe(logs, use_container_width=True)
        conn.close()

if __name__ == "__main__":
    main()
