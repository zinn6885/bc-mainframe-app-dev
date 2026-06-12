# Lab 2 — Console UI troubleshooting

Quick reference when a participant says “I can’t find my resource” or a health check fails.

**Reference screenshots (local, not in git):** `Lab Screenshots Day 3/Lab 2/` — see [README.md](../../../../Lab%20Screenshots%20Day%203/Lab%202/README.md)

---

## ALB subnets must match ASG instance AZs (critical)

**Symptom:** Target group shows one target **healthy** and one **unused** with reason *Target is in an Availability Zone that is not enabled for the load balancer*.

**Cause:** ASG launches instances in **`Private-Subnet-B` (us-east-1b)** and **`Private-Subnet-C` (us-east-1c)**, but the ALB was created in **`Public-Subnet-A` (us-east-1a)** + **`Public-Subnet-C` (us-east-1c)**. AWS cannot route to targets in AZs where the ALB has no subnet.

**Fix (tell the student):**
1. VPC → **Subnets** → create **`Public-Subnet-B`** if missing (Step 1D): us-east-1b, `10.0.6.0/24`, associate with **`Public-RT`**.
2. EC2 → **Load Balancers** → **`ASG-ALB`** → **Network mapping** → **Edit subnets**.
3. Select **`Public-Subnet-B`** + **`Public-Subnet-C`** (remove `Public-Subnet-A` from the ALB).
4. Wait 1–2 minutes → **Target Groups** → **`ASG-TG`** → **Targets** — both should become **healthy**.

**Prevention:** Follow Step 4 exactly — use **`Public-Subnet-B` + `Public-Subnet-C`**, not `Public-Subnet-A`.

---

## us-east-1b instance keeps restarting (restart loop)

**Symptom:** Student reports one instance in **us-east-1c** runs fine, but the **us-east-1b** instance keeps terminating and relaunching. **ASG → Activity** shows a repeating launch/terminate pattern for the same AZ.

**Cause:** Same as above — the **us-east-1b** target fails **ELB health checks** because the ALB has no node in **us-east-1b**. The ASG (with health check type **ELB**) replaces the “unhealthy” instance. This is expected ASG behavior, not a random reboot.

**Diagnosis (ask for screenshots):**
1. **Target Groups → `ASG-TG` → Targets** — us-east-1b row likely **unused** or **unhealthy**
2. **Load Balancers → `ASG-ALB` → Network mapping** — often shows **`Public-Subnet-A` + `Public-Subnet-C`** instead of **B + C**
3. **VPC → Subnets** — **`Public-Subnet-B`** may be missing if Step 1D was skipped

**Fix:** Same four steps as **ALB subnets must match** above. After ALB edit, replacements should stop within **2–5 minutes**.

**If both targets are unhealthy (not unused):** Check launch template user data (`setup/user_data.sh`) and **`Private-RT`** NAT route for **`Private-Subnet-B`**.

**Reply template for students:** See [../instructions.md](../instructions.md) — section *If one instance keeps restarting*.

---

## Security groups — same as Lab 1

**Symptom:** Student types `Lab1-VPC` in the Security groups search box → **No matching resource found**.

**Fix:** Search **`Web-SG`** by name, or match the **VPC ID** column.

---

## Subnets filter

| Page | Filter `Lab1-VPC` |
|------|-------------------|
| VPC → Subnets | Works |
| VPC → Route tables | Works |
| EC2 → Security groups | **Does not work** |

---

## Launch template — where to verify

**Symptom:** Student cannot find Auto Scaling guidance or user data after create.

**UI path:**
1. EC2 → **Launch Templates** → click **`WebServer-LT`**
2. **Default version** should be **1**
3. Sub-tab **Instance details** — AMI, instance type, key pair, security group
4. Sub-tab **Advanced details** (or version actions → **Modify template version**) — **User data** must start with `#!/bin/bash`

---

## Auto Scaling Group — two tabs for grading

| What to verify | Tab |
|----------------|-----|
| Desired 2, Min 2, Max 6 | **Details** (page header) or **Details** tab |
| Private subnets B + C | **Details** → Network |
| Target group `ASG-TG` | **Integrations** or create wizard review |
| Policy `Scale-on-CPU` 70% | **Automatic scaling** |

Step 6 screenshot may show only **Automatic scaling** — accept if header shows Desired **2** and limits **2–6**.

---

## Step 13 — recovery times are not on one AWS page

| Event | Where to find time |
|-------|-------------------|
| Termination initiated | Student's clock / notes when they clicked Terminate |
| Replacement launch | **ASG → Activity** → Start time on launch row after termination |
| Instance healthy | When **Target Groups → Targets** shows new instance **Healthy** |

**Expected range:** **2–8 minutes** (not a hard failure if slightly longer).

---

## Screenshot grading notes

| Step | Accept if screenshot shows |
|------|---------------------------|
| 1 | ≥2 private + ≥2 public subnets in different AZs; includes `Private-Subnet-B/C` and `Public-Subnet-B/C` after Step 1D |
| 4 | ALB **provisioning** or **active**; listener HTTP:80 → `ASG-TG`; subnets in **1b + 1c** preferred |
| 6 | `Scale-on-CPU` 70% on **Automatic scaling**; capacity 2/2/6 visible somewhere on page |
| 8 | 2 **healthy** targets; different AZs; no **unused** targets |
| 9 | Browser only — ALB DNS in address bar; demo page content |
| 12 | 2 healthy targets + browser loads (one or two images) |
| 13 | Written times + calculation (not an AWS console page) |

Full participant guide: [../instructions.md](../instructions.md)
