# Lab 2 — AWS EC2 Setup (Instructor)

**Time:** ~10 minutes  
**Instance:** Amazon Linux 2023, `t2.micro` (free tier eligible)

---

## 1. Launch EC2 instance

1. Open **EC2** → **Instances** → **Launch instance**
2. Set:

| Field | Value |
|-------|-------|
| Name | `Lab2-Broken-System` |
| AMI | **Amazon Linux 2023** |
| Instance type | `t2.micro` |
| Key pair | Create new or select existing (download `.pem`) |
| Security group | Allow **SSH (22)** from your IP |

3. Expand **Advanced details** → **User data**
4. Paste the full contents of [setup/user_data.sh](../setup/user_data.sh)
5. Click **Launch instance**
6. Wait until state is **Running** (~2 minutes)

> If you use User Data, skip Step 3 below. Wait an extra minute after boot for cloud-init to finish.

---

## 2. SSH into the instance

```bash
chmod 400 your-key.pem
ssh -i your-key.pem ec2-user@<public-ip>
```

Replace `your-key.pem` and `<public-ip>` with your key file and the instance public IP from the EC2 console.

---

## 3. Create the broken system (manual option only)

Skip this step if you used **User Data** in Step 1.

**Option A — copy script from your machine:**

```bash
scp -i your-key.pem setup/create_broken_system.sh ec2-user@<public-ip>:~/
ssh -i your-key.pem ec2-user@<public-ip>
chmod +x create_broken_system.sh
./create_broken_system.sh
```

**Option B — paste script on the instance:**

```bash
# On the EC2 instance after SSH login:
curl -sO https://raw.githubusercontent.com/innovationinsoftware/bc-mainframe-app-dev/main/labs/production-support-day2/Lab_02_Linux_Debugging_Root_Cause_Analysis/setup/create_broken_system.sh
chmod +x create_broken_system.sh
./create_broken_system.sh
```

You should see: `=== Broken System Created ===`

---

## 4. Verify the system is broken

Run on the instance:

```bash
systemctl status payment-processor
sudo ss -tulpn | grep 8080
pgrep -af rogue-process.py
sudo journalctl -u payment-processor -n 20
```

**Expected:**

| Check | Expected result |
|-------|-----------------|
| `systemctl status` | `failed` or `inactive (dead)` |
| `sudo ss -tulpn` | `python3` listening on `:8080` with a PID |
| `pgrep` | `/opt/rogue-process.py` |
| `journalctl` | `Address already in use` on port 8080 |

---

## 5. Give students

Provide each student or pair:

1. EC2 **public IP**
2. **`.pem`** key file
3. Link to [instructions_live.md](../instructions_live.md)

Students SSH in and follow Steps 2–7 in that guide.

---

## 6. Reset between students

Copy reset script to the instance (once):

```bash
scp -i your-key.pem setup/reset_lab2.sh ec2-user@<public-ip>:~/
```

Between each student, SSH in and run:

```bash
chmod +x reset_lab2.sh
./reset_lab2.sh
```

Re-verify with Step 4 before the next student starts.

---

## 7. Test from your machine (optional)

Automated end-to-end test — launches instance, verifies broken state, runs fix, terminates:

```bash
python setup/test_aws_lab2.py --terminate
```

Requires AWS credentials. Default region: `us-east-1` (US East (N. Virginia)).

---

## Setup scripts

| Script | Purpose |
|--------|---------|
| [setup/user_data.sh](../setup/user_data.sh) | Paste into EC2 User Data at launch |
| [setup/create_broken_system.sh](../setup/create_broken_system.sh) | Manual setup after SSH |
| [setup/reset_lab2.sh](../setup/reset_lab2.sh) | Reset between students |
| [setup/test_aws_lab2.py](../setup/test_aws_lab2.py) | Automated test |
