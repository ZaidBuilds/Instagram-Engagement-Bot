FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (needed for some python packages like pillow/sqlite)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc6-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create volume for persistent data
VOLUME /app/database
VOLUME /app/sessions
VOLUME /app/logs

# Command to run the bot runner
CMD ["python", "run_bot.py"]
