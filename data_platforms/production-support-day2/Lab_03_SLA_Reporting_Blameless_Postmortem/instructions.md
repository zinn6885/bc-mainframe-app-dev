# Lab 3: SLA Compliance, Operational Reporting & Blameless Postmortem

**Estimated time:** 45–50 minutes  
**Tools needed:** AWS Console, SSH terminal, Microsoft Excel or Google Sheets

**Prerequisite:** Lab 2 EC2 instance (`payment-processor` service) is running and fixed.

**AWS region:** US East (N. Virginia) — `us-east-1`

> **Recommended:** Copy [template/lab3_starter.xlsx](template/lab3_starter.xlsx) to `lab3_[yourname].xlsx` before Step 8. The starter includes all seven sheets with labels and fill-in sections.

### Lab file locations

All paths below are relative to the **Lab 3 folder** (`Lab_03_SLA_Reporting_Blameless_Postmortem/`). Clone or download the course repo, then open a terminal in that folder before running `scp` commands.

| File | Location in repo | When you need it |
|------|------------------|------------------|
| Lab instructions | `instructions.md` | This file — Steps 1–14 |
| CloudWatch agent config | `setup/cloudwatch_agent_config.json` | Step 3, Option A |
| Custom metrics script | `setup/send_metrics.sh` | Step 4, Option A |
| Starter Excel workbook | `template/lab3_starter.xlsx` | Step 8 (copy to your working file first) |
| Architecture diagram | `diagrams/lab3-architecture.png` | Reference (also shown above) |
| EC2 SSH key (`.pem`) | **From your instructor** (same key as Lab 2) | Steps 2, 3, 4 — not in the repo |
| Your working workbook | `lab3_[yourname].xlsx` | **You create this** — copy of the starter, saved locally |

**`scp` tip:** `cd` into `Lab_03_SLA_Reporting_Blameless_Postmortem/` in your cloned repo before running `scp`, so paths like `setup/cloudwatch_agent_config.json` resolve correctly. Replace `/path/to/your-key.pem` with your Lab 2 `.pem` file (e.g. `~/Downloads/lab2-key.pem`).

---

## Lab Objectives

By the end of this lab, you will be able to:

- Collect real metrics from AWS CloudWatch
- Calculate SLA compliance, MTTR, MTBF, and availability
- Build a KPI dashboard in CloudWatch
- Export data to Excel for analysis
- Write a blameless postmortem
- Create a runbook (SOP)

---

## Architecture Overview

![Lab 3 architecture: EC2 metrics to CloudWatch to Excel for SLA reporting](diagrams/lab3-architecture.png)

---

## Step 1 — Verify Your Lab 2 EC2 Instance is Running

1. Sign in to the **AWS Console** and set the region to **US East (N. Virginia)**.
2. Go to **EC2** → **Instances**.
3. Locate your Lab 2 instance (e.g. `Lab2-Broken-System`).
4. Verify **Instance state** = `Running`.
5. Note the **Public IPv4 address**.

---

## Step 2 — SSH into Your EC2 Instance

Use the **`.pem` key file from Lab 2`** (provided by your instructor). It is not stored in the course repo — keep it wherever you saved it when you downloaded it (e.g. `~/Downloads/your-key.pem`).

**Mac/Linux:**

```bash
chmod 400 your-key.pem
ssh -i your-key.pem ec2-user@<your-instance-public-ip>
```

**Windows (PowerShell):**

```powershell
ssh -i your-key.pem ec2-user@<your-instance-public-ip>
```

You should see a prompt like `[ec2-user@ip-... ~]$`.

Verify the service from Lab 2 is still healthy:

```bash
systemctl is-active payment-processor
```

Expect: `active`

---

## Step 3 — Install CloudWatch Agent on EC2

Run in your SSH session:

```bash
sudo yum install -y amazon-cloudwatch-agent
```

**Option A — copy the config file from your machine (recommended):**

**File:** `setup/cloudwatch_agent_config.json` (in the Lab 3 folder — see [Lab file locations](#lab-file-locations))

```bash
# Run on your local machine (not on EC2).
# cd to Lab_03_SLA_Reporting_Blameless_Postmortem/ in your clone first:
cd /path/to/Lab_03_SLA_Reporting_Blameless_Postmortem

scp -i /path/to/your-key.pem setup/cloudwatch_agent_config.json ec2-user@<public-ip>:/tmp/
```

Then on the EC2 instance:

```bash
sudo cp /tmp/cloudwatch_agent_config.json /opt/aws/amazon-cloudwatch-agent/bin/config.json
```

**Option B — create the config on the instance:**

```bash
sudo tee /opt/aws/amazon-cloudwatch-agent/bin/config.json > /dev/null << 'EOF'
{
  "agent": {
    "metrics_collection_interval": 60,
    "run_as_user": "cwagent"
  },
  "metrics": {
    "metrics_collected": {
      "cpu": {
        "measurement": ["cpu_usage_idle", "cpu_usage_user", "cpu_usage_system"],
        "metrics_collection_interval": 60,
        "totalcpu": true
      },
      "mem": {
        "measurement": ["mem_used_percent", "mem_free"],
        "metrics_collection_interval": 60
      },
      "disk": {
        "measurement": ["disk_used_percent"],
        "metrics_collection_interval": 60,
        "resources": ["/"]
      }
    },
    "append_dimensions": {
      "InstanceId": "${aws:InstanceId}",
      "InstanceType": "${aws:InstanceType}"
    }
  }
}
EOF
```

Start the agent and verify:

```bash
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config -m ec2 \
  -c file:/opt/aws/amazon-cloudwatch-agent/bin/config.json -s

sudo systemctl status amazon-cloudwatch-agent
```

Expect: `active (running)`

---

## Step 4 — Create Custom Metrics for payment-processor

The script in this step publishes two **custom CloudWatch metrics** under the namespace **`PaymentProcessor`** (this is not a built-in AWS service):

| Metric | Meaning |
|--------|---------|
| `ServiceHealth` | `1` = `payment-processor` service is up, `0` = down |
| `ResponseTimeMs` | Simulated API response time |

> **Note:** The Linux service from Lab 2 is `payment-processor` (hyphen). The CloudWatch namespace is `PaymentProcessor` (PascalCase, no hyphen).

The EC2 instance needs an **IAM role** so `aws` can publish metrics without access keys. Your instructor attaches `Lab3-EC2-CloudWatch-Role` before class (see instructor setup guide).

**Before continuing — verify credentials on the EC2 instance:**

```bash
aws sts get-caller-identity --region us-east-1
```

Expect JSON with an `Arn` like `arn:aws:sts::...:assumed-role/Lab3-EC2-CloudWatch-Role/...`

| Error | What to do |
|-------|------------|
| `Unable to locate credentials` / `aws login` | IAM role is **not attached** to this EC2 instance — ask your instructor to complete [instructor/AWS_LAB3_SETUP.md](instructor/AWS_LAB3_SETUP.md) Section 1, wait 2 minutes, then retry |
| `AccessDenied` on `put-metric-data` | Role is attached but missing custom-metrics permission — ask instructor to add `Lab3-PutMetricData` policy |

Install cron support (required on Amazon Linux 2023):

```bash
sudo yum install -y cronie
```

**Option A — copy the script from your machine (recommended):**

**File:** `setup/send_metrics.sh` (in the Lab 3 folder — see [Lab file locations](#lab-file-locations))

```bash
# On your local machine.
# cd to Lab_03_SLA_Reporting_Blameless_Postmortem/ in your clone first:
cd /path/to/Lab_03_SLA_Reporting_Blameless_Postmortem

scp -i /path/to/your-key.pem setup/send_metrics.sh ec2-user@<public-ip>:/tmp/
```

On the instance:

```bash
sudo cp /tmp/send_metrics.sh /opt/send_metrics.sh
sudo chmod +x /opt/send_metrics.sh
```

**Option B — create the script on the instance:**

```bash
sudo tee /opt/send_metrics.sh > /dev/null << 'EOF'
#!/bin/bash
set -euo pipefail
TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
INSTANCE_ID=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/instance-id)

if systemctl is-active --quiet payment-processor; then
  SERVICE_STATUS=1
else
  SERVICE_STATUS=0
fi

aws cloudwatch put-metric-data \
  --namespace "PaymentProcessor" \
  --metric-name "ServiceHealth" \
  --value "$SERVICE_STATUS" \
  --unit Count \
  --dimensions InstanceId="$INSTANCE_ID" \
  --region us-east-1

RANDOM_TIME=$((RANDOM % 200 + 50))
aws cloudwatch put-metric-data \
  --namespace "PaymentProcessor" \
  --metric-name "ResponseTimeMs" \
  --value "$RANDOM_TIME" \
  --unit Milliseconds \
  --dimensions InstanceId="$INSTANCE_ID" \
  --region us-east-1

echo "Metrics sent at $(date) status=$SERVICE_STATUS response_ms=$RANDOM_TIME"
EOF
sudo chmod +x /opt/send_metrics.sh
```

Schedule the script every 5 minutes and run it once:

```bash
(crontab -l 2>/dev/null | grep -v send_metrics.sh; echo "*/5 * * * * /opt/send_metrics.sh >> /var/log/send_metrics.log 2>&1") | crontab -
/opt/send_metrics.sh
```

Expect output like: `Metrics sent at ... status=1 response_ms=...`

**Optional — simulate downtime for richer metrics:**

```bash
sudo systemctl stop payment-processor
/opt/send_metrics.sh
sudo systemctl start payment-processor
/opt/send_metrics.sh
```

---

## Step 5 — Create a CloudWatch Dashboard

**Prerequisite:** Step 4 must be complete — you should have seen `Metrics sent at ... status=1 response_ms=...` when you ran `/opt/send_metrics.sh`.

**Important:** `PaymentProcessor` is a **custom metric namespace** created by the Step 4 script. It does **not** appear under EC2 or as a built-in AWS service. You find it under **CloudWatch** → **Metrics** → **All metrics** → **Custom namespaces** → **PaymentProcessor**.

1. In the AWS Console, confirm the region is **US East (N. Virginia) — `us-east-1`**.
2. Open **CloudWatch** → **Dashboards** → **Create dashboard**.
3. Name: `Lab3-SLA-Dashboard`
4. Click **Add widget** and add each metric below. For each widget, click **Browse** (or **Add metrics**), then navigate as described.

### EC2 metrics (built-in)

| Widget type | How to find it | Purpose |
|-------------|----------------|---------|
| Line | **EC2** → **Per-Instance Metrics** → **CPUUtilization** → select your instance | Track server load |
| Line | **EC2** → **Per-Instance Metrics** → **StatusCheckFailed** → select your instance | Track instance health |
| Number | **EC2** → **Per-Instance Metrics** → **CPUUtilization** (Average) → select your instance | Average CPU load |

### PaymentProcessor metrics (custom — from Step 4)

| Widget type | How to find it | Purpose |
|-------------|----------------|---------|
| Line | **All metrics** → **Custom namespaces** → **PaymentProcessor** → **ServiceHealth** → select your **InstanceId** | Service up (1) or down (0) |
| Line | **All metrics** → **Custom namespaces** → **PaymentProcessor** → **ResponseTimeMs** → select your **InstanceId** | API response time |
| Number | **All metrics** → **Custom namespaces** → **PaymentProcessor** → **ServiceHealth** (Average) → select your **InstanceId** | Current service status |

5. Save each widget, then save the dashboard.

> Custom metrics may take 2–5 minutes to appear after Step 4. If you don't see **PaymentProcessor**, run `/opt/send_metrics.sh` again on the EC2 instance and refresh.

**Verify metrics exist before building the dashboard:** **CloudWatch** → **Metrics** → **All metrics** → **PaymentProcessor**. If this folder is empty, return to Step 4.

---

## Step 6 — Create CloudWatch Alarms for SLA Monitoring

Run from your **SSH session** (region must match your console):

**Alarm 1 — Service Down (P1 incident):**

```bash
aws cloudwatch put-metric-alarm \
  --region us-east-1 \
  --alarm-name "PaymentProcessor-ServiceDown" \
  --alarm-description "Alert when payment-processor service stops" \
  --metric-name "ServiceHealth" \
  --namespace "PaymentProcessor" \
  --statistic Average \
  --period 60 \
  --evaluation-periods 1 \
  --threshold 0.5 \
  --comparison-operator LessThanThreshold \
  --treat-missing-data breaching
```

**Alarm 2 — High response time (SLA breach risk):**

```bash
aws cloudwatch put-metric-alarm \
  --region us-east-1 \
  --alarm-name "PaymentProcessor-HighResponseTime" \
  --alarm-description "Response time exceeding 200ms (SLA risk)" \
  --metric-name "ResponseTimeMs" \
  --namespace "PaymentProcessor" \
  --statistic Average \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 200 \
  --comparison-operator GreaterThanThreshold
```

Verify in the console: **CloudWatch** → **Alarms** → both alarms listed (`OK`, `ALARM`, or `INSUFFICIENT_DATA`).

> SNS notifications are optional. Add `--alarm-actions` only if your instructor provides an SNS topic ARN.

---

## Step 7 — Export CloudWatch Data

**Console method:**

1. **CloudWatch** → **Metrics** → **All metrics**
2. Open namespace **PaymentProcessor** → **ServiceHealth**
3. Select your instance dimension
4. Open the **Graphed metrics** tab
5. **Actions** → **Download CSV**

**CLI method (from SSH):**

```bash
TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
INSTANCE_ID=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/instance-id)

aws cloudwatch get-metric-statistics \
  --region us-east-1 \
  --namespace "PaymentProcessor" \
  --metric-name "ServiceHealth" \
  --dimensions Name=InstanceId,Value=$INSTANCE_ID \
  --start-time "$(date -u -d '1 hour ago' --iso-seconds)" \
  --end-time "$(date -u --iso=seconds)" \
  --period 300 \
  --statistics Average
```

---

## Step 8 — Open Your Excel Workbook

1. Copy the starter workbook from `template/lab3_starter.xlsx` (in the Lab 3 folder) to `lab3_[yourname].xlsx` in a folder of your choice (Desktop, Documents, etc.).
2. Open `lab3_[yourname].xlsx` in Excel or Google Sheets.
3. Confirm these seven sheets exist:

| Sheet | What you will complete |
|-------|------------------------|
| Raw Metrics | Paste CloudWatch export (Step 7) |
| SLA Calculations | Metrics table + compliance summary |
| MTTR MTBF | Reliability formulas and values |
| Availability | Uptime and 99.9% SLA check |
| KPI Dashboard | Weekly summary |
| Postmortem | Blameless incident review |
| Runbook | Recovery SOP |

---

## Step 9 — Calculate SLA Metrics

On the **SLA Calculations** sheet, enter your CloudWatch data in the metrics table — **one row per timestamp** (every 5 minutes). Do not enter averages in the table; averages and compliance percentages go in the **summary section at the bottom**.

| Column | Header | What to enter |
|--------|--------|---------------|
| **A** | Timestamp | Time of each reading (e.g. `09:00`, `09:05`) |
| **B** | ServiceHealth | `1` = service up, `0` = service down |
| **C** | ResponseTimeMs | That row's response time in ms from CloudWatch — use **—** when ServiceHealth = 0 |
| **D** | Exceeds 150ms SLA? | **Yes** if ResponseTimeMs > 150, **No** if ≤ 150, **—** when service is down |

**Sample data** (use if your CloudWatch export is sparse):

| Timestamp | ServiceHealth | ResponseTimeMs | Exceeds 150ms SLA? |
|-----------|---------------|----------------|--------------------|
| 09:00 | 1 | 95 | No |
| 09:05 | 1 | 102 | No |
| 09:10 | 0 | — | — |
| 09:15 | 0 | — | — |
| 09:20 | 1 | 180 | Yes |
| 09:25 | 1 | 88 | No |

**SLA targets:**

- P1 response: 5 minutes
- P1 resolution: 1 hour
- Response time threshold: 150 ms

**Fill in the summary section** at the bottom of the sheet:

- **Downtime intervals** — count rows where ServiceHealth = 0
- **Total downtime (minutes)** — intervals × 5
- **Response SLA compliance %** — `(readings ≤ 150 ms) ÷ (readings with data) × 100`
- **Resolution SLA compliance %** — estimate from incident handling (sample: 92%)

**Response SLA compliance — important:**

Only count rows where **ServiceHealth = 1** and **ResponseTimeMs has a number** (not **—**). Downtime rows are **excluded from both** the numerator and denominator — you cannot measure response time when the service is down.

Using the sample data above:

| Row | Counts for Response SLA? | Why |
|-----|--------------------------|-----|
| 09:00 (95 ms) | Yes | ≤ 150 ms ✓ |
| 09:05 (102 ms) | Yes | ≤ 150 ms ✓ |
| 09:10 (down) | **No** | No response time data |
| 09:15 (down) | **No** | No response time data |
| 09:20 (180 ms) | Yes | > 150 ms ✗ |
| 09:25 (88 ms) | Yes | ≤ 150 ms ✓ |

**3 ÷ 4 × 100 = 75%** (3 compliant readings out of 4 rows with response time data)

> If your result is **over 100%**, you likely counted downtime rows in the numerator. Those rows belong only in the downtime calculations, not in response SLA compliance.

---

## Step 10 — Calculate MTTR, MTBF, and Availability

On the **MTTR MTBF** sheet, enter values in the **Value** column using these formulas:

| Metric | Formula |
|--------|---------|
| **MTTR** | Total downtime minutes ÷ number of incidents |
| **MTBF** | Total uptime minutes ÷ number of failures |
| **Availability** | (Total time − downtime) ÷ total time × 100 |

**Example (from sample data above):**

| Metric | Value |
|--------|-------|
| Total time | 60 minutes |
| Downtime | 10 minutes |
| Uptime | 50 minutes |
| Incidents | 1 |
| **MTTR** | 10 ÷ 1 = **10 minutes** |
| **MTBF** | 50 ÷ 1 = **50 minutes** |
| **Availability** | (60 − 10) ÷ 60 × 100 = **83.33%** |

Copy **Availability %** to the **Availability** sheet. Check whether the incident meets the 99.9% monthly SLA (max 43 minutes downtime).

---

## Step 11 — Complete KPI Dashboard

On the **KPI Dashboard** sheet, fill in every blank using your calculations from Steps 9–10:

- Service health (availability, downtime, incident count)
- SLA compliance (response, resolution, overall)
- Reliability (MTTR, MTBF)
- Top alerts (from CloudWatch alarms)
- Three action items for follow-up

---

## Step 12 — Write Blameless Postmortem

On the **Postmortem** sheet, complete every section using your CloudWatch timeline and Lab 2 root cause:

- Incident details (INC-AWS-001, P1, SLA met or not)
- What happened and when (start, end, duration)
- 5 Whys down to root cause
- What went well / what went wrong
- Action items with owner and due date
- Lessons learned

---

## Step 13 — Complete Runbook (SOP)

On the **Runbook** sheet, review the eight recovery steps (acknowledge → verify → close). Confirm commands match your Lab 2 fix flow:

- `sudo ss -tulpn | grep 8080` and `pgrep -af rogue-process.py`
- `sudo kill -9 <PID>` (not `pkill -f`)
- `sudo systemctl reset-failed` before restart

Add escalation contacts at the bottom.

---

## Step 14 — Save Your Workbook

Save `lab3_[yourname].xlsx`. Confirm all seven sheets are complete:

- Raw Metrics
- SLA Calculations
- MTTR MTBF
- Availability
- KPI Dashboard
- Postmortem
- Runbook

---

## Bonus Challenge (Optional)

Your CloudWatch data shows **15 minutes** of downtime. SLA target is **99.9%** availability (max **43 minutes** downtime per month).

**Did you meet SLA if this was the only incident?**

> Yes — 15 minutes is within the 43 minutes allowed for 99.9% monthly availability.

---

## Summary

| Concept | How you applied it |
|---------|-------------------|
| CloudWatch Agent | Installed and configured on EC2 |
| Custom metrics | ServiceHealth and ResponseTimeMs |
| CloudWatch dashboard | Lab3-SLA-Dashboard |
| CloudWatch alarms | Service down and high response time |
| SLA calculations | Compliance from real or sample data |
| MTTR / MTBF / Availability | Calculated in Excel |
| Blameless postmortem | 5 Whys and action items |
| Runbook | Step-by-step recovery SOP |
