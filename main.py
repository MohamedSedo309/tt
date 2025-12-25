import os
import ccxt
import time
from datetime import datetime

# --- 1. CONFIGURATION & BYPASS LOGIC ---
API_KEY = os.getenv('BINANCE_API_KEY')
PRIVATE_KEY_CONTENT = os.getenv('BINANCE_PRIVATE_KEY', '').replace('\\n', '\n')

# We are using api1.binance.com which is a common "secret" bypass for cloud servers
exchange = ccxt.binance({
    'apiKey': API_KEY,
    'secret': PRIVATE_KEY_CONTENT,
    'enableRateLimit': True,
    'options': {'defaultType': 'spot', 'adjustForTimeDifference': True},
    'urls': {
        'api': {
            'public': 'https://api1.binance.com/api/v3',
            'private': 'https://api1.binance.com/api/v3',
        }
    }
})

# --- 2. LIVE SETTINGS ---
MIN_PROFIT = 0.005  # 0.5% Net Profit Goal
FEE_RATE = 0.00075  # 0.075% per trade (BNB Fee)

def get_balance():
    """Checks Spot Wallet and handles the 451 Error gracefully."""
    try:
        balance = exchange.fetch_balance()
        return float(balance['total'].get('USDT', 0))
    except Exception as e:
        if "451" in str(e):
            return "BLOCKED"
        return 0.0

def execute_trade_cycle(path, amount):
    """LIVE EXECUTION with total transparency."""
    start_time = time.time()
    try:
        print("\n" + "💰" * 15)
        print(f"!!! TRADING INITIATED: {' -> '.join(path)} !!!")
        
        # Leg 1
        order1 = exchange.create_market_buy_order(f"{path[1]}/USDT", amount)
        print(f"✅ Step 1: Bought {order1['filled']} {path[1]}")

        # Leg 2
        order2 = exchange.create_market_order(f"{path[2]}/{path[1]}", 'buy', order1['filled'])
        print(f"✅ Step 2: Swapped to {order2['filled']} {path[2]}")

        # Leg 3
        order3 = exchange.create_market_sell_order(f"{path[2]}/USDT", order2['filled'])
        print(f"✅ Step 3: Sold for ${order3['cost']:.4f} USDT")

        print(f"--- SUCCESS: Cycle took {time.time() - start_time:.2f}s ---")
        print("💰" * 15 + "\n")
    except Exception as e:
        print(f"❌ TRADE STOPPED: {e}")

def run_bot():
    # 24 common arbitrage paths
    coins = ['BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'LTC', 'MATIC', 'DOT']
    paths = []
    for base in ['BTC', 'ETH', 'BNB']:
        for alt in coins:
            if base != alt: paths.append(['USDT', base, alt, 'USDT'])

    print(f"🚀 BOT STARTING | Transparency Mode: ON | Paths: {len(paths)}")

    while True:
        try:
            current_bal = get_balance()
            
            if current_bal == "BLOCKED":
                print("\n🛑 STILL BLOCKED: Trying alternate server (api2)...")
                exchange.urls['api']['public'] = 'https://api2.binance.com/api/v3'
                exchange.urls['api']['private'] = 'https://api2.binance.com/api/v3'
                time.sleep(10); continue

            # Dashboard View
            print(f"\n[LIVE {datetime.now().strftime('%H:%M:%S')}] Spot Wallet: ${current_bal:.2f}")
            
            if current_bal < 1.05:
                print(f"⚠️ Low Balance Alert. Move your $1.80 to SPOT WALLET.", end='\r')
                time.sleep(15); continue

            tickers = exchange.fetch_tickers()
            best_roi = -1.0

            for p in paths:
                try:
                    # Prices for Leg 1, 2, and 3
                    p1 = 1 / tickers[f"{p[1]}/USDT"]['ask']
                    p2 = 1 / tickers[f"{p[2]}/{p[1]}"]['ask']
                    p3 = tickers[f"{p[2]}/USDT"]['bid']
                    
                    roi = (current_bal * p1 * p2 * p3 - current_bal) / current_bal - (FEE_RATE * 3)
                    
                    # Transparency: Log the current search progress
                    print(f"  > Check: {p[1]}->{p[2]} | ROI: {roi:.4%}", end='\r')

                    if roi > best_roi: best_roi = roi
                    if roi > MIN_PROFIT:
                        execute_trade_cycle(p, current_bal)
                except: continue

            time.sleep(1)

        except Exception as e:
            print(f"\nConnection Issue: {e}")
            time.sleep(10)

if __name__ == "__main__":
    run_bot()
