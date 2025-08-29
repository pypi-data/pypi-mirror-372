# dependency_check.py
import sys
import subprocess

def pip_install():
    try:
        from kiteconnect import KiteConnect
        from kite_bracket_orders import BracketOrderPlacer
        print("✅ All required packages are installed. Proceeding...")
    except ImportError:
        print("⚠️ Required packages are missing. Installing now...")
        commands = [
            [sys.executable, "-m", "pip", "install", "--upgrade", "kite-order"],
            [sys.executable, "-m", "pip", "install", "--upgrade", "pip", "setuptools"],
            [sys.executable, "-m", "pip", "install", "--upgrade", "kiteconnect"]
        ]
        try:
            for cmd in commands:
                print(f"Running: {' '.join(cmd)}")
                subprocess.check_call(cmd)
            print("\n✅ Dependencies installed successfully. Restart the script to continue.")
            sys.exit()
        except Exception as e:
            print("\n❌ ERROR: Installation failed.")
            print(f"💡 Install manually:\n  {sys.executable} -m pip install --upgrade kite-order\n  {sys.executable} -m pip install --upgrade pip setuptools\n  {sys.executable} -m pip install --upgrade kiteconnect")
            print(f"📄 Details: {e}")
            sys.exit(1)

if __name__ == "__main__":
    pip_install()
