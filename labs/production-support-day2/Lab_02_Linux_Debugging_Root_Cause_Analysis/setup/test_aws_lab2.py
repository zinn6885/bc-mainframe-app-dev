#!/usr/bin/env python3
"""Launch, verify, and optionally tear down Lab 2 AWS EC2 broken system."""

from __future__ import annotations

import argparse
import json
import socket
import sys
import time
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

REGION = "us-east-1"
LAB_TAG = "Lab2-Broken-System-Test"
ROOT = Path(__file__).resolve().parent
USER_DATA = (ROOT / "user_data.sh").read_text(encoding="utf-8")
KEY_PATH = ROOT / "lab2-test-key.pem"


def get_ami(ec2) -> str:
    images = ec2.describe_images(
        Owners=["amazon"],
        Filters=[
            {"Name": "name", "Values": ["al2023-ami-2023.*-x86_64"]},
            {"Name": "state", "Values": ["available"]},
        ],
    )["Images"]
    images.sort(key=lambda x: x["CreationDate"], reverse=True)
    if not images:
        raise RuntimeError("Amazon Linux 2023 AMI not found")
    return images[0]["ImageId"]


def ensure_key_pair(ec2) -> str:
    name = "lab2-broken-system-test"
    try:
        ec2.describe_key_pairs(KeyNames=[name])
        if not KEY_PATH.exists():
            raise RuntimeError(
                f"Key pair '{name}' exists in AWS but {KEY_PATH} is missing locally. "
                "Delete the key pair in AWS or provide the PEM file."
            )
        return name
    except ClientError as e:
        if e.response["Error"]["Code"] != "InvalidKeyPair.NotFound":
            raise

    resp = ec2.create_key_pair(KeyName=name)
    KEY_PATH.write_text(resp["KeyMaterial"], encoding="utf-8")
    print(f"Created key pair '{name}' -> {KEY_PATH}")
    return name


def ensure_security_group(ec2) -> str:
    name = "lab2-broken-system-test-sg"
    try:
        groups = ec2.describe_security_groups(GroupNames=[name])["SecurityGroups"]
        return groups[0]["GroupId"]
    except ClientError as e:
        if e.response["Error"]["Code"] != "InvalidGroup.NotFound":
            raise

    # Get public IP for SSH restriction
    try:
        import urllib.request

        my_ip = urllib.request.urlopen("https://checkip.amazonaws.com", timeout=5).read().decode().strip()
        cidr = f"{my_ip}/32"
    except Exception:
        cidr = "0.0.0.0/0"
        print("Warning: could not detect your IP; opening SSH to 0.0.0.0/0 for test")

    sg = ec2.create_security_group(
        GroupName=name,
        Description="Lab 2 broken system test - SSH only",
    )
    gid = sg["GroupId"]
    ec2.authorize_security_group_ingress(
        GroupId=gid,
        IpPermissions=[
            {
                "IpProtocol": "tcp",
                "FromPort": 22,
                "ToPort": 22,
                "IpRanges": [{"CidrIp": cidr, "Description": "SSH for lab test"}],
            }
        ],
    )
    print(f"Created security group {gid} (SSH from {cidr})")
    return gid


def find_existing(ec2):
    resp = ec2.describe_instances(
        Filters=[
            {"Name": "tag:Name", "Values": [LAB_TAG]},
            {"Name": "instance-state-name", "Values": ["pending", "running", "stopping", "stopped"]},
        ]
    )
    for res in resp["Reservations"]:
        for inst in res["Instances"]:
            return inst
    return None


def wait_running(ec2, instance_id: str, timeout: int = 300) -> dict:
    print(f"Waiting for {instance_id} to be running...")
    waiter = ec2.get_waiter("instance_running")
    waiter.wait(InstanceIds=[instance_id], WaiterConfig={"Delay": 5, "MaxAttempts": timeout // 5})
    return ec2.describe_instances(InstanceIds=[instance_id])["Reservations"][0]["Instances"][0]


def wait_status_ok(ec2, instance_id: str, timeout: int = 300) -> None:
    print("Waiting for status checks...")
    waiter = ec2.get_waiter("instance_status_ok")
    waiter.wait(InstanceIds=[instance_id], WaiterConfig={"Delay": 10, "MaxAttempts": timeout // 10})


def launch(ec2, key_name: str, sg_id: str) -> dict:
    existing = find_existing(ec2)
    if existing:
        print(f"Reusing instance {existing['InstanceId']}")
        if existing["State"]["Name"] == "stopped":
            ec2.start_instances(InstanceIds=[existing["InstanceId"]])
            existing = wait_running(ec2, existing["InstanceId"])
        return existing

    ami = get_ami(ec2)
    print(f"Launching {LAB_TAG} with AMI {ami}")
    resp = ec2.run_instances(
        ImageId=ami,
        InstanceType="t2.micro",
        KeyName=key_name,
        SecurityGroupIds=[sg_id],
        UserData=USER_DATA,
        MinCount=1,
        MaxCount=1,
        TagSpecifications=[
            {
                "ResourceType": "instance",
                "Tags": [
                    {"Key": "Name", "Value": LAB_TAG},
                    {"Key": "Purpose", "Value": "Lab2-Test"},
                ],
            }
        ],
    )
    instance_id = resp["Instances"][0]["InstanceId"]
    return wait_running(ec2, instance_id)


def ssh_verify(host: str, key_path: Path, attempts: int = 12) -> dict:
    import paramiko

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    last_err = None
    for i in range(attempts):
        try:
            client.connect(
                hostname=host,
                username="ec2-user",
                key_filename=str(key_path),
                timeout=20,
                banner_timeout=20,
                auth_timeout=20,
            )
            break
        except Exception as e:
            last_err = e
            print(f"SSH attempt {i + 1}/{attempts} failed: {e}")
            time.sleep(15)
    else:
        raise RuntimeError(f"SSH failed after {attempts} attempts: {last_err}")

    commands = {
        "service_status": "systemctl status payment-processor --no-pager || true",
        "port_8080": "sudo ss -tulpn | grep 8080 || true",
        "rogue_process": "pgrep -af rogue-process.py || true",
        "journal": "sudo journalctl -u payment-processor -n 10 --no-pager || true",
        "setup_log": "cat /var/log/lab2-setup.log 2>/dev/null || echo 'no setup log yet'",
    }
    results = {}
    for name, cmd in commands.items():
        _, stdout, stderr = client.exec_command(cmd, timeout=30)
        out = stdout.read().decode(errors="replace")
        err = stderr.read().decode(errors="replace")
        results[name] = (out + err).strip()
        print(f"\n--- {name} ---\n{results[name][:1500]}")

    # Fix flow
    fix_cmds = """
ROGUE_PID=$(pgrep -f '/opt/rogue-process.py' | head -1)
if [ -z "$ROGUE_PID" ]; then
  ROGUE_PID=$(sudo ss -tulpn | grep ':8080' | sed -n 's/.*pid=\\([0-9]*\\).*/\\1/p' | head -1)
fi
echo "ROGUE_PID=$ROGUE_PID"
sudo kill -9 "$ROGUE_PID"
sleep 3
sudo ss -tulpn | grep 8080 || echo "port 8080 is free"
sudo systemctl reset-failed payment-processor 2>/dev/null || true
sudo systemctl restart payment-processor
sleep 3
systemctl is-active payment-processor
curl -s -o /dev/null -w "HTTP_CODE=%{http_code}" http://localhost:8080 || true
systemctl status payment-processor --no-pager | head -15
"""
    _, stdout, stderr = client.exec_command(fix_cmds, timeout=60)
    fix_out = (stdout.read() + stderr.read()).decode(errors="replace")
    results["fix_flow"] = fix_out.strip()
    print(f"\n--- fix_flow ---\n{results['fix_flow'][:2000]}")

    client.close()

    broken_ok = "8080" in results.get("port_8080", "") and (
        "failed" in results.get("service_status", "").lower()
        or "inactive" in results.get("service_status", "").lower()
    )
    fix_out = results.get("fix_flow", "")
    fixed_ok = (
        "\nactive\n" in f"\n{fix_out.lower()}\n"
        or "active (running)" in fix_out.lower()
        or "http_code=200" in fix_out.lower()
    )
    return {"broken_ok": broken_ok, "fixed_ok": fixed_ok, "results": results}


def terminate(ec2, instance_id: str) -> None:
    print(f"Terminating {instance_id}...")
    ec2.terminate_instances(InstanceIds=[instance_id])
    print("Terminate requested.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Test Lab 2 AWS EC2 setup")
    parser.add_argument("--terminate", action="store_true", help="Terminate test instance after verify")
    parser.add_argument("--launch-only", action="store_true", help="Only launch and print IP")
    args = parser.parse_args()

    ec2 = boto3.client("ec2", region_name=REGION)
    key_name = ensure_key_pair(ec2)
    sg_id = ensure_security_group(ec2)
    inst = launch(ec2, key_name, sg_id)
    instance_id = inst["InstanceId"]
    wait_status_ok(ec2, instance_id)

    public_ip = inst.get("PublicIpAddress")
    if not public_ip:
        inst = ec2.describe_instances(InstanceIds=[instance_id])["Reservations"][0]["Instances"][0]
        public_ip = inst.get("PublicIpAddress")

    print(json.dumps({"instance_id": instance_id, "public_ip": public_ip, "key": str(KEY_PATH)}, indent=2))

    if args.launch_only:
        return 0

    if not public_ip:
        print("FAIL: No public IP assigned")
        return 1

    # Wait for user-data + cloud-init
    print("Waiting 90s for user-data script to complete...")
    time.sleep(90)

    try:
        import paramiko  # noqa: F401
    except ImportError:
        print("Installing paramiko for SSH...")
        import subprocess

        subprocess.check_call([sys.executable, "-m", "pip", "install", "paramiko", "-q"])
        import paramiko  # noqa: F401

    verify = ssh_verify(public_ip, KEY_PATH)
    print("\n=== VERIFICATION ===")
    print(f"broken_state_ok: {verify['broken_ok']}")
    print(f"fix_flow_ok: {verify['fixed_ok']}")

    if args.terminate:
        terminate(ec2, instance_id)

    ok = verify["broken_ok"] and verify["fixed_ok"]
    print("AWS_LAB2_TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
