#!/usr/bin/env python3
"""Validate Day 3 Lab 2 prerequisites and Auto Scaling stack in us-east-1."""

from __future__ import annotations

import argparse
import sys
import urllib.error
import urllib.request

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

REGION = "us-east-1"
VPC_NAME = "Lab1-VPC"
VPC_CIDR = "10.0.0.0/16"

PUBLIC_SUBNETS = {
    "Public-Subnet-A": ("us-east-1a", "10.0.1.0/24"),
    "Public-Subnet-B": ("us-east-1b", "10.0.6.0/24"),
    "Public-Subnet-C": ("us-east-1c", "10.0.5.0/24"),
}
ALB_PUBLIC_SUBNETS = ("Public-Subnet-B", "Public-Subnet-C")
PRIVATE_SUBNETS = {
    "Private-Subnet-B": ("us-east-1b", "10.0.2.0/24"),
    "Private-Subnet-C": ("us-east-1c", "10.0.4.0/24"),
}

WEB_SG_NAME = "Web-SG"
PRIVATE_RT_NAME = "Private-RT"
NAT_NAME = "Lab1-NAT"

LT_NAME = "WebServer-LT"
TG_NAME = "ASG-TG"
ALB_NAME = "ASG-ALB"
ASG_NAME = "WebServer-ASG"


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


def tag_map(tags: list[dict] | None) -> dict[str, str]:
    if not tags:
        return {}
    return {t["Key"]: t["Value"] for t in tags}


def find_vpc(ec2) -> dict | None:
    resp = ec2.describe_vpcs(
        Filters=[{"Name": "tag:Name", "Values": [VPC_NAME]}]
    )
    for vpc in resp["Vpcs"]:
        if vpc.get("CidrBlock") == VPC_CIDR:
            return vpc
    return None


def find_subnets_by_name(ec2, vpc_id: str) -> dict[str, dict]:
    resp = ec2.describe_subnets(
        Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
    )
    result: dict[str, dict] = {}
    for subnet in resp["Subnets"]:
        name = tag_map(subnet.get("Tags")).get("Name")
        if name:
            result[name] = subnet
    return result


def find_sg_by_name(ec2, vpc_id: str, name: str) -> dict | None:
    resp = ec2.describe_security_groups(
        Filters=[
            {"Name": "vpc-id", "Values": [vpc_id]},
            {"Name": "group-name", "Values": [name]},
        ]
    )
    groups = resp.get("SecurityGroups", [])
    return groups[0] if groups else None


def check_subnets(result: CheckResult, subnets: dict[str, dict], expected: dict[str, tuple[str, str]]) -> None:
    for name, (az, cidr) in expected.items():
        subnet = subnets.get(name)
        if not subnet:
            result.fail(f"Subnet {name} not found in {VPC_NAME}")
            continue
        actual_az = subnet["AvailabilityZone"]
        actual_cidr = subnet["CidrBlock"]
        if actual_az != az or actual_cidr != cidr:
            result.fail(
                f"Subnet {name}: expected {az}/{cidr}, got {actual_az}/{actual_cidr}"
            )
        else:
            result.ok(f"{name} in {az} ({cidr})")


def check_web_sg(result: CheckResult, sg: dict | None) -> None:
    if not sg:
        result.fail(f"Security group {WEB_SG_NAME} not found")
        return
    http_ok = False
    for perm in sg.get("IpPermissions", []):
        if perm.get("IpProtocol") == "tcp":
            from_port = perm.get("FromPort", 0)
            to_port = perm.get("ToPort", 0)
            if from_port <= 80 <= to_port:
                for r in perm.get("IpRanges", []):
                    if r.get("CidrIp") in ("0.0.0.0/0", "::/0"):
                        http_ok = True
    if http_ok:
        result.ok(f"{WEB_SG_NAME} allows HTTP:80")
    else:
        result.fail(f"{WEB_SG_NAME} missing inbound HTTP:80 from 0.0.0.0/0")


def check_private_rt_nat(result: CheckResult, ec2, vpc_id: str) -> None:
    resp = ec2.describe_route_tables(
        Filters=[
            {"Name": "vpc-id", "Values": [vpc_id]},
            {"Name": "tag:Name", "Values": [PRIVATE_RT_NAME]},
        ]
    )
    tables = resp.get("RouteTables", [])
    if not tables:
        result.fail(f"Route table {PRIVATE_RT_NAME} not found")
        return
    rt = tables[0]
    nat_route = any(
        r.get("DestinationCidrBlock") == "0.0.0.0/0" and r.get("NatGatewayId")
        for r in rt.get("Routes", [])
    )
    if nat_route:
        result.ok(f"{PRIVATE_RT_NAME} has NAT route 0.0.0.0/0")
    else:
        result.fail(f"{PRIVATE_RT_NAME} missing 0.0.0.0/0 → NAT route")


def check_prerequisites(ec2, result: CheckResult) -> dict | None:
    print("=== Lab 2 Prerequisites ===")
    vpc = find_vpc(ec2)
    if not vpc:
        result.fail(f"VPC {VPC_NAME} ({VPC_CIDR}) not found")
        return None
    result.ok(f"VPC {VPC_NAME} exists ({vpc['VpcId']})")

    subnets = find_subnets_by_name(ec2, vpc["VpcId"])
    check_subnets(result, subnets, PUBLIC_SUBNETS)
    check_subnets(result, subnets, PRIVATE_SUBNETS)

    web_sg = find_sg_by_name(ec2, vpc["VpcId"], WEB_SG_NAME)
    check_web_sg(result, web_sg)
    check_private_rt_nat(result, ec2, vpc["VpcId"])
    return vpc


def check_launch_template(ec2, result: CheckResult) -> None:
    try:
        resp = ec2.describe_launch_templates(
            LaunchTemplateNames=[LT_NAME]
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "InvalidLaunchTemplateName.NotFoundException":
            result.fail(f"Launch template {LT_NAME} not found")
            return
        raise
    templates = resp.get("LaunchTemplates", [])
    if not templates:
        result.fail(f"Launch template {LT_NAME} not found")
        return
    lt = templates[0]
    result.ok(f"Launch template {LT_NAME} (default v{lt.get('DefaultVersionNumber')})")


def check_target_group(elbv2, vpc_id: str, result: CheckResult) -> str | None:
    resp = elbv2.describe_target_groups(Names=[TG_NAME])
    groups = resp.get("TargetGroups", [])
    if not groups:
        result.fail(f"Target group {TG_NAME} not found")
        return None
    tg = groups[0]
    if tg.get("VpcId") != vpc_id:
        result.fail(f"Target group {TG_NAME} not in {VPC_NAME}")
    elif tg.get("Port") != 80 or tg.get("Protocol") != "HTTP":
        result.fail(f"Target group {TG_NAME} must be HTTP:80")
    else:
        result.ok(f"Target group {TG_NAME}")
    return tg["TargetGroupArn"]


def check_alb_subnets(
    elbv2, subnets: dict[str, dict], result: CheckResult, alb_arn: str
) -> None:
    resp = elbv2.describe_load_balancers(LoadBalancerArns=[alb_arn])
    alb = resp.get("LoadBalancers", [{}])[0]
    alb_subnet_ids = {az["SubnetId"] for az in alb.get("AvailabilityZones", [])}
    expected_ids = {
        subnets[name]["SubnetId"]
        for name in ALB_PUBLIC_SUBNETS
        if name in subnets
    }
    if expected_ids and not expected_ids.issubset(alb_subnet_ids):
        result.fail(
            f"ALB {ALB_NAME} must use {ALB_PUBLIC_SUBNETS} "
            f"(got subnet IDs {alb_subnet_ids})"
        )
    elif expected_ids:
        result.ok(f"ALB uses {ALB_PUBLIC_SUBNETS}")


def check_alb(elbv2, vpc_id: str, result: CheckResult) -> str | None:
    resp = elbv2.describe_load_balancers(Names=[ALB_NAME])
    lbs = resp.get("LoadBalancers", [])
    if not lbs:
        result.fail(f"Load balancer {ALB_NAME} not found")
        return None
    alb = lbs[0]
    state = alb.get("State", {}).get("Code", "unknown")
    if alb.get("VpcId") != vpc_id:
        result.fail(f"ALB {ALB_NAME} not in {VPC_NAME}")
    elif state != "active":
        result.fail(f"ALB {ALB_NAME} state is {state} (expected active)")
    else:
        result.ok(f"Load balancer {ALB_NAME} (active)")
    dns = alb.get("DNSName")
    azs = alb.get("AvailabilityZones", [])
    if len(azs) < 2:
        result.fail(f"ALB {ALB_NAME} must span at least 2 AZs (has {len(azs)})")
    else:
        result.ok(f"ALB spans {len(azs)} availability zones")
    return dns


def check_asg(asg_client, result: CheckResult) -> None:
    resp = asg_client.describe_auto_scaling_groups(AutoScalingGroupNames=[ASG_NAME])
    groups = resp.get("AutoScalingGroups", [])
    if not groups:
        result.fail(f"Auto Scaling group {ASG_NAME} not found")
        return
    group = groups[0]
    min_s = group.get("MinSize")
    max_s = group.get("MaxSize")
    desired = group.get("DesiredCapacity")
    if (min_s, desired, max_s) != (2, 2, 6):
        result.fail(f"ASG capacity {min_s}/{desired}/{max_s} (expected 2/2/6)")
    else:
        result.ok(f"Auto Scaling group {ASG_NAME} (2/2/6)")

    azs = group.get("AvailabilityZones", [])
    if len(azs) < 2:
        result.fail(f"ASG must use at least 2 AZs (has {len(azs)})")
    else:
        result.ok(f"ASG spans {len(azs)} availability zones")

    hc = group.get("HealthCheckType", "")
    if hc != "ELB":
        result.fail(f"ASG health check type is {hc} (expected ELB)")
    else:
        result.ok("ASG uses ELB health checks")

    tg_attached = any(
        tg.get("TargetGroupARN", "").endswith(TG_NAME) or TG_NAME in tg.get("TargetGroupARN", "")
        for tg in group.get("TargetGroupARNs", [])
    )
    # Target group ARNs don't contain name — check count instead
    if not group.get("TargetGroupARNs"):
        result.fail("ASG has no target group attached")
    else:
        result.ok("ASG has target group attached")


def check_target_health(elbv2, tg_arn: str | None, result: CheckResult) -> None:
    if not tg_arn:
        return
    resp = elbv2.describe_target_health(TargetGroupArn=tg_arn)
    targets = resp.get("TargetHealthDescriptions", [])
    healthy = [t for t in targets if t.get("TargetHealth", {}).get("State") == "healthy"]
    if len(healthy) >= 2:
        result.ok(f"Target group has {len(healthy)} healthy targets")
    else:
        result.fail(
            f"Target group has {len(healthy)} healthy targets (expected at least 2)"
        )
    azs = {t.get("Target", {}).get("AvailabilityZone") for t in healthy}
    azs.discard(None)
    if len(azs) >= 2:
        result.ok(f"Healthy targets in {len(azs)} AZs")
    elif healthy:
        result.fail("Healthy targets not spread across multiple AZs")


def check_alb_http(dns: str | None, result: CheckResult) -> None:
    if not dns:
        return
    url = f"http://{dns}/"
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            if resp.status == 200 and "Auto Scaling" in body:
                result.ok(f"ALB HTTP 200 at {dns}")
            else:
                result.fail(f"ALB returned {resp.status} without expected page content")
    except (urllib.error.URLError, TimeoutError) as e:
        result.fail(f"ALB HTTP check failed: {e}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Day 3 Lab 2 ASG stack")
    parser.add_argument(
        "--prerequisites-only",
        action="store_true",
        help="Only validate Lab 1 prerequisites and Step 1 subnets",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate prerequisites and full Lab 2 stack (default)",
    )
    parser.add_argument(
        "--check-alb-url",
        action="store_true",
        help="HTTP GET the ALB DNS and verify demo page",
    )
    args = parser.parse_args()

    if not args.prerequisites_only and not args.validate_only and not args.check_alb_url:
        args.validate_only = True

    try:
        session = boto3.Session(region_name=REGION)
        ec2 = session.client("ec2")
        elbv2 = session.client("elbv2")
        asg_client = session.client("autoscaling")
    except NoCredentialsError:
        print("ERROR: AWS credentials not configured.")
        print("Configure credentials (aws configure, env vars, or IAM role) and retry.")
        return 1

    result = CheckResult()
    vpc = check_prerequisites(ec2, result)

    if args.prerequisites_only:
        print()
        if result.passed:
            print("All prerequisite checks passed.")
            return 0
        print(f"{len(result.failures)} check(s) failed.")
        return 1

    if not vpc:
        print(f"\n{len(result.failures)} check(s) failed.")
        return 1

    print("\n=== Lab 2 Resources ===")
    subnets = find_subnets_by_name(ec2, vpc["VpcId"])
    check_launch_template(ec2, result)
    tg_arn = check_target_group(elbv2, vpc["VpcId"], result)
    dns = check_alb(elbv2, vpc["VpcId"], result)
    try:
        alb_arn = elbv2.describe_load_balancers(Names=[ALB_NAME])["LoadBalancers"][0][
            "LoadBalancerArn"
        ]
        check_alb_subnets(elbv2, subnets, result, alb_arn)
    except ClientError:
        pass
    check_asg(asg_client, result)
    check_target_health(elbv2, tg_arn, result)

    if args.check_alb_url:
        print("\n=== ALB HTTP Check ===")
        check_alb_http(dns, result)

    print()
    if result.passed:
        print("All checks passed.")
        return 0
    print(f"{len(result.failures)} check(s) failed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
