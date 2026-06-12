# Lab 3: Alerting on Auto Scaling Events

**Estimated time:** 35–40 minutes  
**Tools needed:** AWS Console (web browser) · email inbox access  
**AWS region:** US East (N. Virginia) — **`us-east-1`** (required)  
**AWS Free Tier:** Yes — SNS, CloudWatch, EventBridge, and Lambda are within free tier limits for this lab. **NAT Gateway and ALB from Labs 1–2 still incur hourly charges.**

### Lab file locations

All paths below are relative to the **Lab 3 folder** (`Day_3_Lab_3_Alerting_Auto_Scaling_Events/`).

| File | Location in repo | When you need it |
|------|------------------|------------------|
| Lab instructions | `instructions.md` | This file — Steps 1–14 |
| Architecture diagram | `diagrams/lab3-alerting-architecture.svg` | Reference |
| Lambda code (optional) | `setup/format_asg_alerts.py` | Copy into Lambda editor (Step 12) |
| Screenshot naming guide | `screenshots/README.md` | After each step |
| Console UI troubleshooting (instructors) | `instructor/CONSOLE_UI_GUIDE.md` | When students are stuck |
| Reference screenshots (local only) | `Lab Screenshots Day 3/Lab 3/` | Compare your screen — **do not commit PNGs to git** |
| Instructor setup (instructors only) | `instructor/AWS_LAB3_SETUP.md` | Pre-class |

---

## Before you start (participants)

1. **Complete Lab 2 first.** You need `WebServer-ASG` running with **Desired = 2**, **Min = 2**, **Max = 6** from [Day 3 Lab 2](../Day_3_Lab_2_Auto_Scaling_High_Availability/instructions.md).
2. Sign in to the **AWS Console** with permissions for SNS, CloudWatch, EventBridge, and (optional) Lambda.
3. Set the region to **US East (N. Virginia)** — top-right corner must show **`us-east-1`**.
4. Have a **real email address** you can access during the lab — you must click the SNS confirmation link.
5. Keep this lab guide open in a second window while you work in the console.

> **Naming is important.** Use the exact resource names in this guide (`ASG-Alerts`, `ASG-Scale-Out-Alert`, etc.) so your instructor can verify your work quickly.

> **Do not delete Lab 2 resources during this lab.** Lab 3 adds alerting on top of your existing Auto Scaling Group.

---

## AWS Console — how to find your lab resources

| Service | Console path | Search / filter tip |
|---------|--------------|---------------------|
| **Auto Scaling Group** | EC2 → **Auto Scaling Groups** | Select **`WebServer-ASG`** — use **Details**, **Activity**, and **Instance management** tabs |
| **SNS topic** | SNS → **Topics** | Topic name **`ASG-Alerts`** |
| **SNS subscription** | SNS → **Subscriptions** | Status must be **Confirmed** before Step 9 |
| **CloudWatch alarms** | CloudWatch → **Alarms** → **All alarms** | Filter or scroll to **`ASG-Scale-Out-Alert`** and **`ASG-Scale-In-Alert`** |
| **EventBridge rules** | Amazon EventBridge → **Rules** | **`ASG-Instance-Launch-Alert`**, **`ASG-Instance-Terminate-Alert`** |
| **Dashboard** | CloudWatch → **Dashboards** | **`ASG-Monitoring-Dashboard`** |

**Extra alarms are normal:** Lab 2 creates **`TargetTracking-WebServer-ASG-AlarmHigh/Low`** alarms automatically. Ignore those — this lab adds **`ASG-Scale-Out-Alert`** and **`ASG-Scale-In-Alert`** only.

**Screenshot privacy:** Steps 3 and 10–11 may show your email address. **Crop or blur your inbox address** before submitting if your instructor requires it. Do not commit screenshot PNGs to GitHub.

**Reference UI (local folder):** See `Lab Screenshots Day 3/Lab 3/README.md` for step-by-step navigation matched to validated captures.

---

## AWS region and screenshot checklist

### Region (required for every step)

| Setting | Value |
|---------|-------|
| **AWS Region** | **US East (N. Virginia)** |
| **Region code** | **`us-east-1`** |
| **Where to check** | Top-right corner of the AWS Console — must show **N. Virginia** or **`us-east-1`** |

> **Include the region in every AWS Console screenshot** (top-right corner) or your instructor cannot verify your work. Labs 1–3 were built in **`us-east-1`** — if you use another region, `WebServer-ASG` and your Lab 2 resources will not appear.

**Before each screenshot:** confirm the region selector shows **`us-east-1`**, then open the console page below.

| Step | AWS Console path | What must be visible in your screenshot |
|------|------------------|----------------------------------------|
| **1** | **EC2** → **Auto Scaling Groups** → `WebServer-ASG` | Region **`us-east-1`** · ASG name **`WebServer-ASG`** · **Details** tab: **Desired 2 / Min 2 / Max 6** · **Activity** tab: **Successful** launch events · **Instance management** tab: **2** instances **InService** |
| **2** | **SNS** → **Topics** → `ASG-Alerts` | Region **`us-east-1`** · topic name **`ASG-Alerts`** · Type **Standard** · **Topic ARN** visible (must contain `:us-east-1:`) |
| **3** | **SNS** → **Subscriptions** *(or your email inbox)* | Region **`us-east-1`** on console screenshot · Protocol **Email** · Topic **`ASG-Alerts`** · Status **Confirmed** — *or* screenshot of AWS confirmation email with **Confirm subscription** link clicked |
| **4** | **CloudWatch** → **Alarms** → **All alarms** → `ASG-Scale-Out-Alert` | Region **`us-east-1`** · alarm name **`ASG-Scale-Out-Alert`** · metric **GroupDesiredCapacity** · condition **Greater than 2** · action **SNS: ASG-Alerts** · state **OK** |
| **5** | **CloudWatch** → **Alarms** → **All alarms** | Region **`us-east-1`** · **both** alarms listed: **`ASG-Scale-Out-Alert`** and **`ASG-Scale-In-Alert`** · scale-in condition **Lower than 2** · both state **OK** (or **INSUFFICIENT_DATA** if just created — wait 5 min and refresh) |
| **6** | **Amazon EventBridge** → **Rules** → `ASG-Instance-Launch-Alert` | Region **`us-east-1`** · rule name **`ASG-Instance-Launch-Alert`** · Status **Enabled** · event pattern shows **`aws.autoscaling`** and **`EC2 Instance Launch Successful`** · **`WebServer-ASG`** in pattern · target **SNS topic ASG-Alerts** |
| **7** | **Amazon EventBridge** → **Rules** | Region **`us-east-1`** · **both** rules listed: **`ASG-Instance-Launch-Alert`** and **`ASG-Instance-Terminate-Alert`** · both **Enabled** |
| **8** | **CloudWatch** → **Dashboards** → `ASG-Monitoring-Dashboard` | Region **`us-east-1`** · dashboard name **`ASG-Monitoring-Dashboard`** · at least **3–4 widgets** visible · metrics include **GroupDesiredCapacity**, **GroupInServiceInstances**, **GroupTotalInstances** for **`WebServer-ASG`** |
| **9** | **EC2** → **Instances** | Region **`us-east-1`** · one instance from **`WebServer-ASG`** with state **`Shutting-down`** or **`Terminated`** · **Instance ID** visible · only **one** instance terminated (not both) |
| **10** | **Your email inbox** *(preferred)* **or** CloudWatch → **`ASG-Scale-In-Alert`** / ASG **Activity** | Email from **AWS Notifications** · subject **`EC2 Instance Terminate Successful`** or **`ASG-Scale-In-Alert`** · *or* console showing terminate event / scale-in alarm |
| **11** | **Your email inbox** *(preferred)* **or** EC2 → **`WebServer-ASG` → Instance management** | Email **`EC2 Instance Launch Successful`** · JSON body includes **Instance ID** · *or* **2 InService** instances after replacement |
| **12** | **Lambda** → **Functions** → `FormatASGAlerts` *(optional)* | Region **`us-east-1`** · function name **`FormatASGAlerts`** · Python runtime · **Environment variable** `SNS_TOPIC_ARN` set · **EventBridge trigger** attached |
| **13** | **EC2** → **Auto Scaling Groups** → `WebServer-ASG` → **Activity** tab *(optional)* | Region **`us-east-1`** · scale-out activity (desired capacity **> 2**) after CPU load — *or* **CloudWatch** → **`ASG-Scale-Out-Alert`** in **In alarm** state |
| **14** | **SNS** → **Topics** or **CloudWatch** → **Alarms** *(optional)* | Region **`us-east-1`** · Lab 3 resources deleted (empty alarms list, or topic `ASG-Alerts` no longer exists) |

**Screenshot filenames:** save as `Step_01_….png` through `Step_14_….png` — see [screenshots/README.md](screenshots/README.md).

**After each screenshot:** reply to your instructor with the checkpoint text for that step (e.g. `"Step 3 completed"`).

---

## Lab objectives

By the end of this lab, you will be able to:

- Create an SNS topic for Auto Scaling alerts with an email subscription
- Configure EventBridge rules for EC2 instance launch and terminate events
- Create CloudWatch alarms to monitor Auto Scaling group capacity changes
- Build a CloudWatch dashboard for Auto Scaling metrics
- (Optional) Create a Lambda function to format and enrich alerts
- Generate load to trigger Auto Scaling and receive email notifications

---

## Architecture overview

![Lab 3 architecture: EventBridge, CloudWatch, SNS, and optional Lambda for ASG alerts](diagrams/lab3-alerting-architecture.svg)

```
WebServer-ASG (from Lab 2)
        │
        ├── Launch / Terminate events ──► EventBridge rules ──► SNS topic ASG-Alerts ──► Email
        │
        ├── GroupDesiredCapacity metric ──► CloudWatch alarms ──► SNS topic ASG-Alerts ──► Email
        │
        └── ASG metrics ──► CloudWatch dashboard ASG-Monitoring-Dashboard

(Optional) EventBridge ──► Lambda FormatASGAlerts ──► SNS (formatted email)
```

**What Lab 2 provides:** `WebServer-ASG` with 2 running instances, ALB, target group.  
**What Lab 3 adds:** SNS topic, email subscription, 2 CloudWatch alarms, 2 EventBridge rules, monitoring dashboard, optional Lambda formatter.

---

## Step 1 — Verify Auto Scaling Group is running

**Console path:** Search bar → **EC2** → left menu **Auto Scaling Groups**

### Action

1. Click **Auto Scaling Groups** in the left navigation (under **Auto Scaling**).
2. Select **`WebServer-ASG`**.
3. On the **Details** tab, confirm:

| Setting | Expected value |
|---------|----------------|
| **Desired capacity** | 2 |
| **Minimum capacity** | 2 |
| **Maximum capacity** | 6 |
| **Status** | Active (no errors) |

4. Click the **Activity** tab.
5. Confirm recent **Launching a new EC2 instance** activities show status **Successful**.

6. Click the **Instance management** tab — confirm **2** instances with lifecycle state **InService** and Health **Healthy**.

### What you should see

| Tab | Expected |
|-----|----------|
| **Details** (or page header) | Desired **2**, Min **2**, Max **6**, status **At desired capacity** |
| **Activity** | **Launching a new EC2 instance** rows with Status **Successful** |
| **Instance management** | **2** rows — Lifecycle **InService**, Health **Healthy** |

**Verify:**

| Check | Expected |
|-------|----------|
| ASG name | `WebServer-ASG` |
| Capacity | Min 2 · Desired 2 · Max 6 |
| Running instances | 2 InService |
| Activity history | Successful launches |

**Screenshot:** **`Step_01_ASG_Verified.png`** — capacity **2/2/6** and **2 InService** instances. **Instance management** tab is clearest; **Details** or **Activity** also accepted.

**Checkpoint:** `"Step 1 completed"`

---

## Step 2 — Create SNS topic for Auto Scaling alerts

**Console path:** Search bar → **SNS** → **Topics** → **Create topic**

### Action

1. Open **Amazon SNS**.
2. In the left menu, click **Topics**.
3. Click **Create topic**.

| Setting | Value |
|---------|-------|
| **Type** | Standard |
| **Name** | `ASG-Alerts` |
| **Display name** | `ASG` (optional — short name shown in SMS/email sender) |

4. Leave other settings at defaults.
5. Click **Create topic**.

6. On the topic details page, **copy the Topic ARN** — you need it in Step 12 (optional Lambda).

   Example format: `arn:aws:sns:us-east-1:123456789012:ASG-Alerts`

**Verify:**

| Check | Expected |
|-------|----------|
| Topic name | `ASG-Alerts` |
| Type | Standard |
| ARN visible | `arn:aws:sns:us-east-1:...:ASG-Alerts` |

**Screenshot:** SNS topic `ASG-Alerts` created with Topic ARN visible.

**Checkpoint:** `"Step 2 completed"`

---

## Step 3 — Create and confirm email subscription

**Console path:** SNS → **Topics** → select `ASG-Alerts` → **Create subscription**

### Action

1. With **`ASG-Alerts`** selected, click **Create subscription**.

| Setting | Value |
|---------|-------|
| **Topic ARN** | (pre-filled — `ASG-Alerts`) |
| **Protocol** | **Email** |
| **Endpoint** | Your real email address (e.g. `you@company.com`) |

2. Click **Create subscription**.

3. Status shows **Pending confirmation** — this is expected.

4. **Check your email inbox** (and spam/junk folder):
   - Look for **AWS Notification - Subscription Confirmation**
   - Open the email and click **Confirm subscription**

5. Return to SNS → **Subscriptions** (left menu).
6. Refresh the page — status should now be **Confirmed**.

> **Important:** Alerts will **not** arrive until the subscription is confirmed. Complete this step before testing in Steps 9–11.

> **Privacy:** Your email address appears in the Subscriptions table. **Crop or blur it** in your screenshot before submitting if required by your instructor.

**Verify:**

| Check | Expected |
|-------|----------|
| Protocol | email |
| Status (after confirm) | Confirmed |
| Topic | ASG-Alerts |

**Screenshot:** Subscription with status **Confirmed** (or confirmation email open).

**Checkpoint:** `"Step 3 completed"`

---

## Step 4 — Create CloudWatch alarm for scale-out events

**Console path:** Search bar → **CloudWatch** → **Alarms** → **All alarms** → **Create alarm**

> **What this alarm does:** Fires when **Group Desired Capacity** goes **above 2** — for example when the ASG scales out due to CPU load or replaces instances during recovery.

### 4A — Select metric

1. Click **Create alarm**.
2. Click **Select metric**.
3. Browse: **AWS/AutoScaling** → metric **GroupDesiredCapacity**.
4. In the search box, type **`WebServer-ASG`** and select the row for your ASG.
5. Click **Select metric**.

### 4B — Configure metric and conditions

| Setting | Value |
|---------|-------|
| **Statistic** | Average |
| **Period** | 1 minute |
| **Threshold type** | Static |
| **Whenever GroupDesiredCapacity is...** | **Greater** than threshold |
| **than...** | `2` |
| **Datapoints to alarm** | 1 out of 1 |

### 4C — Configure actions

1. Under **Notification**, expand **In alarm**.
2. Click **Select an existing SNS topic**.
3. Choose **`ASG-Alerts`**.

### 4D — Name and create

| Setting | Value |
|---------|-------|
| **Alarm name** | `ASG-Scale-Out-Alert` |
| **Alarm description** | `Alert when Auto Scaling Group scales out beyond desired capacity of 2` |

4. Click **Next** through remaining pages (defaults are fine) → **Create alarm**.

5. Open the alarm → **Actions** tab — confirm: *When alarm transitions to in alarm, send message to topic **ASG-Alerts***.

> **Note:** You may also see **`TargetTracking-WebServer-ASG-AlarmHigh`** from Lab 2 on the All alarms page — ignore it for this lab.

**Verify:**

| Check | Expected |
|-------|----------|
| Alarm name | `ASG-Scale-Out-Alert` |
| Condition | > 2 |
| SNS action | ASG-Alerts |
| Initial state | OK (while desired = 2) |

**Screenshot:** **`Step_04_Scale_Out_Alarm.png`** — **`Actions`** tab (preferred) or alarm graph showing **> 2** and SNS **`ASG-Alerts`**.

**Checkpoint:** `"Step 4 completed"`

---

## Step 5 — Create CloudWatch alarm for scale-in events

**Console path:** CloudWatch → **Alarms** → **Create alarm**

> **What this alarm does:** Fires when **Group Desired Capacity** drops **below 2**. During normal lab operation with desired = 2, this alarm may briefly fire during instance replacement — that is expected and useful for learning.

### Action

1. Click **Create alarm** again.

2. **Select metric:** Same path — **AWS/AutoScaling** → **GroupDesiredCapacity** → **`WebServer-ASG`**.

3. **Configure conditions:**

| Setting | Value |
|---------|-------|
| **Statistic** | Average |
| **Period** | 1 minute |
| **Threshold type** | Static |
| **Condition** | **Lower** than threshold |
| **Threshold** | `2` |
| **Datapoints to alarm** | 1 out of 1 |

4. **Notification:** In alarm → SNS topic **`ASG-Alerts`**.

5. **Name:**

| Setting | Value |
|---------|-------|
| **Alarm name** | `ASG-Scale-In-Alert` |
| **Alarm description** | `Alert when Auto Scaling Group scales in below desired capacity of 2` |

6. Click **Create alarm**.

7. On the **All alarms** page, confirm **both** alarms exist:

| Alarm | Condition | Expected state (now) |
|-------|-----------|----------------------|
| `ASG-Scale-Out-Alert` | > 2 | OK |
| `ASG-Scale-In-Alert` | < 2 | OK |

> **Note:** If either alarm shows **INSUFFICIENT_DATA**, wait 3–5 minutes for metrics to populate, then refresh.

**Screenshot:** Both alarms listed with OK status.

**Checkpoint:** `"Step 5 completed"`

---

## Step 6 — Create EventBridge rule for instance launch events

**Console path:** Search bar → **Amazon EventBridge** → **Rules** → **Create rule**

> **What EventBridge does:** Captures **specific AWS API events** (like instance launch) and routes them to targets (like SNS). This gives you immediate notification with event details — not just metric thresholds.

### 6A — Define rule detail

| Setting | Value |
|---------|-------|
| **Name** | `ASG-Instance-Launch-Alert` |
| **Description** | `Alert when Auto Scaling launches a new EC2 instance` |
| **Event bus** | default |
| **Rule type** | **Rule with an event pattern** |
| **Enabled** | Yes |

Click **Next**.

### 6B — Build event pattern

**Option A — Console builder (recommended for beginners):**

1. Select **AWS services**.
2. **Service provider:** Auto Scaling.
3. **Event type:** **EC2 Instance Launch Successful**.
4. Switch to **Event pattern preview** and confirm it includes `"source": ["aws.autoscaling"]`.

**Option B — Custom pattern (matches lab exactly):**

1. Select **Custom pattern (JSON editor)**.
2. Paste:

```json
{
  "source": ["aws.autoscaling"],
  "detail-type": ["EC2 Instance Launch Successful"],
  "detail": {
    "AutoScalingGroupName": ["WebServer-ASG"]
  }
}
```

Click **Next**.

### 6C — Select target

| Setting | Value |
|---------|-------|
| **Target types** | AWS service |
| **Select a target** | **SNS topic** |
| **Topic** | `ASG-Alerts` |

> EventBridge may prompt you to **create a resource-based policy** allowing EventBridge to publish to SNS — click **Create policy** or **Configure details** and accept.

Click **Next** → **Next** → **Create rule**.

**Verify:**

| Check | Expected |
|-------|----------|
| Rule name | `ASG-Instance-Launch-Alert` |
| State | Enabled |
| Target | SNS topic ASG-Alerts |

**Screenshot:** Rule `ASG-Instance-Launch-Alert` with event pattern visible.

**Checkpoint:** `"Step 6 completed"`

---

## Step 7 — Create EventBridge rule for instance terminate events

**Console path:** EventBridge → **Rules** → **Create rule**

### Action

1. Click **Create rule**.

| Setting | Value |
|---------|-------|
| **Name** | `ASG-Instance-Terminate-Alert` |
| **Description** | `Alert when Auto Scaling terminates an EC2 instance` |
| **Event bus** | default |
| **Rule type** | Rule with an event pattern |

2. **Event pattern — Custom pattern (JSON editor):**

```json
{
  "source": ["aws.autoscaling"],
  "detail-type": ["EC2 Instance Terminate Successful"],
  "detail": {
    "AutoScalingGroupName": ["WebServer-ASG"]
  }
}
```

3. Click **Next**.

4. **Target:** AWS service → **SNS topic** → **`ASG-Alerts`**.

5. Accept any SNS permission prompt → **Create rule**.

6. On the **Rules** list, confirm **both** rules:

| Rule | Status |
|------|--------|
| `ASG-Instance-Launch-Alert` | Enabled |
| `ASG-Instance-Terminate-Alert` | Enabled |

**Screenshot:** Both EventBridge rules listed and enabled.

**Checkpoint:** `"Step 7 completed"`

---

## Step 8 — Create CloudWatch dashboard for Auto Scaling metrics

**Console path:** CloudWatch → **Dashboards** → **Create dashboard**

### 8A — Create dashboard

| Setting | Value |
|---------|-------|
| **Dashboard name** | `ASG-Monitoring-Dashboard` |

Click **Create dashboard**.

### 8B — Widget 1 — Group Desired Capacity (line chart)

1. Click **Add widget** → **Line** → **Configure**.
2. **Metrics** tab → **Browse** → **AWS/AutoScaling** → **GroupDesiredCapacity**.
3. Select the metric for **`WebServer-ASG`**.
4. Click **Create widget**.

### 8C — Widget 2 — Group In-Service Instances (number or line)

1. **Add widget** → **Number** (or **Line**).
2. Metric: **AWS/AutoScaling** → **GroupInServiceInstances** → **`WebServer-ASG`**.
3. **Create widget**.

### 8D — Widget 3 — Group Total Instances

1. **Add widget** → **Line**.
2. Metric: **AWS/AutoScaling** → **GroupTotalInstances** → **`WebServer-ASG`**.
3. **Create widget**.

### 8E — Widget 4 — Average CPU Utilization (EC2)

1. **Add widget** → **Line**.
2. **Metrics** → **Browse** → **AWS/EC2** → **CPUUtilization**.
3. Under **AutoScalingGroupName**, select **`WebServer-ASG`**.
   - If that dimension is not listed, use **Graphed metrics** → **Add math** → **Average** across the instance metrics you see for your ASG instances.
4. **Create widget**.

### 8F — Save

Click **Save dashboard**.

> **Empty widgets?** Set the dashboard time range to **3 hours** (top-right). Metrics may take a few minutes to appear after ASG activity.

**Verify:**

| Check | Expected |
|-------|----------|
| Dashboard name | `ASG-Monitoring-Dashboard` |
| Widget count | At least 4 widgets |
| Metrics | Desired capacity, in-service, total instances visible |

> **Widget 5 (Recent Events / Logs table):** Optional — requires additional EventBridge → CloudWatch Logs setup. The four metric widgets above satisfy the lab deliverable.

**Screenshot:** Dashboard with at least 3–4 metric widgets showing ASG data.

**Checkpoint:** `"Step 8 completed"`

---

## Step 9 — Test alerts: terminate an instance

**Console path:** EC2 → **Instances**

> **What happens next:** When you terminate an instance, the ASG detects the capacity drop and launches a replacement. You should receive **EventBridge** and possibly **CloudWatch** emails within 2–3 minutes.

### Action

1. Go to **EC2** → **Instances**.
2. Find an instance belonging to **`WebServer-ASG`**:
   - Check the **Auto Scaling Group** column, or
   - Filter by ASG name, or
   - Look for instances tagged **Name = WebServer-ASG**
3. Select **one** instance only (do not select both).
4. **Instance state** → **Terminate instance**.
5. Confirm **Terminate**.

6. Wait until **Instance state** shows **Shutting-down** or **Terminated**.

7. Open **Auto Scaling Groups** → **`WebServer-ASG`** → **Activity** tab — watch for terminate and replacement launch events.

**Verify:**

| Check | Expected |
|-------|----------|
| Terminated instance | One instance in shutting-down/terminated state |
| ASG Activity | Terminate + new launch activity appears |
| Instance count | ASG begins launching replacement |

**Screenshot:** Instance in terminating state with Instance ID visible.

**Checkpoint:** `"Step 9 completed"`

---

## Step 10 — Check email alerts (terminate event)

**Action:** Wait **2–3 minutes**, then check your email.

### Expected emails

| Subject (approximate) | Source |
|-----------------------|--------|
| `EC2 Instance Terminate Successful` | EventBridge → SNS |
| `ALARM: "ASG-Scale-In-Alert" in US East (N. Virginia)` | CloudWatch (may appear briefly during replacement) |

> Email subjects vary slightly by region wording. Look for messages from **AWS Notifications** (`no-reply@sns.amazonaws.com`). EventBridge messages arrive as **JSON** in the email body (sender may display as **ASG**).

### Also verify in console (if email is delayed)

1. **Auto Scaling Groups** → **`WebServer-ASG`** → **Activity** — terminate row and replacement launch in progress.
2. **CloudWatch** → **Alarms** → **`ASG-Scale-In-Alert`** — may show activity during replacement.

**Screenshot:** **`Step_10_Terminate_Email_Alert.png`** — inbox showing terminate alert **(preferred)**, **or** CloudWatch **`ASG-Scale-In-Alert`** detail / ASG **Activity** terminate row. Redact personal email if submitting inbox captures.

**Checkpoint:** `"Step 10 completed"`

---

## Step 11 — Check email alert (launch / auto-heal event)

**Action:** Wait **2–4 minutes** after Step 9 for the ASG to launch a replacement instance.

### Expected email

| Subject (approximate) | Source |
|-----------------------|--------|
| `EC2 Instance Launch Successful` | EventBridge → SNS |

### Verify in console

1. **Auto Scaling Groups** → **Instance management** — back to **2** InService instances.
2. **EC2** → **Target Groups** → **`ASG-TG`** — **2 healthy** targets (may take 2–3 min after launch).

**Screenshot:** **`Step_11_Launch_Email_Alert.png`** — inbox showing **`EC2 Instance Launch Successful`** with Instance ID in JSON body **(preferred)**, **or** **`WebServer-ASG` → Instance management** showing **2 InService / Healthy** after replacement.

**Checkpoint:** `"Step 11 completed"`

---

## Step 12 — (Optional) Create Lambda function for formatted alerts

> **Skip this step** if you are short on time. Steps 1–11 complete the core lab.

**Console path:** Search bar → **Lambda** → **Functions** → **Create function**

### 12A — Create function

| Setting | Value |
|---------|-------|
| **Function name** | `FormatASGAlerts` |
| **Runtime** | Python 3.12 (or Python 3.9+) |
| **Architecture** | x86_64 |
| **Permissions** | Create a new role with basic Lambda permissions |

Click **Create function**.

### 12B — Configure environment variable

1. **Configuration** tab → **Environment variables** → **Edit**.
2. Add:

| Key | Value |
|-----|-------|
| `SNS_TOPIC_ARN` | Your topic ARN from Step 2 (e.g. `arn:aws:sns:us-east-1:123456789012:ASG-Alerts`) |

3. **Save**.

### 12C — Deploy code

1. **Code** tab → delete the default handler code.
2. Open [setup/format_asg_alerts.py](setup/format_asg_alerts.py) from this lab folder.
3. Copy the entire file contents into the Lambda editor.
4. Click **Deploy**.

### 12D — Add SNS publish permission to Lambda role

1. **Configuration** → **Permissions** → click the **execution role** name (opens IAM).
2. **Add permissions** → **Attach policies** → search **`AmazonSNSFullAccess`** (lab only) or create a minimal policy allowing `sns:Publish` to your topic ARN only.
3. Attach and return to Lambda.

### 12E — Add EventBridge trigger (launch events)

1. Lambda → **FormatASGAlerts** → **Add trigger**.
2. Select **EventBridge (CloudWatch Events)**.
3. **Create a new rule** (or select existing):
   - Name: `FormatASGAlerts-Launch-Trigger`
   - Event pattern: same JSON as Step 6 (Launch Successful for `WebServer-ASG`)
4. **Add**.

> **Instructor note:** For production, point EventBridge to Lambda **instead of** SNS for launch events — or use a separate rule — to avoid duplicate emails. For learning, students may receive both raw EventBridge SNS messages and formatted Lambda messages.

**Screenshot:** Lambda `FormatASGAlerts` with code deployed and EventBridge trigger attached.

**Checkpoint:** `"Step 12 completed"`

---

## Step 13 — (Optional) Generate load to trigger scale-out

> **Note:** Instances are in **private subnets** without public IPs. SSH requires a bastion host. Skip if you cannot reach an instance.

**If you have bastion access:**

```bash
ssh -i your-key.pem ec2-user@<instance-ip-via-bastion>

sudo dnf install -y stress
stress --cpu 2 --timeout 600 &
```

**Monitor:**

1. **Auto Scaling Groups** → **`WebServer-ASG`** → **Activity** — scale-out after 3–5 minutes sustained CPU > 70%.
2. **CloudWatch** → **Alarms** → **`ASG-Scale-Out-Alert`** — state changes to **In alarm** when desired capacity > 2.
3. **Email** — scale-out alarm and launch EventBridge notifications.

**Screenshot (optional):** ASG Activity showing scale-out OR `ASG-Scale-Out-Alert` in alarm state.

**Checkpoint:** `"Step 13 completed"`

---

## Step 14 — Clean up Lab 3 resources (cost control)

> **Delete Lab 3 resources only.** Keep Lab 2 ASG/ALB running if you continue with other exercises, or tear down Lab 2 separately per Lab 2 instructions.

**Delete in this order:**

| # | Resource | Console path | Action |
|---|----------|--------------|--------|
| 1 | Lambda `FormatASGAlerts` (if created) | Lambda → Functions | Delete |
| 2 | EventBridge rules | EventBridge → Rules | Disable → Delete both rules |
| 3 | CloudWatch alarms | CloudWatch → Alarms | Select both → Delete |
| 4 | CloudWatch dashboard | CloudWatch → Dashboards | Delete `ASG-Monitoring-Dashboard` |
| 5 | SNS subscription | SNS → Subscriptions | Delete email subscription |
| 6 | SNS topic | SNS → Topics → `ASG-Alerts` | Delete |

**Screenshot (optional):** Empty alarms list or deleted topic confirmation.

**Checkpoint:** `"Step 14 completed – Lab 3 complete"`

---

## Lab 3 deliverables checklist

| # | Deliverable | Done |
|---|-------------|:----:|
| 1 | ASG `WebServer-ASG` verified running (2/2/6) | ☐ |
| 2 | SNS topic `ASG-Alerts` created | ☐ |
| 3 | Email subscription confirmed | ☐ |
| 4 | CloudWatch alarm `ASG-Scale-Out-Alert` created (> 2) | ☐ |
| 5 | CloudWatch alarm `ASG-Scale-In-Alert` created (< 2) | ☐ |
| 6 | EventBridge rule for instance launch | ☐ |
| 7 | EventBridge rule for instance terminate | ☐ |
| 8 | CloudWatch dashboard `ASG-Monitoring-Dashboard` created | ☐ |
| 9 | Terminated instance triggered email alert | ☐ |
| 10 | New instance launch triggered email alert | ☐ |
| 11 | (Optional) Lambda function `FormatASGAlerts` | ☐ |

---

## Bonus challenge

**Scenario:** Your ASG scales out to 4 instances during peak load. The scale-out alarm triggers at > 2 instances and you receive an email every time.

**Question:** How would you modify the alarm to only alert when scaling out beyond 4 instances (approaching max capacity of 6)?

<details>
<summary>Answer</summary>

Change the **scale-out alarm threshold** from **> 2** to **> 4**. This reduces noise and only alerts when scaling is near the maximum limit of 6 instances.

</details>

---

## Troubleshooting

| Issue | Possible cause | Solution |
|-------|----------------|----------|
| No email received | Subscription not confirmed | Check spam; click Confirm subscription link in Step 3 |
| EventBridge rule not triggering | Wrong event pattern or ASG name | Verify JSON includes `"WebServer-ASG"` exactly |
| CloudWatch alarm shows `INSUFFICIENT_DATA` | Metrics not yet published | Wait 5–10 minutes; refresh alarm page |
| Lambda not sending email | Missing SNS permission or wrong ARN | Set `SNS_TOPIC_ARN` env var; attach `sns:Publish` to role |
| Scale-out alarm on every replacement | Threshold too low (2) | Expected for learning; change to > 3 or > 4 for production |
| Duplicate emails | EventBridge → SNS and Lambda → SNS both active | Disable one target or use Lambda-only for formatted alerts |
| Can't SSH for Step 13 | Instances in private subnet | Use bastion or skip optional step |
| EventBridge cannot publish to SNS | Missing resource policy | Re-save rule target; accept "Create policy" prompt |

---

## Cost management (important)

| Resource | Approximate cost |
|----------|------------------|
| SNS / EventBridge / CloudWatch alarms | Free tier for lab volume |
| Lambda (optional) | Free tier (1M requests/month) |
| ALB + EC2 + NAT (Labs 1–2) | Still running — see Lab 2 cost table |

**When finished:** Delete Lab 3 resources per Step 14. Tear down Lab 2 and Lab 1 separately when done with all Day 3 AWS labs.

---

## Key concepts summary

| Concept | How you applied it |
|---------|---------------------|
| **SNS Topic** | Central notification hub for all ASG alerts |
| **Email Subscription** | Delivers alerts to your inbox (requires confirmation) |
| **CloudWatch Alarm** | Monitors `GroupDesiredCapacity` for scale-out/in |
| **EventBridge Rule** | Captures launch/terminate events with JSON event pattern |
| **Event Pattern** | Filters by `source`, `detail-type`, and ASG name |
| **CloudWatch Dashboard** | Visualizes ASG capacity and CPU metrics |
| **Lambda (Optional)** | Formats raw events into readable email messages |

---

## Quick reference: EventBridge event patterns

| Event type | detail-type value |
|------------|-------------------|
| Instance launch | `EC2 Instance Launch Successful` |
| Instance launch failed | `EC2 Instance Launch Unsuccessful` |
| Instance terminate | `EC2 Instance Terminate Successful` |
| Scale out / scale in | Use CloudWatch metric alarms (not direct EventBridge events) |

---

**Lab 3 complete!** You now have a complete alerting system that notifies you via email whenever your Auto Scaling Group launches or terminates instances.

**Previous:** [Lab 2 — Auto Scaling & High Availability](../Day_3_Lab_2_Auto_Scaling_High_Availability/instructions.md)
