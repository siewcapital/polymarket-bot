#!/usr/bin/env python3
"""
Simple Trading Strategy Example
Demonstrates how to use the bot to automate trades based on simple rules.
"""

import os
import time
import random
from polymarket_bot import PolymarketBot, load_config


def simple_market_maker(bot: PolymarketBot, token_id: str, spread: float = 0.02):
    """
    Simple market maker strategy - places buy and sell orders around current price.
    
    Args:
        bot: Initialized PolymarketBot
        token_id: Token ID to trade
        spread: Spread between buy and sell prices (default 2%)
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Get current market price (simplified - in reality you'd fetch order book)
    current_price = 0.5  # Placeholder
    
    buy_price = current_price - (spread / 2)
    sell_price = current_price + (spread / 2)
    
    logger.info(f"Market maker: Placing orders around {current_price}")
    logger.info(f"Buy at {buy_price}, Sell at {sell_price}")
    
    # Place buy order
    bot.buy(token_id, size=10.0, price=buy_price)
    
    # Place sell order
    bot.sell(token_id, size=10.0, price=sell_price)


def momentum_strategy(bot: PolymarketBot, token_id: str):
    """
    Simple momentum strategy - buys if price is trending up.
    (Placeholder for actual implementation)
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info("Momentum strategy: Checking price trend...")
    
    # In real implementation:
    # 1. Fetch historical prices
    # 2. Calculate momentum indicator
    # 3. Place order if conditions met
    
    # For now, just place a small test buy
    result = bot.buy(token_id, size=5.0, price=0.5)
    return result


def run_autonomous_trading(bot: PolymarketBot, interval: int = 300):
    """
    Run autonomous trading loop.
    
    Args:
        bot: Initialized PolymarketBot
        interval: Seconds between trading cycles (default 5 minutes)
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info("Starting autonomous trading loop...")
    
    # Get available markets
    markets = bot.get_markets(active=True)
    if not markets:
        logger.error("No markets available")
        return
    
    # Select first market for demo
    market = markets[0]
    tokens = market.get("tokens", [])
    if not tokens:
        logger.error("No tokens in selected market")
        return
    
    token_id = tokens[0].get("token_id")
    logger.info(f"Trading on: {market.get('question', 'Unknown')}")
    
    try:
        while bot.running:
            # Check status
            status = bot.status()
            logger.info(f"Status: {status}")
            
            # Only trade if under risk limits
            if status['daily_pnl'] > -status['max_daily_loss']:
                # Place a small test trade
                if random.random() > 0.5:
                    bot.buy(token_id, size=5.0, price=0.5)
                else:
                    bot.sell(token_id, size=5.0, price=0.5)
            else:
                logger.warning("Daily loss limit reached, skipping trade")
            
            # Wait for next cycle
            time.sleep(interval)
            
    except KeyboardInterrupt:
        logger.info("Stopping autonomous trading...")


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Load and initialize bot
    config = load_config()
    bot = PolymarketBot(config)
    
    if not bot.initialize():
        print("Failed to initialize bot")
        exit(1)
    
    # Run autonomous trading
    bot.running = True
    run_autonomous_trading(bot, interval=300)  # 5 minute intervals
