#!/usr/bin/env python3
"""
Webhook server for receiving trading signals.
Can receive signals from external sources (TradingView, webhooks, etc.)
"""

import os
import json
import logging
from typing import Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from polymarket_bot import PolymarketBot, load_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global bot instance
bot: Optional[PolymarketBot] = None


class WebhookHandler(BaseHTTPRequestHandler):
    """Handle incoming webhook requests"""
    
    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.info(f"{self.client_address[0]} - {format % args}")
    
    def do_GET(self):
        """Handle GET requests"""
        parsed = urlparse(self.path)
        
        if parsed.path == "/health":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
            return
        
        if parsed.path == "/status":
            if bot:
                status = bot.status()
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(status).encode())
            else:
                self.send_error(503, "Bot not initialized")
            return
        
        self.send_error(404)
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == "/webhook/trade":
            self.handle_trade_webhook()
            return
        
        if self.path == "/webhook/signal":
            self.handle_signal_webhook()
            return
        
        self.send_error(404)
    
    def handle_trade_webhook(self):
        """Handle direct trade webhook"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            logger.info(f"Received trade webhook: {data}")
            
            # Validate required fields
            required = ['token_id', 'side', 'size']
            for field in required:
                if field not in data:
                    self.send_error(400, f"Missing field: {field}")
                    return
            
            if not bot:
                self.send_error(503, "Bot not initialized")
                return
            
            # Execute trade
            side = data['side'].upper()
            token_id = data['token_id']
            size = float(data['size'])
            price = float(data.get('price', 0.5))
            
            if side == "BUY":
                result = bot.buy(token_id, size, price)
            else:
                result = bot.sell(token_id, size, price)
            
            if result:
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": True,
                    "order": result
                }).encode())
            else:
                self.send_error(400, "Trade failed")
                
        except Exception as e:
            logger.error(f"Webhook error: {e}")
            self.send_error(500, str(e))
    
    def handle_signal_webhook(self):
        """Handle trading signal webhook"""
        """
        Expected format:
        {
            "market": "Will BTC hit $100k by end of 2025?",
            "signal": "BUY",  # or "SELL"
            "confidence": 0.8,
            "size": 10  # USD amount
        }
        """
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            logger.info(f"Received signal: {data}")
            
            # TODO: Map market name to token_id
            # For now, just log the signal
            
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": True,
                "message": "Signal received (market mapping not implemented)"
            }).encode())
            
        except Exception as e:
            logger.error(f"Signal error: {e}")
            self.send_error(500, str(e))


def run_server(port: int = 8080):
    """Run the webhook server"""
    global bot
    
    # Initialize bot
    logger.info("Initializing bot...")
    config = load_config()
    bot = PolymarketBot(config)
    
    if not bot.initialize():
        logger.error("Failed to initialize bot")
        return 1
    
    # Start server
    server = HTTPServer(('0.0.0.0', port), WebhookHandler)
    logger.info(f"🚀 Webhook server running on port {port}")
    logger.info(f"   Health check: http://localhost:{port}/health")
    logger.info(f"   Status: http://localhost:{port}/status")
    logger.info(f"   Trade webhook: http://localhost:{port}/webhook/trade")
    logger.info(f"   Signal webhook: http://localhost:{port}/webhook/signal")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        server.shutdown()
    
    return 0


if __name__ == "__main__":
    import sys
    port = int(os.getenv("WEBHOOK_PORT", "8080"))
    sys.exit(run_server(port))
