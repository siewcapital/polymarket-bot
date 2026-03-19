# Polymarket Trading Bot

A Python trading bot for Polymarket with risk management and Telegram notifications.

## Features

- ✅ Connects to Polymarket CLOB API
- ✅ Places real trades (tested with $10 amounts)
- ✅ Telegram notifications for all trades
- ✅ Risk limits (max daily loss, max trade size)
- ✅ Easy to configure and run

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
# Required - Your Polygon wallet private key
export POLYMARKET_PRIVATE_KEY="your_private_key_here"

# Telegram notifications (optional but recommended)
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="-1003743622774"

# Risk limits
export MAX_DAILY_LOSS="50.0"    # Max $50 loss per day
export MAX_TRADE_SIZE="10.0"    # Max $10 per trade

# For proxy wallets (Magic Link users)
export POLYMARKET_SIGNATURE_TYPE="1"  # or 2
export POLYMARKET_FUNDER_ADDRESS="your_funder_address"
```

### 3. Run the Bot

```bash
# Start the bot
python polymarket_bot.py

# Run with a demo trade
export RUN_DEMO_TRADE=true
python polymarket_bot.py
```

## Usage

### As a Script

```python
from polymarket_bot import PolymarketBot, load_config

# Load config from environment
config = load_config()

# Initialize bot
bot = PolymarketBot(config)
bot.initialize()

# Check balance
balance = bot.get_balance()
print(balance)

# Place a buy order (token_id, size in USD, price)
result = bot.buy(
    token_id="your_token_id_here",
    size=10.0,  # $10
    price=0.5
)

# Place a sell order
result = bot.sell(
    token_id="your_token_id_here",
    size=10.0,
    price=0.5
)

# Check status
status = bot.status()
print(status)
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `POLYMARKET_PRIVATE_KEY` | Yes | - | Your wallet private key |
| `POLYMARKET_HOST` | No | `https://clob.polymarket.com` | API endpoint |
| `POLYMARKET_CHAIN_ID` | No | `137` | Polygon mainnet |
| `POLYMARKET_SIGNATURE_TYPE` | No | `0` | 0=EOA, 1/2=Proxy |
| `POLYMARKET_FUNDER_ADDRESS` | No | - | Required for proxy wallets |
| `TELEGRAM_BOT_TOKEN` | No | - | Bot token for notifications |
| `TELEGRAM_CHAT_ID` | No | `-1003743622774` | Chat/group ID |
| `TELEGRAM_THREAD_ID` | No | - | Topic/thread ID |
| `MAX_DAILY_LOSS` | No | `50.0` | Max daily loss in USD |
| `MAX_TRADE_SIZE` | No | `10.0` | Max trade size in USD |
| `RUN_DEMO_TRADE` | No | `false` | Run demo trade on startup |

## Risk Management

The bot includes built-in risk controls:

- **Daily Loss Limit**: Stops trading after losing a set amount (default $50)
- **Max Trade Size**: Limits individual trade size (default $10)
- **Trade History**: Tracks all trades for accountability

## Telegram Notifications

The bot sends notifications for:
- ✅ Bot startup
- ✅ Trade execution (buy/sell)
- ❌ Errors
- 📊 Daily summary

## Getting Your Private Key

### MetaMask / EOA Wallet

1. Open MetaMask
2. Click the three dots menu → Account Details
3. Click "Show Private Key"
4. Copy and set as `POLYMARKET_PRIVATE_KEY`

### Polymarket.com (Magic Link)

For proxy wallets, you need to:
1. Export your private key from the Polymarket UI
2. Set `POLYMARKET_SIGNATURE_TYPE=1` or `2`
3. Set `POLYMARKET_FUNDER_ADDRESS` to your funding address

## Safety Notes

⚠️ **Never commit your private key to git!**

⚠️ **Start with small amounts - test with $10 trades first**

⚠️ **Monitor your Telegram notifications**

## License

MIT
