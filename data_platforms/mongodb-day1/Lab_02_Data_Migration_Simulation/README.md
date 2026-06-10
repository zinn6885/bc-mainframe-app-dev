# Lab 2: Data Migration Simulation - Oracle to MongoDB

## Complete Student Lab Guide (Validated & Working)

---

## Lab Overview

| Aspect | Details |
|--------|---------|
| **Duration** | 15–20 minutes |
| **Objective** | Simulate an Oracle to MongoDB migration including profiling, cleansing, mapping, and validation |
| **Environment** | AWS EC2 (pre-configured by instructor) |
| **Tools** | Python 3, pymongo, MongoDB Atlas |

---

## Prerequisites

- [ ] Lab 1 completed (MongoDB Atlas cluster ready)
- [ ] AWS EC2 instance running (provided by instructor)
- [ ] MongoDB Atlas connection string ready

> **Which files need your credentials?** See **[Day 1 Configuration Guide](../CONFIGURATION.md)** — only the connection string at the `migration.py` prompt; no script edits on disk.

> **Launching your own EC2?** See **[Appendix A: EC2 Instance Setup Guide](../EC2_Instance_Setup_Guide.md)** — use **EC2 Instance Connect** (browser terminal). Local SSH, PowerShell, and WSL are not required.

> **Atlas UI note:** To browse data, use **Database** → **Data Explorer**, or click **Browse Collections** on your cluster.

---

## Theoretical Foundation: Data Migration

### The ETL Pattern

Data migration follows the **ETL (Extract, Transform, Load)** pattern:

<img src="diagrams/etl-pattern.svg" alt="ETL Pattern: Extract, Transform, Load" width="480"/>

| Phase | What Happens | In This Lab |
|-------|--------------|-------------|
| **Extract** | Read data from source system | Read `customers.csv` (simulating Oracle table) |
| **Transform** | Cleanse, validate, reshape data | Profile, deduplicate, fix missing values, standardize |
| **Load** | Write to target database | Insert documents into MongoDB Atlas |

---

## Part 1: Connect to EC2 Instance (2 minutes)

### Step 1.1: Connect via AWS Console

1. Go to **AWS Console** → **EC2** → **Instances**
2. Select your instance named **`Training-Lab`**
3. Click **Connect** at the top
4. Select the **EC2 Instance Connect** tab
5. Username: `ec2-user`
6. Click **Connect**

A browser terminal opens. You are now logged into your EC2 instance.

**Expected output in the browser terminal:**

```
   ,     #_
   ~\_  ####_        Amazon Linux 2023
  ~~  \_#####\
  ~~     \###|
  ~~       \#/ ___   https://aws.amazon.com/linux/amazon-linux-2023
   ~~       V~' '->
    ~~~         /
      ~~._.   _/
         _/ _/
       _/m/'
[ec2-user@ip-172-31-13-140 ~]$
```

> Your IP address in the prompt will differ — that is normal.

---

## Part 2: Verify Lab Files (1 minute)

### Step 2.1: Navigate to lab directory

```bash
cd /home/ec2-user/lab2
```

**Expected output:** No output — you are now in the `lab2` directory.

### Step 2.2: List files to verify they exist

```bash
ls -la
```

**Expected output:**

```
total 8
drwxr-xr-x. 2 ec2-user ec2-user  47 Jun  9 03:29 .
drwx------. 5 ec2-user ec2-user  98 Jun  9 03:29 ..
-rw-r--r--. 1 ec2-user ec2-user 288 Jun  9 03:29 customers.csv
-rwxr-xr-x. 1 ec2-user ec2-user 4415 Jun  9 03:31 migration.py
```

### Step 2.3: View the source CSV data

```bash
cat customers.csv
```

**Expected output:**

```
customer_id,name,email,state,phone,signup_date
1001,John Smith,john@email.com,NY,555-0101,2024-01-15
1001,John Smith,john@email.com,NY,555-0101,2024-01-15
1002,Jane Doe,,ca,555-0102,2024-02-20
1003, Bob Wilson,bob@email.com,California,,2024-03-10
1004,Alice Brown,,TX,555-0104,2024-01-05
```

**Source data quality issues to notice:**

| Issue | Example in data |
|-------|-----------------|
| Duplicate record | Customer `1001` appears twice |
| Missing emails | Jane Doe, Alice Brown |
| Inconsistent state codes | `ca`, `California` instead of `CA` |
| Leading space | ` Bob Wilson` |

---

## Part 3: Install Required Python Package (1 minute)

### Step 3.1: Install pymongo and certifi

```bash
pip3 install pymongo certifi --user
```

**Expected output:**

```
Collecting pymongo
  Downloading pymongo-4.17.0-cp39-cp39-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (1.0 MB)
     |████████████████████████████████| 1.0 MB 5.2 MB/s
Installing collected packages: pymongo
Successfully installed pymongo-4.17.0
```

---

## Part 4: Test MongoDB Atlas Connection (1 minute)

### Step 4.0: Whitelist your EC2 IP in Atlas (do this first)

From your EC2 terminal, get the instance public IP:

```bash
curl -s https://checkip.amazonaws.com
```

In **MongoDB Atlas** → **Database** → **Network Access** → **Add IP Address**:

1. Paste the IP from the command above, **or**
2. For a class lab only: choose **Allow Access from Anywhere** (`0.0.0.0/0`)

Wait **1–2 minutes** for the rule to become **Active** before testing the connection.

### Step 4.1: Test connection from EC2 to Atlas

Replace the connection string with your own:

```bash
python3 -c "
import certifi
from pymongo import MongoClient
try:
    client = MongoClient(
        'mongodb+srv://YOUR_USERNAME:YOUR_PASSWORD@YOUR_CLUSTER.mongodb.net/',
        tlsCAFile=certifi.where()
    )
    client.admin.command('ping')
    print('✅ Connection successful!')
except Exception as e:
    print(f'❌ Connection failed: {e}')
"
```

**Expected output:**

```
✅ Connection successful!
```

> ⚠️ If you see `SSL handshake failed` or `TLSV1_ALERT_INTERNAL_ERROR`, see **Troubleshooting** below — this is almost always a **Network Access** IP whitelist issue or missing CA certificates on EC2.

---

## Part 5: Run Data Profiling (2 minutes)

### Step 5.1: Execute profiling command

```bash
python3 migration.py --profile
```

**Expected output:**

```
=== DATA PROFILING REPORT ===

Total records: 5
Duplicate customer_id records: 1
Missing emails: 2
Invalid state codes: 1
Names with leading/trailing spaces: 1

Data Quality Score: 0%
```

**What this output means:**

| Finding | Value | Action needed |
|---------|-------|---------------|
| Total records | 5 | Baseline for validation |
| Duplicates | 1 | Customer 1001 appears twice — will remove one |
| Missing emails | 2 | Jane Doe, Alice Brown — will add default |
| Invalid state codes | 1 | `ca`, `California` — will standardize to `CA` |
| Names with spaces | 1 | ` Bob Wilson` — will trim |

---

## Part 6: Run Full Migration (3 minutes)

### Step 6.1: Start migration

```bash
python3 migration.py --migrate
```

**Expected output (Phase 1 — Profiling):**

```
=== DATA PROFILING REPORT ===

Total records: 5
Duplicate customer_id records: 1
Missing emails: 2
Invalid state codes: 1
Names with leading/trailing spaces: 1

Data Quality Score: 0%
```

**Expected output (Phase 2 — Cleansing):**

```
=== CLEANSING DATA ===

Duplicates removed: 1
```

**Expected output (Phase 3 — Connection prompt):**

```
==================================================
ENTER YOUR MONGODB ATLAS CONNECTION STRING
==================================================
Connection string:
```

### Step 6.2: Enter your MongoDB Atlas connection string

**Where to find your connection string:**

1. Open a new browser tab
2. Go to [cloud.mongodb.com](https://cloud.mongodb.com)
3. Go to **Database** → **Clusters**
4. Click **Connect** on your cluster
5. Choose **Drivers** (or **Connect your application**)
6. Copy the connection string (starts with `mongodb+srv://`)
7. Replace `<password>` with your database user password

<img src="../Lab%20Screenshots/Lab02_Step_5.2_MongoDB_Driver_Connection_String.png" alt="MongoDB Atlas Drivers connection string screen" width="720"/>

At the `Connection string:` prompt in your EC2 terminal, paste your connection string:

```
mongodb+srv://YOUR_USERNAME:YOUR_PASSWORD@YOUR_CLUSTER.mongodb.net/
```

Then press **Enter**.

**Expected output (Phase 4 — Loading):**

```
=== LOADING TO MONGODB ===

Loaded 4 documents
Created index on customerId

✅ Migration complete! Loaded 4 documents to MongoDB Atlas
```

**What just happened:**

| Operation | Count |
|-----------|-------|
| Source records read | 5 |
| Duplicates removed | 1 |
| Clean documents loaded | 4 |
| Index created | 1 (on `customerId`) |

---

## Part 7: Verify Migration in MongoDB Atlas (2 minutes)

### Step 7.1: Open Data Explorer

1. Go to **MongoDB Atlas** in your browser
2. Open **Data Explorer**:
   - Left sidebar → **Database** → **Data Explorer**, **or**
   - **Clusters** page → **Browse Collections**
3. Select your cluster and look for database **`migration_db`**

**Expected outcome:**

- Database: `migration_db` (newly created)
- Collection: `customers` (newly created)
- Document count: **4**

<img src="../Lab%20Screenshots/Lab02_Step_6.2_View_Migrated_Documents_customers.png" alt="migration_db.customers documents in Data Explorer" width="720"/>

### Step 7.2: View the cleansed documents

1. Click `migration_db` → `customers`
2. Confirm you are on the **Documents** tab
3. Click any document to expand it

**Expected document structure:**

```json
{
  "_id": ObjectId("6a278d6d87680afb06f99f9a"),
  "customerId": 1001,
  "name": "John Smith",
  "contact": {
    "email": "john@email.com",
    "phone": "5550101"
  },
  "address": {
    "state": "NY"
  },
  "signupDate": ISODate("2024-01-15T00:00:00Z"),
  "dataQuality": {
    "score": 100,
    "issues": []
  }
}
```

### Step 7.3: Verify the data fixes

| Customer | Original issue | After migration |
|----------|----------------|-----------------|
| 1001 (first) | Valid record | **Kept** |
| 1001 (second) | Duplicate | **Removed** ✅ |
| 1002 | Missing email, `ca` state | Email: `unknown@example.com`, State: `CA` ✅ |
| 1003 | ` Bob Wilson`, `California` state | Name: `Bob Wilson`, State: `CA` ✅ |
| 1004 | Missing email | Email: `unknown@example.com` ✅ |

### Source to Target Mapping Summary

<img src="diagrams/field-mapping.svg" alt="Source to Target Mapping" width="520"/>

---

## Lab 2 Summary

### What you accomplished

| Step | Status |
|------|--------|
| Connected to EC2 via EC2 Instance Connect | ✅ |
| Verified lab files exist | ✅ |
| Viewed source CSV data | ✅ |
| Installed pymongo | ✅ |
| Tested MongoDB Atlas connection | ✅ |
| Ran data profiling | ✅ |
| Identified data quality issues | ✅ |
| Ran full migration with cleansing | ✅ |
| Loaded 4 clean documents to Atlas | ✅ |
| Created index on `customerId` | ✅ |
| Verified data in MongoDB Atlas | ✅ |

### Migration summary

| Metric | Before | After |
|--------|--------|-------|
| Record count | 5 | 4 |
| Duplicates | 1 | 0 |
| Missing emails | 2 | 0 (default applied) |
| Invalid state codes | 2 | 0 |
| Names with spaces | 1 | 0 |

### Key commands reference

| Action | Command |
|--------|---------|
| Navigate to lab | `cd /home/ec2-user/lab2` |
| Run profiling | `python3 migration.py --profile` |
| Run migration | `python3 migration.py --migrate` |
| View source data | `cat customers.csv` |
| Test Atlas connection | `python3 -c "..."` (see Part 4) |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `command not found: python3` | Run `sudo dnf install python3 -y` |
| `ModuleNotFoundError: No module named 'pymongo'` | Run `pip3 install pymongo certifi --user` |
| `SSL handshake failed` / `TLSV1_ALERT_INTERNAL_ERROR` | **1)** Run `curl -s https://checkip.amazonaws.com` on EC2 and add that IP to Atlas → **Network Access** (wait 1–2 min). **2)** Run `pip3 install --upgrade pymongo certifi --user`. **3)** Use `tlsCAFile=certifi.where()` in `MongoClient` (see Part 4.1). **4)** Run `sudo dnf update -y ca-certificates` and retry. |
| `Connection failed` (other) | Add EC2 public IP to Atlas → **Network Access** |
| `migration.py` is only ~194 bytes | Ask instructor — file should be ~4 KB; EC2 image may need redeploy |
| Connection string invalid | Re-copy from Atlas → **Connect** → **Drivers** |
| Can't find `migration_db` | Re-run `python3 migration.py --migrate` and refresh Data Explorer |
| EC2 Instance Connect fails | Confirm instance is **Running** and security group allows SSH (port 22) |

---

## Screenshot Reference Summary

| Screenshot | Lab step |
|------------|----------|
| [Lab02_Step_5.2_MongoDB_Driver_Connection_String.png](../Lab%20Screenshots/Lab02_Step_5.2_MongoDB_Driver_Connection_String.png) | 6.2 — Copy Atlas connection string |
| [Lab02_Step_6.2_View_Migrated_Documents_customers.png](../Lab%20Screenshots/Lab02_Step_6.2_View_Migrated_Documents_customers.png) | 7.1 — Verify `migration_db.customers` |

---

## Lab 2 Complete! ✅
