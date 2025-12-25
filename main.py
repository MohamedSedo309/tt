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
exchange.urls['api']['public'] = 'https://data.binance.com/api/v3'
exchange.urls['api']['private'] = 'https://api.binance.com/api/v3'

# --- 2. TRADING SETTINGS ---
INVESTMENT = 1.75  # Amount in USDT to trade
MIN_PROFIT = 0.001 # 0.1% Net Profit AFTER fees
FEE = 0.00075      # 0.075% (With BNB discount)

print("--- AUTHENTICATION LOADED SUCCESSFULLY ---")

def get_triangles():
    """Finds all USDT -> COIN1 -> COIN2 -> USDT paths."""
    # Simplified for common high-volume pairs
    return [
        ['USDT', 'BTC', 'ETH', 'USDT'],
        ['USDT', 'BNB', 'BTC', 'USDT'],
        ['USDT', 'SOL', 'BNB', 'USDT'],
        ['USDT', 'XRP', 'BTC', 'USDT']
    ]

def execute_trade(path):
    try:
        print(f"🔔 Opportunity Found! Path: {' -> '.join(path)}")
        # Step 1: Buy Coin 1 with USDT
        order1 = exchange.create_market_buy_order(f"{path[1]}/USDT", INVESTMENT)
        print(f"✅ Step 1 Complete: Bought {path[1]}")

        # Step 2: Trade Coin 1 for Coin 2
        # (This logic adjusts based on if the pair is BTC/ETH or ETH/BTC)
        order2 = exchange.create_market_order(f"{path[2]}/{path[1]}", 'buy', INVESTMENT)
        print(f"✅ Step 2 Complete: Traded to {path[2]}")

        # Step 3: Sell Coin 2 back to USDT
        order3 = exchange.create_market_sell_order(f"{path[2]}/USDT", INVESTMENT)
        print(f"✅ Step 3 Complete: Returned to USDT")
        
    except Exception as e:
        print(f"❌ Trade failed: {e}")

def run_bot():
    triangles = get_triangles()
    print(f"--- STARTING LIVE TRADING ON {len(triangles)} PATHS ---")
    
    while True:
        try:
            tickers = exchange.fetch_tickers()
            for t in triangles:
                # Basic Math: (Price1 * Price2 * Price3)
                # Example: USDT->BTC (Buy) * BTC->ETH (Buy) * ETH->USDT (Sell)
                p1 = 1 / tickers[f"{t[1]}/USDT"]['ask']
                p2 = 1 / tickers[f"{t[2]}/{t[1]}"]['ask']
                p3 = tickers[f"{t[2]}/USDT"]['bid']
                
                gross_profit = (p1 * p2 * p3)
                net_profit = gross_profit - (FEE * 3) - 1
                
                if net_profit > MIN_PROFIT:
                    execute_trade(t)
            
            print(f"Scanning... Net Profit Potential: {net_profit:.4%}", end='\r')
            time.sleep(1)
        except Exception as e:
            print(f"\nError: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_bot()
