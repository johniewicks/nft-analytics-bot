"""
Simple Monetization System for NFT Analytics Bot
"""

class NFTBotMonetization:
    def __init__(self):
        self.free_limits = {
            'daily_queries': 10,
            'collections': 12,  # Free users get 12 collections
            'api_calls_per_hour': 30
        }
        
        self.premium_features = {
            'price': 9.99,  # per month
            'features': [
                'Unlimited collection tracking',
                'Real-time alerts',
                'Advanced analytics',
                'Portfolio tracking',
                'Custom watchlists',
                'Historical data',
                'API access',
                'Priority support'
            ]
        }
    
    def check_user_tier(self, user_id):
        """Check user's subscription tier"""
        # In production, you'd check a database
        # For now, everyone gets free access
        return {
            'tier': 'free',
            'remaining_queries': self.free_limits['daily_queries'],
            'upgrade_url': 'https://your-payment-link.com/nft-bot-premium'
        }
    
    def create_upgrade_message(self):
        """Create premium upgrade message"""
        features_text = '\n'.join([f'✅ {feature}' for feature in self.premium_features['features']])
        
        return f"""
🌟 **NFT Analytics Bot Premium**

💰 *Only ${self.premium_features['price']}/month*

{features_text}

🚀 **Perfect for:**
• NFT Traders
• Collection Managers
• Investors
• Researchers

🔗 Upgrade: {self.premium_features.get('upgrade_url', 'Coming soon!')}

📊 *Currently tracking 12+ top collections!*
"""
