# Lab 2 — AWS Setup & Validation (Instructor)

**Region:** `us-east-1`  
**Prerequisite:** Day 3 Lab 1 resources deployed

---

## IAM permissions (minimum)

Students and validation script need permissions for:

- `ec2:Describe*`, `ec2:CreateLaunchTemplate`, `ec2:DeleteLaunchTemplate`
- `elasticloadbalancing:*` (or describe + create/delete for ALB, target groups)
- `autoscaling:*` (or describe + create/update/delete ASG)
- Read-only VPC: `ec2:DescribeVpcs`, `ec2:DescribeSubnets`, `ec2:DescribeSecurityGroups`, `ec2:DescribeRouteTables`

Lab 1 creation permissions are separate (VPC, NAT, Network Firewall).

---

## Pre-class checklist

1. [ ] Lab 1 validation passed (`Lab1-VPC`, NAT, `Web-SG`, route tables)
2. [ ] Student accounts can create ALB and ASG (some orgs restrict ELB)
3. [ ] Students know their EC2 key pair name
4. [ ] Instructor ran validation script after building reference lab:

```powershell
cd Day_3_Lab_2_Auto_Scaling_High_Availability
pip install -r setup/requirements.txt
python setup/test_asg_lab2.py --validate-only
```

---

## Validation script usage

| Command | Purpose |
|---------|---------|
| `python setup/test_asg_lab2.py --prerequisites-only` | Check Lab 1 + Step 1 subnets before lab |
| `python setup/test_asg_lab2.py --validate-only` | Check full Lab 2 stack (LT, TG, ALB, ASG, health) |
| `python setup/test_asg_lab2.py --check-alb-url` | Also HTTP GET the ALB DNS (expects 200 + "Auto Scaling") |

**Requirements:** Python 3.9+, `boto3`. AWS credentials via environment, profile, or instance role.

```powershell
pip install -r setup/requirements.txt
```

---

## Expected validation output

```
=== Lab 2 Prerequisites ===
PASS  VPC Lab1-VPC exists (vpc-...)
PASS  Public-Subnet-A in us-east-1a
PASS  Public-Subnet-B in us-east-1b
PASS  Public-Subnet-C in us-east-1c
PASS  Private-Subnet-B in us-east-1b
PASS  Private-Subnet-C in us-east-1c
PASS  Web-SG exists with HTTP:80
PASS  Private-RT has NAT route

=== Lab 2 Resources ===
PASS  Launch template WebServer-LT
PASS  Target group ASG-TG
PASS  Load balancer ASG-ALB (active)
PASS  Auto Scaling group WebServer-ASG (2/2/6)
PASS  Target group has 2 healthy targets
PASS  ASG spans multiple AZs

All checks passed.
```

---

## Teardown order

Delete in this order to avoid dependency errors:

1. **Auto Scaling Group** `WebServer-ASG`
   - EC2 → Auto Scaling Groups → select ASG → **Delete**
   - Or set desired/min/max to 0, wait for instances to terminate, then delete
2. **Load balancer** `ASG-ALB`
   - EC2 → Load Balancers → select → **Delete**
3. **Target group** `ASG-TG`
   - EC2 → Target Groups → select → **Delete**
   - (Must wait until no load balancer references it)
4. **Launch template** `WebServer-LT`
   - EC2 → Launch Templates → select → **Delete template**

**Do not delete** Lab 1 VPC, NAT, or firewall until Lab 1 teardown per Lab 1 instructions.

Optional subnets created in Lab 2 Step 1 (`Private-Subnet-C`, `Public-Subnet-B`, `Public-Subnet-C`) may remain for future labs or be deleted with the VPC.

---

## Cost estimate (reference lab left running)

| Resource | ~Cost/hour |
|----------|------------|
| ALB | $0.0225 + LCU |
| 2× t2.micro | Free tier (750 hrs/mo shared) |
| NAT (Lab 1) | $0.045 |

**Recommendation:** Tear down Lab 2 within 1 hour of class end. NAT from Lab 1 is the largest ongoing cost.

---

## Instructor reference build (manual)

If building a reference environment before class:

1. Complete Lab 1
2. Follow student [instructions.md](../instructions.md) Steps 1–8
3. Run `python setup/test_asg_lab2.py --validate-only --check-alb-url`
4. Optionally run Steps 10–12 to verify auto-healing
5. Tear down or leave running for live demo (cost awareness)

---

## Console path quick reference

| Resource | Console path |
|----------|--------------|
| Launch Templates | EC2 → Launch Templates |
| Target Groups | EC2 → Target Groups |
| Load Balancers | EC2 → Load Balancers |
| Auto Scaling Groups | EC2 → Auto Scaling Groups |
| Subnets | VPC → Subnets |
| Route tables | VPC → Route tables |
