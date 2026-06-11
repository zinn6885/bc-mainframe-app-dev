# Lab 2 — Live (AWS EC2)

**Time:** 20–25 minutes  
**You need:** SSH client, `.pem` key, EC2 public IP (from instructor)

**Scenario:** `payment-processor` is failing. Find the cause, fix it, verify the service runs.

---

## Step 1 — Connect

```bash
chmod 400 your-key.pem
ssh -i your-key.pem ec2-user@<public-ip>
```

---

## Step 2 — Check service status

```bash
systemctl status payment-processor
```

Expect: `failed` or `inactive`.

---

## Step 3 — Check logs

```bash
sudo journalctl -u payment-processor -n 50
```

Expect: `Address already in use` on port 8080.

---

## Step 4 — Find the process on port 8080

```bash
sudo ss -tulpn | grep 8080
pgrep -af rogue-process.py
```

Note the **PID**.

---

## Step 5 — Kill the rogue process

```bash
sudo kill -9 <PID>
```

Confirm port is free (no output = good):

```bash
sudo ss -tulpn | grep 8080
```

---

## Step 6 — Restart the service

```bash
sudo systemctl reset-failed payment-processor
sudo systemctl restart payment-processor
```

---

## Step 7 — Verify

```bash
systemctl is-active payment-processor
curl -s -o /dev/null -w "%{http_code}" http://localhost:8080
```

Expect: `active` and `200`.

---

## Step 8 — Document (if instructor asks)

Complete the Excel mock lab ([instructions.md](instructions.md)) or write a short RCA: what failed, root cause, permanent fix.
