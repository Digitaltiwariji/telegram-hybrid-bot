# Telegram Hybrid Search Bot (Termux)

Hybrid bot = BotFather bot (control panel) + Telethon user (searches your private channels/groups).

## Install on Termux
```bash
pkg update && pkg upgrade -y
pkg install python git -y
git clone https://github.com/your/repo telegram-hybrid-bot
cd telegram-hybrid-bot
pip install -r requirements.txt# telegram-hybrid-bot