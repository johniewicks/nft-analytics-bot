import os
import sys
import logging
from telegram.ext import Application
from protection.license_manager import LicenseValidator
from protection.tamper_detection import TamperDetector

class SecureBot:
    def __init__(self):
        # Security checks
        self.license = LicenseValidator()
        self.tamper = TamperDetector()
        
        # Validate before anything else
        if not self.security_check():
            sys.exit(1)
            
        # Initialize bot
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.app = Application.builder().token(self.token).build()
        
    def security_check(self):
        """Run all security checks"""
        checks = [
            self.license.validate_license(),
            self.tamper.check_integrity(),
            self.check_environment(),
            self.detect_debugging()
        ]
        
        if not all(checks):
            logging.error("SECURITY CHECK FAILED - Bot shutting down")
            
            # Notify owner
            self.send_alert("🚨 Security breach detected!")
            
            # Wipe sensitive data
            self.cleanup()
            
            return False
        return True
    
    def check_environment(self):
        """Check if running in authorized environment"""
        allowed_domains = [
            'railway.app',
            'up.railway.app',
            'localhost'  # For development
        ]
        
        hostname = os.getenv('RAILWAY_PUBLIC_DOMAIN', '')
        return any(domain in hostname for domain in allowed_domains)
    
    def detect_debugging(self):
        """Detect if running in debug mode"""
        import sys
        trace_func = getattr(sys, 'gettrace', None)
        if trace_func and trace_func():
            return False  # Debugger detected
        return True
    
    def send_alert(self, message):
        """Send security alert to owner"""
        owner_id = os.getenv('OWNER_TELEGRAM_ID')
        if owner_id:
            try:
                self.app.bot.send_message(
                    chat_id=owner_id,
                    text=f"🚨 BOT SECURITY ALERT\n\n{message}"
                )
            except:
                pass
    
    def cleanup(self):
        """Remove sensitive data"""
        sensitive_vars = [
            'TELEGRAM_BOT_TOKEN',
            'STRIPE_API_KEY',
            'DATABASE_URL',
            'LICENSE_KEY'
        ]
        
        for var in sensitive_vars:
            if var in os.environ:
                os.environ[var] = 'REDACTED'
    
    def run(self):
        """Start the bot with security monitoring"""
        # Start license heartbeat in background
        import threading
        heartbeat_thread = threading.Thread(target=self.license_heartbeat)
        heartbeat_thread.daemon = True
        heartbeat_thread.start()
        
        # Start bot
        self.app.run_polling()
    
    def license_heartbeat(self):
        """Regular license check"""
        import time
        while True:
            time.sleep(3600)  # Every hour
            if not self.license.validate_license():
                logging.error("License invalid - shutting down")
                os._exit(1)
            self.license.heartbeat()

if __name__ == '__main__':
    bot = SecureBot()
    bot.run()