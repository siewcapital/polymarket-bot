#!/usr/bin/env python3
"""
CLI for Polymarket Trading Bot
Easy commands to interact with the bot.
"""

import os
import sys
import argparse
import json
from polymarket_bot import PolymarketBot, load_config
from position_tracker import PositionTracker


def cmd_status(bot: PolymarketBot):
    """Show bot status"""
    status = bot.status()
    print(json.dumps(status, indent=2))


def cmd_balance(bot: PolymarketBot):
    """Show account balance"""
    balance = bot.get_balance()
    print(json.dumps(balance, indent=2))


def cmd_markets(bot: PolymarketBot, limit: int = 5):
    """List available markets"""
    markets = bot.get_markets(active=True)
    print(f"\n📊 Top {limit} Active Markets:")
    print("=" * 60)
    for i, market in enumerate(markets[:limit]):
        print(f"\n{i+1}. {market.get('question', 'Unknown')}")
        print(f"   Volume: ${market.get('volume', 0):,.0f}")
        print(f"   Liquidity: ${market.get('liquidity', 0):,.0f}")
        tokens = market.get('tokens', [])
        if tokens:
            print(f"   Token ID: {tokens[0].get('token_id', 'N/A')[:30]}...")


def cmd_buy(bot: PolymarketBot, token_id: str, size: float, price: float):
    """Place a buy order"""
    print(f"Buying ${size} of {token_id[:30]}... at ${price}")
    result = bot.buy(token_id, size, price)
    if result:
        print(f"✅ Order placed: {result}")
    else:
        print("❌ Order failed")


def cmd_sell(bot: PolymarketBot, token_id: str, size: float, price: float):
    """Place a sell order"""
    print(f"Selling ${size} of {token_id[:30]}... at ${price}")
    result = bot.sell(token_id, size, price)
    if result:
        print(f"✅ Order placed: {result}")
    else:
        print("❌ Order failed")


def cmd_orders(bot: PolymarketBot):
    """List open orders"""
    orders = bot.get_open_orders()
    print(json.dumps(orders, indent=2))


def cmd_cancel(bot: PolymarketBot):
    """Cancel all orders"""
    print("Cancelling all orders...")
    if bot.cancel_all_orders():
        print("✅ All orders cancelled")
    else:
        print("❌ Failed to cancel orders")


def cmd_positions():
    """Show positions"""
    tracker = PositionTracker()
    tracker.print_summary()


def main():
    parser = argparse.ArgumentParser(
        description="Polymarket Trading Bot CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s status                 # Show bot status
  %(prog)s markets                # List active markets
  %(prog)s balance                # Show account balance
  %(prog)s buy <token_id> 10 0.5  # Buy $10 at $0.50
  %(prog)s sell <token_id> 10 0.6 # Sell $10 at $0.60
  %(prog)s positions              # Show open positions
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Status
    subparsers.add_parser('status', help='Show bot status')
    
    # Balance
    subparsers.add_parser('balance', help='Show account balance')
    
    # Markets
    markets_parser = subparsers.add_parser('markets', help='List active markets')
    markets_parser.add_argument('-l', '--limit', type=int, default=5, help='Number of markets to show')
    
    # Buy
    buy_parser = subparsers.add_parser('buy', help='Place a buy order')
    buy_parser.add_argument('token_id', help='Token ID to buy')
    buy_parser.add_argument('size', type=float, help='Size in USD')
    buy_parser.add_argument('price', type=float, help='Price to pay (0.00-1.00)')
    
    # Sell
    sell_parser = subparsers.add_parser('sell', help='Place a sell order')
    sell_parser.add_argument('token_id', help='Token ID to sell')
    sell_parser.add_argument('size', type=float, help='Size in shares')
    sell_parser.add_argument('price', type=float, help='Price to sell at (0.00-1.00)')
    
    # Orders
    subparsers.add_parser('orders', help='List open orders')
    
    # Cancel
    subparsers.add_parser('cancel', help='Cancel all orders')
    
    # Positions
    subparsers.add_parser('positions', help='Show open positions')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Initialize bot for commands that need it
    commands_needing_bot = ['status', 'balance', 'markets', 'buy', 'sell', 'orders', 'cancel']
    
    bot = None
    if args.command in commands_needing_bot:
        config = load_config()
        bot = PolymarketBot(config)
        if not bot.initialize():
            print("❌ Failed to initialize bot")
            return 1
    
    # Execute command
    if args.command == 'status':
        cmd_status(bot)
    elif args.command == 'balance':
        cmd_balance(bot)
    elif args.command == 'markets':
        cmd_markets(bot, args.limit)
    elif args.command == 'buy':
        cmd_buy(bot, args.token_id, args.size, args.price)
    elif args.command == 'sell':
        cmd_sell(bot, args.token_id, args.size, args.price)
    elif args.command == 'orders':
        cmd_orders(bot)
    elif args.command == 'cancel':
        cmd_cancel(bot)
    elif args.command == 'positions':
        cmd_positions()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
