# filename: install_yfinance.py
import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    import yfinance
    print("yfinance is already installed.")
except ImportError:
    print("Installing yfinance...")
    install("yfinance")
    print("yfinance installed successfully.")