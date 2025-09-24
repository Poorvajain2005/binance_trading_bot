import ccxt

# TESTNET API keys - Replace with your testnet keys from https://testnet.binancefuture.com/
api_key = "YOUR_TESTNET_API_KEY"
api_secret = "YOUR_TESTNET_SECRET"

if api_key == "92b6b6eb2532b7cd28b686bea48e495c9c2ff085a97c9f83ec19afacfd97b4d9" or api_secret =="98b7c4cc4cd359fbecaaf8cd0b643ca9faa9fb9586fd5349e3e1171e8e16440b":
    print("\nSETUP REQUIRED:")
    print("1. Go to https://testnet.binancefuture.com/")
    print("2. Create account (use email, no KYC needed)")
    print("3. Generate API keys with futures permissions")
    print("4. Replace the placeholder keys in this file")
    print("5. Run the script again\n")
    exit(1)

# Create a Binance exchange instance
exchange = ccxt.binance({
    "apiKey": api_key,
    "secret": api_secret,
    "options": {"defaultType": "future"},  # use USDT-M Futures
    "urls": {
        "api": {
            "fapiPublic": "https://testnet.binancefuture.com/fapi/v1",
            "fapiPrivate": "https://testnet.binancefuture.com/fapi/v1",
        }
    }
})

# Using testnet URLs directly

try:
    # Fetch balance
    balance = exchange.fetch_balance()
    print(balance)
except ccxt.AuthenticationError as e:
    print(f"Authentication error: {e}")
except Exception as e:
    print(f"Error: {e}")