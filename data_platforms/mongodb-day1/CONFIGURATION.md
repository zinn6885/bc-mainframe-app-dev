# Day 1 Labs — Configuration Guide

Use this guide to see **which files need your credentials** and **where to paste them**. No Python scripts are edited on disk — credentials are entered at runtime or on the command line.

> **Do not commit or share** your Atlas username, password, or connection string in Git, chat, or screenshots.

---

## Before You Connect from EC2

Complete these steps once per EC2 instance:

1. **Whitelist EC2 IP in Atlas** — run on EC2: `curl -s https://checkip.amazonaws.com`, then Atlas → **Database** → **Network Access** → **Add IP Address**. Wait 1–2 minutes.
2. **Install packages** — `pip3 install pymongo certifi --user`
3. **Use the Drivers connection string** from Atlas → **Connect** → **Drivers** (starts with `mongodb+srv://`)

**Connection string template (replace placeholders):**

```
mongodb+srv://YOUR_USERNAME:YOUR_PASSWORD@YOUR_CLUSTER.mongodb.net/
```

| Placeholder | Where to find it |
|-------------|------------------|
| `YOUR_USERNAME` | Atlas → **Database Access** → your database user |
| `YOUR_PASSWORD` | Password you set when creating the user (replace `<password>` in the copied string) |
| `YOUR_CLUSTER` | Atlas → **Clusters** → hostname (e.g. `lab1-cluster.abc123`) |

> **Do not use** `?ssl=false`. MongoDB Atlas requires TLS. If you see `SSL handshake failed`, see [Lab 2 Troubleshooting](Lab_02_Data_Migration_Simulation/README.md#troubleshooting) or the [EC2 Appendix](EC2_Instance_Setup_Guide.md#troubleshooting).

---

## Lab 1: MongoDB Atlas — CRUD, Indexing & Aggregation

### Files to change

| File | Change needed | Status |
|------|---------------|--------|
| None | Lab 1 is browser-only in Atlas | ✅ No file changes |

**Credentials used:** Atlas web login only (email + password you chose at sign-up).

---

## Lab 2: Data Migration Simulation

### File 1: `migration.py`

| Item | Detail |
|------|--------|
| **Location** | `/home/ec2-user/lab2/migration.py` |
| **Edit the file?** | ❌ No — connection string is entered when prompted |
| **When** | Running `python3 migration.py --migrate` |

**Script behavior:** Prompts for connection string at runtime. The full script in the EC2 Appendix uses `certifi` for Atlas TLS automatically.

```python
conn_str = input("Connection string: ")
client = MongoClient(conn_str, tlsCAFile=certifi.where())
```

**Paste at the prompt:**

```
mongodb+srv://YOUR_USERNAME:YOUR_PASSWORD@YOUR_CLUSTER.mongodb.net/
```

**Commands:**

```bash
cd /home/ec2-user/lab2
python3 migration.py --profile
python3 migration.py --migrate
# When prompted for Connection string:, paste your mongodb+srv:// string
```

### File 2: `customers.csv`

| Item | Detail |
|------|--------|
| **Location** | `/home/ec2-user/lab2/customers.csv` |
| **Edit the file?** | ❌ No — shared sample source data for all students |

---

## Lab 3: Hybrid Data Integration Pipeline

All four scripts take the connection string as a **command-line argument** (single-quoted). Replace placeholders in every command. Each script uses `certifi` for Atlas TLS automatically — no extra flags needed on the command line.

### File 1: `batch_load.py`

```bash
cd /home/ec2-user/lab3
python3 batch_load.py 'mongodb+srv://YOUR_USERNAME:YOUR_PASSWORD@YOUR_CLUSTER.mongodb.net/'
```

### File 2: `api_enrich.py`

```bash
python3 api_enrich.py 'mongodb+srv://YOUR_USERNAME:YOUR_PASSWORD@YOUR_CLUSTER.mongodb.net/'
```

### File 3: `cdc_simulate.py`

```bash
python3 cdc_simulate.py 'mongodb+srv://YOUR_USERNAME:YOUR_PASSWORD@YOUR_CLUSTER.mongodb.net/'
```

### File 4: `query_results.py`

```bash
python3 query_results.py 'mongodb+srv://YOUR_USERNAME:YOUR_PASSWORD@YOUR_CLUSTER.mongodb.net/'
```

**Run in this order:** `batch_load.py` → `api_enrich.py` → `cdc_simulate.py` → `query_results.py`

### Files that do not need changes

| File | Reason |
|------|--------|
| `historical_orders.csv` | Created by `batch_load.py` if missing |
| All `.py` script bodies | Credentials passed at runtime, not hardcoded |

---

## Appendix A: EC2 Instance Setup

### User data script (AWS Console)

| Item | Detail |
|------|--------|
| **Location** | EC2 Launch Wizard → **Advanced details** → **User data** |
| **Edit for your account?** | ❌ No — same script for all students |
| **Notes** | Creates placeholder `migration.py`; replace with full script in Appendix Part 7 |

### `training-key.pem` (optional)

| Item | Detail |
|------|--------|
| **Required for these labs?** | ❌ No — use **EC2 Instance Connect** (browser terminal) |
| **If you downloaded a key pair** | Store securely; `chmod 400 training-key.pem` on Mac/Linux only if using local SSH |

---

## Summary: Where credentials go

| Lab | File / step | Where to put credentials | Format |
|-----|-------------|--------------------------|--------|
| **Lab 1** | Atlas UI | Browser login | N/A |
| **Lab 2** | `migration.py --migrate` | Terminal prompt | `mongodb+srv://USER:PASS@CLUSTER.mongodb.net/` |
| **Lab 3** | `batch_load.py` | Command-line argument | Same (in single quotes) |
| **Lab 3** | `api_enrich.py` | Command-line argument | Same |
| **Lab 3** | `cdc_simulate.py` | Command-line argument | Same |
| **Lab 3** | `query_results.py` | Command-line argument | Same |
| **Appendix** | User data script | No changes | N/A |

---

## Security after labs

1. **Terminate** or **stop** the EC2 instance when finished
2. **Remove** temporary Atlas Network Access rules (e.g. `0.0.0.0/0` or old EC2 IPs)
3. **Rotate** your database user password if it was exposed in chat, logs, or shared screens

---

## Quick links

| Resource | Link |
|----------|------|
| Lab 1 | [Lab_01_MongoDB_Atlas_Fundamentals/README.md](Lab_01_MongoDB_Atlas_Fundamentals/README.md) |
| Lab 2 | [Lab_02_Data_Migration_Simulation/README.md](Lab_02_Data_Migration_Simulation/README.md) |
| Lab 3 | [Lab_03_Hybrid_Data_Integration_Pipeline/README.md](Lab_03_Hybrid_Data_Integration_Pipeline/README.md) |
| EC2 setup | [EC2_Instance_Setup_Guide.md](EC2_Instance_Setup_Guide.md) |
