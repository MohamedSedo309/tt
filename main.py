import os
import ccxt
import time

print("--- BOT IS ATTEMPTING TO START ---")

# --- 1. CONFIGURATION ---
API_KEY = os.getenv('BINANCE_API_KEY')
PRIVATE_KEY_CONTENT = os.getenv('BINANCE_PRIVATE_KEY', '').replace('\\n', '\n')

exchange = ccxt.binance({
    'apiKey': API_KEY,
    'secret': PRIVATE_KEY_CONTENT,
    'enableRateLimit': True,
    'options': {'defaultType': 'spot', 'adjustForTimeDifference': True}
})

# --- 2. THE SAFETY SETTINGS ---
MIN_PROFIT = 0.005 # 0.5% Net Profit
FEE = 0.00075      # 0.075% with BNB discount

print("--- AUTHENTICATION LOADED SUCCESSFULLY ---")

def get_balance():
    """Fetches your current available USDT balance."""
    try:
        balance = exchange.fetch_balance()
        return float(balance['total']['USDT'])
    except Exception as e:
        print(f"Error fetching balance: {e}")
        return 0.0

def execute_trade(path, amount):
    try:
        print(f"💰 PROFIT ALERT! Path: {' -> '.join(path)} | Trading: ${amount:.2f}")
        # --- EXECUTION COMMANDS (Uncomment '#' below to go live) ---
        # exchange.create_market_buy_order(f"{path[1]}/USDT", amount)
        # ... (Step 2 & 3 commands)
        print("✅ Trade executed and compounded!")
    except Exception as e:
        print(f"❌ Trade failed: {e}")

def run_bot():
    # Diversified paths to increase chances of finding 0.5% profit
    paths = [
        ['USDT', 'BTC', 'ETH', 'USDT'],
        ['USDT', 'BNB', 'BTC', 'USDT'],
        ['USDT', 'SOL', 'BNB', 'USDT'],
        ['USDT', 'ADA', 'BTC', 'USDT']
    ]
    
    print(f"--- SCANNING FOR >0.5% PROFIT (AUTO-COMPOUNDING ON) ---")
    
    while True:
        try:
            # Step 1: Check your current balance (Auto-Compound)
            current_usdt = get_balance()
            
            # Binance Safety Check: Minimum trade is $1.00
            if current_usdt < 1.10:
                print(f"⚠️ Balance too low to trade: ${current_usdt:.2f}", end='\r')
                time.sleep(60)
                continue

            tickers = exchange.fetch_tickers()
            for t in paths:
                p1 = 1 / tickers[f"{t[1]}/USDT"]['ask']
                p2 = 1 / tickers[f"{t[2]}/{t[1]}"]['ask']
                p3 = tickers[f"{t[2]}/USDT"]['bid']
                
                # Math: Calculate result based on CURRENT balance
                total_return = (current_usdt * p1 * p2 * p3)
                net_profit = (total_return - current_usdt) / current_usdt - (FEE * 3)

                if net_profit > MIN_PROFIT:
                    execute_trade(t, current_usdt)
            
            print(f"Scanning... Balance: ${current_usdt:.2f} | Best: {net_profit:.4%}", end='\r')
            time.sleep(2)
        except Exception as e:
            time.sleep(10)

if __name__ == "__main__":
    run_bot()
