# Lab 1 — Console UI troubleshooting

Quick reference when a participant says “I can’t find my resource.”

---

## Security groups — most common confusion

**Symptom:** Student types `Lab1-VPC` in the Security groups search box → **No matching resource found**.

**Cause:** The search box matches security group **name**, **ID**, **description**, and **VPC ID** — not the VPC’s **Name tag**.

**Fix (tell the student):**
1. Click **Clear filters**
2. Search **`Web-SG`** or **`Firewall-SG`**
3. Or scroll and match the **VPC ID** column to their lab VPC (same ID as on the Lab1-VPC page)

**Proof it worked:** Two groups in the lab VPC — `Web-SG` (HTTP + SSH inbound) and `Firewall-SG` (HTTP/HTTPS from 10.0.0.0/16), plus one **default** security group (ignore for grading).

---

## Default VPC vs lab VPC

**Symptom:** Student sees two VPCs or two Internet Gateways.

**Expected:** Default VPC `172.31.0.0/16` coexists with **`Lab1-VPC`** `10.0.0.0/16`. Only grade resources tagged/named for the lab.

---

## Route tables — four rows is correct

**Symptom:** Student expects exactly 3 route tables.

**Expected when filtering `Lab1-VPC`:**

| Name | Main | Grade? |
|------|------|--------|
| Public-RT | No | Yes — must have IGW route + Public-Subnet-A |
| *(main / dash)* | **Yes** | Ignore — auto-created |
| Private-RT | No | Yes — NAT route after Step 5 |
| Firewall-RT | No | Yes — Firewall-Subnet-A only |

---

## NAT Gateway — Regional vs Zonal availability mode

**Symptom:** Student on **Create NAT gateway** sees only a **VPC** dropdown — no **Subnet** field.

**Cause:** AWS defaults to **Regional** availability mode (new option). Regional NAT is placed at the VPC level and scales across AZs automatically — the console does not ask for a subnet in that mode.

**Fix (tell the student):**
1. Under **Availability mode**, select **Zonal**
2. **Subnet** appears — choose **`Public-Subnet-A`**
3. **Connectivity type:** **Public**
4. Allocate an Elastic IP and create the gateway

**Proof it worked:** NAT detail shows **State = Available**, **Subnet = Public-Subnet-A**, and a public Elastic IP.

> **Note:** Waiting 1–2 minutes for **Available** is normal. Do not continue to Step 5 route-table updates until the state is **Available**.

---

## Subnets / route tables filter vs security groups

| Page | Filter `Lab1-VPC` |
|------|-------------------|
| Subnets | Works |
| Route tables | Works |
| Security groups | **Does not work** |

---

## Network Firewall Step 8 — Category matching vs 5-tuple

**Symptom:** Student is on **Create Network Firewall rule group** but cannot name rules or set HTTP/TCP ports.

**Cause:** **Category matching** is selected under **Standard stateful rules**. That mode filters AWS threat categories — it does not create custom named rules.

**Fix (tell the student):**
1. Scroll to the **top** — rule group name **`Allow-Web-Traffic`**, capacity **100**
2. Under **Standard stateful rules**, click **5-tuple** (not Category matching)
3. Click **Add rule** — fields appear for **Rule name**, Source, Destination, Protocol (**TCP:80**, **TCP:443**, **TCP:22**), Action (**PASS** / **DROP**)
4. Skip **IP set reference**

---

## Screenshot grading notes

| Step | Accept if screenshot shows |
|------|---------------------------|
| 5 | NAT **Available** AND Private-RT `0.0.0.0/0` → NAT (one or two images) |
| 6 | Inbound rules 100–200 AND Private-Subnet-B association |
| 7 | Web-SG + Firewall-SG inbound rules (not empty SG list with failed filter) |
| 8 | Firewall **READY** and/or policy with **Allow-Web-Traffic** rule group |

Full participant guide: [../instructions.md](../instructions.md)
