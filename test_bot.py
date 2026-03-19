#!/usr/bin/env python3
"""
Test suite for Polymarket Trading Bot
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from polymarket_bot import PolymarketBot, RiskManager, TelegramNotifier
from position_tracker import PositionTracker, Position


class TestRiskManager(unittest.TestCase):
    """Test risk management functionality"""
    
    def setUp(self):
        self.rm = RiskManager(max_daily_loss=50.0, max_trade_size=10.0)
    
    def test_can_trade_within_limits(self):
        """Test that small trades are allowed"""
        can_trade, reason = self.rm.can_trade(5.0)
        self.assertTrue(can_trade)
        self.assertEqual(reason, "OK")
    
    def test_cannot_trade_over_size_limit(self):
        """Test that oversized trades are blocked"""
        can_trade, reason = self.rm.can_trade(20.0)
        self.assertFalse(can_trade)
        self.assertIn("exceeds max", reason)
    
    def test_daily_loss_limit(self):
        """Test that trading stops after daily loss limit"""
        self.rm.daily_pnl = -50.0
        can_trade, reason = self.rm.can_trade(5.0)
        self.assertFalse(can_trade)
        self.assertIn("loss limit reached", reason)
    
    def test_record_trade(self):
        """Test trade recording"""
        self.rm.record_trade("BUY", 10.0, 0.5, "token123")
        self.assertEqual(self.rm.trades_today, 1)
        self.assertEqual(len(self.rm.trades_history), 1)


class TestTelegramNotifier(unittest.TestCase):
    """Test Telegram notification functionality"""
    
    @patch('polymarket_bot.requests.post')
    def test_send_message(self, mock_post):
        """Test sending Telegram message"""
        mock_post.return_value.status_code = 200
        
        notifier = TelegramNotifier("fake_token", "chat123")
        result = notifier.send_message("Test message")
        
        self.assertTrue(result)
        mock_post.assert_called_once()
    
    @patch('polymarket_bot.requests.post')
    def test_notify_trade(self, mock_post):
        """Test trade notification"""
        mock_post.return_value.status_code = 200
        
        notifier = TelegramNotifier("fake_token", "chat123")
        result = notifier.notify_trade("BUY", "token123", 10.0, 0.5, "order456")
        
        self.assertTrue(result)
        mock_post.assert_called_once()


class TestPositionTracker(unittest.TestCase):
    """Test position tracking functionality"""
    
    def setUp(self):
        self.tracker = PositionTracker(state_file="/tmp/test_positions.json")
    
    def tearDown(self):
        """Clean up test files"""
        if os.path.exists("/tmp/test_positions.json"):
            os.remove("/tmp/test_positions.json")
    
    def test_open_position(self):
        """Test opening a position"""
        self.tracker.open_position(
            token_id="token123",
            market_question="Test Market?",
            side="LONG",
            entry_price=0.5,
            size=100.0
        )
        
        pos = self.tracker.get_position("token123")
        self.assertIsNotNone(pos)
        self.assertEqual(pos.side, "LONG")
        self.assertEqual(pos.size, 100.0)
    
    def test_close_position(self):
        """Test closing a position"""
        self.tracker.open_position(
            token_id="token123",
            market_question="Test Market?",
            side="LONG",
            entry_price=0.5,
            size=100.0
        )
        
        pnl = self.tracker.close_position("token123", exit_price=0.6)
        
        # PnL should be (0.6 - 0.5) * 100 = 10
        self.assertEqual(pnl, 10.0)
        self.assertIsNone(self.tracker.get_position("token123"))
    
    def test_position_value(self):
        """Test position value calculation"""
        pos = Position(
            token_id="token123",
            market_question="Test?",
            side="LONG",
            entry_price=0.5,
            size=100.0,
            entry_time="2025-01-01T00:00:00"
        )
        
        value = pos.current_value(0.6)
        self.assertEqual(value, 60.0)
        
        unrealized = pos.unrealized_pnl(0.6)
        self.assertEqual(unrealized, 10.0)


class TestPolymarketBotConfig(unittest.TestCase):
    """Test bot configuration"""
    
    def test_load_config_from_env(self):
        """Test loading config from environment"""
        os.environ["POLYMARKET_PRIVATE_KEY"] = "test_key"
        os.environ["MAX_DAILY_LOSS"] = "100.0"
        
        from polymarket_bot import load_config
        config = load_config()
        
        self.assertEqual(config["private_key"], "test_key")
        self.assertEqual(config["max_daily_loss"], 100.0)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestRiskManager))
    suite.addTests(loader.loadTestsFromTestCase(TestTelegramNotifier))
    suite.addTests(loader.loadTestsFromTestCase(TestPositionTracker))
    suite.addTests(loader.loadTestsFromTestCase(TestPolymarketBotConfig))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
