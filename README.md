# Instagram Engagement Bot - Commercial Edition

## Project Overview
A powerful, multi-account Instagram automation tool designed to grow accounts organically using smart targeting and safe automation practices.

## Key Features
- **Multi-Account Manager**: Run 10-15+ accounts simultaneously.
- **Smart Targeting**: Interact with users via Hashtags or Locations.
- **Safety First**: Random delays, limits, and verified/business account filtering.
- **AI Comments**: Generates context-aware comments using Groq AI.
- **Web Dashboard**: Real-time stats, charts, and settings via Streamlit.
- **Telegram Alerts**: Get notified of logins or errors instantly.
- **Dockerized**: Easy deployment on any VPS.

## Local Setup (Windows)
1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Setup Environment**:
   - Rename `.env.example` to `.env`
   - Add your `GROQ_API_KEY` and Telegram details.
3. **Initialize Database**:
   ```bash
   python src/database.py
   ```
4. **Run Dashboard**:
   - Double click `start_dashboard.bat` or run: `streamlit run dashboard/app.py`
5. **Start Bot**:
   - Double click `start_bot.bat` or run: `python run_bot.py`

## VPS Deployment (Linux/DigitalOcean)
The bot is Docker-ready for easy deployment on a $6/mo VPS.

1. **Install Docker & Docker Compose**:
   ```bash
   sudo apt update
   sudo apt install docker.io docker-compose -y
   ```
2. **Upload Files**:
   Copy all project files to the VPS (e.g., using SCP or Git).
3. **Configure**:
   Create and edit `.env` file with your keys.
4. **Deploy**:
   ```bash
   docker-compose up -d --build
   ```
   - Dashboard will be available at `http://YOUR_VPS_IP:8501`
   - Bots will run in the background with `restart: always` policy.

## Usage Guide
1. **Open Dashboard**.
2. **Add Account**: Go to "Accounts" page, enter credentials and Proxy (optional but recommended for multiple accounts).
3. **Add Targets**: Go to "Targets" page. Add hashtags (e.g., `fitness`) or locations (e.g., `London`).
4. **Configure Settings**: Go to "Settings" to adjust daily limits (Safe defaults are pre-set).
5. **Monitor**: Watch the "Home" page for live stats and charts.

## Safety & Limits
- Default safe limits: ~150 likes, ~40 comments, ~50 follows per day.
- **Warm-up**: For new accounts, lower these limits in Settings to ~50% for the first week.
- **Proxies**: Always use 1 proxy per account if running more than 2-3 accounts from one IP.

## Troubleshooting
- **Login Block**: If login fails, check if the account requires a code (2FA). The bot currently alerts you via Telegram. You may need to login manually on a phone with the proxy IP implementation to clear the challenge (or use `instagrapi` manual session handling).
- **Rate Limits**: If "Action Blocked", the bot will sleep for a while. Increase delays in `src/utils.py` or reduce daily limits.
