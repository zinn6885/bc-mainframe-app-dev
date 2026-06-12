#!/usr/bin/env python3
"""Deploy, validate, and tear down Day 3 Lab 1 VPC networking resources."""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.request
from typing import Any

import boto3
from botocore.exceptions import ClientError

REGION = "us-east-1"
VPC_NAME = "Lab1-VPC"
VPC_CIDR = "10.0.0.0/16"
SUBNETS = {
    "Public-Subnet-A": {"cidr": "10.0.1.0/24", "az_suffix": "a"},
    "Private-Subnet-B": {"cidr": "10.0.2.0/24", "az_suffix": "b"},
    "Firewall-Subnet-A": {"cidr": "10.0.3.0/24", "az_suffix": "a"},
}
IGW_NAME = "Lab1-IGW"
RT_NAMES = ("Public-RT", "Private-RT", "Firewall-RT")
NAT_NAME = "Lab1-NAT"
NACL_NAME = "Web-Subnet-NACL"
SG_WEB = "Web-SG"
SG_FW = "Firewall-SG"
FW_NAME = "Lab1-Firewall"
FW_POLICY = "Lab1-Firewall-Policy"
RULE_GROUP = "Allow-Web-Traffic"


def tag(name: str) -> list[dict[str, str]]:
    return [{"Key": "Name", "Value": name}]


def get_my_ip_cidr() -> str:
    try:
        ip = urllib.request.urlopen("https://checkip.amazonaws.com", timeout=5).read().decode().strip()
        return f"{ip}/32"
    except Exception:
        return "0.0.0.0/0"


def ec2_find_by_name(ec2, resource: str, name: str) -> dict[str, Any] | None:
    filters = [{"Name": "tag:Name", "Values": [name]}]
    if resource == "vpc":
        resp = ec2.describe_vpcs(Filters=filters)
        items = resp.get("Vpcs", [])
    elif resource == "subnet":
        resp = ec2.describe_subnets(Filters=filters)
        items = resp.get("Subnets", [])
    elif resource == "igw":
        resp = ec2.describe_internet_gateways(Filters=filters)
        items = resp.get("InternetGateways", [])
    elif resource == "rt":
        resp = ec2.describe_route_tables(Filters=filters)
        items = resp.get("RouteTables", [])
    elif resource == "nat":
        resp = ec2.describe_nat_gateways(
            Filter=[{"Name": "tag:Name", "Values": [name]}, {"Name": "state", "Values": ["pending", "available"]}]
        )
        items = resp.get("NatGateways", [])
    elif resource == "nacl":
        resp = ec2.describe_network_acls(Filters=filters)
        items = resp.get("NetworkAcls", [])
    elif resource == "sg":
        resp = ec2.describe_security_groups(Filters=filters)
        items = resp.get("SecurityGroups", [])
    else:
        raise ValueError(resource)
    return items[0] if items else None


def az_for_suffix(ec2, suffix: str) -> str:
    zones = ec2.describe_availability_zones(Filters=[{"Name": "region-name", "Values": [REGION]}])[
        "AvailabilityZones"
    ]
    for z in zones:
        if z["ZoneName"].endswith(suffix):
            return z["ZoneName"]
    raise RuntimeError(f"No AZ ending with {suffix} in {REGION}")


def wait_nat(ec2, nat_id: str, timeout: int = 300) -> None:
    print(f"Waiting for NAT {nat_id}...")
    deadline = time.time() + timeout
    while time.time() < deadline:
        nat = ec2.describe_nat_gateways(NatGatewayIds=[nat_id])["NatGateways"][0]
        state = nat["State"]
        if state == "available":
            return
        if state in ("failed", "deleted", "deleting"):
            raise RuntimeError(f"NAT {nat_id} entered state {state}")
        time.sleep(10)
    raise TimeoutError(f"NAT {nat_id} not available within {timeout}s")


def wait_firewall(nfw, name: str, timeout: int = 600) -> None:
    print(f"Waiting for firewall {name}...")
    deadline = time.time() + timeout
    while time.time() < deadline:
        resp = nfw.describe_firewall(FirewallName=name)
        status = resp.get("FirewallStatus", {}).get("Status", "UNKNOWN")
        if status == "READY":
            return
        if status in ("DELETING", "DELETED"):
            raise RuntimeError(f"Firewall {name} status {status}")
        print(f"  Firewall status: {status}")
        time.sleep(15)
    raise TimeoutError(f"Firewall {name} not READY within {timeout}s")


def stateful_rules() -> list[dict[str, Any]]:
    specs = [
        ("PASS", "80", "sid:100"),
        ("PASS", "443", "sid:110"),
        ("DROP", "22", "sid:120"),
    ]
    rules = []
    for action, port, sid in specs:
        rules.append(
            {
                "Action": action,
                "Header": {
                    "Protocol": "TCP",
                    "Source": "10.0.0.0/16",
                    "SourcePort": "ANY",
                    "Direction": "ANY",
                    "Destination": "0.0.0.0/0",
                    "DestinationPort": port,
                },
                "RuleOptions": [{"Keyword": sid}],
            }
        )
    return rules


def deploy(my_ip_cidr: str, wait_fw: bool) -> dict[str, Any]:
    ec2 = boto3.client("ec2", region_name=REGION)
    nfw = boto3.client("network-firewall", region_name=REGION)

    if ec2_find_by_name(ec2, "vpc", VPC_NAME):
        raise RuntimeError(f"{VPC_NAME} already exists. Run --teardown first or use --validate-only.")

    vpc = ec2.create_vpc(CidrBlock=VPC_CIDR, TagSpecifications=[{"ResourceType": "vpc", "Tags": tag(VPC_NAME)}])
    vpc_id = vpc["Vpc"]["VpcId"]
    ec2.modify_vpc_attribute(VpcId=vpc_id, EnableDnsHostnames={"Value": True})
    ec2.modify_vpc_attribute(VpcId=vpc_id, EnableDnsSupport={"Value": True})
    print(f"Created VPC {vpc_id}")

    subnet_ids: dict[str, str] = {}
    for sname, spec in SUBNETS.items():
        az = az_for_suffix(ec2, spec["az_suffix"])
        sub = ec2.create_subnet(
            VpcId=vpc_id,
            CidrBlock=spec["cidr"],
            AvailabilityZone=az,
            TagSpecifications=[{"ResourceType": "subnet", "Tags": tag(sname)}],
        )
        subnet_ids[sname] = sub["Subnet"]["SubnetId"]
        print(f"Created subnet {sname} ({subnet_ids[sname]}) in {az}")

    igw = ec2.create_internet_gateway(
        TagSpecifications=[{"ResourceType": "internet-gateway", "Tags": tag(IGW_NAME)}]
    )
    igw_id = igw["InternetGateway"]["InternetGatewayId"]
    ec2.attach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
    print(f"Created and attached IGW {igw_id}")

    rt_ids: dict[str, str] = {}
    for rt_name in RT_NAMES:
        rt = ec2.create_route_table(
            VpcId=vpc_id, TagSpecifications=[{"ResourceType": "route-table", "Tags": tag(rt_name)}]
        )
        rt_ids[rt_name] = rt["RouteTable"]["RouteTableId"]

    ec2.create_route(RouteTableId=rt_ids["Public-RT"], DestinationCidrBlock="0.0.0.0/0", GatewayId=igw_id)
    for assoc in (
        ("Public-RT", "Public-Subnet-A"),
        ("Private-RT", "Private-Subnet-B"),
        ("Firewall-RT", "Firewall-Subnet-A"),
    ):
        ec2.associate_route_table(RouteTableId=rt_ids[assoc[0]], SubnetId=subnet_ids[assoc[1]])
    print("Created route tables and associations")

    eip = ec2.allocate_address(Domain="vpc")
    allocation_id = eip["AllocationId"]
    nat = ec2.create_nat_gateway(
        SubnetId=subnet_ids["Public-Subnet-A"],
        AllocationId=allocation_id,
        TagSpecifications=[{"ResourceType": "natgateway", "Tags": tag(NAT_NAME)}],
    )
    nat_id = nat["NatGateway"]["NatGatewayId"]
    wait_nat(ec2, nat_id)
    ec2.create_route(RouteTableId=rt_ids["Private-RT"], DestinationCidrBlock="0.0.0.0/0", NatGatewayId=nat_id)
    print(f"Created NAT {nat_id}")

    nacl = ec2.create_network_acl(
        VpcId=vpc_id, TagSpecifications=[{"ResourceType": "network-acl", "Tags": tag(NACL_NAME)}]
    )
    nacl_id = nacl["NetworkAcl"]["NetworkAclId"]
    ec2.create_network_acl_entry(
        NetworkAclId=nacl_id,
        RuleNumber=100,
        Protocol="6",
        RuleAction="allow",
        Egress=False,
        CidrBlock="0.0.0.0/0",
        PortRange={"From": 80, "To": 80},
    )
    ec2.create_network_acl_entry(
        NetworkAclId=nacl_id,
        RuleNumber=110,
        Protocol="6",
        RuleAction="allow",
        Egress=False,
        CidrBlock="0.0.0.0/0",
        PortRange={"From": 443, "To": 443},
    )
    ec2.create_network_acl_entry(
        NetworkAclId=nacl_id,
        RuleNumber=120,
        Protocol="6",
        RuleAction="allow",
        Egress=False,
        CidrBlock=my_ip_cidr,
        PortRange={"From": 22, "To": 22},
    )
    ec2.create_network_acl_entry(
        NetworkAclId=nacl_id,
        RuleNumber=130,
        Protocol="6",
        RuleAction="allow",
        Egress=False,
        CidrBlock="0.0.0.0/0",
        PortRange={"From": 1024, "To": 65535},
    )
    ec2.create_network_acl_entry(
        NetworkAclId=nacl_id,
        RuleNumber=200,
        Protocol="-1",
        RuleAction="deny",
        Egress=False,
        CidrBlock="0.0.0.0/0",
    )
    ec2.create_network_acl_entry(
        NetworkAclId=nacl_id,
        RuleNumber=100,
        Protocol="-1",
        RuleAction="allow",
        Egress=True,
        CidrBlock="0.0.0.0/0",
    )
    priv_subnet_id = subnet_ids["Private-Subnet-B"]
    default_assoc = ec2.describe_network_acls(
        Filters=[{"Name": "association.subnet-id", "Values": [priv_subnet_id]}]
    )["NetworkAcls"][0]["Associations"]
    assoc_id = next(a["NetworkAclAssociationId"] for a in default_assoc if a.get("SubnetId") == priv_subnet_id)
    ec2.replace_network_acl_association(AssociationId=assoc_id, NetworkAclId=nacl_id)
    print(f"Created NACL {nacl_id}")

    web_sg = ec2.create_security_group(
        GroupName=SG_WEB,
        Description="Security group for web servers",
        VpcId=vpc_id,
        TagSpecifications=[{"ResourceType": "security-group", "Tags": tag(SG_WEB)}],
    )
    web_sg_id = web_sg["GroupId"]
    ec2.authorize_security_group_ingress(
        GroupId=web_sg_id,
        IpPermissions=[
            {"IpProtocol": "tcp", "FromPort": 80, "ToPort": 80, "IpRanges": [{"CidrIp": "0.0.0.0/0"}]},
            {"IpProtocol": "tcp", "FromPort": 22, "ToPort": 22, "IpRanges": [{"CidrIp": my_ip_cidr}]},
        ],
    )

    fw_sg = ec2.create_security_group(
        GroupName=SG_FW,
        Description="Security group for network firewall",
        VpcId=vpc_id,
        TagSpecifications=[{"ResourceType": "security-group", "Tags": tag(SG_FW)}],
    )
    fw_sg_id = fw_sg["GroupId"]
    ec2.authorize_security_group_ingress(
        GroupId=fw_sg_id,
        IpPermissions=[
            {"IpProtocol": "tcp", "FromPort": 80, "ToPort": 80, "IpRanges": [{"CidrIp": "10.0.0.0/16"}]},
            {"IpProtocol": "tcp", "FromPort": 443, "ToPort": 443, "IpRanges": [{"CidrIp": "10.0.0.0/16"}]},
        ],
    )
    print(f"Created security groups {web_sg_id}, {fw_sg_id}")

    rg = nfw.create_rule_group(
        RuleGroupName=RULE_GROUP,
        RuleGroup={"RulesSource": {"StatefulRules": stateful_rules()}},
        Type="STATEFUL",
        Capacity=100,
        Description="Lab1 allow HTTP/HTTPS, deny SSH",
    )
    rg_arn = rg["RuleGroupResponse"]["RuleGroupArn"]

    policy = nfw.create_firewall_policy(
        FirewallPolicyName=FW_POLICY,
        FirewallPolicy={
            "StatelessDefaultActions": ["aws:forward_to_sfe"],
            "StatelessFragmentDefaultActions": ["aws:forward_to_sfe"],
            "StatefulRuleGroupReferences": [{"ResourceArn": rg_arn}],
        },
        Description="Lab1 firewall policy",
    )
    policy_arn = policy["FirewallPolicyResponse"]["FirewallPolicyArn"]

    nfw.create_firewall(
        FirewallName=FW_NAME,
        FirewallPolicyArn=policy_arn,
        VpcId=vpc_id,
        SubnetMappings=[{"SubnetId": subnet_ids["Firewall-Subnet-A"]}],
        DeleteProtection=False,
        SubnetChangeProtection=False,
        FirewallPolicyChangeProtection=False,
    )
    print(f"Created firewall {FW_NAME}")
    if wait_fw:
        wait_firewall(nfw, FW_NAME)

    return {"vpc_id": vpc_id, "nat_id": nat_id, "firewall": FW_NAME}


def validate() -> tuple[bool, list[str]]:
    ec2 = boto3.client("ec2", region_name=REGION)
    nfw = boto3.client("network-firewall", region_name=REGION)
    results: list[str] = []
    ok = True

    def check(name: str, passed: bool, detail: str = "") -> None:
        nonlocal ok
        status = "PASS" if passed else "FAIL"
        if not passed:
            ok = False
        line = f"{status}: {name}"
        if detail:
            line += f" — {detail}"
        results.append(line)
        print(line)

    vpc = ec2_find_by_name(ec2, "vpc", VPC_NAME)
    check("vpc_exists", vpc is not None and vpc.get("CidrBlock") == VPC_CIDR, vpc.get("CidrBlock") if vpc else "missing")

    if not vpc:
        return ok, results
    vpc_id = vpc["VpcId"]

    for sname, spec in SUBNETS.items():
        sub = ec2_find_by_name(ec2, "subnet", sname)
        good = sub is not None and sub.get("CidrBlock") == spec["cidr"] and sub.get("VpcId") == vpc_id
        check(f"subnet_{sname}", good, sub.get("CidrBlock") if sub else "missing")

    igw = ec2_find_by_name(ec2, "igw", IGW_NAME)
    igw_attached = igw and any(a.get("VpcId") == vpc_id for a in igw.get("Attachments", []))
    check("igw_attached", bool(igw_attached))

    public_rt = ec2_find_by_name(ec2, "rt", "Public-RT")
    igw_route = False
    if public_rt:
        igw_route = any(
            r.get("DestinationCidrBlock") == "0.0.0.0/0" and r.get("GatewayId", "").startswith("igw-")
            for r in public_rt.get("Routes", [])
        )
    check("public_rt_igw_route", igw_route)

    private_rt = ec2_find_by_name(ec2, "rt", "Private-RT")
    nat_route = False
    if private_rt:
        nat_route = any(
            r.get("DestinationCidrBlock") == "0.0.0.0/0" and r.get("NatGatewayId", "").startswith("nat-")
            for r in private_rt.get("Routes", [])
        )
    check("private_rt_nat_route", nat_route)

    nat = ec2_find_by_name(ec2, "nat", NAT_NAME)
    check("nat_available", nat is not None and nat.get("State") == "available", nat.get("State") if nat else "missing")

    nacl = ec2_find_by_name(ec2, "nacl", NACL_NAME)
    nacl_assoc = False
    if nacl:
        priv = ec2_find_by_name(ec2, "subnet", "Private-Subnet-B")
        if priv:
            nacl_assoc = any(a.get("SubnetId") == priv["SubnetId"] for a in nacl.get("Associations", []))
    check("nacl_on_private_subnet", nacl_assoc)

    web_sg = ec2_find_by_name(ec2, "sg", SG_WEB)
    fw_sg = ec2_find_by_name(ec2, "sg", SG_FW)
    check("sg_web_exists", web_sg is not None)
    check("sg_firewall_exists", fw_sg is not None)

    try:
        fw_resp = nfw.describe_firewall(FirewallName=FW_NAME)
        fw = fw_resp.get("Firewall", {})
        fw_status = fw_resp.get("FirewallStatus", {}).get("Status", "UNKNOWN")
        check("firewall_ready", fw_status in ("READY", "PROVISIONING"), fw_status)
        check("firewall_vpc", fw.get("VpcId") == vpc_id, fw.get("VpcId", ""))
    except ClientError as e:
        check("firewall_ready", False, str(e))

    try:
        rg = nfw.describe_rule_group(RuleGroupName=RULE_GROUP, Type="STATEFUL")
        rules = rg["RuleGroup"]["RulesSource"].get("StatefulRules", [])
        check("rule_group_rules", len(rules) >= 3, f"{len(rules)} rules")
    except ClientError as e:
        check("rule_group_rules", False, str(e))

    return ok, results


def teardown() -> None:
    ec2 = boto3.client("ec2", region_name=REGION)
    nfw = boto3.client("network-firewall", region_name=REGION)

    try:
        nfw.delete_firewall(FirewallName=FW_NAME)
        print(f"Deleting firewall {FW_NAME}...")
        for _ in range(60):
            try:
                resp = nfw.describe_firewall(FirewallName=FW_NAME)
                st = resp.get("FirewallStatus", {}).get("Status", "DELETING")
                if st == "DELETED":
                    break
            except ClientError as e:
                if e.response["Error"]["Code"] in ("ResourceNotFoundException", "InvalidRequestException"):
                    break
            time.sleep(15)
        print("Firewall deleted.")
    except ClientError as e:
        if e.response["Error"]["Code"] != "ResourceNotFoundException":
            print(f"Firewall delete: {e}")

    for name in (FW_POLICY,):
        try:
            arn = nfw.describe_firewall_policy(FirewallPolicyName=name)["FirewallPolicyResponse"]["FirewallPolicyArn"]
            nfw.delete_firewall_policy(FirewallPolicyArn=arn)
            print(f"Deleted policy {name}")
        except ClientError:
            pass

    try:
        arn = nfw.describe_rule_group(RuleGroupName=RULE_GROUP, Type="STATEFUL")["RuleGroupResponse"]["RuleGroupArn"]
        nfw.delete_rule_group(RuleGroupArn=arn)
        print(f"Deleted rule group {RULE_GROUP}")
    except ClientError:
        pass

    nat = ec2_find_by_name(ec2, "nat", NAT_NAME)
    if nat:
        ec2.delete_nat_gateway(NatGatewayId=nat["NatGatewayId"])
        print(f"Deleting NAT {nat['NatGatewayId']}...")
        for _ in range(30):
            nats = ec2.describe_nat_gateways(NatGatewayIds=[nat["NatGatewayId"]])["NatGateways"]
            if not nats or nats[0]["State"] == "deleted":
                break
            time.sleep(10)

    for eip in ec2.describe_addresses()["Addresses"]:
        if eip.get("AllocationId") and not eip.get("AssociationId"):
            try:
                ec2.release_address(AllocationId=eip["AllocationId"])
                print(f"Released EIP {eip.get('PublicIp')}")
            except ClientError:
                pass

    igw = ec2_find_by_name(ec2, "igw", IGW_NAME)
    if igw:
        for att in igw.get("Attachments", []):
            ec2.detach_internet_gateway(InternetGatewayId=igw["InternetGatewayId"], VpcId=att["VpcId"])
        ec2.delete_internet_gateway(InternetGatewayId=igw["InternetGatewayId"])
        print(f"Deleted IGW {igw['InternetGatewayId']}")

    vpc = ec2_find_by_name(ec2, "vpc", VPC_NAME)
    if not vpc:
        print("No VPC to delete.")
        return

    vpc_id = vpc["VpcId"]

    for sg_name in (SG_WEB, SG_FW):
        sg = ec2_find_by_name(ec2, "sg", sg_name)
        if sg:
            try:
                ec2.delete_security_group(GroupId=sg["GroupId"])
                print(f"Deleted security group {sg_name}")
            except ClientError as e:
                print(f"SG delete {sg_name}: {e}")

    nacl = ec2_find_by_name(ec2, "nacl", NACL_NAME)
    if nacl and not nacl.get("IsDefault"):
        vpc_nacls = ec2.describe_network_acls(Filters=[{"Name": "vpc-id", "Values": [vpc_id]}])["NetworkAcls"]
        default_nacl_id = next(n["NetworkAclId"] for n in vpc_nacls if n.get("IsDefault"))
        for assoc in nacl.get("Associations", []):
            if assoc.get("SubnetId"):
                ec2.replace_network_acl_association(
                    AssociationId=assoc["NetworkAclAssociationId"],
                    NetworkAclId=default_nacl_id,
                )
        try:
            ec2.delete_network_acl(NetworkAclId=nacl["NetworkAclId"])
            print(f"Deleted NACL {NACL_NAME}")
        except ClientError as e:
            print(f"NACL delete: {e}")

    for sname in SUBNETS:
        sub = ec2_find_by_name(ec2, "subnet", sname)
        if sub:
            try:
                ec2.delete_subnet(SubnetId=sub["SubnetId"])
                print(f"Deleted subnet {sname}")
            except ClientError as e:
                print(f"Subnet delete {sname}: {e}")

    for rt_name in RT_NAMES:
        rt = ec2_find_by_name(ec2, "rt", rt_name)
        if rt:
            try:
                ec2.delete_route_table(RouteTableId=rt["RouteTableId"])
                print(f"Deleted route table {rt_name}")
            except ClientError as e:
                print(f"RT delete {rt_name}: {e}")

    try:
        ec2.delete_vpc(VpcId=vpc_id)
        print(f"Deleted VPC {vpc_id}")
    except ClientError as e:
        print(f"VPC delete failed: {e}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Day 3 Lab 1 VPC — deploy, validate, teardown")
    parser.add_argument("--deploy", action="store_true", help="Create all lab resources")
    parser.add_argument("--validate-only", action="store_true", help="Validate existing resources")
    parser.add_argument("--teardown", action="store_true", help="Delete lab resources")
    parser.add_argument("--wait-firewall", action="store_true", help="Wait for firewall READY after deploy")
    parser.add_argument("--my-ip", default=None, help="CIDR for SSH rules (default: auto-detect)")
    args = parser.parse_args()

    if not any([args.deploy, args.validate_only, args.teardown]):
        args.validate_only = True

    my_ip = args.my_ip or get_my_ip_cidr()

    if args.teardown:
        teardown()
        return 0

    if args.deploy:
        info = deploy(my_ip, args.wait_firewall)
        print(json.dumps(info, indent=2))

    ok, _ = validate()
    print("\n=== SUMMARY ===")
    print("AWS_LAB1_VPC_TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
