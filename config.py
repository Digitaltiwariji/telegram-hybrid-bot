import json
import os

CONFIG_FILE = "config.json"

# Public Telegram Desktop credentials (no need to create your own)
DEFAULT_API_ID = 2040
DEFAULT_API_HASH = "b18441a1ff607e10a989891a5462e627"

def normalize_phone(p: str) -> str:
    p = p.strip().replace(" ", "").replace("-", "")
    if not p.startswith("+"):
        if p.startswith("91") and len(p) == 12:
            p = "+" + p
        elif len(p) == 10:
            p = "+91" + p
        else:
            p = "+" + p
    return p

def ensure_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)

    print("\n=== FIRST RUN SETUP (no API needed) ===")
    bot_token = input("BOT TOKEN (from @BotFather): ").strip()
    
    api_id_input = input("API ID (press ENTER to skip): ").strip()
    if api_id_input == "":
        api_id = DEFAULT_API_ID
        api_hash = DEFAULT_API_HASH
        print("→ Using public Telegram credentials")
    else:
        api_id = int(api_id_input)
        api_hash = input("API HASH: ").strip()

    phone_raw = input("Phone Number (+91...): ").strip()
    phone = normalize_phone(phone_raw)

    data = {
        "bot_token": bot_token,
        "api_id": api_id,
        "api_hash": api_hash,
        "phone": phone
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Config saved. Using phone {phone}\n")
    return data