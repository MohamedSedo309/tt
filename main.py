import os
import ccxt
import time

# --- 1. CONFIGURATION & AUTH ---
API_KEY = os.getenv('BINANCE_API_KEY')
PRIVATE_KEY_CONTENT = os.getenv('BINANCE_PRIVATE_KEY', '').replace('\\n', '\n')

exchange = ccxt.binance({
    'apiKey': API_KEY,
    'secret': PRIVATE_KEY_CONTENT,
    'enableRateLimit': True,
    'options': {'defaultType': 'spot', 'adjustForTimeDifference': True}
})

# Use Singapore-friendly endpoints
exchange.urls['api']['public'] = 'https://data.binance.com/api/v3'
exchange.urls['api']['private'] = 'https://api.binance.com/api/v3'

# --- 2. TRADING SETTINGS ---
MIN_PROFIT = 0.005  # 0.5% Net Profit
FEE_PERCENT = 0.00075  # 0.075% per trade (With BNB)

def get_balance():
    """Checks your current USDT balance to use for compounding."""
    try:
        balance = exchange.fetch_balance()
        return float(balance['total']['USDT'])
    except:
        return 0.0

def execute_trade_cycle(path, amount):
    """Executes the trades. The '#' makes it 'Simulation Mode' for safety."""
    try:
        print(f"💰 PROFIT FOUND! Path: {' -> '.join(path)} | Amount: ${amount:.2f}")
        
        # --- TO GO LIVE: REMOVE THE '#' FROM THE 3 LINES BELOW ---
        # exchange.create_market_buy_order(f"{path[1]}/USDT", amount)
        # exchange.create_market_order(f"{path[2]}/{path[1]}", 'buy', amount)
        # exchange.create_market_sell_order(f"{path[2]}/USDT", amount)
        
        print("✅ Cycle Finished.")
    except Exception as e:
        print(f"❌ Execution Error: {e}")

def run_scanner():
    # Base coins to check for triangles
    coins = ['BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'LTC']
    paths = []
    for base in ['BTC', 'ETH', 'BNB']:
        for alt in coins:
            if base != alt:
                paths.append(['USDT', base, alt, 'USDT'])

    print(f"🚀 BOT STARTING | Region: Singapore | Paths: {len(paths)}")
    
    while True:
        try:
            current_balance = get_balance()
            
            # Safety: Minimum $1.10 needed for Binance trades
            if current_balance < 1.10:
                print(f"⚠️ Balance too low: ${current_balance:.2f} ", end='\r')
                time.sleep(30)
                continue

            tickers = exchange.fetch_tickers()
            best_opp = -1.0

            for loop in paths:
                try:
                    # Logic: Buy Base -> Buy Alt with Base -> Sell Alt for USDT
                    p1 = 1 / tickers[f"{loop[1]}/USDT"]['ask']
                    p2 = 1 / tickers[f"{loop[2]}/{loop[1]}"]['ask']
                    p3 = tickers[f"{loop[2]}/USDT"]['bid']
                    
                    final_amt = current_balance * p1 * p2 * p3
                    profit = (final_amt - current_balance) / current_balance - (FEE_PERCENT * 3)
                    
                    if profit > best_opp: best_opp = profit
                    if profit > MIN_PROFIT:
                        execute_trade_cycle(loop, current_balance)
                except:
                    continue # Skip if a specific pair isn't trading

            print(f"Scanning... Bal: ${current_balance:.2f} | Best: {best_opp:.4%}", end='\r')
            time.sleep(1)
            
        except Exception as e:
            print(f"\nConnection Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    run_scanner()
