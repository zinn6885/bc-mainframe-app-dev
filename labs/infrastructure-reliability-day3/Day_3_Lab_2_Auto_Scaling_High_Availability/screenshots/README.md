# Lab 2 screenshots

Save your deliverable screenshots **locally** using the filenames below. **Do not commit screenshots to the git repo** — they may show account-specific console details.

**Reference UI (local folder, not in git):** `Lab Screenshots Day 3/Lab 2/README.md` — step-by-step navigation with validated example captures.

See [instructions.md](../instructions.md) for what each screenshot must show.

---

## Region (every console screenshot)

| Item | Required value |
|------|----------------|
| **AWS Region** | **US East (N. Virginia)** |
| **Region code** | **`us-east-1`** |
| **Check before each screenshot** | Top-right corner shows **N. Virginia** or **`us-east-1`** |

Wrong region = wrong AZ names and missing resources. **Always show the region selector in console screenshots.**

Step 9 and Step 12 browser screenshots do not need the AWS region bar — use the **ALB DNS name** in the address bar instead.

---

## Screenshot checklist by step

| Step | Save as | Console / tool | What to verify before you capture |
|------|---------|----------------|-----------------------------------|
| 1 | `Step_01_VPC_Subnets_Verified.png` | **VPC** → **Subnets** | Filter `Lab1-VPC`. See `Private-Subnet-B/C`, `Public-Subnet-B/C`, plus Lab 1 subnets. |
| 2 | `Step_02_Launch_Template.png` | **EC2** → **Launch Templates** → `WebServer-LT` | Version **1**, **Instance details**: `t2.micro`, `Web-SG`, key pair. |
| 3 | `Step_03_Target_Group.png` | **EC2** → **Target Groups** → `ASG-TG` | HTTP:80, health path `/`, success code 200; **Targets** tab = 0. |
| 4 | `Step_04_ALB_Provisioning.png` | **EC2** → **Load Balancers** → `ASG-ALB` | State **provisioning**, subnets **B (1b) + C (1c)**, listener → `ASG-TG`. |
| 5 | `Step_05_ALB_Active.png` | **EC2** → **Load Balancers** → `ASG-ALB` | State **active**, DNS name visible. |
| 6 | `Step_06_Auto_Scaling_Group.png` | **EC2** → **Auto Scaling Groups** → `WebServer-ASG` | **Automatic scaling**: `Scale-on-CPU` 70%; header Desired **2**, limits **2–6**. |
| 7 | `Step_07_ASG_Launch_Activity.png` | **EC2** → **Auto Scaling Groups** → **Activity** | Launch events, Status **Successful**, capacity 0 → 2. |
| 8 | `Step_08_Healthy_Targets.png` | **EC2** → **Target Groups** → **Targets** | 2 targets, both **healthy**, different AZs, no **unused**. |
| 9 | `Step_09_ALB_Browser_Test.png` | **Web browser** | ALB DNS in address bar; demo page with Instance ID. |
| 10 | `Step_10_Instance_Terminated.png` | **EC2** → **Instances** | One `WebServer-ASG` instance **terminating** or **terminated**. |
| 11 | `Step_11_Auto_Healing_Activity.png` | **EC2** → **Auto Scaling Groups** → **Activity** | New launch after termination; Status **Successful**. |
| 12 | `Step_12_Recovery_Healthy.png` | **Target Groups** + **browser** | 2 healthy targets; browser loads ALB page. *(Split part A/B filenames OK.)* |
| 13 | `Step_13_Recovery_Time.png` | Notes / text / spreadsheet | Three times + calculated recovery duration. |
| 14 | `Step_14_CPU_Scaling_Optional.png` | **EC2** → **Auto Scaling Groups** → **Activity** *(optional)* | Scale-out event if you ran CPU stress test. |

Full step instructions: [instructions.md](../instructions.md) · Console UI help: [instructor/CONSOLE_UI_GUIDE.md](../instructor/CONSOLE_UI_GUIDE.md)

---

## Submission format

After each step:

1. Save the screenshot with the filename above (under `Lab Screenshots Day 3/Lab 2/` or your course folder).
2. Reply: `"Step N completed"` (e.g. `"Step 3 completed"`).
3. Attach or upload the matching screenshot to your instructor — **not** to the GitHub repo.

**Minimum deliverables:** Steps **1–13** (Step 14 optional).
