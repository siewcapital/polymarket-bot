# Getting Started with Polymarket Bot

Quick start guide to get your bot running in 5 minutes.

## Prerequisites

- Python 3.8+
- A Polygon wallet with some MATIC for gas
- USDC on Polygon for trading
- (Optional) Telegram bot for notifications

## Step 1: Install

```bash
# Clone repository
git clone https://github.com/siewcapital/polymarket-bot.git
cd polymarket-bot

# Run automated setup
python setup.py
```

## Step 2: Configure

Edit `.env` file with your credentials:

```bash
# Required
POLYMARKET_PRIVATE_KEY=your_private_key_here

# Optional but recommended
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=-1003743622774

# Risk limits (default: $50 daily loss, $10 max trade)
MAX_DAILY_LOSS=50.0
MAX_TRADE_SIZE=10.0
```

## Step 3: Validate

Check your configuration:

```bash
python validate_config.py
```

## Step 4: Test

Run the test suite:

```bash
python test_bot.py
```

## Step 5: Run

### Option A: Simple Bot
```bash
python polymarket_bot.py
```

### Option B: With Demo Trade
```bash
RUN_DEMO_TRADE=true python polymarket_bot.py
```

### Option C: CLI Mode
```bash
# Check status
python cli.py status

# List markets
python cli.py markets

# Place a trade
python cli.py buy <token_id> 10 0.5
```

### Option D: Webhook Server
```bash
python webhook_server.py
```

### Option E: Momentum Strategy
```bash
python momentum_strategy.py <token_id> --size 10
```

### Option F: Market Scanner
```bash
python market_scanner.py
```

### Option G: Docker
```bash
docker-compose up -d
```

## Quick Commands

```bash
# Validate config
python validate_config.py

# Check bot status
python cli.py status

# View positions
python cli.py positions

# Scan markets
python market_scanner.py --type high_probability

# Cancel all orders
python cli.py cancel
```

## Next Steps

1. **Start Small**: Test with $10 trades first
2. **Monitor**: Watch Telegram notifications
3. **Review**: Check positions daily with `python cli.py positions`
4. **Adjust**: Modify risk limits as needed

## Troubleshooting

### "POLYMARKET_PRIVATE_KEY is not set"
- Make sure you've created `.env` file
- Or export the variable: `export POLYMARKET_PRIVATE_KEY=your_key`

### "Failed to initialize bot"
- Check your private key format (64 hex characters)
- Validate config: `python validate_config.py`
- Check network connection

### "Trade blocked by risk manager"
- You've hit a risk limit
- Check status: `python cli.py status`
- Adjust limits in `.env` if needed

## Support

- Check README.md for full documentation
- Review code comments for implementation details
- File issues on GitHub

---

**Ready to trade!** 🚀
