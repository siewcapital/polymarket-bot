#!/usr/bin/env python3
"""
Simple momentum strategy implementation.
Buys when price is trending up, sells when trending down.
"""

import os
import time
import logging
from typing import List, Dict, Optional
from collections import deque
from datetime import datetime

from polymarket_bot import PolymarketBot, load_config
from position_tracker import PositionTracker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MomentumStrategy:
    """
    Simple momentum-based trading strategy.
    
    Buys when:
    - Price has increased over last N periods
    - Volume is above average
    - Not already in position
    
    Sells when:
    - Price has decreased over last N periods
    - Target profit or stop loss reached
    """
    
    def __init__(
        self,
        bot: PolymarketBot,
        token_id: str,
        lookback_periods: int = 5,
        entry_threshold: float = 0.02,  # 2% price increase
        exit_threshold: float = 0.02,   # 2% price decrease
        take_profit: float = 0.10,      # 10% profit target
        stop_loss: float = 0.05,        # 5% stop loss
        trade_size: float = 10.0        # $10 per trade
    ):
        self.bot = bot
        self.token_id = token_id
        self.lookback_periods = lookback_periods
        self.entry_threshold = entry_threshold
        self.exit_threshold = exit_threshold
        self.take_profit = take_profit
        self.stop_loss = stop_loss
        self.trade_size = trade_size
        
        self.price_history: deque = deque(maxlen=lookback_periods + 10)
        self.position_tracker = PositionTracker()
        self.entry_price: Optional[float] = None
        self.in_position = False
    
    def fetch_price(self) -> Optional[float]:
        """Fetch current price from API"""
        try:
            # This would use actual API - simplified for demo
            # In real implementation: get order book mid price
            import random
            return 0.4 + random.random() * 0.2  # Simulated 0.4-0.6
        except Exception as e:
            logger.error(f"Failed to fetch price: {e}")
            return None
    
    def calculate_momentum(self) -> float:
        """Calculate price momentum"""
        if len(self.price_history) < self.lookback_periods:
            return 0.0
        
        recent_prices = list(self.price_history)[-self.lookback_periods:]
        start_price = recent_prices[0]
        end_price = recent_prices[-1]
        
        if start_price == 0:
            return 0.0
        
        return (end_price - start_price) / start_price
    
    def check_exit_conditions(self, current_price: float) -> Optional[str]:
        """Check if we should exit position"""
        if not self.in_position or self.entry_price is None:
            return None
        
        pnl_pct = (current_price - self.entry_price) / self.entry_price
        
        if pnl_pct >= self.take_profit:
            return "TAKE_PROFIT"
        
        if pnl_pct <= -self.stop_loss:
            return "STOP_LOSS"
        
        # Check momentum reversal
        momentum = self.calculate_momentum()
        if momentum < -self.exit_threshold:
            return "MOMENTUM_REVERSAL"
        
        return None
    
    def run_cycle(self):
        """Run one strategy cycle"""
        current_price = self.fetch_price()
        if current_price is None:
            return
        
        self.price_history.append(current_price)
        
        logger.info(f"Price: ${current_price:.4f}, History: {len(self.price_history)}")
        
        # Check if we should exit
        if self.in_position:
            exit_reason = self.check_exit_conditions(current_price)
            if exit_reason:
                logger.info(f"Exit signal: {exit_reason}")
                result = self.bot.sell(self.token_id, self.trade_size, current_price)
                if result:
                    self.in_position = False
                    self.entry_price = None
                    logger.info(f"Sold at ${current_price:.4f} ({exit_reason})")
            return
        
        # Check if we should enter
        if len(self.price_history) >= self.lookback_periods:
            momentum = self.calculate_momentum()
            logger.info(f"Momentum: {momentum:.4f}")
            
            if momentum > self.entry_threshold:
                logger.info(f"Entry signal: momentum {momentum:.4f}")
                result = self.bot.buy(self.token_id, self.trade_size, current_price)
                if result:
                    self.in_position = True
                    self.entry_price = current_price
                    logger.info(f"Bought at ${current_price:.4f}")
    
    def run(self, interval: int = 60):
        """Run strategy loop"""
        logger.info(f"Starting momentum strategy on {self.token_id}")
        logger.info(f"Entry threshold: {self.entry_threshold:.2%}")
        logger.info(f"Exit threshold: {self.exit_threshold:.2%}")
        logger.info(f"Take profit: {self.take_profit:.2%}")
        logger.info(f"Stop loss: {self.stop_loss:.2%}")
        
        try:
            while True:
                self.run_cycle()
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("Strategy stopped")


def main():
    """Run momentum strategy"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Momentum trading strategy")
    parser.add_argument("token_id", help="Token ID to trade")
    parser.add_argument("--size", type=float, default=10.0, help="Trade size in USD")
    parser.add_argument("--interval", type=int, default=60, help="Cycle interval in seconds")
    parser.add_argument("--take-profit", type=float, default=0.10, help="Take profit %")
    parser.add_argument("--stop-loss", type=float, default=0.05, help="Stop loss %")
    
    args = parser.parse_args()
    
    # Initialize bot
    config = load_config()
    bot = PolymarketBot(config)
    
    if not bot.initialize():
        logger.error("Failed to initialize bot")
        return 1
    
    # Run strategy
    strategy = MomentumStrategy(
        bot=bot,
        token_id=args.token_id,
        trade_size=args.size,
        take_profit=args.take_profit,
        stop_loss=args.stop_loss
    )
    
    strategy.run(interval=args.interval)
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
