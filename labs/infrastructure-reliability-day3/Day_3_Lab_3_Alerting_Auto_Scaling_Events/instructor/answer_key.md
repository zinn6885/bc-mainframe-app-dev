# Lab 3 — Answer Key (Instructor)

Use this to verify student submissions (screenshots or live console review). All resources must be in **`us-east-1`**. Prerequisite: **`WebServer-ASG`** from Lab 2.

---

## Prerequisites (Lab 2)

| Resource | Expected value |
|----------|----------------|
| Auto Scaling Group | `WebServer-ASG` |
| Capacity | Min 2 · Desired 2 · Max 6 |
| InService instances | 2 |
| Activity | Recent Successful launch events |

---

## Step 2 — SNS Topic

| Field | Expected value |
|-------|----------------|
| Name | `ASG-Alerts` |
| Type | Standard |
| ARN | `arn:aws:sns:us-east-1:<account-id>:ASG-Alerts` |

---

## Step 3 — Email Subscription

| Field | Expected value |
|-------|----------------|
| Protocol | email |
| Topic | ASG-Alerts |
| Status | **Confirmed** (not Pending confirmation) |

Student must show confirmed subscription or confirmation email before Step 9 testing.

---

## Step 4 — Scale-Out Alarm

| Field | Expected value |
|-------|----------------|
| Name | `ASG-Scale-Out-Alert` |
| Metric | AWS/AutoScaling · GroupDesiredCapacity · WebServer-ASG |
| Statistic | Average |
| Period | 1 minute |
| Condition | Greater than **2** |
| Datapoints | 1 out of 1 |
| Action | SNS → ASG-Alerts (In alarm) |
| Normal state | OK (while desired = 2) |

---

## Step 5 — Scale-In Alarm

| Field | Expected value |
|-------|----------------|
| Name | `ASG-Scale-In-Alert` |
| Metric | Same as scale-out |
| Condition | Lower than **2** |
| Action | SNS → ASG-Alerts (In alarm) |
| Both alarms | Listed together · initially OK |

---

## Step 6 — Launch EventBridge Rule

| Field | Expected value |
|-------|----------------|
| Name | `ASG-Instance-Launch-Alert` |
| State | ENABLED |
| Event pattern | `source: aws.autoscaling` · `detail-type: EC2 Instance Launch Successful` · `AutoScalingGroupName: WebServer-ASG` |
| Target | SNS topic ASG-Alerts |

Expected JSON:

```json
{
  "source": ["aws.autoscaling"],
  "detail-type": ["EC2 Instance Launch Successful"],
  "detail": {
    "AutoScalingGroupName": ["WebServer-ASG"]
  }
}
```

---

## Step 7 — Terminate EventBridge Rule

| Field | Expected value |
|-------|----------------|
| Name | `ASG-Instance-Terminate-Alert` |
| State | ENABLED |
| detail-type | `EC2 Instance Terminate Successful` |
| Target | SNS topic ASG-Alerts |

Both rules visible on EventBridge Rules list.

---

## Step 8 — CloudWatch Dashboard

| Field | Expected value |
|-------|----------------|
| Name | `ASG-Monitoring-Dashboard` |
| Widgets | At least 3–4 (required: GroupDesiredCapacity, GroupInServiceInstances, GroupTotalInstances) |
| Optional 4th | CPUUtilization for ASG instances |

---

## Steps 9–11 — Alert testing

| Check | Expected |
|-------|----------|
| Step 9 | One instance terminated (not both) |
| ASG Activity | Terminate + replacement launch |
| Step 10 email | EventBridge terminate notification within ~3 min |
| Step 11 email | EventBridge launch notification within ~4 min of terminate |
| Final ASG state | 2 InService instances restored |

CloudWatch scale-in alarm email may appear briefly during replacement — accept as valid.

**Screenshot alternatives (Steps 10–11):** Accept console evidence if email is delayed — Step 10: **`ASG-Scale-In-Alert`** detail or ASG **Activity** terminate row; Step 11: **`WebServer-ASG` → Instance management** with 2 **InService**. EventBridge emails arrive as **JSON** (sender may show **ASG**). Do not require unredacted personal email in submissions.

**Step 1:** Accept **Details**, **Activity**, or **Instance management** tab if capacity 2/2/6 and 2 healthy instances are visible.

See [CONSOLE_UI_GUIDE.md](CONSOLE_UI_GUIDE.md) for full grading notes.

---

## Step 12 — Lambda (optional)

| Field | Expected value |
|-------|----------------|
| Function name | `FormatASGAlerts` |
| Runtime | Python 3.9+ |
| Env var | `SNS_TOPIC_ARN` = ASG-Alerts topic ARN |
| IAM | Role allows `sns:Publish` |
| Trigger | EventBridge rule for launch (or custom) |

---

## Step 13 — CPU scale-out (optional)

| Check | Expected (if attempted) |
|-------|-------------------------|
| Sustained CPU >70% | ASG desired > 2 |
| ASG-Scale-Out-Alert | In alarm when desired > 2 |
| Email | Launch EventBridge + alarm notification |

---

## Grading rubric (suggested)

| Criteria | Points |
|----------|--------|
| Prerequisites: ASG 2/2/6 running | 5 |
| SNS topic + confirmed email subscription | 15 |
| Both CloudWatch alarms configured correctly | 20 |
| Both EventBridge rules with correct patterns + SNS target | 20 |
| CloudWatch dashboard with ASG metrics | 10 |
| Terminate test + terminate email screenshot | 15 |
| Launch/auto-heal email screenshot | 15 |
| **Total** | **100** |

Optional Lambda: +10 bonus points.

Deduct 5 if region is not us-east-1. Deduct 10 if SNS subscription never confirmed.

---

## Bonus question answer

Change scale-out alarm threshold from **> 2** to **> 4** to alert only when approaching max capacity (6).

---

## Troubleshooting quick answers

| Student report | Instructor response |
|----------------|---------------------|
| No emails at all | Confirm SNS subscription first — Step 3 |
| Only CloudWatch email, no EventBridge | Check rule enabled and ASG name in JSON |
| EventBridge email but no alarm | Normal at steady state — alarm fires on capacity change |
| INSUFFICIENT_DATA on alarms | Wait 5 min after alarm creation |
| Two terminate emails | May have terminated two instances — remind: one only |
| Lambda AccessDenied on sns:Publish | Attach SNS publish policy to execution role |
