#!/bin/bash
# Lab 2: Create Broken System
# Run as ec2-user on Amazon Linux 2023 after SSH login

set -euo pipefail

echo "=== Creating Lab 2 Broken System ==="

# 1. Create a rogue process that blocks port 8080
echo "Creating rogue process on port 8080..."
sudo tee /opt/rogue-process.py > /dev/null << 'EOF'
#!/usr/bin/env python3
import os
import signal
import socket
import sys

def signal_handler(sig, frame):
    print("Rogue process shutting down...")
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('0.0.0.0', 8080))
sock.listen(5)
print("Rogue process listening on port 8080. PID:", os.getpid())

while True:
    try:
        conn, addr = sock.accept()
        conn.sendall(b"Legacy process running\n")
        conn.close()
    except OSError:
        pass
EOF

sudo chmod +x /opt/rogue-process.py

# Start rogue process (blocks port 8080)
sudo pkill -f rogue-process.py 2>/dev/null || true
sudo nohup python3 /opt/rogue-process.py > /var/log/rogue-process.log 2>&1 &
sleep 2

# 2. Create a broken systemd service
echo "Creating broken payment-processor service..."
sudo tee /etc/systemd/system/payment-processor.service > /dev/null << 'EOF'
[Unit]
Description=Payment Processor Service
After=network.target

[Service]
Type=simple
User=ec2-user
ExecStart=/usr/bin/python3 -m http.server 8080
Restart=no
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# 3. Reload systemd and try to start the service (will fail)
sudo systemctl daemon-reload
sudo systemctl enable payment-processor.service
sudo systemctl start payment-processor.service 2>/dev/null || true

echo ""
echo "=== Broken System Created ==="
echo "What's broken:"
echo "  - payment-processor.service fails to start"
echo "  - Port 8080 is blocked by rogue process"
echo "  - Logs show 'address already in use'"
echo ""
echo "Student tasks:"
echo "  1. systemctl status payment-processor"
echo "  2. journalctl -u payment-processor -n 50"
echo "  3. ss -tulpn | grep 8080"
echo "  4. kill the rogue process"
echo "  5. systemctl restart payment-processor"
echo "  6. Verify with systemctl is-active payment-processor"
