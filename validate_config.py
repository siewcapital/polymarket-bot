#!/usr/bin/env python3
"""
Configuration validator for Polymarket Trading Bot.
Checks that all required settings are correct before starting.
"""

import os
import sys
import re
from typing import List, Tuple


class ConfigValidator:
    """Validate bot configuration"""
    
    REQUIRED_VARS = [
        "POLYMARKET_PRIVATE_KEY"
    ]
    
    OPTIONAL_VARS = [
        "POLYMARKET_HOST",
        "POLYMARKET_CHAIN_ID",
        "POLYMARKET_SIGNATURE_TYPE",
        "POLYMARKET_FUNDER_ADDRESS",
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_CHAT_ID",
        "TELEGRAM_THREAD_ID",
        "MAX_DAILY_LOSS",
        "MAX_TRADE_SIZE",
        "WEBHOOK_PORT",
        "RUN_DEMO_TRADE"
    ]
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_private_key(self, key: str) -> bool:
        """Validate private key format"""
        if not key:
            self.errors.append("POLYMARKET_PRIVATE_KEY is not set")
            return False
        
        # Check if it looks like a hex key (with or without 0x prefix)
        key_clean = key[2:] if key.startswith("0x") else key
        
        if len(key_clean) != 64:
            self.errors.append(f"POLYMARKET_PRIVATE_KEY should be 64 hex chars (got {len(key_clean)})")
            return False
        
        if not all(c in "0123456789abcdefABCDEF" for c in key_clean):
            self.errors.append("POLYMARKET_PRIVATE_KEY contains invalid characters")
            return False
        
        return True
    
    def validate_telegram(self, token: str, chat_id: str) -> bool:
        """Validate Telegram configuration"""
        if not token and not chat_id:
            self.warnings.append("Telegram notifications disabled (no token/chat_id)")
            return True
        
        if token and not chat_id:
            self.errors.append("TELEGRAM_BOT_TOKEN set but TELEGRAM_CHAT_ID is missing")
            return False
        
        if chat_id and not token:
            self.errors.append("TELEGRAM_CHAT_ID set but TELEGRAM_BOT_TOKEN is missing")
            return False
        
        # Basic token format check
        if token and not re.match(r"^\d+:[A-Za-z0-9_-]+$", token):
            self.warnings.append("TELEGRAM_BOT_TOKEN format looks unusual")
        
        return True
    
    def validate_numeric(self, var_name: str, value: str, min_val: float = None, max_val: float = None) -> bool:
        """Validate numeric environment variable"""
        if not value:
            return True  # Optional
        
        try:
            num_val = float(value)
            if min_val is not None and num_val < min_val:
                self.errors.append(f"{var_name} must be >= {min_val}")
                return False
            if max_val is not None and num_val > max_val:
                self.errors.append(f"{var_name} must be <= {max_val}")
                return False
            return True
        except ValueError:
            self.errors.append(f"{var_name} must be a number")
            return False
    
    def validate_all(self) -> Tuple[bool, List[str], List[str]]:
        """Run all validations"""
        
        # Check required variables
        for var in self.REQUIRED_VARS:
            value = os.getenv(var)
            if var == "POLYMARKET_PRIVATE_KEY":
                self.validate_private_key(value)
        
        # Validate Telegram config
        self.validate_telegram(
            os.getenv("TELEGRAM_BOT_TOKEN", ""),
            os.getenv("TELEGRAM_CHAT_ID", "")
        )
        
        # Validate numeric values
        self.validate_numeric("MAX_DAILY_LOSS", os.getenv("MAX_DAILY_LOSS", ""), min_val=0)
        self.validate_numeric("MAX_TRADE_SIZE", os.getenv("MAX_TRADE_SIZE", ""), min_val=0.01)
        self.validate_numeric("POLYMARKET_CHAIN_ID", os.getenv("POLYMARKET_CHAIN_ID", ""))
        self.validate_numeric("POLYMARKET_SIGNATURE_TYPE", os.getenv("POLYMARKET_SIGNATURE_TYPE", ""), min_val=0, max_val=2)
        
        # Check signature type vs funder address
        sig_type = os.getenv("POLYMARKET_SIGNATURE_TYPE", "0")
        funder = os.getenv("POLYMARKET_FUNDER_ADDRESS", "")
        
        if sig_type in ["1", "2"] and not funder:
            self.errors.append("POLYMARKET_FUNDER_ADDRESS required when using proxy wallet (signature_type=1 or 2)")
        
        # Risk warnings
        max_loss = float(os.getenv("MAX_DAILY_LOSS", "50"))
        max_trade = float(os.getenv("MAX_TRADE_SIZE", "10"))
        
        if max_loss > 1000:
            self.warnings.append(f"MAX_DAILY_LOSS is high (${max_loss:.2f})")
        
        if max_trade > 100:
            self.warnings.append(f"MAX_TRADE_SIZE is high (${max_trade:.2f})")
        
        is_valid = len(self.errors) == 0
        return is_valid, self.errors, self.warnings
    
    def print_report(self):
        """Print validation report"""
        is_valid, errors, warnings = self.validate_all()
        
        print("\n" + "=" * 60)
        print("🔍 CONFIGURATION VALIDATION REPORT")
        print("=" * 60)
        
        if is_valid:
            print("\n✅ Configuration is VALID")
        else:
            print("\n❌ Configuration has ERRORS")
        
        if errors:
            print("\n🚫 Errors:")
            for error in errors:
                print(f"   • {error}")
        
        if warnings:
            print("\n⚠️  Warnings:")
            for warning in warnings:
                print(f"   • {warning}")
        
        print("\n📋 Current Configuration:")
        print(f"   Chain ID: {os.getenv('POLYMARKET_CHAIN_ID', '137')}")
        print(f"   Max Daily Loss: ${os.getenv('MAX_DAILY_LOSS', '50.0')}")
        print(f"   Max Trade Size: ${os.getenv('MAX_TRADE_SIZE', '10.0')}")
        print(f"   Telegram: {'✅ Enabled' if os.getenv('TELEGRAM_BOT_TOKEN') else '❌ Disabled'}")
        print(f"   Demo Mode: {os.getenv('RUN_DEMO_TRADE', 'false')}")
        
        print("=" * 60)
        
        return is_valid


def main():
    """Run validation"""
    validator = ConfigValidator()
    is_valid = validator.print_report()
    
    return 0 if is_valid else 1


if __name__ == "__main__":
    sys.exit(main())
