#!/usr/bin/env python3
"""
Setup script for Polymarket Trading Bot
Helps configure environment and verify installation.
"""

import os
import sys
import subprocess


def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True


def install_dependencies():
    """Install required packages"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def setup_env():
    """Create .env file from example"""
    if os.path.exists(".env"):
        print("⚠️  .env already exists")
        return True
    
    print("\n🔧 Setting up environment...")
    
    # Copy example
    with open(".env.example", "r") as f:
        template = f.read()
    
    # Get user input
    print("\nEnter your configuration (press Enter to skip):")
    
    private_key = input("Private Key (will be hidden in .env): ").strip()
    bot_token = input("Telegram Bot Token: ").strip()
    chat_id = input(f"Telegram Chat ID [default: -1003743622774]: ").strip() or "-1003743622774"
    thread_id = input("Telegram Thread ID [optional]: ").strip()
    
    # Fill template
    env_content = template
    if private_key:
        env_content = env_content.replace("your_private_key_here", private_key)
    if bot_token:
        env_content = env_content.replace("your_bot_token_here", bot_token)
    env_content = env_content.replace("-1003743622774", chat_id)
    if thread_id:
        env_content = env_content.replace("# TELEGRAM_THREAD_ID=409", f"TELEGRAM_THREAD_ID={thread_id}")
    
    # Write .env
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("✅ .env file created")
    return True


def test_imports():
    """Test that all imports work"""
    print("\n🧪 Testing imports...")
    try:
        from py_clob_client.client import ClobClient
        from py_clob_client.clob_types import MarketOrderArgs
        import requests
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def main():
    """Main setup"""
    print("=" * 50)
    print("🤖 Polymarket Trading Bot Setup")
    print("=" * 50)
    
    # Check Python
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Test imports
    if not test_imports():
        sys.exit(1)
    
    # Setup environment
    setup_env()
    
    print("\n" + "=" * 50)
    print("✅ Setup complete!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Edit .env file with your credentials")
    print("2. Run: python polymarket_bot.py")
    print("3. Or run with demo trade: RUN_DEMO_TRADE=true python polymarket_bot.py")
    print("\n⚠️  Remember: Never commit your .env file to git!")


if __name__ == "__main__":
    main()
