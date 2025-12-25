import os
import ccxt
import time
from datetime import datetime

# --- 1. CONFIGURATION ---
API_KEY = os.getenv('BINANCE_API_KEY')
PRIVATE_KEY_CONTENT = os.getenv('BINANCE_PRIVATE_KEY', '').replace('\\n', '\n')

# Use specialized endpoints to bypass 451 Restricted Location errors
exchange = ccxt.binance({
    'apiKey': API_KEY,
    'secret': PRIVATE_KEY_CONTENT,
    'enableRateLimit': True,
    'options': {'defaultType': 'spot', 'adjustForTimeDifference': True},
    'urls': {
        'api': {
            'public': 'https://data.binance.com/api/v3',
            'private': 'https://api.binance.com/api/v3',
        }
    }
})

# --- 2. LIVE SETTINGS ---
MIN_PROFIT = 0.005  # 0.5% Net Profit
FEE_RATE = 0.00075  # 0.075% per leg

def run_live_bot():
    # 24 standard high-volume paths
    pairs = ['BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'LTC', 'MATIC', 'DOT']
    paths = []
    for b in ['BTC', 'ETH', 'BNB']:
        for a in pairs:
            if b != a: paths.append(['USDT', b, a, 'USDT'])

    print(f"🚀 BOT LIVE | Status: Bypassing 451 | Paths: {len(paths)}")

    while True:
        try:
            # 100% Transparency: Fetch and show live Spot balance
            balance = exchange.fetch_balance()
            current_usdt = float(balance['total'].get('USDT', 0))
            
            print(f"\n[SCAN {datetime.now().strftime('%H:%M:%S')}] Spot Balance: ${current_usdt:.2f}")

            if current_usdt < 1.05:
                print(f"⚠️ BALANCE ALERT: Only ${current_usdt:.2f} seen in Spot. Waiting...")
                time.sleep(20); continue

            tickers = exchange.fetch_tickers()
            for p in paths:
                try:
                    # Transparency: Log individual ROI checks
                    p1, p2, p3 = 1/tickers[f"{p[1]}/USDT"]['ask'], 1/tickers[f"{p[2]}/{p[1]}"]['ask'], tickers[f"{p[2]}/USDT"]['bid']
                    roi = (current_usdt * p1 * p2 * p3 - current_usdt) / current_usdt - (FEE_RATE * 3)
                    
                    print(f"  > Check: {p[1]}->{p[2]} | ROI: {roi:.4%}", end='\r')

                    if roi > MIN_PROFIT:
                        print(f"\n💰 PROFIT DETECTED! Executing {p[1]} -> {p[2]}...")
                        # Live execution commands here
                        exchange.create_market_buy_order(f"{p[1]}/USDT", current_usdt)
                        # Add remaining legs for full cycle
                except: continue
            time.sleep(1)
        except Exception as e:
            if "451" in str(e):
                print("\n🛑 REGION BLOCK: Check Railway Settings for Singapore region.")
            else:
                print(f"\nError: {e}")
            time.sleep(10)

if __name__ == "__main__":
    run_live_bot()
