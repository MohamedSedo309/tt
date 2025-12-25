import os
import ccxt
import time
from datetime import datetime

# --- 1. CONFIGURATION WITH BYPASS ENDPOINTS ---
API_KEY = os.getenv('BINANCE_API_KEY')
PRIVATE_KEY_CONTENT = os.getenv('BINANCE_PRIVATE_KEY', '').replace('\\n', '\n')

# Cycle through these if one is blocked
ENDPOINTS = [
    'https://api1.binance.com/api/v3',
    'https://api2.binance.com/api/v3',
    'https://api3.binance.com/api/v3',
    'https://data.binance.com/api/v3'
]

def create_exchange(endpoint):
    return ccxt.binance({
        'apiKey': API_KEY,
        'secret': PRIVATE_KEY_CONTENT,
        'enableRateLimit': True,
        'options': {'defaultType': 'spot', 'adjustForTimeDifference': True},
        'urls': {'api': {'public': endpoint, 'private': endpoint}}
    })

# Initialize with first endpoint
exchange = create_exchange(ENDPOINTS[0])

# --- 2. LIVE BOT LOGIC ---
def run_bot():
    global exchange
    endpoint_idx = 0
    print(f"🚀 BOT STARTING | Status: Bypassing Regional Blocks")

    while True:
        try:
            # Transparency: Fetch and show live Spot balance
            balance = exchange.fetch_balance()
            current_usdt = float(balance['total'].get('USDT', 0))
            
            print(f"\n[SCAN {datetime.now().strftime('%H:%M:%S')}] Spot Balance: ${current_usdt:.2f}")

            if current_usdt < 1.05:
                print(f"⚠️ Only ${current_usdt:.2f} seen. Move your 1.80 to SPOT WALLET.", end='\r')
                time.sleep(10); continue

            # Scanning logic... (Standard 24 paths)
            tickers = exchange.fetch_tickers()
            print(f"  > Successfully connected to {ENDPOINTS[endpoint_idx]}")
            time.sleep(2)

        except Exception as e:
            if "451" in str(e):
                endpoint_idx = (endpoint_idx + 1) % len(ENDPOINTS)
                new_url = ENDPOINTS[endpoint_idx]
                print(f"\n🛑 451 BLOCK on current server. Switching to {new_url}...")
                exchange = create_exchange(new_url)
                time.sleep(5)
            else:
                print(f"\nError: {e}")
                time.sleep(10)

if __name__ == "__main__":
    run_bot()
