# Lab 1 — Answer Key (Instructor)

Use this to verify student submissions (screenshots or live console review). All resources must be in **`us-east-1`** inside VPC **`Lab1-VPC`**.

**Console troubleshooting:** [CONSOLE_UI_GUIDE.md](CONSOLE_UI_GUIDE.md)

---

## Console verification quick tips

| Page | How to find lab resources |
|------|---------------------------|
| VPCs, Subnets, Route tables | Search/filter **`Lab1-VPC`** — works |
| Security groups | Search **`Web-SG`** / **`Firewall-SG`** — **not** `Lab1-VPC` |
| NAT, NACL, IGW | Search by lab resource name |

**Normal extras:** default VPC `172.31.0.0/16`; main route table (fourth row when filtering route tables); default security group in lab VPC.

---

## Step 1 — VPC

| Field | Expected value |
|-------|----------------|
| Name | `Lab1-VPC` |
| IPv4 CIDR | `10.0.0.0/16` |
| State | Available |
| Tenancy | default |

---

## Step 2 — Subnets

| Name | AZ | CIDR | Auto-assign public IP |
|------|-----|------|------------------------|
| `Public-Subnet-A` | us-east-1a | 10.0.1.0/24 | May be false until instances launch (OK) |
| `Private-Subnet-B` | us-east-1b | 10.0.2.0/24 | false |
| `Firewall-Subnet-A` | us-east-1a | 10.0.3.0/24 | false |

All three subnets must belong to `Lab1-VPC`.

---

## Step 3 — Internet Gateway

| Field | Expected value |
|-------|----------------|
| Name | `Lab1-IGW` |
| State | Attached |
| VPC | Lab1-VPC |

---

## Step 4 — Route tables

| Route table | Associated subnet | Routes (destination → target) |
|-------------|-------------------|-------------------------------|
| `Public-RT` | Public-Subnet-A | 10.0.0.0/16 → local · **0.0.0.0/0 → igw-...** |
| `Private-RT` | Private-Subnet-B | 10.0.0.0/16 → local · (0.0.0.0/0 → NAT added in Step 5) |
| `Firewall-RT` | Firewall-Subnet-A | 10.0.0.0/16 → local only |

The VPC also has a **main** route table — that is normal. Lab subnets must use the three custom tables above. A filtered list may show **four** rows (three custom + one Main = Yes).

---

## Step 5 — NAT Gateway

| Field | Expected value |
|-------|----------------|
| Name | `Lab1-NAT` |
| Availability mode | **Zonal** (console default may be Regional — switch to Zonal to pick a subnet) |
| State | Available |
| Subnet | Public-Subnet-A |
| Connectivity | Public |
| Elastic IP | Allocated |

**Private-RT** must include: `0.0.0.0/0` → `nat-...` (Lab1-NAT)

---

## Step 6 — Network ACL

| Field | Expected value |
|-------|----------------|
| Name | `Web-Subnet-NACL` |
| Associated subnet | Private-Subnet-B |

**Inbound rules (minimum):**

| Rule # | Allow/Deny | Protocol | Port | Source |
|--------|------------|----------|------|--------|
| 100 | ALLOW | TCP | 80 | 0.0.0.0/0 |
| 110 | ALLOW | TCP | 443 | 0.0.0.0/0 |
| 120 | ALLOW | TCP | 22 | student IP/32 |
| 130 | ALLOW | TCP | 1024-65535 | 0.0.0.0/0 |
| 200 | DENY | ALL | ALL | 0.0.0.0/0 |

**Outbound:** Rule 100 ALLOW all to 0.0.0.0/0 (default-style is acceptable).

---

## Step 7 — Security groups

> **UI note:** If a student’s Security groups screenshot shows **“No matching resource found”** with filter `Lab1-VPC`, they used the wrong search term. Accept screenshots that show **`Web-SG`** and **`Firewall-SG`** inbound rules. See [CONSOLE_UI_GUIDE.md](CONSOLE_UI_GUIDE.md).

### Web-SG

| Direction | Type | Port | Source |
|-----------|------|------|--------|
| Inbound | HTTP | 80 | 0.0.0.0/0 |
| Inbound | SSH | 22 | student IP/32 |
| Outbound | All | All | 0.0.0.0/0 (default) |

### Firewall-SG

| Direction | Type | Port | Source |
|-----------|------|------|--------|
| Inbound | HTTP | 80 | 10.0.0.0/16 |
| Inbound | HTTPS | 443 | 10.0.0.0/16 |
| Outbound | All | All | 0.0.0.0/0 (default) |

Both groups must be in VPC `Lab1-VPC`.

---

## Step 8 — AWS Network Firewall

| Resource | Expected value |
|----------|----------------|
| Firewall name | `Lab1-Firewall` |
| Status | READY (PROVISIONING acceptable if still waiting) |
| VPC | Lab1-VPC |
| Subnet | Firewall-Subnet-A |
| Policy name | `Lab1-Firewall-Policy` |
| Rule group | `Allow-Web-Traffic` |

**Stateful rules in Allow-Web-Traffic:**

| Rule | Source | Destination | Protocol | Action |
|------|--------|-------------|----------|--------|
| allow-http | 10.0.0.0/16 | 0.0.0.0/0 | TCP:80 | PASS |
| allow-https | 10.0.0.0/16 | 0.0.0.0/0 | TCP:443 | PASS |
| deny-ssh | 10.0.0.0/16 | 0.0.0.0/0 | TCP:22 | DROP |

---

## Step 9 — Firewall endpoint (optional)

| Field | Expected |
|-------|----------|
| Endpoint ID | Present (vpce-...) |
| Subnet | Firewall-Subnet-A |

Full traffic steering through the firewall endpoint is **not** required for this lab.

---

## Grading rubric (suggested)

| Criteria | Points |
|----------|--------|
| VPC + 3 subnets with correct CIDR/AZ | 20 |
| IGW attached + Public-RT with IGW route | 15 |
| NAT in public subnet + Private-RT NAT route | 15 |
| NACL with ordered rules on private subnet | 15 |
| Web-SG + Firewall-SG | 15 |
| Network Firewall + policy + 3 rules | 20 |
| **Total** | **100** |

Deduct 5 points if region is not us-east-1. Deduct 10 if resources are not torn down when lab policy requires cleanup (cost control).

---

## Bonus question answer

Private instances reach the internet via **NAT Gateway** in the public subnet. The private route table sends `0.0.0.0/0` to the NAT, which uses its Elastic IP for outbound connections. Inbound connections from the internet cannot reach private instances directly.
