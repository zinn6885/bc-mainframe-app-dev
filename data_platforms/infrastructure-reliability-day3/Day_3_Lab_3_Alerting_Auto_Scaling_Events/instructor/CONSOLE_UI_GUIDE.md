# Lab 3 — Console UI troubleshooting

Quick reference when a participant says “I can’t find my resource” or alerts do not arrive.

**Reference screenshots (local, not in git):** `Lab Screenshots Day 3/Lab 3/` — see [README.md](../../../../Lab%20Screenshots%20Day%203/Lab%203/README.md)

---

## SNS subscription must be Confirmed before testing

**Symptom:** No email after Step 9 terminate test.

**Cause:** Subscription still **Pending confirmation**.

**Fix:**
1. SNS → **Subscriptions** → select pending row → **Request confirmation** (or recreate subscription).
2. Check spam/junk for **AWS Notification - Subscription Confirmation**.
3. Refresh until Status = **Confirmed**.

---

## CloudWatch — extra alarms from Lab 2

**Symptom:** Student sees `TargetTracking-WebServer-ASG-AlarmHigh-…` and `AlarmLow-…` and thinks lab is wrong.

**Cause:** Auto Scaling **target tracking policy** from Lab 2 creates its own alarms.

**Fix:** Ignore those for Lab 3 grading. Only verify **`ASG-Scale-Out-Alert`** and **`ASG-Scale-In-Alert`**.

---

## CloudWatch alarm INSUFFICIENT_DATA

**Symptom:** New alarms show **INSUFFICIENT_DATA** for several minutes.

**Cause:** `GroupDesiredCapacity` metrics not yet published for the evaluation period.

**Fix:** Wait **3–5 minutes**, refresh. With desired = 2, both lab alarms should reach **OK**.

---

## Step 4 — capture Actions tab

**Symptom:** Student screenshot shows graph only; instructor cannot see SNS action.

**UI path:** CloudWatch → **Alarms** → **`ASG-Scale-Out-Alert`** → **Actions** tab → row: *When alarm transitions to in alarm, send message to topic **ASG-Alerts***.

Accept **Details** or **Actions** tab if threshold **> 2** and SNS topic are visible.

---

## EventBridge — event pattern and SNS permission

**Symptom:** Rule exists but no email on launch/terminate.

**Checks:**
1. Rule **Enabled**; JSON includes exact string **`WebServer-ASG`** (case-sensitive).
2. **Targets** tab → SNS topic **`ASG-Alerts`**.
3. If target save failed: re-open rule → edit target → accept **Create policy** for EventBridge → SNS.

**UI path:** EventBridge → **Rules** → rule name → **Event pattern** tab (JSON) and **Targets** tab.

---

## Dashboard shows “No data available”

**Symptom:** Step 8 widgets empty.

**Fix:**
1. Set dashboard time range to **3h** or **1h** (top-right of dashboard).
2. Confirm widgets use **AWS/AutoScaling** metrics filtered to **`WebServer-ASG`**.
3. Accept screenshot if **widget titles** and metric names are correct — data may lag a few minutes.

---

## Step 9 — terminate only ONE instance

**Symptom:** ASG stuck at 0 instances or long outage.

**Cause:** Student terminated **both** instances.

**Fix:** Terminate **one** instance only. ASG should launch replacement within 2–4 minutes.

**Verify:** EC2 → **Instances** → filter by ASG column **`WebServer-ASG`**.

---

## Steps 10–11 — email vs console deliverables

| Step | Preferred screenshot | Acceptable alternative |
|------|---------------------|------------------------|
| **10** | Inbox — **EC2 Instance Terminate Successful** or **ASG-Scale-In-Alert** email | CloudWatch **`ASG-Scale-In-Alert`** detail, or ASG **Activity** terminate row |
| **11** | Inbox — **EC2 Instance Launch Successful** with Instance ID in JSON body | **`WebServer-ASG` → Instance management** — 2 **InService** after replacement |

**Note:** EventBridge emails arrive as **JSON** in the message body (sender display name may show **ASG**). This is expected.

**Privacy:** Do not require students to submit screenshots showing personal email addresses or full SNS subscription ARNs — redacted captures are fine.

---

## Screenshot grading notes

| Step | Accept if screenshot shows |
|------|---------------------------|
| 1 | `WebServer-ASG` capacity **2/2/6** and **2** healthy/InService instances (any of Details, Activity, Instance management tabs) |
| 2 | Topic **`ASG-Alerts`**, Type Standard, Topic ARN with `:us-east-1:` |
| 3 | Subscription **Confirmed** (email address may be redacted) |
| 4 | **`ASG-Scale-Out-Alert`**, condition **> 2**, SNS **`ASG-Alerts`** |
| 5 | Both lab alarms listed |
| 6 | Launch rule **Enabled**, event pattern with **`WebServer-ASG`**, SNS target |
| 7 | Both EventBridge rules **Enabled** |
| 8 | Dashboard **`ASG-Monitoring-Dashboard`**, ≥3 widgets with ASG metrics |
| 9 | One instance terminating/terminated, Instance ID visible |
| 10 | Terminate alert email **or** scale-in alarm / Activity evidence |
| 11 | Launch alert email **or** 2 InService instances after heal |

Full participant guide: [../instructions.md](../instructions.md)
