# Lab 1 — AWS Setup (Instructor)

Complete this **before class** to verify permissions, console paths, and the validation script. Students follow [instructions.md](../instructions.md) in the AWS Console — this guide is for instructors.

**Region:** US East (N. Virginia) — **`us-east-1`**

---

## Prerequisites

| Item | Requirement |
|------|-------------|
| AWS account | IAM user or role with VPC, EC2 (EIP), and Network Firewall permissions |
| Python 3.10+ | For validation script |
| boto3 | `pip install -r setup/requirements.txt` |

### Minimum IAM permissions (student accounts)

Students need permissions equivalent to:

- `ec2:*` (VPC, subnets, IGW, NAT, EIP, NACL, security groups, route tables)
- `network-firewall:*` (firewall, policy, rule groups)

For tighter policies, scope to `us-east-1` and tag-based conditions. For training accounts, a broader VPC + Network Firewall policy is typical.

---

## 1. Install validation script dependencies

From the lab folder (`Day_3_Lab_1_VPC_Networking_Firewall/`):

```powershell
pip install -r setup/requirements.txt
```

Ensure AWS credentials are configured (environment variables, `~/.aws/credentials`, or SSO).

Test credentials:

```powershell
python -c "import boto3; print(boto3.client('sts').get_caller_identity())"
```

---

## 2. Validation script usage

Script: [setup/test_vpc_lab1.py](../setup/test_vpc_lab1.py)

| Command | Purpose |
|---------|---------|
| `python setup/test_vpc_lab1.py --validate-only` | Check existing lab resources by name (after manual build or student submission) |
| `python setup/test_vpc_lab1.py --deploy` | Create all lab resources programmatically (instructor pre-test) |
| `python setup/test_vpc_lab1.py --deploy --wait-firewall` | Deploy and wait for firewall READY (adds ~5–10 min) |
| `python setup/test_vpc_lab1.py --teardown` | Delete lab resources in safe order |

**Recommended pre-class workflow:**

```powershell
# Option A: Validate your own manual walkthrough
python setup/test_vpc_lab1.py --validate-only

# Option B: Full automated deploy + validate + teardown (costs ~$0.45 for ~1 hour; teardown immediately to minimize)
python setup/test_vpc_lab1.py --deploy --wait-firewall
python setup/test_vpc_lab1.py --validate-only
python setup/test_vpc_lab1.py --teardown
```

---

## 3. Manual walkthrough checklist

Follow [instructions.md](../instructions.md) once in the console:

| Step | Verify |
|------|--------|
| 1 | VPC `Lab1-VPC` · 10.0.0.0/16 · Available |
| 2 | Three subnets with correct names, AZs, CIDRs |
| 3 | `Lab1-IGW` attached to Lab1-VPC |
| 4 | Public-RT / Private-RT / Firewall-RT with correct associations; Public-RT has IGW route |
| 5 | `Lab1-NAT` Available in Public-Subnet-A; Private-RT has NAT route |
| 6 | `Web-Subnet-NACL` on Private-Subnet-B with rules 100–200 |
| 7 | `Web-SG` and `Firewall-SG` with correct inbound rules |
| 8 | `Lab1-Firewall` READY with `Lab1-Firewall-Policy` and `Allow-Web-Traffic` |

Run `python setup/test_vpc_lab1.py --validate-only` — all lines should show `PASS`.

---

## 4. Console navigation reference

### VPC Dashboard

**Search** → **VPC** → left menu: Your VPCs, Subnets, Route tables, Internet gateways, NAT gateways, Network ACLs, Security groups

### Network Firewall

**Search** → **Network Firewall** → Firewalls, Firewall policies, Network Firewall rule groups

### Common UI labels (2026)

| This guide says | Console may show |
|-----------------|------------------|
| Name tag | Name |
| Create VPC → VPC only | Resources to create: VPC only |
| Edit routes | Routes tab → Edit routes |
| Allocate Elastic IP | Allocate Elastic IP (button on NAT form) |

---

## 5. Tear down order (cost control)

Deleting out of order causes errors or lingering charges:

1. **Network Firewall** → delete `Lab1-Firewall`
2. **Firewall policies** → delete `Lab1-Firewall-Policy`
3. **Rule groups** → delete `Allow-Web-Traffic`
4. **NAT Gateways** → delete `Lab1-NAT` (wait until deleted)
5. **Elastic IPs** → release unused EIP from NAT
6. **Internet gateways** → detach `Lab1-IGW`, then delete
7. **VPC** → delete `Lab1-VPC` (removes subnets, route tables, NACLs, security groups)

Or run: `python setup/test_vpc_lab1.py --teardown`

---

## 6. Troubleshooting (instructor)

| Issue | Cause | Fix |
|-------|-------|-----|
| `Network Firewall not available in region` | Wrong region | Use us-east-1 |
| NAT create page has no Subnet field | Regional availability mode | Select **Zonal**, then choose `Public-Subnet-A` |
| NAT create fails | No subnet with IGW route | Fix Public-RT before NAT |
| `--validate-only` fails on firewall | Still PROVISIONING | Wait 5–10 min or use `--wait-firewall` on deploy |
| VPC delete fails | NAT or firewall still exists | Run teardown script or delete manually in order above |
| Student CIDR conflict | Existing 10.0.0.0/16 VPC | Use 172.16.0.0/16 and update all subnet CIDRs in instructions |

---

## 7. What to distribute to students

| Item | Value |
|------|-------|
| Lab guide | [instructions.md](../instructions.md) |
| Region | **us-east-1** |
| Resource names | Exact names from guide (Lab1-VPC, etc.) |
| SSH CIDR | Each student uses their own `x.x.x.x/32` |
| Cost reminder | Tear down NAT + Firewall within 1 hour |

Do **not** share instructor AWS credentials. Each student uses their own account or dedicated lab account.
