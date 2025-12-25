import os
import ccxt
import time
from datetime import datetime

# --- 1. CONFIGURATION ---
API_KEY = os.getenv('BINANCE_API_KEY')
PRIVATE_KEY_CONTENT = os.getenv('BINANCE_PRIVATE_KEY', '').replace('\\n', '\n')

exchange = ccxt.binance({
    'apiKey': API_KEY,
    'secret': PRIVATE_KEY_CONTENT,
    'enableRateLimit': True,
    'options': {'defaultType': 'spot', 'adjustForTimeDifference': True}
})

# Singapore Safe Endpoints
exchange.urls['api']['public'] = 'https://data.binance.com/api/v3'
exchange.urls['api']['private'] = 'https://api.binance.com/api/v3'

# --- 2. LIVE SETTINGS ---
MIN_PROFIT = 0.005  # 0.5% Net Goal
FEE = 0.00075      # 0.075% (Assumes BNB for fees)

def get_balance():
    try:
        balance = exchange.fetch_balance()
        return float(balance['total']['USDT'])
    except Exception as e:
        print(f"!! Balance Error: {e}")
        return 0.0

def execute_trade(path, amount):
    """LIVE EXECUTION with full transparency logs."""
    start_time = time.time()
    try:
        print("\n" + "💰" * 15)
        print(f"!!! ARBITRAGE DETECTED: {' -> '.join(path)} !!!")
        
        # LEG 1
        print(f"Executing Leg 1: Buying {path[1]} with ${amount:.2f} USDT...")
        order1 = exchange.create_market_buy_order(f"{path[1]}/USDT", amount)
        qty1 = order1['filled']
        print(f"✅ Success: Bought {qty1:.6f} {path[1]}")

        # LEG 2
        print(f"Executing Leg 2: Swapping {path[1]} for {path[2]}...")
        order2 = exchange.create_market_order(f"{path[2]}/{path[1]}", 'buy', qty1)
        qty2 = order2['filled']
        print(f"✅ Success: Received {qty2:.6f} {path[2]}")

        # LEG 3
        print(f"Executing Leg 3: Selling {path[2]} back to USDT...")
        order3 = exchange.create_market_sell_order(f"{path[2]}/USDT", qty2)
        final_usdt = order3['cost']
        print(f"✅ Success: Returned to ${final_usdt:.4f} USDT")

        # PROFIT REPORT
        net = final_usdt - amount
        print(f"--- TRADE SUMMARY ---")
        print(f"Profit/Loss: ${net:.6f}")
        print(f"Time Taken:  {time.time() - start_time:.2f}s")
        print("💰" * 15 + "\n")
    except Exception as e:
        print(f"❌ EXECUTION FAILED: {e}")

def run_bot():
    coins = ['BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'LTC', 'MATIC', 'DOT']
    paths = []
    for base in ['BTC', 'ETH', 'BNB']:
        for alt in coins:
            if base != alt: paths.append(['USDT', base, alt, 'USDT'])

    print(f"🚀 BOT LIVE IN SINGAPORE | Total Paths: {len(paths)}")

    while True:
        try:
            current_usdt = get_balance()
            if current_usdt < 1.05:
                print(f"⚠️ Low Balance: ${current_usdt:.2f} | Deposit USDT to resume.", end='\r')
                time.sleep(10); continue

            tickers = exchange.fetch_tickers()
            best_roi = -1.0
            best_path = ""

            # Transparency Section: Log every check
            print(f"\n[SCAN {datetime.now().strftime('%H:%M:%S')}] Balance: ${current_usdt:.2f}")
            
            for p in paths:
                try:
                    # Raw Price Capture
                    p1 = 1 / tickers[f"{p[1]}/USDT"]['ask']
                    p2 = 1 / tickers[f"{p[2]}/{p[1]}"]['ask']
                    p3 = tickers[f"{p[2]}/USDT"]['bid']
                    
                    # Math Logic
                    roi = (current_usdt * p1 * p2 * p3 - current_usdt) / current_usdt - (FEE * 3)
                    
                    # Keep track of best
                    if roi > best_roi:
                        best_roi = roi
                        best_path = f"{p[1]}->{p[2]}"

                    # Trigger Trade
                    if roi > MIN_PROFIT:
                        execute_trade(p, current_usdt)
                except: continue

            print(f"  > Current Best: {best_path} at {best_roi:.4%}")
            time.sleep(1) # Controls scan speed

        except Exception as e:
            print(f"Main Loop Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_bot()
