#!/bin/bash
# Railway build script with protection

# 1. Remove development files
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +
rm -rf .git tests examples *.md *.txt

# 2. Obfuscate Python code
pip install pyarmor
pyarmor gen --exact -O build/ bot.py

# 3. Generate unique build ID
BUILD_ID=$(date +%s%N | sha256sum | head -c 32)
echo "BUILD_ID=$BUILD_ID" >> .env

# 4. Create startup script
cat > start_encrypted.sh << 'EOF'
#!/bin/bash
# Encrypted startup - prevents code theft

export PYTHONPATH="/app/build"
export SECURE_MODE="1"

# Verify environment
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "ERROR: Bot token not set"
    exit 1
fi

# Check for tampering
CHECKSUM=$(find /app -type f -name "*.py" -exec sha256sum {} \; | sha256sum)
if [ "$CHECKSUM" != "$EXPECTED_CHECKSUM" ]; then
    echo "TAMPERING DETECTED: Code has been modified"
    exit 99
fi

# Run obfuscated bot
python -c "
import os
import sys
sys.path.insert(0, os.getenv('PYTHONPATH', '/app/build'))
from bot import SecureBot
bot = SecureBot()
bot.run()
"
EOF

chmod +x start_encrypted.sh