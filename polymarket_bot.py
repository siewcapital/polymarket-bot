#!/usr/bin/env python3
"""
Polymarket Trading Bot
- Connects to Polymarket CLOB API
- Places trades with risk limits
- Posts notifications to Telegram
"""

import os
import json
import time
import logging
import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, Dict, Any
import requests

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import MarketOrderArgs, OrderType, ApiCreds
from py_clob_client.order_builder.constants import BUY, SELL

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Send notifications to Telegram"""
    
    def __init__(self, bot_token: str, chat_id: str, thread_id: Optional[str] = None):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.thread_id = thread_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
    
    def send_message(self, message: str) -> bool:
        """Send message to Telegram"""
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            if self.thread_id:
                payload["message_thread_id"] = self.thread_id
            
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False
    
    def notify_trade(self, side: str, token: str, size: float, price: float, order_id: str):
        """Notify about a trade"""
        emoji = "🟢" if side == "BUY" else "🔴"
        message = f"""{emoji} *POLY TRADE EXECUTED*

*Side:* {side}
*Token:* `{token[:20]}...`
*Size:* ${size:.2f}
*Price:* {price:.4f}
*Order ID:* `{order_id}`
*Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return self.send_message(message)
    
    def notify_error(self, error: str):
        """Notify about an error"""
        message = f"""❌ *POLY BOT ERROR*

```{error}```

*Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return self.send_message(message)
    
    def notify_daily_summary(self, pnl: float, trades_count: int):
        """Notify daily summary"""
        emoji = "🟢" if pnl >= 0 else "🔴"
        message = f"""{emoji} *DAILY SUMMARY*

*PnL:* ${pnl:.2f}
*Trades:* {trades_count}
*Date:* {datetime.now().strftime('%Y-%m-%d')}
"""
        return self.send_message(message)


class RiskManager:
    """Manage trading risk limits"""
    
    def __init__(self, max_daily_loss: float = 50.0, max_trade_size: float = 10.0):
        self.max_daily_loss = max_daily_loss
        self.max_trade_size = max_trade_size
        self.daily_pnl = 0.0
        self.trades_today = 0
        self.last_reset = datetime.now().date()
        self.trades_history: list = []
    
    def reset_if_new_day(self):
        """Reset daily limits if it's a new day"""
        today = datetime.now().date()
        if today != self.last_reset:
            logger.info(f"New day - resetting risk limits. Previous PnL: ${self.daily_pnl:.2f}")
            self.daily_pnl = 0.0
            self.trades_today = 0
            self.trades_history = []
            self.last_reset = today
    
    def can_trade(self, trade_size: float) -> tuple[bool, str]:
        """Check if trade is allowed under risk limits"""
        self.reset_if_new_day()
        
        if trade_size > self.max_trade_size:
            return False, f"Trade size ${trade_size} exceeds max ${self.max_trade_size}"
        
        if self.daily_pnl <= -self.max_daily_loss:
            return False, f"Daily loss limit reached: ${self.daily_pnl:.2f}"
        
        return True, "OK"
    
    def record_trade(self, side: str, size: float, price: float, token: str):
        """Record a trade"""
        self.trades_today += 1
        self.trades_history.append({
            "time": datetime.now().isoformat(),
            "side": side,
            "size": size,
            "price": price,
            "token": token
        })
    
    def update_pnl(self, pnl: float):
        """Update daily PnL"""
        self.daily_pnl += pnl


class PolymarketBot:
    """Polymarket Trading Bot"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client: Optional[ClobClient] = None
        self.telegram: Optional[TelegramNotifier] = None
        self.risk_manager: Optional[RiskManager] = None
        self.running = False
        
    def initialize(self) -> bool:
        """Initialize bot components"""
        try:
            # Initialize Telegram
            if self.config.get("telegram_bot_token"):
                self.telegram = TelegramNotifier(
                    bot_token=self.config["telegram_bot_token"],
                    chat_id=self.config["telegram_chat_id"],
                    thread_id=self.config.get("telegram_thread_id")
                )
                logger.info("Telegram notifier initialized")
            
            # Initialize Risk Manager
            self.risk_manager = RiskManager(
                max_daily_loss=self.config.get("max_daily_loss", 50.0),
                max_trade_size=self.config.get("max_trade_size", 10.0)
            )
            logger.info("Risk manager initialized")
            
            # Initialize Polymarket client
            self.client = ClobClient(
                host=self.config.get("host", "https://clob.polymarket.com"),
                key=self.config["private_key"],
                chain_id=self.config.get("chain_id", 137),
                signature_type=self.config.get("signature_type", 0),
                funder=self.config.get("funder_address")
            )
            
            # Create or derive API credentials
            api_creds = self.client.create_or_derive_api_creds()
            self.client.set_api_creds(api_creds)
            logger.info("Polymarket client initialized and authenticated")
            
            # Send startup notification
            if self.telegram:
                self.telegram.send_message(
                    "🤖 *Polymarket Bot Started*\n\nRisk limits: "
                    f"Max daily loss ${self.risk_manager.max_daily_loss}, "
                    f"Max trade ${self.risk_manager.max_trade_size}"
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize bot: {e}")
            if self.telegram:
                self.telegram.notify_error(f"Initialization failed: {str(e)}")
            return False
    
    def get_balance(self) -> Dict[str, Any]:
        """Get account balance"""
        try:
            balance = self.client.get_balance()
            return balance
        except Exception as e:
            logger.error(f"Failed to get balance: {e}")
            return {}
    
    def get_markets(self, active: bool = True) -> list:
        """Get available markets"""
        try:
            markets = self.client.get_markets(active=active)
            return markets.get("data", [])
        except Exception as e:
            logger.error(f"Failed to get markets: {e}")
            return []
    
    def place_market_order(
        self, 
        token_id: str, 
        side: int, 
        size: float, 
        price: float = 0.5,
        tick_size: str = "0.01",
        neg_risk: bool = False
    ) -> Optional[Dict]:
        """Place a market order"""
        try:
            # Check risk limits
            can_trade, reason = self.risk_manager.can_trade(size)
            if not can_trade:
                logger.warning(f"Trade blocked by risk manager: {reason}")
                return None
            
            side_str = "BUY" if side == BUY else "SELL"
            logger.info(f"Placing {side_str} order: size=${size}, token={token_id[:20]}...")
            
            # Create order arguments
            order_args = MarketOrderArgs(
                token_id=token_id,
                price=price,
                size=size,
                side=side
            )
            
            # Post order
            response = self.client.create_and_post_order(
                order_args=order_args,
                order_type=OrderType.GTC
            )
            
            if response:
                logger.info(f"Order placed successfully: {response}")
                
                # Record trade
                self.risk_manager.record_trade(side_str, size, price, token_id)
                
                # Notify Telegram
                if self.telegram:
                    order_id = response.get("orderID", "unknown")
                    self.telegram.notify_trade(side_str, token_id, size, price, order_id)
                
                return response
            else:
                logger.error("Order placement returned empty response")
                return None
                
        except Exception as e:
            logger.error(f"Failed to place order: {e}")
            if self.telegram:
                self.telegram.notify_error(f"Order failed: {str(e)}")
            return None
    
    def buy(self, token_id: str, size: float, price: float = 0.5) -> Optional[Dict]:
        """Place a buy order"""
        return self.place_market_order(token_id, BUY, size, price)
    
    def sell(self, token_id: str, size: float, price: float = 0.5) -> Optional[Dict]:
        """Place a sell order"""
        return self.place_market_order(token_id, SELL, size, price)
    
    def get_open_orders(self) -> list:
        """Get open orders"""
        try:
            orders = self.client.get_open_orders()
            return orders
        except Exception as e:
            logger.error(f"Failed to get open orders: {e}")
            return []
    
    def cancel_all_orders(self) -> bool:
        """Cancel all open orders"""
        try:
            self.client.cancel_all()
            logger.info("All orders cancelled")
            return True
        except Exception as e:
            logger.error(f"Failed to cancel orders: {e}")
            return False
    
    def run_demo_trade(self):
        """Run a demo trade with $10"""
        try:
            # Get active markets
            markets = self.get_markets(active=True)
            if not markets:
                logger.error("No active markets found")
                return None
            
            # Find a liquid market (first one for demo)
            market = markets[0]
            logger.info(f"Selected market: {market.get('question', 'Unknown')}")
            
            # Get token ID for Yes outcome
            tokens = market.get("tokens", [])
            if not tokens:
                logger.error("No tokens found for market")
                return None
            
            token_id = tokens[0].get("token_id")
            if not token_id:
                logger.error("No token ID found")
                return None
            
            logger.info(f"Placing demo BUY order on token: {token_id[:30]}...")
            
            # Place $10 buy order
            result = self.buy(token_id, size=10.0, price=0.5)
            
            if result:
                logger.info(f"Demo trade successful: {result}")
            else:
                logger.error("Demo trade failed")
            
            return result
            
        except Exception as e:
            logger.error(f"Demo trade error: {e}")
            return None
    
    def status(self) -> Dict[str, Any]:
        """Get bot status"""
        if not self.risk_manager:
            return {"error": "Bot not initialized"}
        
        self.risk_manager.reset_if_new_day()
        
        return {
            "running": self.running,
            "daily_pnl": self.risk_manager.daily_pnl,
            "trades_today": self.risk_manager.trades_today,
            "max_daily_loss": self.risk_manager.max_daily_loss,
            "max_trade_size": self.risk_manager.max_trade_size,
            "date": str(self.risk_manager.last_reset)
        }


def load_config() -> Dict[str, Any]:
    """Load configuration from environment variables"""
    config = {
        # Required
        "private_key": os.getenv("POLYMARKET_PRIVATE_KEY"),
        
        # Optional with defaults
        "host": os.getenv("POLYMARKET_HOST", "https://clob.polymarket.com"),
        "chain_id": int(os.getenv("POLYMARKET_CHAIN_ID", "137")),
        "signature_type": int(os.getenv("POLYMARKET_SIGNATURE_TYPE", "0")),
        "funder_address": os.getenv("POLYMARKET_FUNDER_ADDRESS"),
        
        # Telegram
        "telegram_bot_token": os.getenv("TELEGRAM_BOT_TOKEN"),
        "telegram_chat_id": os.getenv("TELEGRAM_CHAT_ID", "-1003743622774"),
        "telegram_thread_id": os.getenv("TELEGRAM_THREAD_ID"),
        
        # Risk limits
        "max_daily_loss": float(os.getenv("MAX_DAILY_LOSS", "50.0")),
        "max_trade_size": float(os.getenv("MAX_TRADE_SIZE", "10.0")),
    }
    
    return config


def main():
    """Main entry point"""
    logger.info("Starting Polymarket Trading Bot...")
    
    # Load config
    config = load_config()
    
    if not config["private_key"]:
        logger.error("POLYMARKET_PRIVATE_KEY environment variable is required!")
        logger.error("Set it with: export POLYMARKET_PRIVATE_KEY=your_key_here")
        return 1
    
    # Initialize bot
    bot = PolymarketBot(config)
    
    if not bot.initialize():
        logger.error("Bot initialization failed")
        return 1
    
    # Show status
    status = bot.status()
    logger.info(f"Bot status: {json.dumps(status, indent=2)}")
    
    # Run demo trade if requested
    if os.getenv("RUN_DEMO_TRADE", "false").lower() == "true":
        logger.info("Running demo trade...")
        result = bot.run_demo_trade()
        if result:
            logger.info("Demo trade completed successfully")
        else:
            logger.error("Demo trade failed")
    
    logger.info("Bot ready. Use bot.buy() or bot.sell() to place trades.")
    
    # Keep running for continuous operation
    bot.running = True
    while bot.running:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            bot.running = False
    
    return 0


if __name__ == "__main__":
    exit(main())
