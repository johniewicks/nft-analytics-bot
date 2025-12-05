import hashlib
import os
import sys

class TamperDetector:
    def __init__(self):
        self.expected_hashes = {
            'bot.py': 'a1b2c3...',  # Pre-calculated SHA256
            'requirements.txt': 'd4e5f6...',
            # Add all critical files
        }
        
    def check_integrity(self):
        """Check if files have been tampered with"""
        for filename, expected_hash in self.expected_hashes.items():
            filepath = os.path.join(os.path.dirname(__file__), '..', filename)
            if os.path.exists(filepath):
                current_hash = self.calculate_hash(filepath)
                if current_hash != expected_hash:
                    self.log_tampering(filename, current_hash)
                    return False
        return True
    
    def calculate_hash(self, filepath):
        """Calculate SHA256 hash of file"""
        sha256 = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def log_tampering(self, filename, found_hash):
        """Log tampering attempt"""
        import logging
        logging.critical(f"TAMPERING DETECTED: {filename}")
        logging.critical(f"Expected: {self.expected_hashes[filename]}")
        logging.critical(f"Found: {found_hash}")
        
        # Send to security logging service
        self.report_tampering(filename)
    
    def report_tampering(self, filename):
        """Report tampering to your monitoring"""
        import requests
        try:
            requests.post('https://your-monitoring.com/alert', json={
                'event': 'tampering',
                'file': filename,
                'bot_id': os.getenv('BOT_ID'),
                'timestamp': __import__('datetime').datetime.now().isoformat()
            })
        except:
            pass