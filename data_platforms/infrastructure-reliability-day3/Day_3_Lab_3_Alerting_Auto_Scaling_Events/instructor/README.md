# Lab 3 — Instructor Package

**Estimated setup time:** 10–15 minutes (first time) · 5 minutes (repeat classes)  
**Region:** US East (N. Virginia) — **`us-east-1`**

---

## Before class

1. Confirm students completed **[Day 3 Lab 2](../../Day_3_Lab_2_Auto_Scaling_High_Availability/instructions.md)** (`WebServer-ASG` at 2/2/6 with 2 healthy instances).
2. Follow **[AWS_LAB3_SETUP.md](AWS_LAB3_SETUP.md)** — run the validation script after building the reference lab.
3. Walk through **[instructions.md](../instructions.md)** Steps 1–11 in the console to confirm UI paths match.
4. Review **[CONSOLE_UI_GUIDE.md](CONSOLE_UI_GUIDE.md)** — validated screenshot expectations and common student issues.
5. Tell students:
   - Region must be **`us-east-1`**
   - Exact resource names from the guide
   - **Confirm SNS email subscription before Step 9** — most common failure
   - Terminate **one** instance only in Step 9
   - Step 12 (Lambda) is optional — core lab ends at Step 11
   - Delete Lab 3 resources in Step 14; keep or tear down Lab 2 separately

---

## Materials

| File | Purpose |
|------|---------|
| [AWS_LAB3_SETUP.md](AWS_LAB3_SETUP.md) | Pre-lab IAM, validation script, teardown order |
| [answer_key.md](answer_key.md) | Expected values per step for grading |
| [../instructions.md](../instructions.md) | Student guide — Steps 1–14 |
| [CONSOLE_UI_GUIDE.md](CONSOLE_UI_GUIDE.md) | Console troubleshooting and screenshot grading |
| [../setup/test_alerting_lab3.py](../setup/test_alerting_lab3.py) | Validate alerting stack |
| [../setup/format_asg_alerts.py](../setup/format_asg_alerts.py) | Lambda reference code |
| [../setup/requirements.txt](../setup/requirements.txt) | Python dependencies |

---

## Quick validation (instructor)

From the lab folder:

```powershell
cd Day_3_Lab_3_Alerting_Auto_Scaling_Events
pip install -r setup/requirements.txt
python setup/test_alerting_lab3.py
```

Before students start (Lab 2 prerequisite only):

```powershell
python setup/test_alerting_lab3.py --prerequisites-only
```

After optional Lambda step:

```powershell
python setup/test_alerting_lab3.py --include-lambda
```

---

## Pacing guide (35–40 min class block)

| Time | Activity |
|------|----------|
| 0–3 min | Step 1 — Verify ASG running |
| 3–8 min | Steps 2–3 — SNS topic + email confirm (**pause until confirmed**) |
| 8–18 min | Steps 4–5 — Two CloudWatch alarms |
| 18–25 min | Steps 6–7 — Two EventBridge rules |
| 25–30 min | Step 8 — Dashboard widgets |
| 30–33 min | Step 9 — Terminate one instance |
| 33–38 min | Steps 10–11 — Check emails + ASG recovery |
| 38–40 min | Deliverables checklist, Step 14 teardown reminder |

> **Tip:** While students wait for email in Steps 10–11, have them open the CloudWatch dashboard and ASG Activity tab to narrate the event timeline.

---

## Common student mistakes

| Mistake | Fix |
|---------|-----|
| Lab 2 ASG not running | Complete Lab 2 first; run `--prerequisites-only` |
| No emails | Subscription not confirmed — resend confirmation from SNS |
| Wrong ASG name in EventBridge JSON | Must be exactly `WebServer-ASG` |
| Terminated both instances | ASG recovers but alerts are noisy — terminate one only |
| EventBridge target fails | Accept SNS resource policy prompt when creating rule |
| Alarm INSUFFICIENT_DATA | Wait 5 min after creation |
| Duplicate emails with Lambda | Expected if both SNS and Lambda targets exist — explain in Step 12 |
| Deleted Lab 2 ASG during cleanup | Step 14 deletes Lab 3 only — clarify in class |

---

## Demo script (instructor-led recap)

1. Show SNS topic with confirmed subscription.
2. Show both EventBridge rules enabled with JSON patterns.
3. Terminate one instance live — narrate Activity tab timeline.
4. Show incoming email on projector (EventBridge terminate + launch).
5. Open `ASG-Monitoring-Dashboard` — point out desired capacity dip/recovery.
6. Relate to Module 12 topics: alerting automation, notification routing, observability.

---

## Student guide

[../instructions.md](../instructions.md) — Steps 1–14 (AWS Console)
