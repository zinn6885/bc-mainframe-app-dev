#!/bin/bash
# Lab 2 — Auto Scaling web server bootstrap (Amazon Linux 2023)
set -euo pipefail

yum update -y
yum install -y httpd
systemctl start httpd
systemctl enable httpd

# IMDSv2-compatible metadata (works on AL2023 default settings)
TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" \
  -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
INSTANCE_ID=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" \
  http://169.254.169.254/latest/meta-data/instance-id)
AVAILABILITY_ZONE=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" \
  http://169.254.169.254/latest/meta-data/placement/availability-zone)
PRIVATE_IP=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" \
  http://169.254.169.254/latest/meta-data/local-ipv4)

cat << EOF > /var/www/html/index.html
<!DOCTYPE html>
<html>
<head>
    <title>Auto Scaling Demo</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 50px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .container {
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            padding: 30px;
            display: inline-block;
        }
        .instance-details {
            text-align: left;
            background: rgba(0,0,0,0.3);
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
        }
        h1 { color: #ffd700; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Auto Scaling Group Demo</h1>
        <h2>Instance Details</h2>
        <div class="instance-details">
            <p><strong>Instance ID:</strong> $INSTANCE_ID</p>
            <p><strong>Availability Zone:</strong> $AVAILABILITY_ZONE</p>
            <p><strong>Private IP:</strong> $PRIVATE_IP</p>
            <p><strong>Server Time:</strong> $(date)</p>
        </div>
        <p>This server is part of an Auto Scaling Group</p>
        <p><small>If you terminate me, I will be automatically replaced!</small></p>
    </div>
</body>
</html>
EOF

chmod 644 /var/www/html/index.html
echo "Web server setup complete" > /tmp/setup.log
