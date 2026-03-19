# Polymarket Trading Bot

A Python trading bot for Polymarket with risk management and Telegram notifications.

## Features

- ✅ Connects to Polymarket CLOB API
- ✅ Places real trades (tested with $10 amounts)
- ✅ Telegram notifications for all trades
- ✅ Risk limits (max daily loss, max trade size)
- ✅ Position tracking with PnL calculation
- ✅ CLI for easy operation
- ✅ Webhook server for external signals
- ✅ Market scanner for opportunities
- ✅ Docker support
- ✅ Unit tests
- ✅ Easy setup and configuration

## Quick Start (Automated)

```bash
# Clone the repo
git clone https://github.com/siewcapital/polymarket-bot.git
cd polymarket-bot

# Run setup (installs dependencies, creates .env)
python setup.py

# Edit .env with your credentials
nano .env

# Run the bot
python polymarket_bot.py
```

## Manual Setup

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

## CLI Usage

The bot includes a command-line interface for easy operation:

```bash
# Show bot status
python cli.py status

# List active markets
python cli.py markets

# Show account balance
python cli.py balance

# Place orders
python cli.py buy <token_id> 10 0.5   # Buy $10 at $0.50
python cli.py sell <token_id> 10 0.6  # Sell $10 at $0.60

# View and manage orders
python cli.py orders
python cli.py cancel

# Track positions
python cli.py positions
```

## Webhook Server

Run the webhook server to receive trading signals from external sources:

```bash
# Start webhook server on port 8080
python webhook_server.py

# Or specify custom port
WEBHOOK_PORT=3000 python webhook_server.py
```

### Webhook Endpoints

- `GET /health` - Health check
- `GET /status` - Bot status
- `POST /webhook/trade` - Execute trade directly
- `POST /webhook/signal` - Receive trading signal

### Example Webhook Request

```bash
curl -X POST http://localhost:8080/webhook/trade \
  -H "Content-Type: application/json" \
  -d '{
    "token_id": "your_token_id",
    "side": "BUY",
    "size": 10,
    "price": 0.5
  }'
```

## Position Tracking

The bot automatically tracks all positions and calculates PnL:

```python
from position_tracker import PositionTracker

tracker = PositionTracker()
tracker.print_summary()
```

Positions are saved to `positions.json` for persistence.

## Setup Script

Run the interactive setup:

```bash
python setup.py
```

This will:
1. Check Python version
2. Install dependencies
3. Test imports
4. Create `.env` file from template

## Docker Deployment

Run with Docker:

```bash
# Build and run
docker-compose up -d

# With webhook server
docker-compose --profile webhook up -d

# View logs
docker-compose logs -f
```

## Market Scanner

Scan for trading opportunities:

```bash
# Full market scan
python market_scanner.py

# Specific scan types
python market_scanner.py --type high_probability
python market_scanner.py --type undervalued
python market_scanner.py --type volume

# Save results to file
python market_scanner.py --output scan_results.json
```

## Testing

Run the test suite:

```bash
python test_bot.py
```

Tests cover:
- Risk management
- Telegram notifications
- Position tracking
- Configuration loading

## Systemd Service

Install as a system service:

```bash
# Copy service file
sudo cp polymarket-bot.service /etc/systemd/system/

# Edit paths and user in service file
sudo systemctl edit polymarket-bot

# Start service
sudo systemctl enable polymarket-bot
sudo systemctl start polymarket-bot

# View logs
sudo journalctl -u polymarket-bot -f
```

## File Structure

```
polymarket-bot/
├── polymarket_bot.py      # Main trading bot
├── cli.py                 # Command-line interface
├── webhook_server.py      # HTTP webhook server
├── position_tracker.py    # Position tracking & PnL
├── market_scanner.py      # Market opportunity scanner
├── strategy_example.py    # Example trading strategies
├── setup.py               # Interactive setup script
├── test_bot.py            # Unit tests
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker image
├── docker-compose.yml     # Docker Compose config
├── polymarket-bot.service # systemd service file
├── README.md              # Documentation
├── LICENSE                # MIT License
└── .env.example           # Environment template
```

## Getting Your Private Key

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
