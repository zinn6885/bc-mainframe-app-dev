"""
Lambda handler for Day 3 Lab 3 — format Auto Scaling EventBridge events into readable SNS emails.

Deploy to Lambda function FormatASGAlerts (Python 3.9+).
Set environment variable SNS_TOPIC_ARN to your ASG-Alerts topic ARN.
"""

import json
import os
from datetime import datetime

import boto3

sns = boto3.client("sns")
SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN", "")


def lambda_handler(event, context):
    """Format Auto Scaling events into readable email alerts."""

    if not SNS_TOPIC_ARN:
        raise ValueError("SNS_TOPIC_ARN environment variable is not set")

    detail = event.get("detail", {})
    detail_type = event.get("detail-type", "Unknown")

    group_name = detail.get("AutoScalingGroupName", "Unknown")
    instance_id = detail.get("EC2InstanceId", "Unknown")
    cause = detail.get("Cause", "Unknown")
    status_code = detail.get("StatusCode", "Unknown")
    status_message = detail.get("StatusMessage", "No additional info")
    timestamp = event.get("time", datetime.now().isoformat())

    if "Launch" in detail_type:
        event_emoji = "🟢"
        event_title = "INSTANCE LAUNCHED"
    elif "Terminate" in detail_type:
        event_emoji = "🔴"
        event_title = "INSTANCE TERMINATED"
    else:
        event_emoji = "🔵"
        event_title = "AUTO SCALING EVENT"

    message = f"""
{event_emoji} {event_title}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Event Type: {detail_type}
Auto Scaling Group: {group_name}
Instance ID: {instance_id}
Time: {timestamp}

Cause: {cause}
Status: {status_code} - {status_message}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
View in AWS Console: https://console.aws.amazon.com/ec2/home?region=us-east-1#Instances:
"""

    response = sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject=f"ASG Alert: {event_title} - {group_name}",
        Message=message,
    )

    print(f"Sent alert to SNS: {response['MessageId']}")

    return {
        "statusCode": 200,
        "body": json.dumps(f"Alert sent for {detail_type}"),
    }
