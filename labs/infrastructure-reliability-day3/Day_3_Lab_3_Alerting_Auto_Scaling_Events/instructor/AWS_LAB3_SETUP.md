# Lab 3 — AWS Setup & Validation (Instructor)

**Region:** `us-east-1`  
**Prerequisite:** Day 3 Lab 2 — `WebServer-ASG` running at 2/2/6

---

## IAM permissions (minimum)

Students and validation script need permissions for:

- `autoscaling:DescribeAutoScalingGroups`
- `sns:CreateTopic`, `sns:Subscribe`, `sns:ListTopics`, `sns:ListSubscriptionsByTopic`, `sns:DeleteTopic`, `sns:Unsubscribe`
- `cloudwatch:PutMetricAlarm`, `cloudwatch:DescribeAlarms`, `cloudwatch:PutDashboard`, `cloudwatch:GetDashboard`, `cloudwatch:DeleteAlarms`, `cloudwatch:DeleteDashboards`
- `events:PutRule`, `events:DescribeRule`, `events:ListTargetsByRule`, `events:PutTargets`, `events:DeleteRule`, `events:EnableRule`, `events:DisableRule`
- `lambda:CreateFunction`, `lambda:UpdateFunctionCode`, `lambda:GetFunction`, `lambda:DeleteFunction`, `lambda:AddPermission` (optional Step 12)
- `iam:PassRole` (Lambda execution role — optional)

EventBridge → SNS requires accepting the **resource-based policy** on the SNS topic (console creates this automatically).

---

## Pre-class checklist

1. [ ] Lab 2 validation passed (`WebServer-ASG` 2/2/6, 2 healthy targets)
2. [ ] Student accounts can create SNS topics and CloudWatch alarms (some orgs restrict SNS email)
3. [ ] Students can receive external email (corporate filters may block `sns.amazonaws.com`)
4. [ ] Instructor ran validation script after building reference lab:

```powershell
cd Day_3_Lab_3_Alerting_Auto_Scaling_Events
pip install -r setup/requirements.txt
python setup/test_alerting_lab3.py
```

5. [ ] Instructor confirmed SNS subscription on reference account

---

## Validation script usage

| Command | Purpose |
|---------|---------|
| `python setup/test_alerting_lab3.py --prerequisites-only` | Check Lab 2 ASG before lab |
| `python setup/test_alerting_lab3.py` | Check full Lab 3 stack (default) |
| `python setup/test_alerting_lab3.py --include-lambda` | Also require `FormatASGAlerts` Lambda |

**Requirements:** Python 3.9+, `boto3`. AWS credentials via environment, profile, or instance role.

---

## Expected validation output

```
=== Lab 3 Prerequisites ===
PASS  Auto Scaling group WebServer-ASG running (2/2/6)
PASS  ASG has 2 InService instance(s)

=== SNS ===
PASS  SNS topic ASG-Alerts
PASS  Email subscription confirmed (1)

=== CloudWatch Alarms ===
PASS  Alarm ASG-Scale-Out-Alert (GreaterThanThreshold, threshold 2)
PASS  ASG-Scale-Out-Alert sends to ASG-Alerts
PASS  Alarm ASG-Scale-In-Alert (LessThanThreshold, threshold 2)
PASS  ASG-Scale-In-Alert sends to ASG-Alerts

=== EventBridge Rules ===
PASS  Rule ASG-Instance-Launch-Alert enabled
PASS  Rule ASG-Instance-Launch-Alert event pattern correct
PASS  Rule ASG-Instance-Launch-Alert targets ASG-Alerts
PASS  Rule ASG-Instance-Terminate-Alert enabled
PASS  Rule ASG-Instance-Terminate-Alert event pattern correct
PASS  Rule ASG-Instance-Terminate-Alert targets ASG-Alerts

=== CloudWatch Dashboard ===
PASS  Dashboard ASG-Monitoring-Dashboard has 4 widget(s)
PASS  Dashboard includes GroupDesiredCapacity
PASS  Dashboard includes GroupInServiceInstances
PASS  Dashboard includes GroupTotalInstances

All checks passed.
```

---

## End-to-end test (instructor)

After building the reference lab:

1. Terminate **one** ASG instance (EC2 → Instances).
2. Within **2–3 minutes**, verify:
   - Email: `EC2 Instance Terminate Successful`
   - ASG Activity: replacement launch started
3. Within **4–6 minutes**, verify:
   - Email: `EC2 Instance Launch Successful`
   - ASG back to 2 InService instances
4. Run `python setup/test_alerting_lab3.py` — all checks pass.

---

## Teardown order

Delete **Lab 3 resources only** (keep Lab 2 unless full Day 3 teardown):

1. **Lambda** `FormatASGAlerts` (if created)
2. **EventBridge rules** `ASG-Instance-Launch-Alert`, `ASG-Instance-Terminate-Alert`
   - Disable first if delete fails due to in-flight invocations
3. **CloudWatch alarms** `ASG-Scale-Out-Alert`, `ASG-Scale-In-Alert`
4. **CloudWatch dashboard** `ASG-Monitoring-Dashboard`
5. **SNS subscription** (email)
6. **SNS topic** `ASG-Alerts`

Lab 2 teardown (ASG, ALB, TG, LT) remains per [Lab 2 teardown guide](../../Day_3_Lab_2_Auto_Scaling_High_Availability/instructor/AWS_LAB2_SETUP.md#teardown-order).

---

## Cost estimate (Lab 3 only)

| Resource | ~Cost |
|----------|-------|
| SNS notifications | Free tier (1,000 email notifications) |
| CloudWatch alarms | Free tier (10 alarms) |
| EventBridge | Free tier (custom events) |
| Lambda (optional) | Free tier |
| **Labs 1–2 still running** | NAT ~$0.045/hr · ALB ~$0.0225/hr |

**Recommendation:** Delete Lab 3 SNS/alarms/rules after class. Tear down Lab 2 within 1 hour if not continuing.

---

## Console path quick reference

| Resource | Console path |
|----------|--------------|
| SNS Topics | SNS → Topics |
| SNS Subscriptions | SNS → Subscriptions |
| CloudWatch Alarms | CloudWatch → Alarms → All alarms |
| CloudWatch Dashboards | CloudWatch → Dashboards |
| EventBridge Rules | Amazon EventBridge → Rules |
| Lambda Functions | Lambda → Functions |
| Auto Scaling Groups | EC2 → Auto Scaling Groups |

---

## Instructor reference build (manual)

1. Complete Lab 2
2. Follow student [instructions.md](../instructions.md) Steps 1–8
3. Run `python setup/test_alerting_lab3.py`
4. Run Steps 9–11 to verify email delivery
5. Optionally deploy Step 12 Lambda
6. Tear down Lab 3 per teardown order above
