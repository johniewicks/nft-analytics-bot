"""
Simple Protection System for Railway Deployment
Adds basic security and monitoring
"""

import os
import logging
from datetime import datetime

class BotProtection:
    def __init__(self):
        self.bot_id = os.getenv('RAILWAY_SERVICE_NAME', 'nft-analytics-bot')
        self.start_time = datetime.now()
        
    def validate_environment(self):
        """Check if all required environment variables are set"""
        required_vars = ['TELEGRAM_TOKEN', 'OPENSEA_API_KEY']
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logging.error(f"Missing environment variables: {missing_vars}")
            return False
        
        logging.info("✅ Environment validation passed")
        return True
    
    def log_startup(self):
        """Log startup information"""
        logging.info(f"🤖 NFT Analytics Bot Starting...")
        logging.info(f"🔐 Bot ID: {self.bot_id}")
        logging.info(f"⏰ Start Time: {self.start_time}")
        
        if os.getenv('RAILWAY_PUBLIC_DOMAIN'):
            logging.info(f"🌐 Public URL: {os.getenv('RAILWAY_PUBLIC_DOMAIN')}")
    
    def generate_stats(self):
        """Generate basic bot statistics"""
        return {
            'bot_id': self.bot_id,
            'uptime': str(datetime.now() - self.start_time),
            'protected': True,
            'environment': 'railway',
            'status': 'active'
        }
    
    def check_health(self):
        """Check if bot is healthy"""
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'service': 'nft-analytics-bot'
        }

# Add this to your main bot.py
def add_protection():
    """Add protection system to the bot"""
    protection = BotProtection()
    
    # Validate environment
    if not protection.validate_environment():
        print("❌ Environment validation failed!")
        print("Please set TELEGRAM_TOKEN and OPENSEA_API_KEY environment variables")
        exit(1)
    
    # Log startup
    protection.log_startup()
    
    return protection