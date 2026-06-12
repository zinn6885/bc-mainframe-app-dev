#!/usr/bin/env python3
"""Execute Day 3 Lab 2 Step 2: create WebServer-LT launch template."""

from __future__ import annotations

import base64
import sys
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

REGION = "us-east-1"
VPC_NAME = "Lab1-VPC"
LT_NAME = "WebServer-LT"
LT_VERSION_DESC = "Version 1 - Web Server"
WEB_SG_NAME = "Web-SG"
INSTANCE_TYPE = "t2.micro"
KEY_NAME = "lab-day3-key"
USER_DATA_PATH = Path(__file__).resolve().parent / "user_data.sh"
KEY_PATH = Path(__file__).resolve().parent / f"{KEY_NAME}.pem"


def tag_map(tags: list[dict] | None) -> dict[str, str]:
    if not tags:
        return {}
    return {t["Key"]: t["Value"] for t in tags}


def find_vpc(ec2) -> dict:
    resp = ec2.describe_vpcs(
        Filters=[{"Name": "tag:Name", "Values": [VPC_NAME]}]
    )
    vpcs = resp.get("Vpcs", [])
    if not vpcs:
        raise RuntimeError(f"{VPC_NAME} not found")
    return vpcs[0]


def find_web_sg(ec2, vpc_id: str) -> str:
    resp = ec2.describe_security_groups(
        Filters=[
            {"Name": "vpc-id", "Values": [vpc_id]},
            {"Name": "group-name", "Values": [WEB_SG_NAME]},
        ]
    )
    groups = resp.get("SecurityGroups", [])
    if not groups:
        raise RuntimeError(f"{WEB_SG_NAME} not found")
    return groups[0]["GroupId"]


def find_al2023_ami(ec2) -> str:
    resp = ec2.describe_images(
        Owners=["amazon"],
        Filters=[
            {"Name": "name", "Values": ["al2023-ami-2023*-x86_64"]},
            {"Name": "state", "Values": ["available"]},
        ],
    )
    images = sorted(
        resp.get("Images", []),
        key=lambda image: image["CreationDate"],
        reverse=True,
    )
    if not images:
        raise RuntimeError("Amazon Linux 2023 AMI not found")
    return images[0]["ImageId"]


def ensure_key_pair(ec2) -> str:
    resp = ec2.describe_key_pairs()
    names = {kp["KeyName"] for kp in resp.get("KeyPairs", [])}
    if names:
        key_name = sorted(names)[0]
        print(f"USING  existing key pair: {key_name}")
        return key_name

    create = ec2.create_key_pair(KeyName=KEY_NAME)
    KEY_PATH.write_text(create["KeyMaterial"], encoding="utf-8")
    print(f"CREATED key pair: {KEY_NAME} (saved to {KEY_PATH.name})")
    return KEY_NAME


def load_user_data() -> str:
    if not USER_DATA_PATH.is_file():
        raise RuntimeError(f"Missing user data script: {USER_DATA_PATH}")
    script = USER_DATA_PATH.read_text(encoding="utf-8")
    if not script.startswith("#!/bin/bash"):
        raise RuntimeError("user_data.sh must start with #!/bin/bash")
    return base64.b64encode(script.encode("utf-8")).decode("ascii")


def create_launch_template(ec2, ami_id: str, sg_id: str, key_name: str, user_data_b64: str) -> None:
    ec2.create_launch_template(
        LaunchTemplateName=LT_NAME,
        VersionDescription=LT_VERSION_DESC,
        LaunchTemplateData={
            "ImageId": ami_id,
            "InstanceType": INSTANCE_TYPE,
            "KeyName": key_name,
            "SecurityGroupIds": [sg_id],
            "UserData": user_data_b64,
            "BlockDeviceMappings": [
                {
                    "DeviceName": "/dev/xvda",
                    "Ebs": {
                        "VolumeSize": 8,
                        "VolumeType": "gp2",
                        "DeleteOnTermination": True,
                    },
                }
            ],
        },
    )
    print(f"CREATED launch template: {LT_NAME}")


def verify_launch_template(ec2) -> None:
    resp = ec2.describe_launch_templates(LaunchTemplateNames=[LT_NAME])
    lt = resp["LaunchTemplates"][0]
    version = lt.get("DefaultVersionNumber")
    if version != 1:
        raise RuntimeError(f"{LT_NAME} default version is {version}, expected 1")

    ver_resp = ec2.describe_launch_template_versions(
        LaunchTemplateName=LT_NAME,
        Versions=[str(version)],
    )
    data = ver_resp["LaunchTemplateVersions"][0]["LaunchTemplateData"]
    if data.get("InstanceType") != INSTANCE_TYPE:
        raise RuntimeError(f"Instance type mismatch: {data.get('InstanceType')}")
    if not data.get("UserData"):
        raise RuntimeError("User data missing from launch template")

    print(f"VERIFIED {LT_NAME}: default version {version}")
    print(f"VERIFIED AMI: {data.get('ImageId')}")
    print(f"VERIFIED instance type: {data.get('InstanceType')}")
    print(f"VERIFIED key pair: {data.get('KeyName')}")
    print(f"VERIFIED security groups: {data.get('SecurityGroupIds')}")
    print("VERIFIED user data: present (starts with #!/bin/bash)")


def main() -> int:
    ec2 = boto3.client("ec2", region_name=REGION)

    print("=== Step 2: Create Launch Template ===")
    try:
        ec2.describe_launch_templates(LaunchTemplateNames=[LT_NAME])
    except ClientError as exc:
        if exc.response["Error"]["Code"] != "InvalidLaunchTemplateName.NotFoundException":
            raise
    else:
        print(f"EXISTS  {LT_NAME} already present — verifying")
        verify_launch_template(ec2)
        print('\nCheckpoint: "Step 2 completed"')
        return 0

    vpc = find_vpc(ec2)
    sg_id = find_web_sg(ec2, vpc["VpcId"])
    ami_id = find_al2023_ami(ec2)
    key_name = ensure_key_pair(ec2)
    user_data_b64 = load_user_data()

    print(f"USING  AMI: {ami_id}")
    print(f"USING  security group: {WEB_SG_NAME} ({sg_id})")

    create_launch_template(ec2, ami_id, sg_id, key_name, user_data_b64)
    verify_launch_template(ec2)
    print('\nCheckpoint: "Step 2 completed"')
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ClientError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
