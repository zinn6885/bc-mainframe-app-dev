#!/usr/bin/env python3
"""Execute Day 3 Lab 2 Step 1: verify Lab 1 resources and create HA subnets."""

from __future__ import annotations

import sys

import boto3
from botocore.exceptions import ClientError

REGION = "us-east-1"
VPC_NAME = "Lab1-VPC"
VPC_CIDR = "10.0.0.0/16"

PRIVATE_SUBNET = {
    "name": "Private-Subnet-C",
    "az": "us-east-1c",
    "cidr": "10.0.4.0/24",
    "rt_name": "Private-RT",
}
PUBLIC_SUBNET = {
    "name": "Public-Subnet-C",
    "az": "us-east-1c",
    "cidr": "10.0.5.0/24",
    "rt_name": "Public-RT",
}


def tag_map(tags: list[dict] | None) -> dict[str, str]:
    if not tags:
        return {}
    return {t["Key"]: t["Value"] for t in tags}


def find_vpc(ec2) -> dict:
    resp = ec2.describe_vpcs(
        Filters=[{"Name": "tag:Name", "Values": [VPC_NAME]}]
    )
    for vpc in resp["Vpcs"]:
        if vpc.get("CidrBlock") == VPC_CIDR:
            return vpc
    raise RuntimeError(f"VPC {VPC_NAME} ({VPC_CIDR}) not found")


def find_subnets_by_name(ec2, vpc_id: str) -> dict[str, dict]:
    resp = ec2.describe_subnets(Filters=[{"Name": "vpc-id", "Values": [vpc_id]}])
    result: dict[str, dict] = {}
    for subnet in resp["Subnets"]:
        name = tag_map(subnet.get("Tags")).get("Name")
        if name:
            result[name] = subnet
    return result


def find_route_table(ec2, vpc_id: str, name: str) -> dict:
    resp = ec2.describe_route_tables(
        Filters=[
            {"Name": "vpc-id", "Values": [vpc_id]},
            {"Name": "tag:Name", "Values": [name]},
        ]
    )
    tables = resp.get("RouteTables", [])
    if not tables:
        raise RuntimeError(f"Route table {name} not found")
    return tables[0]


def subnet_associated(rt: dict, subnet_id: str) -> bool:
    return any(
        a.get("SubnetId") == subnet_id
        for a in rt.get("Associations", [])
    )


def create_subnet(ec2, vpc_id: str, spec: dict) -> dict:
    resp = ec2.create_subnet(
        TagSpecifications=[
            {
                "ResourceType": "subnet",
                "Tags": [{"Key": "Name", "Value": spec["name"]}],
            }
        ],
        VpcId=vpc_id,
        AvailabilityZone=spec["az"],
        CidrBlock=spec["cidr"],
    )
    subnet = resp["Subnet"]
    print(f"CREATED {spec['name']}: {subnet['SubnetId']} ({spec['az']}, {spec['cidr']})")
    return subnet


def associate_subnet(ec2, rt_id: str, subnet_id: str, name: str) -> None:
    ec2.associate_route_table(RouteTableId=rt_id, SubnetId=subnet_id)
    print(f"ASSOCIATED {name} with route table {rt_id}")


def ensure_subnet(ec2, vpc_id: str, spec: dict, subnets: dict[str, dict]) -> dict:
    existing = subnets.get(spec["name"])
    if existing:
        print(
            f"EXISTS  {spec['name']}: {existing['SubnetId']} "
            f"({existing['AvailabilityZone']}, {existing['CidrBlock']})"
        )
        return existing

    subnet = create_subnet(ec2, vpc_id, spec)
    subnets[spec["name"]] = subnet
    return subnet


def ensure_rt_association(ec2, vpc_id: str, spec: dict, subnet: dict) -> None:
    rt = find_route_table(ec2, vpc_id, spec["rt_name"])
    if subnet_associated(rt, subnet["SubnetId"]):
        print(f"EXISTS  {spec['name']} already on {spec['rt_name']}")
        return
    associate_subnet(ec2, rt["RouteTableId"], subnet["SubnetId"], spec["name"])


def verify_web_sg(ec2, vpc_id: str) -> None:
    resp = ec2.describe_security_groups(
        Filters=[
            {"Name": "vpc-id", "Values": [vpc_id]},
            {"Name": "group-name", "Values": ["Web-SG"]},
        ]
    )
    groups = resp.get("SecurityGroups", [])
    if not groups:
        raise RuntimeError("Web-SG not found")
    sg = groups[0]
    http_ok = any(
        perm.get("IpProtocol") == "tcp"
        and perm.get("FromPort", 0) <= 80 <= perm.get("ToPort", 0)
        and any(r.get("CidrIp") == "0.0.0.0/0" for r in perm.get("IpRanges", []))
        for perm in sg.get("IpPermissions", [])
    )
    if not http_ok:
        raise RuntimeError("Web-SG missing inbound HTTP:80 from 0.0.0.0/0")
    print(f"VERIFIED Web-SG ({sg['GroupId']}) allows HTTP:80")


def print_summary(subnets: dict[str, dict]) -> None:
    print("\n=== Step 1 Summary ===")
    required = [
        "Public-Subnet-A",
        "Public-Subnet-C",
        "Private-Subnet-B",
        "Private-Subnet-C",
        "Firewall-Subnet-A",
    ]
    for name in required:
        s = subnets.get(name)
        if s:
            print(
                f"  {name}: {s['AvailabilityZone']} {s['CidrBlock']} ({s['SubnetId']})"
            )
        else:
            print(f"  {name}: MISSING")


def main() -> int:
    ec2 = boto3.client("ec2", region_name=REGION)

    print("=== Step 1A: Verify Lab 1 resources ===")
    vpc = find_vpc(ec2)
    print(f"VERIFIED {VPC_NAME}: {vpc['VpcId']} ({vpc['CidrBlock']}) state={vpc['State']}")

    subnets = find_subnets_by_name(ec2, vpc["VpcId"])
    for name in ("Public-Subnet-A", "Private-Subnet-B", "Firewall-Subnet-A"):
        if name not in subnets:
            raise RuntimeError(f"Lab 1 subnet {name} not found — complete Lab 1 first")
        s = subnets[name]
        print(f"VERIFIED {name}: {s['AvailabilityZone']} {s['CidrBlock']}")

    verify_web_sg(ec2, vpc["VpcId"])

    print("\n=== Step 1B: Private-Subnet-C ===")
    private = ensure_subnet(ec2, vpc["VpcId"], PRIVATE_SUBNET, subnets)
    ensure_rt_association(ec2, vpc["VpcId"], PRIVATE_SUBNET, private)

    print("\n=== Step 1C: Public-Subnet-C ===")
    public = ensure_subnet(ec2, vpc["VpcId"], PUBLIC_SUBNET, subnets)
    ensure_rt_association(ec2, vpc["VpcId"], PUBLIC_SUBNET, public)

    subnets = find_subnets_by_name(ec2, vpc["VpcId"])
    print_summary(subnets)
    print('\nCheckpoint: "Step 1 completed"')
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ClientError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
