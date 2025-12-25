import os
import ccxt
import time

# --- 1. CONFIGURATION ---
API_KEY = os.getenv('BINANCE_API_KEY')
PRIVATE_KEY_CONTENT = os.getenv('BINANCE_PRIVATE_KEY', '').replace('\\n', '\n')

exchange = ccxt.binance({
    'apiKey': API_KEY,
    'secret': PRIVATE_KEY_CONTENT,
    'enableRateLimit': True,
    'options': {'defaultType': 'spot', 'adjustForTimeDifference': True}
})

# Singapore/International safe endpoints
exchange.urls['api']['public'] = 'https://data.binance.com/api/v3'
exchange.urls['api']['private'] = 'https://api.binance.com/api/v3'

# --- 2. THE STRATEGY SETTINGS ---
MIN_PROFIT = 0.005 # 0.5% net profit goal
FEE = 0.00075      # 0.075% (Assumes you have BNB for fees)

def get_balance():
    try:
        balance = exchange.fetch_balance()
        return float(balance['total']['USDT'])
    except: return 0.0

def execute_trade(path, amount):
    """Refined execution: Step 2 trades the middle coin immediately."""
    try:
        print(f"💰 PROFIT DETECTED! Path: {'->'.join(path)} | Size: ${amount:.2f}")
        # --- REMOVE '#' BELOW TO GO LIVE ---
        # exchange.create_market_buy_order(f"{path[1]}/USDT", amount)
        # exchange.create_market_order(f"{path[2]}/{path[1]}", 'buy', amount)
        # exchange.create_market_sell_order(f"{path[2]}/USDT", amount)
        print("✅ Cycle Complete.")
    except Exception as e:
        print(f"❌ Execution Error: {e}")

def run_bot():
    # Expanded list of high-volume coins to find more opportunities
    coins = ['BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'DOT', 'LTC', 'MATIC', 'TRX']
    paths = []
    for c1 in coins[:3]: # BTC, ETH, BNB as base 'bridge' coins
        for c2 in coins:
            if c1 != c2:
                paths.append(['USDT', c1, c2, 'USDT'])

    print(f"🚀 Scanner Live in Singapore | Monitoring {len(paths)} Paths")

    while True:
        try:
            current_usdt = get_balance()
            if current_usdt < 1.05:
                print(f"⚠️ Low Balance: ${current_usdt:.2f}. Deposit to continue.", end='\r')
                time.sleep(30); continue

            tickers = exchange.fetch_tickers()
            best_profit = -1.0
            
            for t in paths:
                try:
                    # Real-world Bid/Ask logic
                    p1 = 1 / tickers[f"{t[1]}/USDT"]['ask']
                    p2 = 1 / tickers
