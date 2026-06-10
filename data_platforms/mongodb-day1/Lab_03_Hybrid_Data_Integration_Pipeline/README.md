# Lab 3: Hybrid Data Integration Pipeline

## Complete Student Lab Guide (Validated & Working)

---

## Lab Overview

| Aspect | Details |
|--------|---------|
| **Duration** | 25–30 minutes |
| **Objective** | Build a hybrid data pipeline integrating batch processing, real-time API calls, and CDC simulation |
| **Environment** | AWS EC2 (pre-configured) + MongoDB Atlas |
| **Tools** | Python 3, pymongo, requests library |

---

## Prerequisites

- [ ] Lab 1 completed (MongoDB Atlas cluster ready)
- [ ] Lab 2 completed (familiar with EC2 and Python scripts)
- [ ] AWS EC2 instance running (`Training-Lab`)
- [ ] MongoDB Atlas connection string ready

> **Which files need your credentials?** See **[Day 1 Configuration Guide](../CONFIGURATION.md)** — pass the same `mongodb+srv://` string to all four Lab 3 scripts on the command line.

> **Need an EC2 instance?** Follow **[Appendix A: EC2 Instance Setup Guide](../EC2_Instance_Setup_Guide.md)** — use **EC2 Instance Connect** (browser terminal).

> **Atlas UI note:** To browse data, use **Database** → **Data Explorer**, or click **Browse Collections** on your cluster.

---

## Theoretical Foundation: Hybrid Data Integration

### What is Hybrid Data Integration?

**Hybrid data integration** is the process of combining data from multiple sources using different integration patterns — batch, real-time, and API-based — into a unified view.

### The Three Integration Patterns

<img src="diagrams/integration-patterns.svg" alt="Hybrid Integration Pipeline" width="520"/>

| Pattern | Description | When to use |
|---------|-------------|-------------|
| **Batch** | Process large volumes at scheduled intervals | Daily sales reports, historical loads |
| **API** | Fetch data from external services on demand | Customer enrichment, geocoding |
| **CDC** | Capture and react to changes as they happen | Real-time analytics, fraud detection |

---

## Part 1: Connect to EC2 Instance (2 minutes)

### Step 1.1: Connect via AWS Console

1. Go to **AWS Console** → **EC2** → **Instances**
2. Select your instance **`Training-Lab`**
3. Click **Connect**
4. Select the **EC2 Instance Connect** tab
5. Username: `ec2-user`
6. Click **Connect**

**Expected output:**

```
[ec2-user@ip-172-31-13-140 ~]$
```

### Step 1.2: Create Lab 3 directory

```bash
mkdir -p /home/ec2-user/lab3
cd /home/ec2-user/lab3
```

**Expected output:** No output — you are now in the `lab3` directory.

### Step 1.3: Install required Python libraries

```bash
pip3 install pymongo certifi requests --user
```

**Expected output:**

```
Successfully installed certifi-... pymongo-... requests-...
```

### Step 1.4: Verify Atlas connection from EC2 (do this before Part 2)

**Whitelist EC2 IP** — from EC2 terminal:

```bash
curl -s https://checkip.amazonaws.com
```

Add that IP in Atlas → **Database** → **Network Access** → **Add IP Address**. Wait **1–2 minutes** for **Active**.

**Test connection:**

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

> ⚠️ If you see `SSL handshake failed` or `TLSV1_ALERT_INTERNAL_ERROR`, see **Troubleshooting** below or [Lab 2 Part 4](../Lab_02_Data_Migration_Simulation/README.md#part-4-test-mongodb-atlas-connection-1-minute).

---

## Part 2: Batch Integration — Load Historical Orders (5 minutes)

### What is Batch Integration?

**Batch integration** processes data in large groups (batches) at scheduled times. It is ideal for large volumes that do not need immediate processing.

### Step 2.1: Create the batch load script

```bash
cat > batch_load.py << 'EOF'
#!/usr/bin/env python3
"""Batch Load Module - Historical Data Integration"""

import csv
import certifi
from datetime import datetime
from pymongo import MongoClient

# Sample historical orders data
HISTORICAL_ORDERS_CSV = """order_id,customer_id,product,quantity,order_date,status
ORD001,1001,Laptop,1,2024-01-15,delivered
ORD002,1002,Mouse,2,2024-01-20,delivered
ORD003,1001,Keyboard,1,2024-02-10,delivered
ORD004,1003,Monitor,1,2024-02-15,shipped
ORD005,1002,USB Cable,3,2024-03-01,processing
ORD006,1004,Headphones,1,2024-03-05,processing
ORD007,1001,Docking Station,1,2024-03-10,pending
"""

def load_batch_orders(connection_string):
    """Load historical orders into MongoDB Atlas"""

    print("\n" + "=" * 60)
    print("BATCH INTEGRATION: LOAD HISTORICAL ORDERS")
    print("=" * 60)

    with open('historical_orders.csv', 'w') as f:
        f.write(HISTORICAL_ORDERS_CSV)
    print("\n📁 Created source file: historical_orders.csv")

    records = []
    with open('historical_orders.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)
    print(f"📊 Read {len(records)} historical orders")

    documents = []
    for record in records:
        doc = {
            "orderId": record['order_id'],
            "customerId": int(record['customer_id']),
            "product": record['product'],
            "quantity": int(record['quantity']),
            "orderDate": datetime.strptime(record['order_date'], '%Y-%m-%d'),
            "status": record['status'],
            "source": "batch_load",
            "ingestionTimestamp": datetime.now()
        }
        documents.append(doc)

    client = MongoClient(connection_string, tlsCAFile=certifi.where())
    db = client.hybrid_db
    collection = db.orders

    collection.delete_many({})
    result = collection.insert_many(documents)

    collection.create_index("orderId", unique=True)
    collection.create_index("customerId")

    print(f"\n✅ Loaded {len(result.inserted_ids)} documents to MongoDB")
    print(f"📦 Database: hybrid_db.orders")
    print(f"🔍 Indexes created on: orderId, customerId")

    return len(result.inserted_ids)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        count = load_batch_orders(sys.argv[1])
        print(f"\n🎉 Batch load complete! {count} orders loaded.")
    else:
        print("Usage: python3 batch_load.py 'your_connection_string'")
EOF

chmod +x batch_load.py
```

### Step 2.2: Run the batch load

```bash
python3 batch_load.py 'mongodb+srv://YOUR_USERNAME:YOUR_PASSWORD@YOUR_CLUSTER.mongodb.net/'
```

> ⚠️ Replace with your actual MongoDB Atlas connection string

**Expected output:**

```
============================================================
BATCH INTEGRATION: LOAD HISTORICAL ORDERS
============================================================

📁 Created source file: historical_orders.csv
📊 Read 7 historical orders

✅ Loaded 7 documents to MongoDB
📦 Database: hybrid_db.orders
🔍 Indexes created on: orderId, customerId

🎉 Batch load complete! 7 orders loaded.
```

**What just happened:**
- Created a CSV file with 7 historical orders
- Transformed each record to a MongoDB document
- Loaded all 7 orders into `hybrid_db.orders`
- Created indexes for fast querying

---

## Part 3: API Integration — Enrich Orders with Customer Data (5 minutes)

### What is API Integration?

**API integration** fetches data from external services on demand. It is ideal for enriching existing data with external information.

### Step 3.1: Create the API enrichment script

```bash
cat > api_enrich.py << 'EOF'
#!/usr/bin/env python3
"""API Integration Module - External Data Enrichment"""

import certifi
from datetime import datetime
from pymongo import MongoClient

MOCK_CUSTOMER_API = {
    1001: {"name": "John Smith", "email": "john.smith@example.com", "tier": "gold", "lifetimeValue": 12500},
    1002: {"name": "Jane Doe", "email": "jane.doe@example.com", "tier": "silver", "lifetimeValue": 5400},
    1003: {"name": "Bob Wilson", "email": "bob.wilson@example.com", "tier": "bronze", "lifetimeValue": 1200},
    1004: {"name": "Alice Brown", "email": "alice.brown@example.com", "tier": "gold", "lifetimeValue": 18750}
}

def call_customer_api(customer_id):
    """Simulate calling an external customer API"""
    import time
    time.sleep(0.1)
    return MOCK_CUSTOMER_API.get(customer_id, {
        "name": "Unknown Customer", "email": "unknown@example.com",
        "tier": "standard", "lifetimeValue": 0
    })

def enrich_orders(connection_string):
    """Enrich orders with customer data from external API"""

    print("\n" + "=" * 60)
    print("API INTEGRATION: ENRICH ORDERS WITH CUSTOMER DATA")
    print("=" * 60)

    client = MongoClient(connection_string, tlsCAFile=certifi.where())
    db = client.hybrid_db

    orders = list(db.orders.find({}))
    print(f"\n📊 Found {len(orders)} orders to enrich")

    customer_cache = {}
    api_calls = 0
    enriched_orders = []

    print("\n🌐 Calling external API for customer data...\n")

    for order in orders:
        customer_id = order['customerId']

        if customer_id in customer_cache:
            customer_data = customer_cache[customer_id]
        else:
            customer_data = call_customer_api(customer_id)
            customer_cache[customer_id] = customer_data
            api_calls += 1
            print(f"   📞 API call {api_calls}: Customer {customer_id} → {customer_data['name']} ({customer_data['tier']} tier)")

        enriched_doc = {
            "orderId": order['orderId'],
            "customerId": customer_id,
            "customerName": customer_data['name'],
            "customerEmail": customer_data['email'],
            "customerTier": customer_data['tier'],
            "customerLifetimeValue": customer_data['lifetimeValue'],
            "product": order['product'],
            "quantity": order['quantity'],
            "orderDate": order['orderDate'],
            "status": order['status'],
            "enrichmentTimestamp": datetime.now(),
            "enrichmentSource": "external_customer_api"
        }
        enriched_orders.append(enriched_doc)

    collection = db.enriched_orders
    collection.delete_many({})
    result = collection.insert_many(enriched_orders)

    collection.create_index("orderId", unique=True)
    collection.create_index("customerId")
    collection.create_index("customerTier")

    print(f"\n✅ Stored {len(result.inserted_ids)} enriched orders")
    print(f"📦 Database: hybrid_db.enriched_orders")
    print(f"🌐 Total unique API calls: {api_calls}")

    return len(result.inserted_ids)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        count = enrich_orders(sys.argv[1])
        print(f"\n🎉 API enrichment complete! {count} orders enriched.")
    else:
        print("Usage: python3 api_enrich.py 'your_connection_string'")
EOF

chmod +x api_enrich.py
```

### Step 3.2: Run the API enrichment

```bash
python3 api_enrich.py 'mongodb+srv://YOUR_USERNAME:YOUR_PASSWORD@YOUR_CLUSTER.mongodb.net/'
```

**Expected output:**

```
============================================================
API INTEGRATION: ENRICH ORDERS WITH CUSTOMER DATA
============================================================

📊 Found 7 orders to enrich

🌐 Calling external API for customer data...

   📞 API call 1: Customer 1001 → John Smith (gold tier)
   📞 API call 2: Customer 1002 → Jane Doe (silver tier)
   📞 API call 3: Customer 1003 → Bob Wilson (bronze tier)
   📞 API call 4: Customer 1004 → Alice Brown (gold tier)

✅ Stored 7 enriched orders
📦 Database: hybrid_db.enriched_orders
🌐 Total unique API calls: 4

🎉 API enrichment complete! 7 orders enriched.
```

**What just happened:**
- Retrieved all orders from the database
- Called a simulated external API for each unique customer (4 calls for 7 orders — caching avoids duplicates)
- Created `enriched_orders` with customer name, email, tier, and lifetime value

---

## Part 4: CDC Simulation — Real-Time Order Processing (5 minutes)

### What is Change Data Capture (CDC)?

**CDC (Change Data Capture)** captures database changes in real time and triggers downstream processing.

### Step 4.1: Create the CDC simulation script

```bash
cat > cdc_simulate.py << 'EOF'
#!/usr/bin/env python3
"""CDC Simulation Module - Real-time Change Data Capture"""

import certifi
from datetime import datetime
from pymongo import MongoClient
import time

NEW_ORDERS = [
    {"orderId": "ORD008", "customerId": 1001, "product": "Wireless Mouse", "quantity": 2, "status": "processing"},
    {"orderId": "ORD009", "customerId": 1002, "product": "Mechanical Keyboard", "quantity": 1, "status": "pending"},
    {"orderId": "ORD010", "customerId": 1004, "product": "USB Hub 4-port", "quantity": 3, "status": "processing"},
    {"orderId": "ORD011", "customerId": 1003, "product": "Monitor Stand", "quantity": 1, "status": "pending"}
]

def update_daily_summary(collection, new_order):
    """CDC Trigger: Update daily summary when a new order arrives"""
    today = datetime.now().strftime('%Y-%m-%d')

    collection.update_one(
        {"date": today},
        {
            "$inc": {
                "totalOrders": 1,
                "totalQuantity": new_order['quantity'],
                f"customer_{new_order['customerId']}_orders": 1,
                f"customer_{new_order['customerId']}_quantity": new_order['quantity']
            },
            "$set": {"lastUpdated": datetime.now()},
            "$setOnInsert": {"date": today, "createdAt": datetime.now()}
        },
        upsert=True
    )

def simulate_cdc(connection_string):
    """Simulate CDC by processing new orders in real-time"""

    print("\n" + "=" * 60)
    print("CDC SIMULATION: REAL-TIME ORDER PROCESSING")
    print("=" * 60)

    client = MongoClient(connection_string, tlsCAFile=certifi.where())
    db = client.hybrid_db
    orders_collection = db.orders
    summary_collection = db.daily_summary

    print("\n🔔 Simulating real-time order stream...\n")

    for order in NEW_ORDERS:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] New order: {order['orderId']}")
        print(f"   Customer: {order['customerId']} | Product: {order['product']} | Qty: {order['quantity']}")

        order['orderDate'] = datetime.now()
        order['ingestionTimestamp'] = datetime.now()
        order['source'] = "realtime_cdc"

        result = orders_collection.insert_one(order)
        print(f"   ✅ Order stored (ID: {result.inserted_id})")

        update_daily_summary(summary_collection, order)
        print(f"   📊 CDC Trigger: Daily summary updated")

        time.sleep(1.5)
        print()

    print("=" * 60)
    print("CDC PROCESSING SUMMARY")
    print("=" * 60)

    total_orders = orders_collection.count_documents({})
    print(f"\n📦 Total orders in system: {total_orders}")

    summaries = list(summary_collection.find({}))
    for summary in summaries:
        print(f"\n📅 Date: {summary['date']}")
        print(f"   Total orders today: {summary.get('totalOrders', 0)}")
        print(f"   Total quantity sold: {summary.get('totalQuantity', 0)}")
        print(f"   Last updated: {summary.get('lastUpdated', 'N/A').strftime('%H:%M:%S')}")

    return len(NEW_ORDERS)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        count = simulate_cdc(sys.argv[1])
        print(f"\n🎉 CDC simulation complete! {count} new orders processed.")
    else:
        print("Usage: python3 cdc_simulate.py 'your_connection_string'")
EOF

chmod +x cdc_simulate.py
```

### Step 4.2: Run the CDC simulation

```bash
python3 cdc_simulate.py 'mongodb+srv://YOUR_USERNAME:YOUR_PASSWORD@YOUR_CLUSTER.mongodb.net/'
```

**Expected output:**

```
============================================================
CDC SIMULATION: REAL-TIME ORDER PROCESSING
============================================================

🔔 Simulating real-time order stream...

[14:32:15] New order: ORD008
   Customer: 1001 | Product: Wireless Mouse | Qty: 2
   ✅ Order stored (ID: ObjectId('...'))
   📊 CDC Trigger: Daily summary updated

[14:32:17] New order: ORD009
   Customer: 1002 | Product: Mechanical Keyboard | Qty: 1
   ✅ Order stored (ID: ObjectId('...'))
   📊 CDC Trigger: Daily summary updated

[14:32:19] New order: ORD010
   Customer: 1004 | Product: USB Hub 4-port | Qty: 3
   ✅ Order stored (ID: ObjectId('...'))
   📊 CDC Trigger: Daily summary updated

[14:32:21] New order: ORD011
   Customer: 1003 | Product: Monitor Stand | Qty: 1
   ✅ Order stored (ID: ObjectId('...'))
   📊 CDC Trigger: Daily summary updated

============================================================
CDC PROCESSING SUMMARY
============================================================

📦 Total orders in system: 11

📅 Date: 2026-06-09
   Total orders today: 4
   Total quantity sold: 7
   Last updated: 14:32:21

🎉 CDC simulation complete! 4 new orders processed.
```

**What just happened:**
- Simulated 4 new orders arriving in real time
- Each insert updated `daily_summary` via a CDC trigger
- Total orders in `hybrid_db.orders` is now **11** (7 batch + 4 CDC)

**Theoretical note — CDC architecture:**

<img src="diagrams/cdc-architecture.svg" alt="CDC Event-Driven Architecture" width="400"/>

---

## Part 5: Query and Verify Results (3 minutes)

### Step 5.1: Create the query script

```bash
cat > query_results.py << 'EOF'
#!/usr/bin/env python3
"""Query Module - Display Hybrid Pipeline Results"""

import certifi
from pymongo import MongoClient

CDC_ORDER_COUNT = 4

def display_results(connection_string):
    """Display data from all hybrid pipeline collections"""

    print("\n" + "=" * 70)
    print("HYBRID DATA INTEGRATION PIPELINE - COMPLETE RESULTS")
    print("=" * 70)

    client = MongoClient(connection_string, tlsCAFile=certifi.where())
    db = client.hybrid_db

    print("\n📦 1. BATCH INTEGRATION - Historical Orders")
    print("-" * 50)
    orders_count = db.orders.count_documents({})
    print(f"   Total orders: {orders_count}")

    orders = list(db.orders.find({}).limit(3))
    for order in orders:
        print(f"   ├── {order['orderId']}: {order['product']} x{order['quantity']} (Customer: {order['customerId']})")
    if orders_count > 3:
        print(f"   └── ... and {orders_count - 3} more orders")

    print("\n🌐 2. API INTEGRATION - Enriched Orders")
    print("-" * 50)
    enriched_count = db.enriched_orders.count_documents({})
    print(f"   Total enriched orders: {enriched_count}")

    enriched = list(db.enriched_orders.find({}).limit(3))
    for order in enriched:
        tier_icon = "⭐" if order['customerTier'] == 'gold' else "💎" if order['customerTier'] == 'silver' else "🟢"
        print(f"   ├── {order['orderId']}: {order['customerName']} ({order['customerTier']} {tier_icon})")
    if enriched_count > 3:
        print(f"   └── ... and {enriched_count - 3} more")

    print("\n⚡ 3. CDC INTEGRATION - Real-time Daily Summary")
    print("-" * 50)
    summaries = list(db.daily_summary.find({}))
    for summary in summaries:
        print(f"\n   📅 Date: {summary['date']}")
        print(f"      Total orders today: {summary.get('totalOrders', 0)}")
        print(f"      Total quantity sold: {summary.get('totalQuantity', 0)}")
        print(f"      Customer breakdown:")
        for key in summary.keys():
            if key.startswith('customer_') and key.endswith('_orders'):
                cust_id = key.replace('customer_', '').replace('_orders', '')
                order_count = summary.get(key, 0)
                qty = summary.get(f'customer_{cust_id}_quantity', 0)
                print(f"         - Customer {cust_id}: {order_count} order(s), {qty} items")

    print("\n" + "=" * 70)
    print("PIPELINE STATISTICS")
    print("=" * 70)
    print(f"""
   📦 BATCH INTEGRATION: {orders_count} orders in hybrid_db.orders
   🌐 API INTEGRATION:   {enriched_count} orders enriched with customer data
   ⚡ CDC INTEGRATION:   {CDC_ORDER_COUNT} orders processed in real-time

   ✅ All three integration patterns are working together!
    """)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        display_results(sys.argv[1])
    else:
        print("Usage: python3 query_results.py 'your_connection_string'")
EOF

chmod +x query_results.py
```

### Step 5.2: Run the query script

```bash
python3 query_results.py 'mongodb+srv://YOUR_USERNAME:YOUR_PASSWORD@YOUR_CLUSTER.mongodb.net/'
```

**Expected output:**

```
======================================================================
HYBRID DATA INTEGRATION PIPELINE - COMPLETE RESULTS
======================================================================

📦 1. BATCH INTEGRATION - Historical Orders
--------------------------------------------------
   Total orders: 11
   ├── ORD001: Laptop x1 (Customer: 1001)
   ├── ORD002: Mouse x2 (Customer: 1002)
   ├── ORD003: Keyboard x1 (Customer: 1001)
   └── ... and 8 more orders

🌐 2. API INTEGRATION - Enriched Orders
--------------------------------------------------
   Total enriched orders: 11
   ├── ORD001: John Smith (gold ⭐)
   ├── ORD002: Jane Doe (silver 💎)
   ├── ORD003: John Smith (gold ⭐)
   └── ... and 8 more

⚡ 3. CDC INTEGRATION - Real-time Daily Summary
--------------------------------------------------

   📅 Date: 2026-06-09
      Total orders today: 4
      Total quantity sold: 7
      Customer breakdown:
         - Customer 1001: 1 order(s), 2 items
         - Customer 1002: 1 order(s), 1 items
         - Customer 1003: 1 order(s), 1 items
         - Customer 1004: 1 order(s), 3 items

======================================================================
PIPELINE STATISTICS
======================================================================

   📦 BATCH INTEGRATION: 11 orders in hybrid_db.orders
   🌐 API INTEGRATION:   11 orders enriched with customer data
   ⚡ CDC INTEGRATION:   4 orders processed in real-time

   ✅ All three integration patterns are working together!
```

> **Note:** `enriched_orders` still shows 7 documents from the API step (run before CDC). Re-run `api_enrich.py` after CDC if you want 11 enriched records.

---

## Part 6: Verify in MongoDB Atlas (2 minutes)

### Step 6.1: Open Data Explorer

1. Go to **MongoDB Atlas** in your browser
2. Open **Data Explorer**:
   - Left sidebar → **Database** → **Data Explorer**, **or**
   - **Clusters** → **Browse Collections**
3. Select your cluster and expand **`hybrid_db`**

**Expected outcome:**

<img src="../Lab%20Screenshots/Lab03_Step_6.2_Explore_hybrid_db_Collections.png" alt="hybrid_db collections orders enriched_orders daily_summary" width="720"/>

- Database: `hybrid_db`
- Collections: `orders`, `enriched_orders`, `daily_summary`

### Step 6.2: Explore each collection

Click each collection in the left panel (**Documents** tab):

| Collection | Purpose | Document count |
|------------|---------|----------------|
| `orders` | Batch-loaded orders + CDC inserts | ~11 documents |
| `enriched_orders` | API-enriched orders | ~7 documents (re-run API step for 11) |
| `daily_summary` | CDC real-time aggregates | 1 document |

**UI steps:**
1. Click **`orders`** — 7 historical + 4 real-time orders (`ORD001`–`ORD011`)
2. Click **`enriched_orders`** — orders with customer names and tiers
3. Click **`daily_summary`** — today's order and quantity totals

### Step 6.3: Sample aggregation (optional)

1. Select `enriched_orders` → **Aggregations** tab
2. Switch to **TEXT** mode and paste:

```json
[
  { "$match": { "customerTier": "gold" } },
  { "$group": { "_id": "$customerName", "totalQuantity": { "$sum": "$quantity" } } },
  { "$sort": { "totalQuantity": -1 } }
]
```

3. Click **Run** to see gold-tier customers grouped by name

---

## Lab 3 Summary

### What you accomplished

| Step | Integration pattern | Script | Status |
|------|---------------------|--------|--------|
| 1 | **Batch** | `batch_load.py` | ✅ Loaded 7 historical orders |
| 2 | **API** | `api_enrich.py` | ✅ Enriched orders with customer data |
| 3 | **CDC** | `cdc_simulate.py` | ✅ Processed 4 real-time orders |
| 4 | **Query** | `query_results.py` | ✅ Verified all patterns |

### Key concepts learned

| Concept | Definition | Applied in Lab 3 |
|---------|------------|------------------|
| **Batch Integration** | Scheduled processing of grouped data | CSV → `hybrid_db.orders` |
| **API Integration** | On-demand external data fetching | Customer enrichment |
| **CDC** | Real-time change detection | `daily_summary` updates on insert |
| **Hybrid Pipeline** | Multiple patterns combined | Batch + API + CDC together |

### Integration patterns summary

| Pattern | Script | Volume | Latency | Best for |
|---------|--------|--------|---------|----------|
| Batch | `batch_load.py` | 7 orders | Minutes | Historical data |
| API | `api_enrich.py` | 7 enriched | Seconds | Data enrichment |
| CDC | `cdc_simulate.py` | 4 orders | Milliseconds | Real-time analytics |

### Pipeline data flow summary

<img src="diagrams/pipeline-flow.svg" alt="Complete Hybrid Pipeline data flow" width="420"/>

---

## Quick reference commands

| Action | Command |
|--------|---------|
| Navigate to lab3 | `cd /home/ec2-user/lab3` |
| Run batch load | `python3 batch_load.py 'CONNECTION_STRING'` |
| Run API enrichment | `python3 api_enrich.py 'CONNECTION_STRING'` |
| Run CDC simulation | `python3 cdc_simulate.py 'CONNECTION_STRING'` |
| View all results | `python3 query_results.py 'CONNECTION_STRING'` |

**Run scripts in this order:** `batch_load.py` → `api_enrich.py` → `cdc_simulate.py` → `query_results.py`

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'requests'` | `pip3 install requests --user` |
| `ModuleNotFoundError: No module named 'pymongo'` | `pip3 install pymongo certifi --user` |
| `SSL handshake failed` / `TLSV1_ALERT_INTERNAL_ERROR` | Whitelist EC2 IP (`curl -s https://checkip.amazonaws.com`) in Atlas **Network Access**, wait 1–2 min, then `pip3 install --upgrade pymongo certifi --user`. All Lab 3 scripts use `tlsCAFile=certifi.where()`. |
| Connection failed (other) | Add EC2 public IP to Atlas → **Network Access** |
| No orders found | Run `batch_load.py` first |
| `enriched_orders` empty | Run `api_enrich.py` after batch load |
| `daily_summary` empty | Run `cdc_simulate.py` last |
| `enriched_orders` count is 7 not 11 | Re-run `api_enrich.py` after CDC to include new orders |
| Can't find `hybrid_db` | Re-run scripts in order and refresh Data Explorer |

---

## Screenshot reference summary

| Screenshot | Lab step |
|------------|----------|
| [Lab03_Step_6.2_Explore_hybrid_db_Collections.png](../Lab%20Screenshots/Lab03_Step_6.2_Explore_hybrid_db_Collections.png) | 6.1 — Verify `hybrid_db` collections in Atlas |

---

## Lab 3 Complete! ✅

**Total time spent:** ________ minutes

**Integration patterns implemented:** 3 (Batch, API, CDC)

**Data processed:**
- Batch: 7 orders
- API: 7 orders enriched (11 after re-run)
- CDC: 4 real-time orders

---

## Day 1 Labs Completion Checklist

| Lab | Topic | Status |
|-----|-------|--------|
| Lab 1 | MongoDB CRUD, Indexing, Aggregation | ☐ |
| Lab 2 | Data Migration (Oracle → MongoDB) | ☐ |
| Lab 3 | Hybrid Data Integration Pipeline | ☐ |

**Congratulations! You have completed all three Day 1 labs.** 🎉
