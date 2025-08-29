import logging
import json
import os
import sys
import subprocess

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# --- Configuration ---
CONFIG_DIR = 'credentials'  # Folder for config files
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')  # Full path to config.json

def read_config():
    """Read config, create if missing API_KEY/SECRET"""
    if not os.path.exists(CONFIG_FILE):
        logging.warning(f"⚠️  '{CONFIG_FILE}' not found. Creating new config file...")
        return {}

    with open(CONFIG_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            logging.error("❌ Failed to parse JSON. Creating empty config.")
            return {}

def write_config(config_data):
    """Writes updated config to file, creates directory if missing"""
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)  # Create credentials folder if it doesn't exist
        logging.info(f"📁 Created '{CONFIG_DIR}' folder.")

    with open(CONFIG_FILE, 'w') as f:
        json.dump(config_data, f, indent=4)
    logging.info(f"💾 Configuration saved to '{CONFIG_FILE}'")

def prompt_credentials():
    """Prompt user for API key/secret"""
    print("🔑 Enter your Kite API credentials:")
    api_key = input("👉 API_KEY: ").strip()
    api_secret = input("🔐 API_SECRET: ").strip()
    return api_key, api_secret

def main():
    # --- Dependency Check ---
    try:
        from kiteconnect import KiteConnect
    except ImportError:
        print("⚠️  The 'kiteconnect' library is not installed.")
        print("🔄 Attempting to install it now...")
        try:
            print("⬆️  Upgrading pip and setuptools...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "setuptools"])
            print("📦 Installing kiteconnect...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "kiteconnect"])
            print("\n✅ Dependencies installed successfully.")
            print("🔁 Please restart the script to continue.")
        except Exception as e:
            print("\n❌ ERROR: Failed to install dependencies.")
            print(f"💡 Install manually:\n  {sys.executable} -m pip install --upgrade pip setuptools\n  {sys.executable} -m pip install --upgrade kiteconnect")
            print(f"📄 Details: {e}")
        sys.exit()

    config = read_config()

    # Ensure KITE section and credentials exist
    if 'KITE' not in config:
        config['KITE'] = {}

    if not config['KITE'].get('API_KEY') or not config['KITE'].get('API_SECRET'):
        logging.info("📝 API_KEY and/or API_SECRET not found in config.")
        api_key, api_secret = prompt_credentials()
        config['KITE']['API_KEY'] = api_key
        config['KITE']['API_SECRET'] = api_secret
        write_config(config)

    api_key = config['KITE']['API_KEY']
    api_secret = config['KITE']['API_SECRET']
    access_token = config.get('SESSION', {}).get('ACCESS_TOKEN')

    kite = KiteConnect(api_key=api_key)

    # --- Step 1: Try existing access token ---
    if access_token:
        logging.info("🔑 Found an existing access token. Attempting login...")
        try:
            kite.set_access_token(access_token)
            profile = kite.profile()
            logging.info(f"✅ Logged in as:🧔 {profile.get('user_name')} ({profile.get('user_id')})")
            return
        except Exception as e:
            logging.warning(f"⚠️  Token failed: {e}. Trying fresh login...")

    # --- Step 2: Fresh login flow ---
    logging.info("🔐 Generating new session...")

    login_url = kite.login_url()
    print("\n" + "="*80)
    print("🌐 Please login using the following URL:")
    print(login_url)
    print("="*80 + "\n")

    request_token = input("📥 After login, paste the 'request_token' from URL: ")
    if "request_token=" in request_token:
        request_token = request_token.split("request_token=")[1].split("&")[0]

    try:
        data = kite.generate_session(request_token, api_secret=api_secret)
        new_access_token = data["access_token"]
        logging.info("🔓 Session generated!")

        # Save token
        config.setdefault('SESSION', {})['ACCESS_TOKEN'] = new_access_token
        write_config(config)

        kite.set_access_token(new_access_token)
        profile = kite.profile()
        logging.info(f"🎉 Successfully logged in! Welcome,🧔 {profile.get('user_name')} ({profile.get('user_id')})")

    except Exception as e:
        logging.error(f"❌ Authentication failed: {e}")
