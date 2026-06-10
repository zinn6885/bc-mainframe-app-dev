# Appendix A: Creating an EC2 Instance for Lab 2

## Complete Step-by-Step Guide (Validated & Working)

Use this guide to create the **`Training-Lab`** EC2 instance for **Lab 2** and **Lab 3**. Connection is via **EC2 Instance Connect** (browser terminal) — no local SSH, PowerShell, or WSL required.

---

## Overview

| Aspect | Details |
|--------|---------|
| **Duration** | 10–15 minutes |
| **Instance type** | t2.micro or t3.micro (free tier eligible) |
| **OS** | Amazon Linux 2023 |
| **Cost** | Free tier eligible (750 hours/month) |
| **Instance name** | `Training-Lab` |

---

## Prerequisites

- [ ] AWS account with administrator access
- [ ] Web browser
- [ ] 10–15 minutes of setup time

> **Configuration:** The user data script needs **no personal credentials**. For Atlas connection strings used after setup, see **[Day 1 Configuration Guide](CONFIGURATION.md)**.

---

## Part 1: Log into AWS Console (1 minute)

### Step 1.1: Access AWS Console

1. Open your web browser
2. Go to: **https://console.aws.amazon.com/**
3. Enter your email and password
4. Click **Sign In**

**Expected outcome:** AWS Management Console home page with the services grid.

---

## Part 2: Navigate to EC2 Dashboard (1 minute)

### Step 2.1: Open EC2 Service

1. In the top search bar, type **EC2**
2. Click **EC2** under **Services**
3. Or find EC2 under **Compute** in the Services menu

**Expected outcome:** EC2 Dashboard showing resources in your selected region.

---

## Part 3: Launch an Instance (5 minutes)

### Step 3.1: Start Launch Wizard

1. Click the orange **Launch instance** button

**Expected outcome:** Launch instance configuration page.

---

### Step 3.2: Name Your Instance

Under **Name and tags**, enter:

```
Training-Lab
```

**Expected outcome:** The name appears next to the instance in the instances list.

---

### Step 3.3: Choose Amazon Machine Image (AMI)

Under **Application and OS Images (Amazon Machine Image)**:

1. Select the **Quick Start** tab
2. For OS, select **Amazon Linux**
3. Select **Amazon Linux 2023 AMI**
4. Architecture: **64-bit (x86)**

**Expected outcome:**

```
Amazon Linux 2023 AMI 2023.12.20260608.0 x86_64 HVM kernel-6.1
```

---

### Step 3.4: Choose Instance Type

Under **Instance type**, select **`t2.micro`** or **`t3.micro`**.

**Expected outcome:** **Free tier eligible** appears next to the instance type.

---

### Step 3.5: Create Key Pair (optional for Instance Connect)

> **Note:** EC2 Instance Connect does not require a local `.pem` file. Create a key pair only if your organization requires it.

1. Under **Key pair (login)**, click **Create new key pair**
2. Configure:

| Setting | Value |
|---------|-------|
| **Key pair name** | `training-key` |
| **Key pair type** | RSA |
| **Private key file format** | .pem |

3. Click **Create key pair**

**Expected outcome:** The file `training-key.pem` downloads automatically.

> ⚠️ **Important:** Save this file securely. You cannot download it again.

---

### Step 3.6: Configure Network Settings

1. Under **Network settings**, click **Edit**
2. Configure:

| Setting | Value |
|---------|-------|
| **Network** | Leave default VPC |
| **Subnet** | No preference |
| **Auto-assign public IP** | Enable |

**Security group:**

1. Select **Create security group**
2. Add SSH rule:

| Type | Protocol | Port | Source | Purpose |
|------|----------|------|--------|---------|
| SSH | TCP | 22 | `0.0.0.0/0` | Required for EC2 Instance Connect |

**Expected outcome:** Security group named `launch-wizard-1` is created.

> **Security note:** For a short training session, SSH from anywhere is acceptable. **Terminate** the instance after training.

---

### Step 3.7: Configure Storage

Under **Configure storage**, set **Size** to **20** GB.

**Expected outcome:** Root volume shows 20 GB gp3.

---

### Step 3.8: Add User Data Script (Critical Step)

1. Scroll to **Advanced details** and expand
2. Find **User data**
3. Select **As text**
4. Paste the following script:

```bash
#!/bin/bash
# One-click setup for Day 1 Training - Lab 2

# Update system
dnf update -y

# Install Python and tools
dnf install -y python3 python3-pip

# Install Python libraries
pip3 install pymongo pandas certifi

# Create lab directories
mkdir -p /home/ec2-user/lab2 /home/ec2-user/lab3

# Create Lab 2 data file
cat > /home/ec2-user/lab2/customers.csv << 'EOF'
customer_id,name,email,state,phone,signup_date
1001,John Smith,john@email.com,NY,555-0101,2024-01-15
1001,John Smith,john@email.com,NY,555-0101,2024-01-15
1002,Jane Doe,,ca,555-0102,2024-02-20
1003, Bob Wilson,bob@email.com,California,,2024-03-10
1004,Alice Brown,,TX,555-0104,2024-01-05
EOF

# Create placeholder migration script (replace in Part 7)
cat > /home/ec2-user/lab2/migration.py << 'EOF'
#!/usr/bin/env python3
import csv
from datetime import datetime
from pymongo import MongoClient

print("=== Lab 2: Data Migration ===")
print("Ready to migrate! Run with: python3 migration.py")
EOF

chmod +x /home/ec2-user/lab2/migration.py
chown -R ec2-user:ec2-user /home/ec2-user

echo "Setup complete!" >> /var/log/cloud-init-output.log
```

**Expected outcome:** The script runs automatically when the instance first boots.

---

### Step 3.9: Launch the Instance

1. Review the **Summary** panel on the right
2. Click the orange **Launch instance** button

**Expected outcome:**

```
Success: Successfully initiated launch of instance (i-xxxxxxxxxxxxxxxxx)
```

---

## Part 4: Wait for Instance Initialization (2 minutes)

### Step 4.1: Monitor Instance Status

1. Click **View all instances**
2. Watch the **Instance state** column

**Expected progression:**

| Time | Instance state | Status check |
|------|----------------|--------------|
| Initial | `pending` | `initializing` |
| After 2–3 min | `running` | `2/2 checks passed` |

---

## Part 5: Connect to Your Instance (2 minutes)

### Step 5.1: Use EC2 Instance Connect

1. Select your instance **`Training-Lab`**
2. Click **Connect** at the top
3. Select the **EC2 Instance Connect** tab
4. Username: `ec2-user`
5. Click **Connect**

**Expected outcome:** A browser terminal opens:

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

---

## Part 6: Verify Setup (2 minutes)

### Step 6.1: Check lab directory

```bash
ls -la /home/ec2-user/lab2/
```

**Expected output:**

```
total 8
drwxr-xr-x. 2 ec2-user ec2-user  47 Jun  9 03:29 .
drwx------. 5 ec2-user ec2-user  98 Jun  9 03:29 ..
-rw-r--r--. 1 ec2-user ec2-user 288 Jun  9 03:29 customers.csv
-rwxr-xr-x. 1 ec2-user ec2-user 194 Jun  9 03:29 migration.py
```

> `migration.py` at **194 bytes** is the placeholder from user data — replace it in Part 7.

### Step 6.2: Check CSV data

```bash
cat /home/ec2-user/lab2/customers.csv
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

### Step 6.3: Check Python version

```bash
python3 --version
```

**Expected output:**

```
Python 3.9.25
```

---

## Part 7: Install Complete Migration Script (2 minutes)

### Step 7.1: Replace placeholder with full script

```bash
cat > /home/ec2-user/lab2/migration.py << 'EOF'
#!/usr/bin/env python3
"""Migration script for Oracle to MongoDB simulation"""

import argparse
import csv
import certifi
from datetime import datetime
from pymongo import MongoClient

def profile_data(csv_file):
    print("\n=== DATA PROFILING REPORT ===\n")
    records = []
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)

    total = len(records)
    print(f"Total records: {total}")

    customer_ids = [r['customer_id'] for r in records]
    duplicates = len(customer_ids) - len(set(customer_ids))
    print(f"Duplicate customer_id records: {duplicates}")

    missing_email = sum(1 for r in records if not r.get('email', '').strip())
    print(f"Missing emails: {missing_email}")

    states = [r.get('state', '').strip().lower() for r in records]
    valid_states = ['ny', 'ca', 'tx']
    invalid_states = sum(1 for s in states if s and s not in valid_states)
    print(f"Invalid state codes: {invalid_states}")

    whitespace_names = sum(1 for r in records if r.get('name', '') != r.get('name', '').strip())
    print(f"Names with leading/trailing spaces: {whitespace_names}")

    issues = duplicates + missing_email + invalid_states + whitespace_names
    quality_score = max(0, int((1 - issues / total) * 100)) if total else 0
    print(f"\nData Quality Score: {quality_score}%")
    return records

def cleanse_data(records):
    print("\n=== CLEANSING DATA ===\n")
    seen = set()
    unique_records = []
    for r in records:
        if r['customer_id'] not in seen:
            seen.add(r['customer_id'])
            unique_records.append(r)
    print(f"Duplicates removed: {len(records) - len(unique_records)}")

    for r in unique_records:
        if not r.get('email', '').strip():
            r['email'] = 'unknown@example.com'
        state = r.get('state', '').strip().lower()
        if state in ['ca', 'california']:
            r['state'] = 'CA'
        elif state in ['ny', 'new york']:
            r['state'] = 'NY'
        elif state in ['tx', 'texas']:
            r['state'] = 'TX'
        else:
            r['state'] = state.upper() if state else 'UNKNOWN'
        r['name'] = r.get('name', '').strip()
        if r.get('phone'):
            r['phone'] = r['phone'].replace('-', '')
    return unique_records

def load_to_mongodb(records, conn_str):
    print("\n=== LOADING TO MONGODB ===\n")
    client = MongoClient(conn_str, tlsCAFile=certifi.where())
    db = client.migration_db
    collection = db.customers
    documents = []
    for r in records:
        doc = {
            "customerId": int(r['customer_id']),
            "name": r['name'],
            "contact": {"email": r['email'], "phone": r.get('phone', '')},
            "address": {"state": r['state']},
            "signupDate": datetime.strptime(r['signup_date'], '%Y-%m-%d'),
            "dataQuality": {"score": 100, "issues": []}
        }
        documents.append(doc)
    collection.delete_many({})
    result = collection.insert_many(documents)
    collection.create_index("customerId", unique=True)
    print(f"Loaded {len(result.inserted_ids)} documents")
    print("Created index on customerId")
    return len(result.inserted_ids)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--profile', action='store_true')
    parser.add_argument('--migrate', action='store_true')
    args = parser.parse_args()

    csv_file = '/home/ec2-user/lab2/customers.csv'

    if args.profile:
        profile_data(csv_file)
    elif args.migrate:
        records = profile_data(csv_file)
        cleansed = cleanse_data(records)
        print("\n" + "=" * 50)
        print("ENTER YOUR MONGODB ATLAS CONNECTION STRING")
        print("=" * 50)
        conn_str = input("Connection string: ")
        count = load_to_mongodb(cleansed, conn_str)
        print(f"\n✅ Migration complete! Loaded {count} documents to MongoDB Atlas")
    else:
        print("Usage: python3 migration.py --profile OR --migrate")

if __name__ == "__main__":
    main()
EOF
```

### Step 7.2: Make script executable

```bash
chmod +x /home/ec2-user/lab2/migration.py
```

### Step 7.3: Verify script size

```bash
ls -la /home/ec2-user/lab2/migration.py
```

**Expected output:**

```
-rwxr-xr-x. 1 ec2-user ec2-user 4415 Jun  9 03:31 /home/ec2-user/lab2/migration.py
```

> File size should be **~4000–5000 bytes** (not 194).

---

## Part 8: Test the Setup (2 minutes)

### Step 8.1: Run data profiling

```bash
cd /home/ec2-user/lab2
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

### Step 8.2: Whitelist EC2 IP in Atlas

From the EC2 terminal:

```bash
curl -s https://checkip.amazonaws.com
```

In Atlas → **Database** → **Network Access** → **Add IP Address**, paste that IP (or use **Allow Access from Anywhere** for class labs). Wait **1–2 minutes** for the rule to show **Active**.

### Step 8.3: Install certifi (SSL certificates)

```bash
pip3 install --upgrade pymongo certifi --user
```

### Step 8.4: Test MongoDB connection

Replace with your Atlas connection string:

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

> If you see `SSL handshake failed` or `TLSV1_ALERT_INTERNAL_ERROR`, see **Troubleshooting** — whitelist the EC2 IP first, then ensure `certifi` is installed.

---

## EC2 Setup Summary Checklist

| Step | Task | Done |
|------|------|------|
| 1 | Log into AWS Console | ☐ |
| 2 | Navigate to EC2 Dashboard | ☐ |
| 3 | Click Launch instance | ☐ |
| 4 | Name instance `Training-Lab` | ☐ |
| 5 | Select Amazon Linux 2023 AMI | ☐ |
| 6 | Select t2.micro / t3.micro | ☐ |
| 7 | Create key pair `training-key` (optional) | ☐ |
| 8 | Security group — SSH port 22 | ☐ |
| 9 | Storage 20 GB | ☐ |
| 10 | Add User Data script | ☐ |
| 11 | Launch instance | ☐ |
| 12 | Wait for **Running** + **2/2 checks** | ☐ |
| 13 | Connect via EC2 Instance Connect | ☐ |
| 14 | Verify lab files exist | ☐ |
| 15 | Install full migration script (Part 7) | ☐ |
| 16 | Test `python3 migration.py --profile` | ☐ |
| 17 | Test MongoDB connection | ☐ |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Instance stuck on **pending** | Wait up to 5 minutes, refresh page |
| Cannot connect via Instance Connect | Security group must allow SSH (port 22) |
| User data script didn't run | `sudo cat /var/log/cloud-init-output.log` |
| `migration.py` shows 194 bytes | Run Part 7 to replace with full script |
| `pymongo` not found | `pip3 install pymongo certifi --user` |
| `SSL handshake failed` / `TLSV1_ALERT_INTERNAL_ERROR` | Whitelist EC2 IP in Atlas **Network Access** (`curl -s https://checkip.amazonaws.com`), wait 1–2 min, then `pip3 install --upgrade certifi --user` and use `tlsCAFile=certifi.where()` in `MongoClient` |
| Connection failed (other) | Add EC2 public IP to Atlas **Network Access** |
| `command not found: python3` | `sudo dnf install python3 -y` |

---

## Cost Management

### Stop vs terminate

| Action | When to use | What happens |
|--------|-------------|--------------|
| **Stop** | After class, before next session | No compute charges (storage only) |
| **Terminate** | Training complete | Instance permanently deleted |

### Stop instance

1. **EC2** → **Instances**
2. Select instance → **Instance state** → **Stop instance**

### Terminate instance

1. **EC2** → **Instances**
2. Select instance → **Instance state** → **Terminate instance**

> ⚠️ **Warning:** Terminating is permanent and irreversible.

---

## Next steps

Once setup is complete, proceed to:

- **[Lab 2: Data Migration Simulation](Lab_02_Data_Migration_Simulation/README.md)**
- **[Lab 3: Hybrid Data Integration Pipeline](Lab_03_Hybrid_Data_Integration_Pipeline/README.md)**

---

## EC2 Instance Ready ✅
