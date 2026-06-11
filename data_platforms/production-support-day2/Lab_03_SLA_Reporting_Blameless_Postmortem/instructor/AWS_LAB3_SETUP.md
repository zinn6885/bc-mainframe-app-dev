# Lab 3 — AWS Setup (Instructor)

Complete this **before class**, after Lab 2 EC2 is running. Students follow [instructions.md](../instructions.md) — this guide is for you to prepare and verify the environment manually.

**Region:** US East (N. Virginia) — `us-east-1`

---

## Prerequisites

| Item | Requirement |
|------|-------------|
| Lab 2 EC2 | Running, `payment-processor` **active** |
| SSH access | Your `.pem` key works |
| AWS Console | Signed in to the same account students use |

---

## 1. Attach IAM role to the Lab 2 EC2 instance

Custom metrics (Step 4) require the instance to call `cloudwatch:PutMetricData`.

### Create the role (one time)

1. **IAM** → **Roles** → **Create role**
2. **Trusted entity:** AWS service → **EC2**
3. **Permissions** — attach:
   - `CloudWatchAgentServerPolicy` (CloudWatch agent in Step 3)
   - `CloudWatchAgentAdminPolicy` (CloudWatch agent in Step 3)
4. **Role name:** `Lab3-EC2-CloudWatch-Role`
5. Create role
6. Open the new role → **Add permissions** → **Create inline policy** → **JSON** → paste [setup/lab3_put_metric_data_policy.json](../setup/lab3_put_metric_data_policy.json) → name it `Lab3-PutMetricData` → create

> **Important:** The CloudWatch agent policies alone do **not** allow `PaymentProcessor` custom metrics (`send_metrics.sh`). The inline policy above grants `cloudwatch:PutMetricData` for Step 4.

### Create instance profile and attach to EC2

1. **IAM** → **Roles** → `Lab3-EC2-CloudWatch-Role` → note the role
2. **EC2** → **Instances** → select Lab 2 instance
3. **Actions** → **Security** → **Modify IAM role**
4. Select `Lab3-EC2-CloudWatch-Role` (or create an instance profile with that role)
5. Save

Wait 1–2 minutes for the role to propagate before testing metrics.

---

## 2. Verify Lab 2 instance (console)

1. **EC2** → **Instances** (region: **US East (N. Virginia)**)
2. Confirm instance state = **Running**
3. Note **Public IPv4** and **Instance ID** for students

---

## 3. Instructor walkthrough — test all steps manually

Follow [instructions.md](../instructions.md) in order. Quick verification checklist:

| Step | Verify |
|------|--------|
| 1 | EC2 instance visible, Running |
| 2 | SSH login works; `systemctl is-active payment-processor` → `active` |
| 3 | `sudo systemctl status amazon-cloudwatch-agent` → `active (running)` |
| 4 | `/opt/send_metrics.sh` prints `status=1`; check `/var/log/send_metrics.log` |
| 5 | **CloudWatch** → **Dashboards** → `Lab3-SLA-Dashboard` shows widgets |
| 6 | **CloudWatch** → **Alarms** → `PaymentProcessor-ServiceDown` and `PaymentProcessor-HighResponseTime` |
| 7 | CSV export or `get-metric-statistics` returns datapoints |
| 8–14 | Excel workbook with all seven sheets |

---

## 4. Simulate downtime (recommended for richer metrics)

On the EC2 instance via SSH:

```bash
sudo systemctl stop payment-processor
/opt/send_metrics.sh
sleep 60
sudo systemctl start payment-processor
/opt/send_metrics.sh
```

This produces `ServiceHealth = 0` then `1` in CloudWatch for students to analyze.

---

## 5. Console navigation reference

### EC2 Monitoring tab

1. **EC2** → **Instances** → select your instance (checkbox or instance ID)
2. Bottom panel opens → click **Monitoring** tab  
   (or open the instance detail page — tabs at the top)
3. Shows default EC2 metrics (CPU, network). Custom metrics are in CloudWatch.

### CloudWatch dashboard

**CloudWatch** → **Dashboards** → `Lab3-SLA-Dashboard`

### Custom metrics

**CloudWatch** → **Metrics** → **All metrics** → **PaymentProcessor**

### Alarms

**CloudWatch** → **Alarms** → **All alarms**

---

## 6. Helper files (optional for students)

Students can copy these via `scp` instead of pasting long scripts:

| File | Purpose |
|------|---------|
| [setup/cloudwatch_agent_config.json](../setup/cloudwatch_agent_config.json) | CloudWatch agent config |
| [setup/send_metrics.sh](../setup/send_metrics.sh) | Custom metrics cron script |

```bash
scp -i your-key.pem setup/cloudwatch_agent_config.json ec2-user@<public-ip>:/tmp/
scp -i your-key.pem setup/send_metrics.sh ec2-user@<public-ip>:/tmp/
```

---

## 7. Troubleshooting

| Problem | Fix |
|---------|-----|
| `Unable to locate credentials` / `aws login` | **No IAM role on the EC2 instance.** Attach `Lab3-EC2-CloudWatch-Role` (Section 1), wait 2 min, then run `aws sts get-caller-identity --region us-east-1` on the instance — it must return an ARN, not an error |
| `AccessDenied` on `put-metric-data` | Role attached but missing `Lab3-PutMetricData` inline policy — add policy from [setup/lab3_put_metric_data_policy.json](../setup/lab3_put_metric_data_policy.json), wait 2 min, retry |
| `crontab: command not found` | Run `sudo yum install -y cronie` |
| Custom metrics not in console | Wait 5 min; run `/opt/send_metrics.sh` manually |
| Dashboard shows "No data" | Confirm region is `us-east-1`; metrics exist under PaymentProcessor |
| Alarms `INSUFFICIENT_DATA` | Normal until enough datapoints arrive (~5–10 min) |
| `send_metrics.sh: cannot execute` | Windows line endings — re-copy via `scp` or run `sed -i 's/\r$//' /opt/send_metrics.sh` |

---

## 8. Cleanup (after class)

Optional — remove lab resources to avoid cost:

- **CloudWatch** → delete dashboard `Lab3-SLA-Dashboard`
- **CloudWatch** → delete alarms `PaymentProcessor-*`
- Terminate Lab 2 EC2 if no longer needed (see Lab 2 instructor guide)
