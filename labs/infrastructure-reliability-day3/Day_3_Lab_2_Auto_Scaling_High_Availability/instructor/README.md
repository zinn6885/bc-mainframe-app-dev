# Lab 2 — Instructor Package

**Estimated setup time:** 15–20 minutes (first time) · 5 minutes (repeat classes)  
**Region:** US East (N. Virginia) — **`us-east-1`**

---

## Before class

1. Confirm students completed **[Day 3 Lab 1](../../Day_3_Lab_1_VPC_Networking_Firewall/instructions.md)** (VPC, NAT, `Web-SG`, `Private-Subnet-B`, `Public-Subnet-A`).
2. Follow **[AWS_LAB2_SETUP.md](AWS_LAB2_SETUP.md)** — run the validation script once yourself after building the lab.
3. Walk through **[instructions.md](../instructions.md)** Steps 1–9 in the console to confirm UI paths match.
4. Tell students:
   - Region must be **`us-east-1`**
   - Exact resource names from the guide
   - Lab 1 must be complete (NAT + Web-SG required)
   - Step 1 adds subnets if missing — do not skip
   - Tear down Lab 2 resources after class to limit ALB/NAT costs

---

## Materials

| File | Purpose |
|------|---------|
| [AWS_LAB2_SETUP.md](AWS_LAB2_SETUP.md) | Pre-lab IAM, validation script, teardown order |
| [answer_key.md](answer_key.md) | Expected values per step for grading |
| [../instructions.md](../instructions.md) | Student guide — Steps 1–14 |
| [../setup/test_asg_lab2.py](../setup/test_asg_lab2.py) | Validate Lab 1 prerequisites and Lab 2 resources |
| [../setup/requirements.txt](../setup/requirements.txt) | Python dependencies |
| [../setup/user_data.sh](../setup/user_data.sh) | Bootstrap script for launch template |
| [CONSOLE_UI_GUIDE.md](CONSOLE_UI_GUIDE.md) | UI troubleshooting (unused targets, SG search, ASG tabs) |

---

## Quick validation (instructor)

From the lab folder:

```powershell
cd Day_3_Lab_2_Auto_Scaling_High_Availability
pip install -r setup/requirements.txt
python setup/test_asg_lab2.py --validate-only
```

After you build the lab manually, all checks should print `PASS`.

To validate Lab 1 prerequisites only (before students start Lab 2):

```powershell
python setup/test_asg_lab2.py --prerequisites-only
```

---

## Pacing guide (45–50 min class block)

| Time | Activity |
|------|----------|
| 0–5 min | Verify Lab 1 complete; Step 1 subnet checks |
| 5–10 min | Step 2 — Launch Template + user data |
| 10–15 min | Steps 3–4 — Target Group + ALB (provisioning) |
| 15–20 min | Step 5 — Wait for ALB active |
| 20–30 min | Step 6 — Create ASG (walk through all wizard pages) |
| 30–35 min | Steps 7–8 — Launch activity + healthy targets |
| 35–40 min | Step 9 — Browser test via ALB DNS |
| 40–48 min | Steps 10–13 — Terminate, auto-heal, recovery time |
| 48–50 min | Deliverables checklist, Step 14 optional, tear-down reminder |

> **Tip:** Start Step 4 (ALB) early — it provisions while students create the launch template. Have students open the ALB DNS in the browser only after Step 8 shows healthy targets.

---

## Common student mistakes

| Mistake | Fix |
|---------|-----|
| Lab 1 not complete | No NAT → user data yum fails; no Web-SG → launch template fails |
| Only one private subnet in ASG | Edit ASG → add second private subnet in different AZ |
| Selected public subnets for ASG | Instances must use **private** subnets only |
| Skipped Step 1C/1D (public subnets) | ALB requires `Public-Subnet-B` + `Public-Subnet-C` |
| One target **unused** in target group | ALB used `Public-Subnet-A` instead of B+C — edit ALB subnets |
| **us-east-1b** instance keeps restarting; **us-east-1c** OK | ALB not in us-east-1b → ELB health fail → ASG replacement loop — fix ALB to **Public-Subnet-B + Public-Subnet-C** |
| User data not pasted | Instances launch but targets stay unhealthy — no Apache |
| Health check type = EC2 instead of ELB | Change to ELB when attaching target group |
| Terminated both instances at once | ASG replaces both but recovery takes longer — terminate **one** only |
| Wrong region | Recreate in us-east-1; subnet AZ names won't match |

---

## Demo script (instructor-led recap)

1. Show ALB DNS in browser — refresh to show different Instance IDs.
2. Terminate one instance live — narrate ASG Activity tab.
3. Show target group drop to 1 healthy, then return to 2.
4. State recovery time aloud and relate to RTO concepts from Module 11.

---

## Student guide

[../instructions.md](../instructions.md) — Steps 1–14 (AWS Console)
