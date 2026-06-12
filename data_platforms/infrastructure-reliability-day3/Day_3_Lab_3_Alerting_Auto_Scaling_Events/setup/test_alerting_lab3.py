#!/usr/bin/env python3
"""Validate Day 3 Lab 3 alerting stack (SNS, CloudWatch, EventBridge) in us-east-1."""

from __future__ import annotations

import argparse
import json
import sys

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

REGION = "us-east-1"
ASG_NAME = "WebServer-ASG"

SNS_TOPIC_NAME = "ASG-Alerts"
SCALE_OUT_ALARM = "ASG-Scale-Out-Alert"
SCALE_IN_ALARM = "ASG-Scale-In-Alert"
DASHBOARD_NAME = "ASG-Monitoring-Dashboard"
LAUNCH_RULE = "ASG-Instance-Launch-Alert"
TERMINATE_RULE = "ASG-Instance-Terminate-Alert"
LAMBDA_NAME = "FormatASGAlerts"

LAUNCH_PATTERN = {
    "source": ["aws.autoscaling"],
    "detail-type": ["EC2 Instance Launch Successful"],
    "detail": {"AutoScalingGroupName": [ASG_NAME]},
}
TERMINATE_PATTERN = {
    "source": ["aws.autoscaling"],
    "detail-type": ["EC2 Instance Terminate Successful"],
    "detail": {"AutoScalingGroupName": [ASG_NAME]},
}


class CheckResult:
    def __init__(self) -> None:
        self.failures: list[str] = []

    def ok(self, message: str) -> None:
        print(f"PASS  {message}")

    def fail(self, message: str) -> None:
        print(f"FAIL  {message}")
        self.failures.append(message)

    @property
    def passed(self) -> bool:
        return not self.failures


def pattern_matches(actual: dict | str | None, expected: dict) -> bool:
    if actual is None:
        return False
    if isinstance(actual, str):
        try:
            actual = json.loads(actual)
        except json.JSONDecodeError:
            return False
    return actual == expected


def check_asg_prerequisite(asg_client, result: CheckResult) -> None:
    print("=== Lab 3 Prerequisites ===")
    resp = asg_client.describe_auto_scaling_groups(AutoScalingGroupNames=[ASG_NAME])
    groups = resp.get("AutoScalingGroups", [])
    if not groups:
        result.fail(f"Auto Scaling group {ASG_NAME} not found — complete Lab 2 first")
        return
    group = groups[0]
    min_s = group.get("MinSize")
    max_s = group.get("MaxSize")
    desired = group.get("DesiredCapacity")
    if (min_s, desired, max_s) != (2, 2, 6):
        result.fail(f"ASG capacity {min_s}/{desired}/{max_s} (expected 2/2/6)")
    else:
        result.ok(f"Auto Scaling group {ASG_NAME} running (2/2/6)")

    instances = group.get("Instances", [])
    in_service = [i for i in instances if i.get("LifecycleState") == "InService"]
    if len(in_service) >= 2:
        result.ok(f"ASG has {len(in_service)} InService instance(s)")
    else:
        result.fail(f"ASG has {len(in_service)} InService instance(s) (expected at least 2)")


def check_sns(sns, result: CheckResult) -> str | None:
    print("\n=== SNS ===")
    resp = sns.list_topics()
    topic_arn = None
    for topic in resp.get("Topics", []):
        arn = topic["TopicArn"]
        if arn.endswith(f":{SNS_TOPIC_NAME}"):
            topic_arn = arn
            break
    if not topic_arn:
        result.fail(f"SNS topic {SNS_TOPIC_NAME} not found")
        return None
    result.ok(f"SNS topic {SNS_TOPIC_NAME}")

    subs = sns.list_subscriptions_by_topic(TopicArn=topic_arn)
    email_subs = [
        s
        for s in subs.get("Subscriptions", [])
        if s.get("Protocol") == "email"
    ]
    if not email_subs:
        result.fail("No email subscription on ASG-Alerts")
    else:
        confirmed = [s for s in email_subs if s.get("SubscriptionArn") != "PendingConfirmation"]
        if confirmed:
            result.ok(f"Email subscription confirmed ({len(confirmed)})")
        else:
            result.fail("Email subscription pending confirmation — check inbox")
    return topic_arn


def check_cloudwatch_alarms(cw, result: CheckResult) -> None:
    print("\n=== CloudWatch Alarms ===")
    resp = cw.describe_alarms(AlarmNames=[SCALE_OUT_ALARM, SCALE_IN_ALARM])
    alarms = {a["AlarmName"]: a for a in resp.get("MetricAlarms", [])}

    for name, op, threshold in [
        (SCALE_OUT_ALARM, "GreaterThanThreshold", 2.0),
        (SCALE_IN_ALARM, "LessThanThreshold", 2.0),
    ]:
        alarm = alarms.get(name)
        if not alarm:
            result.fail(f"Alarm {name} not found")
            continue
        if alarm.get("ComparisonOperator") != op:
            result.fail(f"{name} comparison operator is {alarm.get('ComparisonOperator')} (expected {op})")
        elif float(alarm.get("Threshold", -1)) != threshold:
            result.fail(f"{name} threshold is {alarm.get('Threshold')} (expected {threshold})")
        else:
            result.ok(f"Alarm {name} ({op}, threshold {int(threshold)})")

        actions = alarm.get("AlarmActions", [])
        if not any(SNS_TOPIC_NAME in a for a in actions):
            result.fail(f"{name} does not notify {SNS_TOPIC_NAME}")
        else:
            result.ok(f"{name} sends to {SNS_TOPIC_NAME}")


def check_eventbridge(events, result: CheckResult) -> None:
    print("\n=== EventBridge Rules ===")
    for rule_name, expected_pattern in [
        (LAUNCH_RULE, LAUNCH_PATTERN),
        (TERMINATE_RULE, TERMINATE_PATTERN),
    ]:
        try:
            resp = events.describe_rule(Name=rule_name)
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                result.fail(f"EventBridge rule {rule_name} not found")
                continue
            raise

        if resp.get("State") != "ENABLED":
            result.fail(f"Rule {rule_name} is not ENABLED")
        else:
            result.ok(f"Rule {rule_name} enabled")

        actual_pattern = resp.get("EventPattern")
        if not pattern_matches(actual_pattern, expected_pattern):
            result.fail(f"Rule {rule_name} event pattern does not match expected JSON")
        else:
            result.ok(f"Rule {rule_name} event pattern correct")

        targets = events.list_targets_by_rule(Rule=rule_name)
        target_list = targets.get("Targets", [])
        if not target_list:
            result.fail(f"Rule {rule_name} has no targets")
            continue
        arn = target_list[0].get("Arn", "")
        if SNS_TOPIC_NAME not in arn:
            result.fail(f"Rule {rule_name} target is not {SNS_TOPIC_NAME}")
        else:
            result.ok(f"Rule {rule_name} targets {SNS_TOPIC_NAME}")


def check_dashboard(cw, result: CheckResult) -> None:
    print("\n=== CloudWatch Dashboard ===")
    try:
        resp = cw.get_dashboard(DashboardName=DASHBOARD_NAME)
    except ClientError as e:
        if e.response["Error"]["Code"] == "DashboardNotFoundError":
            result.fail(f"Dashboard {DASHBOARD_NAME} not found")
            return
        raise

    body = resp.get("DashboardBody", "")
    if not body:
        result.fail(f"Dashboard {DASHBOARD_NAME} is empty")
        return

    try:
        parsed = json.loads(body)
    except json.JSONDecodeError:
        result.fail(f"Dashboard {DASHBOARD_NAME} body is not valid JSON")
        return

    widgets = parsed.get("widgets", [])
    if len(widgets) >= 3:
        result.ok(f"Dashboard {DASHBOARD_NAME} has {len(widgets)} widget(s)")
    else:
        result.fail(f"Dashboard {DASHBOARD_NAME} has {len(widgets)} widget(s) (expected at least 3)")

    metrics_text = body
    for metric in ["GroupDesiredCapacity", "GroupInServiceInstances", "GroupTotalInstances"]:
        if metric in metrics_text:
            result.ok(f"Dashboard includes {metric}")
        else:
            result.fail(f"Dashboard missing metric {metric}")


def check_lambda_optional(lambda_client, result: CheckResult, optional: bool) -> None:
    print("\n=== Lambda (Optional) ===")
    try:
        resp = lambda_client.get_function(FunctionName=LAMBDA_NAME)
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            if optional:
                print(f"SKIP  Lambda {LAMBDA_NAME} not deployed (optional)")
            else:
                result.fail(f"Lambda {LAMBDA_NAME} not found")
            return
        raise

    result.ok(f"Lambda function {LAMBDA_NAME} exists")
    runtime = resp.get("Configuration", {}).get("Runtime", "")
    if runtime.startswith("python3"):
        result.ok(f"Lambda runtime {runtime}")
    else:
        result.fail(f"Lambda runtime {runtime} (expected python3.x)")

    env = resp.get("Configuration", {}).get("Environment", {}).get("Variables", {})
    if env.get("SNS_TOPIC_ARN"):
        result.ok("Lambda has SNS_TOPIC_ARN environment variable")
    else:
        result.fail("Lambda missing SNS_TOPIC_ARN environment variable")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Day 3 Lab 3 alerting stack")
    parser.add_argument(
        "--prerequisites-only",
        action="store_true",
        help="Only validate Lab 2 ASG prerequisite",
    )
    parser.add_argument(
        "--include-lambda",
        action="store_true",
        help="Require optional Lambda function FormatASGAlerts",
    )
    args = parser.parse_args()

    try:
        session = boto3.Session(region_name=REGION)
        asg_client = session.client("autoscaling")
        sns = session.client("sns")
        cw = session.client("cloudwatch")
        events = session.client("events")
        lambda_client = session.client("lambda")
    except NoCredentialsError:
        print("ERROR: AWS credentials not configured.")
        print("Configure credentials (aws configure, env vars, or IAM role) and retry.")
        return 1

    result = CheckResult()
    check_asg_prerequisite(asg_client, result)

    if args.prerequisites_only:
        print()
        if result.passed:
            print("All prerequisite checks passed.")
            return 0
        print(f"{len(result.failures)} check(s) failed.")
        return 1

    check_sns(sns, result)
    check_cloudwatch_alarms(cw, result)
    check_eventbridge(events, result)
    check_dashboard(cw, result)
    check_lambda_optional(lambda_client, result, optional=not args.include_lambda)

    print()
    if result.passed:
        print("All checks passed.")
        return 0
    print(f"{len(result.failures)} check(s) failed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
