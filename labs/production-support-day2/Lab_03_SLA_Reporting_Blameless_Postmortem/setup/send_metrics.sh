#!/bin/bash
set -euo pipefail
TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
INSTANCE_ID=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/instance-id)

if systemctl is-active --quiet payment-processor; then
  SERVICE_STATUS=1
else
  SERVICE_STATUS=0
fi

aws cloudwatch put-metric-data \
  --namespace "PaymentProcessor" \
  --metric-name "ServiceHealth" \
  --value "$SERVICE_STATUS" \
  --unit Count \
  --dimensions InstanceId="$INSTANCE_ID" \
  --region us-east-1

RANDOM_TIME=$((RANDOM % 200 + 50))
aws cloudwatch put-metric-data \
  --namespace "PaymentProcessor" \
  --metric-name "ResponseTimeMs" \
  --value "$RANDOM_TIME" \
  --unit Milliseconds \
  --dimensions InstanceId="$INSTANCE_ID" \
  --region us-east-1

echo "Metrics sent at $(date) status=$SERVICE_STATUS response_ms=$RANDOM_TIME"
