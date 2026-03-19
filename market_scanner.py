#!/usr/bin/env python3
"""
Market scanner for Polymarket.
Finds trading opportunities based on various criteria.
"""

import os
import sys
import json
import logging
from typing import List, Dict, Any
from datetime import datetime
from polymarket_bot import PolymarketBot, load_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MarketScanner:
    """Scan Polymarket for trading opportunities"""
    
    def __init__(self, bot: PolymarketBot):
        self.bot = bot
    
    def get_all_markets(self, active_only: bool = True) -> List[Dict]:
        """Get all markets from API"""
        markets = []
        next_cursor = None
        
        while True:
            try:
                # Use the client's get_markets method
                result = self.bot.client.get_markets(
                    active=active_only,
                    next_cursor=next_cursor
                )
                
                batch = result.get("data", [])
                markets.extend(batch)
                
                next_cursor = result.get("next_cursor")
                if not next_cursor or next_cursor == "LTE=":
                    break
                    
            except Exception as e:
                logger.error(f"Error fetching markets: {e}")
                break
        
        return markets
    
    def filter_by_volume(self, markets: List[Dict], min_volume: float = 100000) -> List[Dict]:
        """Filter markets by minimum volume"""
        return [
            m for m in markets 
            if float(m.get("volume", 0) >= min_volume)
        ]
    
    def filter_by_spread(self, markets: List[Dict], max_spread: float = 0.05) -> List[Dict]:
        """Filter markets by tight spreads"""
        filtered = []
        for market in markets:
            # Calculate spread if bid/ask available
            tokens = market.get("tokens", [])
            if tokens:
                # Simplified - would need order book data for real spread
                filtered.append(market)
        return filtered
    
    def find_arbitrage_opportunities(self, markets: List[Dict]) -> List[Dict]:
        """Find potential arbitrage opportunities"""
        opportunities = []
        
        for market in markets:
            tokens = market.get("tokens", [])
            if len(tokens) >= 2:
                # Check if sum of prices < 1 (arbitrage)
                prices = []
                for token in tokens:
                    # Would need actual order book data
                    pass
        
        return opportunities
    
    def get_high_probability_trades(self, markets: List[Dict], threshold: float = 0.8) -> List[Dict]:
        """Find markets with high probability outcomes"""
        high_prob = []
        
        for market in markets:
            tokens = market.get("tokens", [])
            for token in tokens:
                price = float(token.get("price", 0))
                if price >= threshold or price <= (1 - threshold):
                    high_prob.append({
                        "market": market.get("question"),
                        "outcome": token.get("outcome"),
                        "price": price,
                        "implied_probability": price * 100,
                        "token_id": token.get("token_id"),
                        "volume": market.get("volume"),
                        "liquidity": market.get("liquidity")
                    })
        
        return sorted(high_prob, key=lambda x: abs(0.5 - x["price"]), reverse=True)
    
    def get_undervalued(self, markets: List[Dict], max_price: float = 0.3) -> List[Dict]:
        """Find potentially undervalued outcomes"""
        undervalued = []
        
        for market in markets:
            tokens = market.get("tokens", [])
            for token in tokens:
                price = float(token.get("price", 0))
                if 0.05 <= price <= max_price:
                    undervalued.append({
                        "market": market.get("question"),
                        "outcome": token.get("outcome"),
                        "price": price,
                        "potential_return": (1 / price - 1) * 100,
                        "token_id": token.get("token_id"),
                        "volume": market.get("volume")
                    })
        
        return sorted(undervalued, key=lambda x: x["potential_return"], reverse=True)
    
    def scan(self, scan_type: str = "all") -> Dict[str, Any]:
        """Run market scan"""
        logger.info(f"Starting market scan: {scan_type}")
        
        # Get markets
        markets = self.get_all_markets(active_only=True)
        logger.info(f"Found {len(markets)} active markets")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "total_markets": len(markets),
            "scans": {}
        }
        
        if scan_type in ["all", "volume"]:
            high_volume = self.filter_by_volume(markets, min_volume=500000)
            results["scans"]["high_volume"] = {
                "count": len(high_volume),
                "markets": [
                    {
                        "question": m.get("question"),
                        "volume": m.get("volume"),
                        "liquidity": m.get("liquidity")
                    }
                    for m in high_volume[:10]
                ]
            }
        
        if scan_type in ["all", "high_probability"]:
            high_prob = self.get_high_probability_trades(markets, threshold=0.75)
            results["scans"]["high_probability"] = {
                "count": len(high_prob),
                "opportunities": high_prob[:10]
            }
        
        if scan_type in ["all", "undervalued"]:
            undervalued = self.get_undervalued(markets, max_price=0.25)
            results["scans"]["undervalued"] = {
                "count": len(undervalued),
                "opportunities": undervalued[:10]
            }
        
        return results
    
    def print_scan_results(self, results: Dict):
        """Pretty print scan results"""
        print("\n" + "=" * 70)
        print("🔍 MARKET SCAN RESULTS")
        print("=" * 70)
        print(f"Timestamp: {results['timestamp']}")
        print(f"Total Markets: {results['total_markets']}")
        
        for scan_name, scan_data in results["scans"].items():
            print(f"\n📊 {scan_name.replace('_', ' ').upper()}")
            print("-" * 70)
            
            if scan_name == "high_volume":
                for m in scan_data["markets"][:5]:
                    print(f"\n{m['question'][:60]}...")
                    print(f"   Volume: ${m['volume']:,.0f}")
                    print(f"   Liquidity: ${m['liquidity']:,.0f}")
            
            elif scan_name == "high_probability":
                for opp in scan_data["opportunities"][:5]:
                    print(f"\n{opp['market'][:50]}...")
                    print(f"   Outcome: {opp['outcome']}")
                    print(f"   Price: ${opp['price']:.3f} ({opp['implied_probability']:.1f}%)")
            
            elif scan_name == "undervalued":
                for opp in scan_data["opportunities"][:5]:
                    print(f"\n{opp['market'][:50]}...")
                    print(f"   Outcome: {opp['outcome']}")
                    print(f"   Price: ${opp['price']:.3f}")
                    print(f"   Potential Return: {opp['potential_return']:.1f}%")
        
        print("\n" + "=" * 70)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Scan Polymarket for opportunities")
    parser.add_argument(
        "--type", 
        choices=["all", "volume", "high_probability", "undervalued"],
        default="all",
        help="Type of scan to run"
    )
    parser.add_argument("--output", "-o", help="Save results to JSON file")
    
    args = parser.parse_args()
    
    # Initialize bot (for API access)
    config = load_config()
    bot = PolymarketBot(config)
    
    if not bot.initialize():
        print("Failed to initialize bot")
        return 1
    
    # Run scan
    scanner = MarketScanner(bot)
    results = scanner.scan(scan_type=args.type)
    
    # Display results
    scanner.print_scan_results(results)
    
    # Save to file if requested
    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to {args.output}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
