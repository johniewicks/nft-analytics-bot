import hashlib
import requests
import os
from datetime import datetime

class LicenseValidator:
    def __init__(self):
        self.license_key = os.getenv('LICENSE_KEY')
        self.bot_id = os.getenv('BOT_ID', self.generate_bot_id())
        self.license_server = "https://your-license-server.com"  # Your private server
        
    def generate_bot_id(self):
        """Generate unique bot ID based on system"""
        system_info = os.uname()
        bot_hash = hashlib.sha256(
            f"{system_info.nodename}-{system_info.machine}".encode()
        ).hexdigest()[:16]
        return f"BOT-{bot_hash}"
    
    def validate_license(self):
        """Check if bot is properly licensed"""
        # Local validation first
        if not self.license_key:
            return False
        
        # Check against license server
        try:
            response = requests.post(
                f"{self.license_server}/validate",
                json={
                    'license_key': self.license_key,
                    'bot_id': self.bot_id,
                    'timestamp': datetime.now().isoformat()
                },
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('valid', False)
        except:
            # Fallback to offline validation
            return self.offline_validation()
        
        return False
    
    def offline_validation(self):
        """Offline license check"""
        # Create a time-based validation
        import time
        installed_time = os.getenv('INSTALL_TIME')
        if not installed_time:
            return True  # First run
        
        current_time = time.time()
        max_runtime = 30 * 24 * 3600  # 30 days max without license
        
        return (current_time - float(installed_time)) < max_runtime
    
    def heartbeat(self):
        """Send regular heartbeat to license server"""
        try:
            requests.post(
                f"{self.license_server}/heartbeat",
                json={
                    'bot_id': self.bot_id,
                    'status': 'running',
                    'users': self.get_user_count()
                }
            )
        except:
            pass