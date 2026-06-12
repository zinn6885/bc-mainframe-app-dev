# Lab 3 screenshots

## Region (every AWS Console screenshot)

| Setting | Value |
|---------|-------|
| **AWS Region** | **US East (N. Virginia)** |
| **Region code** | **`us-east-1`** |
| **Where to check** | Top-right corner of the AWS Console |

**Always include the region selector in AWS Console screenshots.** Steps 10–11 prefer your **email inbox**; console alternatives are listed below.

**Reference UI (local folder, not in git):** `Lab Screenshots Day 3/Lab 3/README.md` — step-by-step navigation with validated example captures.

Full step-by-step console paths and what to capture: [instructions.md — AWS region and screenshot checklist](../instructions.md#aws-region-and-screenshot-checklist)

> **Privacy:** Crop or blur your email address in Steps 3 and 10–11 before submitting. **Do not commit PNG files to GitHub.**

---

## Filename and console checklist

| Step | Save as | AWS Console path | What must be visible |
|------|---------|------------------|----------------------|
| 1 | `Step_01_ASG_Verified.png` | **EC2** → **Auto Scaling Groups** → `WebServer-ASG` | Region **`us-east-1`** · Desired **2** / Min **2** / Max **6** · 2 **InService** / **Healthy** instances |
| 2 | `Step_02_SNS_Topic.png` | **SNS** → **Topics** → `ASG-Alerts` | Region **`us-east-1`** · topic **`ASG-Alerts`** · **Topic ARN** (contains `:us-east-1:`) |
| 3 | `Step_03_Email_Subscription_Confirmed.png` | **SNS** → **Subscriptions** *or* email inbox | Status **Confirmed** *(redact email address if required)* |
| 4 | `Step_04_Scale_Out_Alarm.png` | **CloudWatch** → `ASG-Scale-Out-Alert` → **Actions** tab | Region **`us-east-1`** · **> 2** threshold · notifies **ASG-Alerts** |
| 5 | `Step_05_Both_Alarms_OK.png` | **CloudWatch** → **Alarms** → **All alarms** | Both **`ASG-Scale-Out-Alert`** and **`ASG-Scale-In-Alert`** · state **OK** or **INSUFFICIENT_DATA** |
| 6 | `Step_06_Launch_EventBridge_Rule.png` | **EventBridge** → **Rules** → `ASG-Instance-Launch-Alert` | Region **`us-east-1`** · **Enabled** · launch event pattern · target **ASG-Alerts** |
| 7 | `Step_07_Both_EventBridge_Rules.png` | **EventBridge** → **Rules** | Both launch and terminate rules **Enabled** |
| 8 | `Step_08_CloudWatch_Dashboard.png` | **CloudWatch** → **Dashboards** → `ASG-Monitoring-Dashboard` | Region **`us-east-1`** · 3–4 widgets · ASG capacity metrics (empty charts OK — set time range to **3h**) |
| 9 | `Step_09_Instance_Terminating.png` | **EC2** → **Instances** | Region **`us-east-1`** · one instance **Shutting-down** / **Terminated** · Instance ID |
| 10 | `Step_10_Terminate_Email_Alert.png` | **Email inbox** *(preferred)* or **CloudWatch** / **ASG Activity** | Terminate email **or** scale-in alarm / Activity terminate row |
| 11 | `Step_11_Launch_Email_Alert.png` | **Email inbox** *(preferred)* or **ASG Instance management** | Launch email with Instance ID **or** 2 **InService** after heal |
| 12 | `Step_12_Lambda_Optional.png` | **Lambda** → `FormatASGAlerts` *(optional)* | Code deployed · EventBridge trigger · `SNS_TOPIC_ARN` env var |
| 13 | `Step_13_CPU_Scaling_Optional.png` | **EC2** → **ASG** → **Activity** *(optional)* | Scale-out activity or scale-out alarm **In alarm** |
| 14 | `Step_14_Cleanup_Optional.png` | **CloudWatch** or **SNS** *(optional)* | Lab 3 resources deleted |

When submitting to your instructor, reply with the checkpoint text (e.g. `"Step 3 completed"`) and attach the matching screenshot.

Instructor grading notes: [instructor/CONSOLE_UI_GUIDE.md](../instructor/CONSOLE_UI_GUIDE.md)
