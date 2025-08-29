import subprocess

def pip_upgrade():
    commands = [
        "pip install --upgrade kite-order",
        "pip install -U pip setuptools",
        "pip install --upgrade kiteconnect"
    ]
    for cmd in commands:
        print(f"Running: {cmd}")
        subprocess.run(cmd, shell=True, check=True)