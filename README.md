# URL To Video Downloader Bot

Telegram bot to download videos and audio from supported websites using yt-dlp.

## Supported Sites
YouTube, Instagram, TikTok, Facebook, Twitter/X, Reddit, Pinterest, Threads, Vimeo, Twitch, Dailymotion, and all other yt-dlp supported websites.

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Install FFmpeg
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

### 3. Configure environment
Create a `.env` file in the project root:
```env
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token
MONGO_URI=mongodb://localhost:27017
OWNER_ID=your_user_id
```

### 4. Run the bot
```bash
python main.py
```

## Commands

### User Commands
- `/start` - Start the bot

### Owner Commands
- `/stats` - Bot statistics
- `/users` - Total users
- `/broadcast` - Broadcast message (reply to message)
- `/addsudo <user_id>` - Add sudo user
- `/remsudo <user_id>` - Remove sudo user
- `/sudolist` - List sudo users
- `/addchannel @channel` - Add force-sub channel
- `/delchannel @channel` - Remove channel
- `/listchannels` - List channels
- `/maintenance on|off` - Toggle maintenance

## Features
- Download video in multiple qualities (144p to 4K)
- Download audio as MP3
- Dynamic force-subscribe system
- Rate limiting (one download per user)
- Progress tracking
- 2GB file size limit
- Automatic cleanup
