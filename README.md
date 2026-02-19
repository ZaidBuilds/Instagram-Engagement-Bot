# Instagram Engagement Bot 🚀

An **AI-powered automation bot** that helps Instagram accounts grow organically by automating engagement activities across multiple accounts. The bot intelligently likes, comments, and follows accounts based on target hashtags and locations while maintaining natural behavior patterns.

---

## 🌟 Features

- **Multi-Account Management**: Manage multiple Instagram accounts simultaneously with independent settings and tracking
- **AI-Powered Comments**: Uses Groq AI API to generate human-like, contextually relevant comments (with fallback templates)
- **Smart Targeting**: Target users by:
  - Hashtags
  - Locations
  - Engagement metrics
- **Intelligent Automation**: 
  - Random delays and action patterns to mimic human behavior
  - Daily action limits to avoid Instagram rate limits
  - Automatic session management with persistent login
- **Real-Time Dashboard**: Streamlit-based interactive dashboard to:
  - Monitor engagement metrics in real-time
  - Track action history (likes, comments, follows)
  - Visualize growth trends
  - Manage account settings and targets
- **Proxy Support**: Built-in proxy rotation for enhanced security
- **Notification Alerts**: Telegram integration for real-time alerts and status updates
- **Database Tracking**: SQLite database to track all actions, targets, and account metrics
- **Docker Support**: Fully containerized deployment for easy setup across any environment

---

## 📋 Requirements

- Python 3.8+
- Instagram account credentials
- Groq API key (for AI comment generation)
- Telegram Bot token (optional, for notifications)
- Docker & Docker Compose (optional, for containerized deployment)

**Dependencies:**
- `instagrapi` - Instagram API client
- `streamlit` - Dashboard framework
- `groq` - AI comment generation
- `pandas` - Data analysis
- `schedule` - Job scheduling
- `plotly` - Interactive visualizations
- `python-dotenv` - Environment variable management
- `pillow` - Image processing
- `watchdog` - File system monitoring

---

## 🚀 Installation & Setup

### 1. **Prerequisites**

Make sure you have:
- Python 3.8 or higher
- pip (Python package manager)
- Git (to clone the repository)

### 2. **Clone the Repository**

```bash
git clone <repository-url>
cd "Instagram engagement bot"
```

### 3. **Install Dependencies**

```bash
pip install -r requirements.txt
```

**Note:** If you encounter issues with C++ build tools or Rust compilation on Windows, refer to the [TROUBLESHOOTING.md](TROUBLESHOOTING.md) file for detailed solutions.

### 4. **Environment Configuration**

Create a `.env` file in the project root with your credentials:

```env
GROQ_API_KEY=your_groq_api_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here
```

**Getting Your API Keys:**
- **Groq API Key**: Sign up at [console.groq.com](https://console.groq.com) and generate an API key
- **Telegram Bot Token**: Create a bot with [@BotFather](https://t.me/botfather) on Telegram

### 5. **Initialize the Database**

The database will be automatically initialized on first run, but you can manually set it up:

```bash
python check_setup.py
```

---

## 💻 Quick Start

### Option A: Windows Batch Scripts

Simply run the batch script:

```bash
start_bot.bat
```

This will start the bot with all configured accounts.

### Option B: Direct Python Execution

```bash
python run_bot.py
```

### Option C: Docker (Recommended)

Ensure Docker Desktop is running, then:

```bash
docker-compose up --build
```

---

## 📊 Dashboard

Access the interactive dashboard to monitor and manage your bot:

```bash
streamlit run dashboard/app.py
```

The dashboard provides:
- **Real-time Metrics**: Live engagement statistics for each account
- **Action History**: Detailed logs of all bot activities
- **Growth Charts**: Visual trends and analytics
- **Settings Management**: Configure bot behavior and account limits
- **Target Management**: Add/remove/modify hashtags and location targets

---

## 🛠️ Project Structure

```
├── run_bot.py              # Main bot runner (entry point)
├── check_setup.py          # System setup verification
├── requirements.txt        # Python dependencies
├── docker-compose.yml      # Docker composition file
├── Dockerfile             # Docker image definition
├── setup_env.bat          # Windows environment setup
├── start_bot.bat          # Windows bot startup script
├── start_dashboard.bat    # Windows dashboard startup script
│
├── src/                   # Core bot logic
│   ├── bot_engine.py      # Main Instagram bot automation logic
│   ├── ai_generator.py    # AI comment generation using Groq API
│   ├── database.py        # SQLite database operations
│   ├── notifications.py   # Telegram alert system
│   └── utils.py           # Utility functions (logging, sleep, etc.)
│
├── dashboard/             # Streamlit web interface
│   └── app.py            # Dashboard application
│
├── database/             # SQLite database files (auto-created)
│   └── bot.db
│
├── logs/                 # Bot activity logs
│   └── *.log
│
├── sessions/             # Instagram session files (auto-created)
│   └── username.json
│
├── TROUBLESHOOTING.md    # Common issues and solutions
└── README.md            # This file
```

---

## ⚙️ Configuration

### Database Setup

The bot uses SQLite3 with the following main tables:

- **accounts**: Instagram account credentials and settings
- **targets**: Hashtags, locations, and user targets
- **settings**: Per-account configuration (action limits, delays)
- **actions**: Log of all activities (likes, comments, follows)

### Account Management

Add accounts via the dashboard or by inserting directly into the database:

```sql
INSERT INTO accounts (username, password, proxy, active) 
VALUES ('your_username', 'your_password', NULL, 1);
```

### Target Configuration

Configure targets (hashtags/locations) from the dashboard or database:

```sql
INSERT INTO targets (account_id, target_type, target_value, active) 
VALUES (1, 'hashtag', 'instagram', 'active');
```

### Bot Settings

Customize bot behavior per account:

- **Daily Limits**: Max likes, comments, follows per day
- **Random Delays**: Min/max seconds between actions to appear human
- **Comment Generation**: Enable/disable AI comments
- **Proxy Settings**: Rotate proxy for security

---

## 📱 Features in Detail

### AI Comment Generation

The bot generates contextually relevant comments using Groq's Claude model:
- Analyzes post captions
- Generates human-like responses
- Falls back to templates if API is unavailable
- Configurable per account

### Action Limits

Prevent Instagram rate limiting with configurable daily limits:
- Default: 50 likes, 10 comments, 5 follows per day per account
- Automatically resets at midnight
- Tracked in real-time via database

### Session Management

- Persistent login sessions stored as JSON files
- Automatic re-login on session expiration
- Proxy rotation for enhanced security

### Logging

All activities are logged to:
- Console output (INFO level)
- Log files in `logs/` directory
- Database for historical analysis

---

## 🚨 Troubleshooting

If you encounter issues during installation or runtime, please refer to [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed solutions.

**Common Issues:**
- C++ Build Tools missing (Windows)
- MoviePy compilation errors
- Rust compiler requirements
- Docker dependency issues

---

## 🐳 Docker Deployment

### Building the Docker Image

```bash
docker-compose build
```

### Running with Docker

```bash
docker-compose up
```

### Accessing Services

- **Bot**: Runs in background as service
- **Dashboard**: Access via `http://localhost:8501`
- **Database**: SQLite database persisted in volume

### Docker Configuration

Edit `docker-compose.yml` to customize:
- Port mappings
- Volume mounts
- Environment variables
- Resource limits

---

## 📝 Usage Examples

### Basic Bot Operation

```python
from src.bot_engine import InstagramBot
from src.database import get_connection

# Create bot instance
bot = InstagramBot(
    account_id=1,
    username="your_username",
    password="your_password",
    proxy=None,  # Optional proxy
    settings={'daily_likes': 50, 'daily_comments': 10}
)

# Login to Instagram
if bot.login():
    print("Successfully logged in!")
    # Bot will now automatically process targets
```

### Running Multiple Accounts

The main `run_bot.py` automatically handles multiple accounts:
- Reads all active accounts from database
- Creates separate thread for each account
- Independent action tracking per account
- Scheduled task execution every hour

---

## 🔐 Security & Safety

### Best Practices

1. **Use Environment Variables**: Never hardcode credentials or API keys
2. **Proxy Usage**: Recommended for enhanced account security
3. **Rate Limiting**: Bot includes default limits to avoid Instagram detection
4. **Session Management**: Sessions are stored locally and encrypted
5. **Account Safety**:
   - Start with conservative action limits
   - Gradually increase as account ages
   - Monitor for signs of account restriction
   - Use dedicated proxy IPs if possible

### Instagram Terms of Service

⚠️ **Note**: This bot automates Instagram engagement. While it attempts to mimic human behavior, use responsibly and in accordance with Instagram's Terms of Service. The authors are not responsible for account suspension or violations.

---

## 📊 Database Schema

### Accounts Table
```sql
CREATE TABLE accounts (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password TEXT,
    proxy TEXT,
    active INTEGER,
    created_at TIMESTAMP
);
```

### Targets Table
```sql
CREATE TABLE targets (
    id INTEGER PRIMARY KEY,
    account_id INTEGER,
    target_type TEXT,           -- 'hashtag', 'location', 'user'
    target_value TEXT,
    status TEXT,                -- 'active', 'inactive'
    created_at TIMESTAMP
);
```

### Actions Table
```sql
CREATE TABLE actions (
    id INTEGER PRIMARY KEY,
    account_id INTEGER,
    action_type TEXT,           -- 'like', 'comment', 'follow', 'unfollow'
    target_user TEXT,
    created_at TIMESTAMP
);
```

---

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is provided as-is for educational purposes. Users are responsible for ensuring compliance with Instagram's Terms of Service and local laws.

---

## 📞 Support

For issues, questions, or suggestions:
- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) first
- Review the code comments in `src/` directory
- Check dashboard error logs

---

## 🔄 Version History

**v1.0.0** - Initial Release
- Multi-account support
- AI-powered comment generation
- Real-time dashboard
- Docker deployment
- Telegram notifications
- Comprehensive logging

---

**Happy Growing! 🌱**

*Remember: Quality over quantity. Focus on genuine engagement and account growth over time.*
