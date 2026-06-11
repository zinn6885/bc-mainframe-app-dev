#!/bin/bash
# User Data script for Lab 2 - Broken System (runs as root at instance launch)

set -euo pipefail

# Create rogue process
cat > /opt/rogue-process.py << 'EOF'
#!/usr/bin/env python3
import os
import signal
import socket
import sys

signal.signal(signal.SIGTERM, lambda s, f: sys.exit(0))
signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('0.0.0.0', 8080))
sock.listen(5)
print("Rogue process listening on port 8080. PID:", os.getpid())

while True:
    try:
        conn, addr = sock.accept()
        conn.sendall(b"Legacy process blocking port 8080\n")
        conn.close()
    except OSError:
        pass
EOF

chmod +x /opt/rogue-process.py
nohup python3 /opt/rogue-process.py > /var/log/rogue-process.log 2>&1 &
sleep 2

# Create broken service
cat > /etc/systemd/system/payment-processor.service << 'EOF'
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

systemctl daemon-reload
systemctl enable payment-processor.service
systemctl start payment-processor.service 2>/dev/null || true

echo "Lab 2 broken system ready" > /var/log/lab2-setup.log
