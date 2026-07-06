import json
import os

CONFIG_FILE = "config.json"

def ensure_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)

    print("\n=== FIRST RUN SETUP ===")
    bot_token = input("BOT TOKEN (from @BotFather): ").strip()
    api_id = int(input("API ID (from my.telegram.org): ").strip())
    api_hash = input("API HASH: ").strip()
    phone = input("Phone Number (+91...): ").strip()

    data = {
        "bot_token": bot_token,
        "api_id": api_id,
        "api_hash": api_hash,
        "phone": phone
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)

    print("Config saved. Proceeding to login...\n")
    return data