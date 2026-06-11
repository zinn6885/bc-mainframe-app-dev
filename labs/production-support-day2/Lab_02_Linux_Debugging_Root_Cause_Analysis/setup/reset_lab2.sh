#!/bin/bash
# Reset Lab 2 environment for the next student or session

set -euo pipefail

echo "=== Resetting Lab 2 Environment ==="

# Stop payment-processor if running
sudo systemctl stop payment-processor.service 2>/dev/null || true

# Kill rogue process on port 8080
ROGUE_PID=$(pgrep -f '/opt/rogue-process.py' | head -1)
if [ -z "${ROGUE_PID}" ]; then
  ROGUE_PID=$(sudo ss -tulpn | grep ':8080' | sed -n 's/.*pid=\([0-9]*\).*/\1/p' | head -1)
fi
if [ -n "${ROGUE_PID}" ]; then
  sudo kill -9 "${ROGUE_PID}" 2>/dev/null || true
fi
sudo pkill -f '/opt/rogue-process.py' 2>/dev/null || true

# Recreate broken state
sudo nohup python3 /opt/rogue-process.py > /var/log/rogue-process.log 2>&1 &
sleep 2
sudo systemctl start payment-processor.service 2>/dev/null || true

echo "Environment reset. Ready for next student."
