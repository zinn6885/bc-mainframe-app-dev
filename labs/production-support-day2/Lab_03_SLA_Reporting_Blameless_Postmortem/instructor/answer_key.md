# Lab 3 — Instructor Answer Key

**Solution workbook:** [lab3_solution.xlsx](lab3_solution.xlsx)  
**Student guide:** [instructions.md](../instructions.md)  
**Setup guide:** [AWS_LAB3_SETUP.md](AWS_LAB3_SETUP.md)

---

## Expected SLA Calculations (sample data)

Enter **one row per timestamp** in the metrics table. Column C is each reading's response time (not an average). Column D is **Yes** / **No** / **—** per row.

| Timestamp | ServiceHealth | ResponseTimeMs | Exceeds 150ms SLA? |
|-----------|---------------|----------------|--------------------|
| 09:00 | 1 | 95 | No |
| 09:05 | 1 | 102 | No |
| 09:10 | 0 | — | — |
| 09:15 | 0 | — | — |
| 09:20 | 1 | 180 | Yes |
| 09:25 | 1 | 88 | No |

| Calculation | Result |
|-------------|--------|
| Downtime intervals | 2 (× 5 min = **10 minutes**) |
| Response times > 150 ms | 09:20 → **180 ms** (1 breach) |
| Response SLA compliance | 3 of 4 readings ≤ 150 ms → **75%** (exclude downtime rows — only count rows where ServiceHealth = 1 and ResponseTimeMs has a value) |
| Resolution SLA compliance | **92%** (sample) |
| Overall SLA | **83.5%** (average of response + resolution) |
| MTTR | 10 ÷ 1 = **10 minutes** |
| MTBF | 50 ÷ 1 = **50 minutes** |
| Availability | (60 − 10) ÷ 60 × 100 = **83.33%** |

---

## Workbook sheet checklist

| Sheet | Key content to verify |
|-------|----------------------|
| Raw Metrics | 6 sample rows or student's CloudWatch export |
| SLA Calculations | Metrics table + summary rows filled |
| MTTR MTBF | All 7 metrics with values |
| Availability | 83.33% and 99.9% check = Yes |
| KPI Dashboard | All sections filled (no blanks left) |
| Postmortem | 5 Whys, root cause, action items |
| Runbook | 8 steps + escalation contacts |

See [lab3_solution.xlsx](lab3_solution.xlsx) for the completed reference.

---

## Expected postmortem summary

| Field | Expected content |
|-------|------------------|
| Incident ID | INC-AWS-001 |
| Service | payment-processor |
| Severity | P1 |
| Root cause | Port 8080 held by `rogue-process.py`; `payment-processor` failed to bind |
| Duration | ~10 minutes (from CloudWatch ServiceHealth = 0 windows) |
| 5 Whys chain | Service down → port in use → rogue process → no pre-start port check → runbook gap |

---

## Expected runbook highlights

Students should reference Lab 2 commands:

- `sudo ss -tulpn | grep 8080`
- `pgrep -af rogue-process.py`
- `sudo kill -9 <PID>` (not `pkill -f` — can kill SSH session)
- `sudo systemctl reset-failed payment-processor` before restart

---

## CloudWatch verification

| Resource | Expected name / state |
|----------|----------------------|
| Dashboard | `Lab3-SLA-Dashboard` — 6 widgets |
| Alarm 1 | `PaymentProcessor-ServiceDown` — triggers when ServiceHealth < 0.5 |
| Alarm 2 | `PaymentProcessor-HighResponseTime` — triggers when ResponseTimeMs > 200 |
| Namespace | `PaymentProcessor` |
| Metrics | `ServiceHealth`, `ResponseTimeMs` |

---

## Bonus challenge answer

15 minutes downtime vs 99.9% SLA (43 min/month budget):

> **Yes** — 15 minutes is within the 43-minute monthly allowance for 99.9% availability.

---

## Common mistakes to watch for

| Mistake | Correction |
|---------|------------|
| Wrong AWS region | Must use `us-east-1` in console and CLI |
| Missing IAM role | Attach `Lab3-EC2-CloudWatch-Role` before Step 4 |
| Using `pkill -f rogue-process` | Use `kill -9 <PID>` from `pgrep` |
| Forgetting `cronie` | `sudo yum install -y cronie` before crontab |
| MTTR uses uptime instead of downtime | MTTR = downtime ÷ incidents |
| Postmortem blames a person | Reinforce blameless culture — focus on systems and process |
| Response SLA > 100% | Downtime rows counted in numerator — exclude rows where ServiceHealth = 0; only count rows with ResponseTimeMs data (3 ÷ 4 = 75%) |
