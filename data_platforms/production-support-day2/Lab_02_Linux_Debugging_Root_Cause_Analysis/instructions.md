# Lab 2 — Mock (Excel)

**Time:** 25–30 minutes  
**You need:** Excel or Google Sheets

Optional starter: [template/lab2_starter.xlsx](template/lab2_starter.xlsx)

**Scenario:** L2 engineer for FinTech PayCore — `payment-processor` fails due to a port 8080 conflict. Document the investigation and RCA in Excel.

---

## Step 1 — Create workbook

Create a blank workbook. Save as `lab2_linux_debugging_rca.xlsx`.

---

## Step 2 — Investigation Log sheet

Sheet name: **Investigation Log**

Row 1 headers:

| Step | Command / Action | Output Observed | What It Tells You | Status |

---

## Step 3 — Linux Commands sheet

Sheet name: **Linux Commands**

| Command | Purpose | Example |
|---------|---------|---------|
| `systemctl status <service>` | Check if service is running | `systemctl status payment-processor` |
| `systemctl restart <service>` | Restart a service | `systemctl restart payment-processor` |
| `journalctl -u <service> -n 50` | View service logs | `journalctl -u payment-processor -n 50` |
| `ss -tulpn` | List ports and processes | `ss -tulpn \| grep 8080` |
| `ps aux \| grep <name>` | Find process | `ps aux \| grep 9876` |
| `kill -9 <PID>` | Kill process | `kill -9 9876` |

---

## Step 4 — Add investigation rows (diagnose)

| Step | Command / Action | Output Observed | What It Tells You | Status |
|------|------------------|-----------------|-------------------|--------|
| 1 | `systemctl status payment-processor` | `inactive (dead) / failed` | Service not running | Completed |
| 2 | `systemctl restart payment-processor` | `Address already in use` | Port conflict | Completed |
| 3 | `journalctl -u payment-processor -n 50` | `port 8080 already in use` | Port 8080 occupied | Completed |

---

## Step 5 — Add investigation rows (find rogue process)

| Step | Command / Action | Output Observed | What It Tells You | Status |
|------|------------------|-----------------|-------------------|--------|
| 4 | `ss -tulpn \| grep 8080` | PID 9876 on port 8080 | Rogue process found | Completed |
| 5 | `ps aux \| grep 9876` | `old-process /opt/legacy/app` | Legacy app still running | Completed |

---

## Step 6 — Add investigation rows (fix)

| Step | Command / Action | Output Observed | What It Tells You | Status |
|------|------------------|-----------------|-------------------|--------|
| 6 | `kill -9 9876` | Process terminated | Port freed | Completed |
| 7 | `systemctl restart payment-processor` | `Started payment-processor.service` | Service started | Completed |
| 8 | `systemctl status payment-processor` | `active (running)` | Service healthy | Completed |
| 9 | Test transaction | `Success` | Verified | Completed |

---

## Step 7 — 5 Whys Analysis sheet

Sheet name: **5 Whys Analysis**

| Why # | Question | Answer |
|-------|----------|--------|
| 1 | Why did payment-processor fail to start? | Port 8080 already in use |
| 2 | Why was port 8080 in use? | Old legacy process still running |
| 3 | Why was legacy process still running? | Migration script did not stop it |
| 4 | Why did migration not stop it? | Stop command missing from runbook |
| 5 | Why was stop command missing? | Runbook not reviewed after migration |

**Root Cause:** Incomplete runbook and missing post-migration validation.

---

## Step 8 — RCA Report sheet

Sheet name: **RCA Report**. Paste:

```
ROOT CAUSE ANALYSIS REPORT
Incident ID: INC-002 | Date: 2026-06-10 | Service: payment-processor | Severity: P1

SUMMARY: Service failed to start — port 8080 conflict.

TIMELINE:
09:00 Service failed | 09:05 Port conflict in logs | 09:10 PID 9876 found
09:12 Process killed, service restarted | 09:15 Verified | Downtime: 15 min

ROOT CAUSE: Legacy process left running after migration; runbook incomplete.

CORRECTIVE ACTIONS:
1. Update runbook — stop legacy process before starting new service
2. Add port check to deployment script
3. Automated health validation after migrations
```

---

## Step 9 — Permanent Fix sheet

Sheet name: **Permanent Fix**

| Fix Type | Action | Owner | Due Date |
|----------|--------|-------|----------|
| Runbook Update | Stop legacy process before new service | L2 Team | 2026-06-11 |
| Automation Script | Port conflict check in pipeline | DevOps | 2026-06-15 |
| Monitoring Alert | Alert if port 8080 occupied | Monitoring | 2026-06-12 |
| Runbook Review | Quarterly review | L2 Lead | Ongoing |

---

## Step 10 — Save

Save as `lab2_[yourname].xlsx`. Confirm 5 sheets: Investigation Log, Linux Commands, 5 Whys Analysis, RCA Report, Permanent Fix.
