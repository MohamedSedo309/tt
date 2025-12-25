import os
import ccxt
import time
from datetime import datetime

# --- 1. CONFIGURATION & AUTH ---
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

# --- 2. LIVE STRATEGY SETTINGS ---
MIN_PROFIT = 0.005  # 0.5% Net Profit threshold
FEE_RATE = 0.00075  # 0.075% per leg (Total 0.225% for 3 trades)

def get_balance():
    try:
        balance = exchange.fetch_balance()
        return float(balance['total']['USDT'])
    except: return 0.0

def execute_live_trade(path, amount):
    """LIVE EXECUTION: Orders are sent immediately to Binance."""
    start_time = time.time()
    try:
        print("\n" + "="*50)
        print(f"🚨 LIVE TRADE INITIATED | Path: {' -> '.join(path)}")
        print(f"💰 Starting Capital: ${amount:.4f} USDT")

        # Leg 1: USDT -> Base Coin
        order1 = exchange.create_market_buy_order(f"{path[1]}/USDT", amount)
        buy_qty = order1['filled']
        print(f"Leg 1: Bought {buy_qty:.6f} {path[1]}")

        # Leg 2: Base Coin -> Alt Coin
        order2 = exchange.create_market_order(f"{path[2]}/{path[1]}", 'buy', buy_qty)
        alt_qty = order2['filled']
        print(f"Leg 2: Swapped to {alt_qty:.6f} {path[2]}")

        # Leg 3: Alt Coin -> USDT
        order3 = exchange.create_market_sell_order(f"{path[2]}/USDT", alt_qty)
        final_usdt = order3['cost']
        print(f"Leg 3: Returned to ${final_usdt:.4f} USDT")

        # Calculate Results
        execution_time = time.time() - start_time
        gross_profit = final_usdt - amount
        total_fees = (amount + final_usdt) * FEE_RATE # Simplified fee estimate
        net_profit = gross_profit - total_fees

        print("-" * 30)
        print(f"📊 SUMMARY REPORT ({datetime.now().strftime('%H:%M:%S')})")
        print(f"   Net Profit:  ${net_profit:.6f}")
        print(f"   Total Fees:  ${total_fees:.6f}")
        print(f"   Time Taken:  {execution_time:.2f} seconds")
        print("="*50 + "\n")

    except Exception as e:
        print(f"❌ CRITICAL EXECUTION ERROR: {e}")

def run_scanner():
    coins = ['BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'LTC', 'MATIC', 'DOT']
    paths = []
    for base in ['BTC', 'ETH', 'BNB']:
        for alt in coins:
            if base != alt:
                paths.append(['USDT', base, alt, 'USDT'])

    print(f"🚀 BOT LIVE IN SINGAPORE | Monitoring {len(paths)} Paths")
    
    while True:
        try:
            current_bal = get_balance()
            if current_bal < 1.10:
                print(f"⚠️ Balance ${current_bal:.2f} too low for trade legs. Waiting...", end='\r')
                time.sleep(30); continue

            tickers = exchange.fetch_tickers()
            best_opp = -1.0

            for loop in paths:
                try:
                    p1 = 1 / tickers[f"{loop[1]}/USDT"]['ask']
                    p2 = 1 / tickers[f"{loop[2]}/{loop[1]}"]['ask']
                    p3 = tickers[f"{loop[2]}/USDT"]['bid']
                    
                    est_return = current_bal * p1 * p2 * p3
                    net = (est_return - current_bal) / current_bal - (FEE_RATE * 3)
                    
                    if net > best_opp: best_opp = net
                    if net > MIN_PROFIT:
                        execute_live_trade(loop, current_bal)
                except: continue

            print(f"Scanning... Bal: ${current_bal:.2f} | Best Opp: {best_opp:.4%}", end='\r')
            time.sleep(1)
        except Exception as e:
            time.sleep(10)

if __name__ == "__main__":
    run_scanner()
