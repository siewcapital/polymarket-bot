#!/usr/bin/env python3
"""
Position tracker for Polymarket trades.
Tracks open positions and calculates PnL.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class Position:
    """Represents a trading position"""
    token_id: str
    market_question: str
    side: str  # 'LONG' or 'SHORT'
    entry_price: float
    size: float  # In shares
    entry_time: str
    
    def current_value(self, current_price: float) -> float:
        """Calculate current position value"""
        return self.size * current_price
    
    def unrealized_pnl(self, current_price: float) -> float:
        """Calculate unrealized PnL"""
        if self.side == "LONG":
            return self.size * (current_price - self.entry_price)
        else:  # SHORT
            return self.size * (self.entry_price - current_price)


class PositionTracker:
    """Track positions and calculate PnL"""
    
    def __init__(self, state_file: str = "positions.json"):
        self.state_file = state_file
        self.positions: Dict[str, Position] = {}
        self.trade_history: List[Dict] = []
        self.load_state()
    
    def load_state(self):
        """Load positions from file"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r") as f:
                    data = json.load(f)
                    self.positions = {
                        k: Position(**v) for k, v in data.get("positions", {}).items()
                    }
                    self.trade_history = data.get("trade_history", [])
            except Exception as e:
                print(f"Failed to load state: {e}")
    
    def save_state(self):
        """Save positions to file"""
        data = {
            "positions": {k: asdict(v) for k, v in self.positions.items()},
            "trade_history": self.trade_history[-1000:]  # Keep last 1000 trades
        }
        with open(self.state_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def open_position(
        self, 
        token_id: str, 
        market_question: str,
        side: str, 
        entry_price: float, 
        size: float
    ):
        """Open a new position"""
        position = Position(
            token_id=token_id,
            market_question=market_question,
            side=side,
            entry_price=entry_price,
            size=size,
            entry_time=datetime.now().isoformat()
        )
        
        # If position exists, update it
        if token_id in self.positions:
            existing = self.positions[token_id]
            if existing.side == side:
                # Same side - add to position
                total_size = existing.size + size
                avg_price = ((existing.entry_price * existing.size) + (entry_price * size)) / total_size
                existing.size = total_size
                existing.entry_price = avg_price
            else:
                # Opposite side - reduce or flip
                if existing.size > size:
                    existing.size -= size
                else:
                    position.size = size - existing.size
                    self.positions[token_id] = position
        else:
            self.positions[token_id] = position
        
        # Record trade
        self.trade_history.append({
            "time": datetime.now().isoformat(),
            "action": "OPEN",
            "token_id": token_id,
            "side": side,
            "price": entry_price,
            "size": size
        })
        
        self.save_state()
    
    def close_position(self, token_id: str, exit_price: float, size: Optional[float] = None):
        """Close or reduce a position"""
        if token_id not in self.positions:
            return None
        
        position = self.positions[token_id]
        close_size = size or position.size
        
        # Calculate realized PnL
        if position.side == "LONG":
            pnl = close_size * (exit_price - position.entry_price)
        else:
            pnl = close_size * (position.entry_price - exit_price)
        
        # Update or remove position
        if close_size >= position.size:
            del self.positions[token_id]
        else:
            position.size -= close_size
        
        # Record trade
        self.trade_history.append({
            "time": datetime.now().isoformat(),
            "action": "CLOSE",
            "token_id": token_id,
            "side": position.side,
            "price": exit_price,
            "size": close_size,
            "realized_pnl": pnl
        })
        
        self.save_state()
        return pnl
    
    def get_position(self, token_id: str) -> Optional[Position]:
        """Get a specific position"""
        return self.positions.get(token_id)
    
    def get_all_positions(self) -> Dict[str, Position]:
        """Get all open positions"""
        return self.positions.copy()
    
    def get_daily_pnl(self) -> float:
        """Calculate today's realized PnL"""
        today = datetime.now().date().isoformat()
        pnl = 0.0
        
        for trade in self.trade_history:
            if trade["time"].startswith(today) and "realized_pnl" in trade:
                pnl += trade["realized_pnl"]
        
        return pnl
    
    def get_stats(self) -> Dict:
        """Get trading statistics"""
        total_trades = len(self.trade_history)
        winning_trades = sum(1 for t in self.trade_history if t.get("realized_pnl", 0) > 0)
        losing_trades = sum(1 for t in self.trade_history if t.get("realized_pnl", 0) < 0)
        
        total_pnl = sum(t.get("realized_pnl", 0) for t in self.trade_history)
        
        return {
            "open_positions": len(self.positions),
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "win_rate": winning_trades / total_trades if total_trades > 0 else 0,
            "total_realized_pnl": total_pnl,
            "daily_pnl": self.get_daily_pnl()
        }
    
    def print_summary(self):
        """Print position summary"""
        print("\n" + "=" * 50)
        print("📊 POSITION SUMMARY")
        print("=" * 50)
        
        if not self.positions:
            print("No open positions")
        else:
            for token_id, pos in self.positions.items():
                print(f"\n{pos.market_question[:50]}...")
                print(f"  Side: {pos.side}")
                print(f"  Size: {pos.size:.4f} shares")
                print(f"  Entry: ${pos.entry_price:.4f}")
                print(f"  Opened: {pos.entry_time}")
        
        stats = self.get_stats()
        print(f"\n📈 Stats:")
        print(f"  Total Trades: {stats['total_trades']}")
        print(f"  Win Rate: {stats['win_rate']*100:.1f}%")
        print(f"  Total PnL: ${stats['total_realized_pnl']:.2f}")
        print(f"  Today's PnL: ${stats['daily_pnl']:.2f}")
        print("=" * 50)


if __name__ == "__main__":
    # Demo usage
    tracker = PositionTracker()
    tracker.print_summary()
