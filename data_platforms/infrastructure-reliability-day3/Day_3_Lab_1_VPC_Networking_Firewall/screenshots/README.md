# Lab 1 screenshots

Save your deliverable screenshots locally using the filenames below. **Do not commit screenshots to the git repo** — they may show account-specific console details.

See [instructions.md](../instructions.md) for what each screenshot must show.

---

## Filename pattern

| Step | Save your screenshot as |
|------|-------------------------|
| 1 | `Step_01_VPC_Created.png` |
| 2 | `Step_02_Subnets_Created.png` |
| 3 | `Step_03_IGW_Attached.png` |
| 4 | `Step_04_Route_Tables.png` |
| 5 | `Step_05_NAT_Gateway.png` |
| 6 | `Step_06_NACL_Rules.png` |
| 7 | `Step_07_Security_Groups.png` |
| 8 | `Step_08_Network_Firewall.png` |
| 9 | `Step_09_Firewall_Endpoint.png` (optional) |

---

## What each screenshot must show

### Step 1 — VPC created
- **Page:** VPC → **Your VPCs**
- **Must show:** `Lab1-VPC` · CIDR `10.0.0.0/16` · State **Available**

### Step 2 — Subnets created
- **Page:** VPC → **Subnets** · filter `Lab1-VPC`
- **Must show:** all three subnets with CIDRs `10.0.1.0/24`, `10.0.2.0/24`, `10.0.3.0/24`

### Step 3 — Internet Gateway attached
- **Page:** VPC → **Internet gateways**
- **Must show:** `Lab1-IGW` · State **Attached** · VPC `Lab1-VPC`

### Step 4 — Route tables
- **Page:** VPC → **Route tables** · filter `Lab1-VPC`
- **Must show:** `Public-RT`, `Private-RT`, `Firewall-RT` (Main route table row is OK)
- **Also:** `Public-RT` → **Routes** → `0.0.0.0/0` → IGW

### Step 5 — NAT Gateway
- NAT detail: **Available** · `Public-Subnet-A`
- `Private-RT` → **Routes** → `0.0.0.0/0` → NAT

### Step 6 — NACL rules
- `Web-Subnet-NACL` inbound rules 100–200
- Subnet association: `Private-Subnet-B`

### Step 7 — Security groups
- **Do not** search `Lab1-VPC` on this page — search **`Web-SG`** and **`Firewall-SG`**
- Inbound rules for both groups

### Step 8 — Network Firewall
- `Lab1-Firewall` **READY** and/or `Lab1-Firewall-Policy` with `Allow-Web-Traffic`

### Step 9 — Firewall endpoint (optional)
- Firewall **Details** → Endpoint ID `vpce-…` · subnet `Firewall-Subnet-A`
