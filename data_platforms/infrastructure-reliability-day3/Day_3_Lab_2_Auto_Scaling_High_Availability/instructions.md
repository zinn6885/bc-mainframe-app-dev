# Lab 2: Auto Scaling & High Availability

**Estimated time:** 45–50 minutes  
**Tools needed:** AWS Console (web browser)  
**AWS region:** US East (N. Virginia) — **`us-east-1`** (required)  
**AWS Free Tier:** Yes — ALB and ASG are within free tier limits when used briefly. **NAT Gateway from Lab 1 still incurs hourly charges** — tear down when finished.

### Lab file locations

All paths below are relative to the **Lab 2 folder** (`Day_3_Lab_2_Auto_Scaling_High_Availability/`).

| File | Location in repo | When you need it |
|------|------------------|------------------|
| Lab instructions | `instructions.md` | This file — Steps 1–14 |
| Architecture diagram | `diagrams/lab2-asg-architecture.svg` | Reference |
| User data script | `setup/user_data.sh` | Copy into Launch Template (Step 2) |
| Screenshot naming guide | `screenshots/README.md` | After each step |
| Console UI troubleshooting (instructors) | `instructor/CONSOLE_UI_GUIDE.md` | When students are stuck |
| Reference screenshots (local only) | `Lab Screenshots Day 3/Lab 2/` | Compare your screen — **do not commit PNGs to git** |

---

## Before you start (participants)

1. **Complete Lab 1 first.** You need `Lab1-VPC`, `Web-SG`, NAT Gateway, and route tables from [Day 3 Lab 1](../Day_3_Lab_1_VPC_Networking_Firewall/instructions.md).
2. Sign in to the **AWS Console** with an account that can create EC2, ELB, and Auto Scaling resources.
3. Set the region to **US East (N. Virginia)** — top-right corner must show **`us-east-1`**.
4. Have an **EC2 key pair** available (same one you used in Lab 1 or any existing key).
5. Keep this lab guide open in a second window while you work in the console.

> **Naming is important.** Use the exact resource names in this guide (`WebServer-LT`, `ASG-ALB`, etc.) so your instructor can verify your work quickly.

---

## AWS region and screenshot checklist

### Region (required for every step)

| Setting | Value |
|---------|-------|
| **AWS Region** | **US East (N. Virginia)** |
| **Region code** | **`us-east-1`** |
| **Where to check** | Top-right corner of the AWS Console — must show **N. Virginia** or **`us-east-1`** |

> **Include the region in every screenshot** (top-right of the console) or your instructor cannot verify your work. If you use the wrong region, subnet AZ names and resources will not match this lab.

**Before each screenshot:** confirm the region selector shows **`us-east-1`**, then navigate to the console page listed below.

| Step | AWS Console path | What must be visible in your screenshot |
|------|------------------|----------------------------------------|
| **1** | **VPC** → **Subnets** (filter by `Lab1-VPC`) | Region **`us-east-1`** · `Lab1-VPC` subnets · **two private** in different AZs (`Private-Subnet-B`, `Private-Subnet-C`) · **two public** for ALB in different AZs (`Public-Subnet-B`, `Public-Subnet-C`) · plus Lab 1 subnets (`Public-Subnet-A`, `Firewall-Subnet-A`) |
| **2** | **EC2** → **Launch Templates** → `WebServer-LT` | Region **`us-east-1`** · template name **`WebServer-LT`** · **Default version = 1** · **Auto Scaling guidance** enabled · security group **`Web-SG`** |
| **3** | **EC2** → **Target Groups** → `ASG-TG` | Region **`us-east-1`** · name **`ASG-TG`** · Protocol **HTTP**, Port **80** · Health check path **`/`** · Success codes **200** · **0 registered targets** (before ASG launches) |
| **4** | **EC2** → **Load Balancers** → `ASG-ALB` | Region **`us-east-1`** · name **`ASG-ALB`** · State **`provisioning`** · subnets **`Public-Subnet-B`** (1b) + **`Public-Subnet-C`** (1c) · Listener **HTTP:80** → **`ASG-TG`** |
| **5** | **EC2** → **Load Balancers** → `ASG-ALB` | Region **`us-east-1`** · State **`active`** · **DNS name** visible (e.g. `ASG-ALB-….elb.amazonaws.com`) |
| **6** | **EC2** → **Auto Scaling Groups** → `WebServer-ASG` | Region **`us-east-1`** · name **`WebServer-ASG`** · header **Desired 2 / limits 2–6** · **Automatic scaling** tab · policy **`Scale-on-CPU`** at **70%** · (verify subnets on **Details** tab) |
| **7** | **EC2** → **Auto Scaling Groups** → `WebServer-ASG` → **Activity** tab | Region **`us-east-1`** · **Launching a new EC2 instance** message · Status **Successful** · capacity increasing to **2** |
| **8** | **EC2** → **Target Groups** → `ASG-TG` → **Targets** tab | Region **`us-east-1`** · **2 registered targets** · both **Health status = healthy** · **different Availability Zones** |
| **9** | **Browser** (not AWS Console) | Address bar shows **ALB DNS name** · web page shows **Instance ID**, **Availability Zone**, **Private IP** · title **Auto Scaling Group Demo** |
| **10** | **EC2** → **Instances** | Region **`us-east-1`** · one **`WebServer-ASG`** instance with state **`shutting-down`** or **`terminated`** · **Instance ID** visible |
| **11** | **EC2** → **Auto Scaling Groups** → `WebServer-ASG` → **Activity** tab | Region **`us-east-1`** · new **Launching a new EC2 instance** entry **after** Step 10 termination · Status **Successful** |
| **12** | **EC2** → **Target Groups** → `ASG-TG` → **Targets** tab **and** browser | Region **`us-east-1`** on console screenshot · **2 healthy targets** again · browser still loads demo page via ALB DNS |
| **13** | Your notes or a text file | **Three timestamps** recorded: termination time · replacement launch time · new instance healthy time · **recovery time calculation** |
| **14** | **EC2** → **Auto Scaling Groups** → `WebServer-ASG` → **Activity** tab *(optional)* | Region **`us-east-1`** · scale-out activity (desired capacity **> 2**) after CPU load |

**Screenshot filenames:** save as `Step_01_….png` through `Step_14_….png` — see [screenshots/README.md](screenshots/README.md).

**After each screenshot:** reply to your instructor with the checkpoint text for that step (e.g. `"Step 3 completed"`).

---

## Lab objectives

By the end of this lab, you will be able to:

- Create a Launch Template for web servers
- Configure an Application Load Balancer across multiple Availability Zones
- Create an Auto Scaling Group with min/max/desired capacity
- Test high availability by terminating an instance
- Observe auto-healing in action
- Configure scaling policies based on CPU utilization

---

## Architecture overview

![Lab 2 architecture: ALB, target group, and Auto Scaling Group across two AZs](diagrams/lab2-asg-architecture.svg)

```
                    Internet
                        │
              Application Load Balancer (ASG-ALB)
              DNS: ASG-ALB-xxxx.elb.amazonaws.com
                        │
              Target Group (ASG-TG, HTTP:80)
                        │
         ┌──────────────┴──────────────┐
         │                             │
   Private-Subnet-B              Private-Subnet-C
   us-east-1b · 10.0.2.0/24      us-east-1c · 10.0.4.0/24
   EC2 Web Server 1              EC2 Web Server 2
         │                             │
         └──────── Auto Scaling Group ─┘
              WebServer-ASG
              Min: 2 · Desired: 2 · Max: 6
              Scale-out: CPU > 70% (target tracking)
```

**What Lab 1 provides:** VPC, NAT Gateway, `Web-SG`, `Private-Subnet-B`, `Public-Subnet-A`.  
**What Lab 2 adds:** `Private-Subnet-C`, `Public-Subnet-B`, `Public-Subnet-C`, Launch Template, Target Group, ALB, ASG.

> **AZ alignment (critical):** ASG instances run in **us-east-1b** and **us-east-1c**. The ALB must use **`Public-Subnet-B` (1b)** and **`Public-Subnet-C` (1c)** — **not** `Public-Subnet-A` (1a).

### If one instance keeps restarting (common issue)

**Symptom:** Instance in **us-east-1c** is stable, but **us-east-1b** keeps terminating and relaunching (or only one target ever becomes healthy).

**Cause:** The ALB is not enabled in **us-east-1b**, so the target in that AZ fails the **ELB health check**. The ASG replaces the “unhealthy” instance — which looks like a restart loop.

**Fix before continuing past Step 8:**
1. **EC2 → Target Groups → `ASG-TG` → Targets** — check the **us-east-1b** row. If status is **unused**, read the reason (*Availability Zone not enabled for the load balancer*).
2. **EC2 → Load Balancers → `ASG-ALB` → Network mapping → Edit subnets** — select **`Public-Subnet-B` (1b)** + **`Public-Subnet-C` (1c)** only.
3. If **`Public-Subnet-B`** is missing, create it in **Step 1D** first.
4. Wait **2–3 minutes** — both targets should show **healthy**.

Full instructor guide: [instructor/CONSOLE_UI_GUIDE.md](instructor/CONSOLE_UI_GUIDE.md)

---

## Step 1 — Verify Lab 1 resources and add subnets for high availability

**Console path:** Search bar → **VPC** → **VPC Dashboard**

### 1A — Verify existing Lab 1 resources

1. Go to **Your VPCs** → confirm **`Lab1-VPC`** exists with State = **Available** and CIDR **`10.0.0.0/16`**.
2. Go to **Subnets** → filter by `Lab1-VPC`. Confirm these exist:

| Subnet name | AZ | CIDR | Purpose |
|-------------|-----|------|---------|
| `Public-Subnet-A` | us-east-1a | 10.0.1.0/24 | NAT Gateway (Lab 1) |
| `Private-Subnet-B` | us-east-1b | 10.0.2.0/24 | ASG instances (AZ-b) |
| `Firewall-Subnet-A` | us-east-1a | 10.0.3.0/24 | Network Firewall (Lab 1) |

3. Go to **Security groups** → confirm **`Web-SG`** exists in `Lab1-VPC` with inbound **HTTP:80** from `0.0.0.0/0`.

### 1B — Create second private subnet (if missing)

> **Why:** Auto Scaling needs **at least two private subnets in different AZs** for cross-AZ high availability.

**Console path:** VPC Dashboard → **Subnets** → **Create subnet**

| Setting | Value |
|---------|-------|
| **VPC** | `Lab1-VPC` |
| **Subnet name** | `Private-Subnet-C` |
| **Availability Zone** | **us-east-1c** |
| **IPv4 CIDR block** | `10.0.4.0/24` |

Click **Create subnet**.

**Associate with private route table:**

1. VPC Dashboard → **Route tables** → select **`Private-RT`**.
2. **Subnet associations** → **Edit subnet associations**.
3. Check **`Private-Subnet-C`** (keep **`Private-Subnet-B`** checked) → **Save changes**.

### 1C — Create second public subnet (if missing)

> **Why:** The Application Load Balancer needs **at least two public subnets in different AZs**.

**Console path:** VPC Dashboard → **Subnets** → **Create subnet**

| Setting | Value |
|---------|-------|
| **VPC** | `Lab1-VPC` |
| **Subnet name** | `Public-Subnet-C` |
| **Availability Zone** | **us-east-1c** |
| **IPv4 CIDR block** | `10.0.5.0/24` |

Click **Create subnet**.

**Associate with public route table:**

1. Route tables → select **`Public-RT`**.
2. **Subnet associations** → **Edit subnet associations**.
3. Check **`Public-Subnet-C`** (keep **`Public-Subnet-A`** checked) → **Save changes**.

### 1D — Create public subnet for ALB in us-east-1b (required)

> **Required — do not skip.** ASG instances launch in **us-east-1b** and **us-east-1c**. Without **`Public-Subnet-B`**, you cannot place the ALB in us-east-1b. The us-east-1b instance will fail health checks and the ASG will keep replacing it (looks like a restart loop).

**Console path:** VPC Dashboard → **Subnets** → **Create subnet**

| Setting | Value |
|---------|-------|
| **VPC** | `Lab1-VPC` |
| **Subnet name** | `Public-Subnet-B` |
| **Availability Zone** | **us-east-1b** |
| **IPv4 CIDR block** | `10.0.6.0/24` |

Click **Create subnet**.

**Associate with public route table:**

1. Route tables → select **`Public-RT`**.
2. **Subnet associations** → **Edit subnet associations**.
3. Check **`Public-Subnet-B`** (keep **`Public-Subnet-A`** and **`Public-Subnet-C`** checked) → **Save changes**.

**Verify:**

| Check | Expected |
|-------|----------|
| Private subnets in different AZs | `Private-Subnet-B` (us-east-1b) + `Private-Subnet-C` (us-east-1c) |
| Public subnets for ALB | `Public-Subnet-B` (us-east-1b) + `Public-Subnet-C` (us-east-1c) |
| Lab 1 public subnet | `Public-Subnet-A` (us-east-1a) — NAT only, not used by ALB |
| Both private subnets use `Private-RT` | Route table shows NAT route `0.0.0.0/0 → Lab1-NAT` |
| All public subnets use `Public-RT` | Route table shows IGW route `0.0.0.0/0 → Lab1-IGW` |

**Screenshot:** Subnets list filtered by `Lab1-VPC` showing private subnets **B/C**, public subnets **A/B/C**, and `Firewall-Subnet-A`.

**Checkpoint:** `"Step 1 completed"`

---

## Step 2 — Create Launch Template

**Console path:** Search bar → **EC2** → **Launch Templates** → **Create launch template**

| Setting | Value |
|---------|-------|
| **Launch template name** | `WebServer-LT` |
| **Template version description** | `Version 1 - Web Server` |
| **Auto Scaling guidance** | **Check this box** |

**Launch template contents:**

| Setting | Value |
|---------|-------|
| **AMI** | **Amazon Linux 2023 AMI** (Free tier eligible) |
| **Instance type** | `t2.micro` (Free tier) |
| **Key pair** | Select your existing key pair |
| **Security groups** | Select **`Web-SG`** (from Lab 1) |
| **Storage** | Default (1 volume, 8 GB gp2) |

**Advanced details — User data:** Copy the entire script from [`setup/user_data.sh`](setup/user_data.sh) and paste into the **User data** field.

> **Tip:** Open `setup/user_data.sh` in your lab folder. Select all → copy → paste into the console User data box. Do not type it manually.

Click **Create launch template**.

**Verify:**

| Check | Expected |
|-------|----------|
| Template name | `WebServer-LT` |
| Default version | 1 |
| Auto Scaling guidance | Enabled |
| Security group | `Web-SG` |
| User data | Script present (starts with `#!/bin/bash`) |

**UI tip:** After create, open **`WebServer-LT`** → confirm **Default version = 1** → sub-tab **Instance details** (AMI, `t2.micro`, `Web-SG`, key pair). User data is under **Advanced details** on the version.

**Screenshot:** Launch template detail — `WebServer-LT`, version **1**, `Web-SG` on **Instance details**.

**Checkpoint:** `"Step 2 completed"`

---

## Step 3 — Create Target Group

**Console path:** EC2 Dashboard → **Target Groups** → **Create target group**

| Setting | Value |
|---------|-------|
| **Choose target type** | **Instances** |
| **Target group name** | `ASG-TG` |
| **Protocol** | HTTP |
| **Port** | 80 |
| **IP address type** | IPv4 |
| **VPC** | `Lab1-VPC` |
| **Protocol version** | HTTP1 |

**Health check settings:**

| Setting | Value |
|---------|-------|
| **Health check protocol** | HTTP |
| **Health check path** | `/` |
| **Health check port** | Traffic port (80) |
| **Healthy threshold** | 2 |
| **Unhealthy threshold** | 2 |
| **Timeout** | 5 seconds |
| **Interval** | 10 seconds |
| **Success codes** | 200 |

Click **Next**.

**Register targets:** Leave empty — the Auto Scaling Group registers instances automatically.

Click **Create target group**.

**Verify:**

| Check | Expected |
|-------|----------|
| Target group name | `ASG-TG` |
| Protocol / port | HTTP / 80 |
| VPC | Lab1-VPC |
| Registered targets | 0 (empty until ASG launches instances) |

**Screenshot:** Target group detail showing name, health check settings, and 0 registered targets.

**Checkpoint:** `"Step 3 completed"`

---

## Step 4 — Create Application Load Balancer

**Console path:** EC2 Dashboard → **Load Balancers** → **Create load balancer** → **Application Load Balancer** → **Create**

| Setting | Value |
|---------|-------|
| **Load balancer name** | `ASG-ALB` |
| **Scheme** | **Internet-facing** |
| **IP address type** | IPv4 |
| **VPC** | `Lab1-VPC` |

**Network mapping — select exactly two public subnets in different AZs:**

| Subnet | AZ | Purpose |
|--------|-----|---------|
| `Public-Subnet-B` | us-east-1b | ALB node — same AZ as `Private-Subnet-B` |
| `Public-Subnet-C` | us-east-1c | ALB node — same AZ as `Private-Subnet-C` |

> **Do not** select `Public-Subnet-A` for the ALB. It is in **us-east-1a** where no ASG instances run. A common mistake is picking **`Public-Subnet-A` + `Public-Subnet-C`** — that leaves **us-east-1b** uncovered and causes the **us-east-1b instance restart loop**.

**Before you click Create — confirm Network mapping shows:**

| Subnet selected | AZ | Select? |
|-----------------|-----|---------|
| `Public-Subnet-B` | us-east-1b | **Yes** |
| `Public-Subnet-C` | us-east-1c | **Yes** |
| `Public-Subnet-A` | us-east-1a | **No** |

**Security groups:**

| Setting | Value |
|---------|-------|
| **Security group** | **`Web-SG`** |

**Listeners and routing:**

| Setting | Value |
|---------|-------|
| **Protocol** | HTTP |
| **Port** | 80 |
| **Default action** | Forward to **`ASG-TG`** |

Click **Create load balancer**.

**Verify:**

| Check | Expected |
|-------|----------|
| Load balancer name | `ASG-ALB` |
| State | `provisioning` (will become `active` in Step 5) |
| Scheme | Internet-facing |
| AZ mappings | Two public subnets in different AZs |
| Listener | HTTP:80 → ASG-TG |

**Screenshot:** Load balancer detail showing `provisioning` status and two AZ mappings.

**Checkpoint:** `"Step 4 completed"`

---

## Step 5 — Wait for Load Balancer to become active

**Action:**

1. Stay on **Load Balancers** → select **`ASG-ALB`**.
2. Wait **3–5 minutes**, then click **Refresh**.
3. Confirm **State** changes from `provisioning` to **`active`**.
4. Copy the **DNS name** (example: `ASG-ALB-1234567890.us-east-1.elb.amazonaws.com`).

**Verify:**

| Check | Expected |
|-------|----------|
| State | `active` |
| DNS name | Visible and ends with `.elb.amazonaws.com` |

> **Note:** The DNS name will not serve a web page yet — instances are not running until Step 6–7.

**Screenshot:** Load balancer showing `active` status and DNS name visible.

**Checkpoint:** `"Step 5 completed"`

---

## Step 6 — Create Auto Scaling Group

**Console path:** EC2 Dashboard → **Auto Scaling Groups** → **Create Auto Scaling group**

### 6A — Choose launch template

| Setting | Value |
|---------|-------|
| **Auto Scaling group name** | `WebServer-ASG` |
| **Launch template** | `WebServer-LT` |
| **Version** | Default (1) |

Click **Next**.

### 6B — Configure network

| Setting | Value |
|---------|-------|
| **VPC** | `Lab1-VPC` |
| **Availability Zones and subnets** | Select **`Private-Subnet-B`** and **`Private-Subnet-C`** only |

> **Important:** Select **private** subnets only — not public subnets. Instances should not receive public IPs.

Click **Next**.

### 6C — Configure load balancing

| Setting | Value |
|---------|-------|
| **Load balancing** | Attach to an existing load balancer |
| **Choose target groups** | Choose from your load balancers |
| **Existing load balancer target groups** | **`ASG-TG`** |
| **Health check type** | **ELB** (recommended) |

Click **Next**.

### 6D — Configure group size and scaling

| Setting | Value |
|---------|-------|
| **Desired capacity** | `2` |
| **Minimum capacity** | `2` |
| **Maximum capacity** | `6` |

**Scaling policies:**

| Setting | Value |
|---------|-------|
| **Scaling policies** | Target tracking scaling policy |
| **Scaling policy name** | `Scale-on-CPU` |
| **Metric type** | Average CPU utilization |
| **Target value** | `70` |
| **Instances warmup** | 60 seconds |

Click **Next**.

### 6E — Configure notifications

Skip (optional) → **Next**.

### 6F — Configure tags

| Setting | Value |
|---------|-------|
| **Key** | `Name` |
| **Value** | `WebServer-ASG` |
| **Tag instances** | **Yes** |

Click **Create Auto Scaling group**.

**Verify:**

| Check | Expected |
|-------|----------|
| ASG name | `WebServer-ASG` |
| Desired / Min / Max | 2 / 2 / 6 |
| Subnets | Private-Subnet-B + Private-Subnet-C |
| Target group | ASG-TG attached |
| Health check | ELB |
| Scaling policy | Scale-on-CPU at 70% |

**UI tip:** After create, open **`WebServer-ASG`**. Page header shows **Desired capacity 2** and **Scaling limits 2–6**. Open **Automatic scaling** tab for **`Scale-on-CPU`** at **70%**. Use **Details** tab to confirm private subnets and target group.

**Screenshot:** **`WebServer-ASG`** → **Automatic scaling** tab showing **`Scale-on-CPU`** at **70%**; header shows Desired **2** / limits **2–6**.

**Checkpoint:** `"Step 6 completed"`

---

## Step 7 — Monitor instance launch

**Console path:** EC2 Dashboard → **Auto Scaling Groups** → **`WebServer-ASG`** → **Activity** tab

**Action:**

1. Watch for activity similar to:

   > Launching a new EC2 instance. Status Reason: … increasing the capacity from 0 to 2.

2. Wait **2–3 minutes** for both instances to launch.
3. Confirm activity entries show **Successful**.

**Also check:** EC2 Dashboard → **Instances** — you should see **two** new instances with tag `Name = WebServer-ASG`, State = `running`.

**Verify:**

| Check | Expected |
|-------|----------|
| Activity | Launch events with Status = Successful |
| Instance count | 2 running instances |
| AZ distribution | Instances spread across us-east-1b and us-east-1c |

**Screenshot:** Activity tab showing successful launch events.

**Checkpoint:** `"Step 7 completed"`

---

## Step 8 — Verify target group health

**Console path:** EC2 Dashboard → **Target Groups** → **`ASG-TG`** → **Targets** tab

**Action:**

1. Wait until both instances show **Health status = healthy** (may take 1–2 minutes after launch).
2. Confirm instances are in **different Availability Zones** (**us-east-1b** and **us-east-1c**).
3. **Stop here if one target is not healthy** — do not continue to Step 9 until both are **healthy**.

### Target status guide

| Health status | What it means | What to do |
|---------------|---------------|------------|
| **healthy** | ALB can reach Apache on port 80 | Continue |
| **initial** / **draining** | Health check in progress | Wait 2–3 minutes, refresh |
| **unhealthy** | Health check failed (no web server or SG block) | Verify user data in `WebServer-LT`; `Web-SG` allows HTTP:80 |
| **unused** | Instance AZ not on the ALB | **Edit `ASG-ALB` subnets** → **`Public-Subnet-B` + `Public-Subnet-C`** (Step 4 fix) |

> **Restart loop?** If **us-east-1b** keeps launching and terminating while **us-east-1c** is fine, the **unused** / wrong-AZ ALB mapping is almost always the cause. Fix the ALB subnets, then watch **ASG → Activity** — replacements should stop.

**Verify:**

| Check | Expected |
|-------|----------|
| Registered targets | 2 |
| Health status | Both `healthy` (not **unused**) |
| Availability Zones | **us-east-1b** and **us-east-1c** |

**Screenshot:** Targets tab showing two **healthy** instances in **us-east-1b** and **us-east-1c**.

**Checkpoint:** `"Step 8 completed"`

---

## Step 9 — Test load balancer

**Action:**

1. Go to **Load Balancers** → **`ASG-ALB`** → copy the **DNS name**.
2. Open a **new browser tab** and paste the DNS name (use `http://` if your browser does not add it automatically).
3. Refresh the page **5–10 times**.

**Expected result:**

- Each refresh shows the Auto Scaling demo web page.
- The **Instance ID** may change between refreshes (load balancer distributes traffic).
- Page shows Availability Zone and Private IP for the serving instance.

**Verify:**

| Check | Expected |
|-------|----------|
| Browser response | HTTP 200 — demo page loads |
| Page content | Instance ID, AZ, Private IP visible |
| Load distribution | Instance ID may vary on refresh |

**Screenshot:** Browser showing the demo page with Instance ID visible and the ALB DNS in the address bar.

**Checkpoint:** `"Step 9 completed"`

---

## Step 10 — Test high availability: terminate one instance

**Console path:** EC2 Dashboard → **Instances**

**Action:**

1. Find one instance launched by the ASG (tag **`Name = WebServer-ASG`**).
2. Select the instance → **Instance state** → **Terminate instance**.
3. Click **Terminate** to confirm.
4. Note the **time** you initiated termination (for Step 13).

**Verify:**

| Check | Expected |
|-------|----------|
| Instance state | `shutting-down` then `terminated` |
| Remaining instances | 1 still running (temporarily) |

**Screenshot:** Instances list showing one instance terminating/terminated with Instance ID visible.

**Checkpoint:** `"Step 10 completed"`

---

## Step 11 — Observe auto healing

**Console path:** Auto Scaling Groups → **`WebServer-ASG`** → **Activity** tab

**Action:**

1. Watch for new activity within **2–3 minutes**:

   > Launching a new EC2 instance. … increasing the capacity from 1 to 2.

2. Note the **start time** of the replacement launch.

**Expected result:** ASG automatically launches a replacement instance to restore desired capacity of 2.

**Verify:**

| Check | Expected |
|-------|----------|
| New launch activity | Appears after termination |
| Status | Successful |
| Desired capacity | Still 2 |

**Screenshot:** Activity tab showing replacement launch after termination time.

**Checkpoint:** `"Step 11 completed"`

---

## Step 12 — Verify new instance is healthy

**Console path:** Target Groups → **`ASG-TG`** → **Targets** tab

**Action:**

1. Wait until the **new** instance shows **healthy** (1–3 minutes after launch).
2. Refresh the **load balancer DNS** in your browser.

**Expected result:**

- Target group shows **two healthy** instances again.
- Browser still serves the demo page (may show a different Instance ID).

**Verify:**

| Check | Expected |
|-------|----------|
| Healthy targets | 2 |
| Browser | Demo page loads via ALB DNS |

**Screenshot:** Target group with two healthy instances **and** browser showing the demo page.

**Checkpoint:** `"Step 12 completed"`

---

## Step 13 — Measure recovery time

**Action:** Record these times from Steps 10–12:

| Event | Your time |
|-------|-----------|
| Instance termination initiated | ____:____ |
| ASG activity shows replacement launch started | ____:____ |
| New instance shows healthy in target group | ____:____ |

**Calculate recovery time:**

```
Recovery Time = (Time instance healthy) − (Time termination initiated)
```

**Example:** 10:05:00 − 10:02:30 = **2 minutes 30 seconds**

**Where to find times on AWS:**

| Event | Console location |
|-------|------------------|
| Termination initiated | Your note when you clicked **Terminate** (EC2 → Instances) |
| Replacement launch | **Auto Scaling Groups** → **`WebServer-ASG`** → **Activity** → Start time on launch row |
| Instance healthy | When **Target Groups** → **`ASG-TG`** → **Targets** shows replacement **Healthy** |

**Expected range:** Typically **2–8 minutes** (boot, user data, and health check thresholds affect duration).

**Screenshot:** Your written recovery time calculation (notebook, text file, or spreadsheet) — not a single AWS console page.

**Checkpoint:** `"Step 13 completed"`

---

## Step 14 — (Optional) Generate CPU load to test scaling policy

> **Note:** Instances are in **private subnets** without public IPs. Direct SSH is not possible unless you use a bastion host in a public subnet. This step is **optional** — skip if you cannot SSH.

**If you have bastion access:**

```bash
ssh -i your-key.pem ec2-user@<instance-private-ip-via-bastion>

sudo dnf install -y stress
stress --cpu 2 --timeout 600 &
```

**Monitor:** EC2 → Auto Scaling Groups → `WebServer-ASG` → **Activity** tab. After **3–5 minutes** of sustained CPU above 70%, ASG may launch additional instances (up to max 6).

**Screenshot (optional):** ASG activity showing scale-out event.

**Checkpoint:** `"Step 14 completed – Lab 2 complete"`

---

## Lab 2 deliverables checklist

| # | Deliverable | Done |
|---|-------------|:----:|
| 1 | Launch template `WebServer-LT` created | ☐ |
| 2 | Target group `ASG-TG` created | ☐ |
| 3 | Application Load Balancer `ASG-ALB` active | ☐ |
| 4 | Auto Scaling Group `WebServer-ASG` created | ☐ |
| 5 | Desired = 2, Min = 2, Max = 6 | ☐ |
| 6 | Two private subnets in different AZs selected | ☐ |
| 7 | Both instances healthy in target group | ☐ |
| 8 | Load balancer serves web page in browser | ☐ |
| 9 | Terminated instance automatically replaced | ☐ |
| 10 | Recovery time calculated (typically 2–8 minutes) | ☐ |

---

## Bonus challenge

**Scenario:** Your Auto Scaling Group has Min=2, Max=6. It is Black Friday and traffic spikes. CPU reaches 85% for 10 minutes.

**Question:** What happens to your ASG? How many instances will you have?

<details>
<summary>Answer</summary>

The **target tracking scaling policy** triggers scale-out. ASG launches additional instances until average CPU drops toward the **70% target**. It will add instances up to the **maximum of 6**. After traffic drops, scale-in removes excess instances (but never below **minimum of 2**).

</details>

---

## Troubleshooting

| Issue | Possible cause | Solution |
|-------|----------------|----------|
| ASG shows 0 instances | Launch template or subnet issue | Check Activity tab for errors; verify subnets use `Private-RT` with NAT route |
| Instances not healthy | Apache not running or user data failed | Wait 3 min; check user data was pasted correctly; verify `Web-SG` allows HTTP:80 |
| Load balancer DNS no response | Security group or no healthy targets | Ensure `Web-SG` allows HTTP:80; wait for targets to become healthy |
| Only one AZ has instances | Only one private subnet selected | Edit ASG → add second private subnet in different AZ |
| `Access Denied` on yum in user data | Private subnet missing NAT route | Confirm `Private-RT` has `0.0.0.0/0 → Lab1-NAT` |
| Scaling policy not triggering | CPU not sustained >70% | Run `stress` for 10+ minutes (optional Step 14) |
| Can't SSH into instance | Instance in private subnet | Use bastion in public subnet, or skip Step 14 |
| ALB creation fails (subnets) | Only one public subnet | Create `Public-Subnet-C` in Step 1C and `Public-Subnet-B` in Step 1D |
| One target **unused** / wrong AZ | ALB subnets do not cover instance AZs | Use **`Public-Subnet-B` + `Public-Subnet-C`** on ALB (Step 4); see [CONSOLE_UI_GUIDE.md](instructor/CONSOLE_UI_GUIDE.md) |
| **us-east-1b** instance keeps restarting; **us-east-1c** fine | ALB missing **us-east-1b** subnet (often `Public-Subnet-A` + `Public-Subnet-C` by mistake) | Create **`Public-Subnet-B`** (Step 1D) → edit **`ASG-ALB`** → subnets **B + C** only → wait for both targets **healthy** |
| ASG Activity shows repeated launch/terminate in one AZ | ELB health check failing for that AZ | Fix ALB subnet mapping first; then check user data and `Private-RT` NAT route for **`Private-Subnet-B`** |

---

## Cost management (important)

| Resource | Approximate cost |
|----------|------------------|
| ALB | ~$0.0225/hour + LCU charges (minimal for lab traffic) |
| EC2 t2.micro × 2 | Free tier eligible (750 hrs/month) |
| NAT Gateway (Lab 1) | ~$0.045/hour — **still running from Lab 1** |

**When finished:** Delete resources in this order (see [instructor teardown guide](instructor/AWS_LAB2_SETUP.md#teardown-order)):

1. Auto Scaling Group `WebServer-ASG` (set desired/min/max to 0 first, or delete ASG)
2. Load balancer `ASG-ALB`
3. Target group `ASG-TG`
4. Launch template `WebServer-LT`

Lab 1 resources (VPC, NAT, Firewall) are torn down separately per Lab 1 instructions.

---

## Key concepts summary

| Concept | How you applied it |
|---------|---------------------|
| **Launch Template** | Defined AMI, instance type, user data for all ASG instances |
| **Target Group** | Health checks verify Apache is serving HTTP 200 on `/` |
| **Application Load Balancer** | Distributes traffic across AZs and instances |
| **Auto Scaling Group** | Maintains desired count; replaces failed instances |
| **Desired Capacity** | Target number of running instances (2) |
| **Min/Max Capacity** | Scaling boundaries (2–6 instances) |
| **Scaling Policy** | Target tracking on CPU at 70% |
| **Auto Healing** | Terminated instance replaced automatically |
| **Cross-AZ Deployment** | Instances in us-east-1b and us-east-1c for fault tolerance |

---

**Lab 2 complete!** You now have a production-style Auto Scaling Group with cross-AZ high availability and auto-healing.

**Next:** Continue with **[Lab 3 — Alerting on Auto Scaling Events](../Day_3_Lab_3_Alerting_Auto_Scaling_Events/instructions.md)** or tear down resources per cost management above.
