import os
import ccxt
import time

print("--- BOT IS ATTEMPTING TO START ---")

# --- SECURITY: Get keys from Railway Variables ---
API_KEY = os.getenv('BINANCE_API_KEY')
# Fix: Ensure the private key handles new lines correctly
PRIVATE_KEY_CONTENT = os.getenv('BINANCE_PRIVATE_KEY', '').replace('\\n', '\n')

# Initialize Binance with Ed25519 Support
exchange = ccxt.binance({
    'apiKey': API_KEY,
    'secret': PRIVATE_KEY_CONTENT,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'spot',
        'adjustForTimeDifference': True,
    }
})

# Bypass US Cloud restrictions
exchange.urls['api']['public'] = 'https://data.binance.com/api/v3'
exchange.urls['api']['private'] = 'https://api.binance.com/api/v3'

print("--- AUTHENTICATION LOADED SUCCESSFULLY ---")
# ... (all your other functions like find_triangles and run_scanner)

# --- THE START COMMAND ---
if __name__ == "__main__":
    print("--- STARTING THE SCANNER ENGINE ---")
    try:
        # 1. Find the paths
        all_loops = find_triangles('USDT')
        
        # 2. Start the infinite loop
        if all_loops:
            run_scanner(all_loops)
        else:
            print("❌ No trading loops found. Check if Binance is reachable.")
            
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
