# Lab 1: VPC Networking & Firewall Subnet

**Folder:** `Day_3_Lab_1_VPC_Networking_Firewall`  
**Estimated time:** 50–60 minutes  
**Module alignment:** Modules 9–10 (Infrastructure Reliability & Network Security)  
**AWS region:** US East (N. Virginia) — `us-east-1`

![Lab 1 architecture: custom VPC with public, private, and firewall subnets](diagrams/lab1-vpc-architecture.svg)

---

## Start here

1. Confirm AWS Console region is **`us-east-1`** (N. Virginia).
2. Look up your public IP (search "what is my IP") — needed for SSH rules.
3. Open **[instructions.md](instructions.md)** and follow Steps 1–9.

---

## What you need

| Item | Source |
|------|--------|
| Lab steps | [instructions.md](instructions.md) |
| AWS account | Your own or instructor-provided |
| Region | **us-east-1** (required) |
| Architecture diagram | [diagrams/lab1-vpc-architecture.svg](diagrams/lab1-vpc-architecture.svg) |
| Screenshot guide | [screenshots/README.md](screenshots/README.md) |

> **Instructor materials** (setup guide, answer key, validation script) are in the [`instructor/`](instructor/) folder.

> **Console tip:** On **Security groups**, searching `Lab1-VPC` returns no results — search `Web-SG` / `Firewall-SG` instead. See [instructions.md — AWS Console finder table](instructions.md#aws-console-how-to-find-your-lab-resources).

---

## Cost warning

NAT Gateway (~$0.045/hr) and Network Firewall (~$0.395/hr) incur charges. Complete within **1 hour** and tear down resources using the checklist at the end of [instructions.md](instructions.md).

---

## Related labs

| Lab | Topic |
|-----|-------|
| **This lab (1)** | VPC networking, NACLs, security groups, Network Firewall |
| [Lab 2](../Day_3_Lab_2_Auto_Scaling_High_Availability/README.md) | Auto Scaling Group, ALB, cross-AZ high availability, auto-healing |
| [Lab 3](../Day_3_Lab_3_Alerting_Auto_Scaling_Events/README.md) | SNS alerts, CloudWatch alarms, EventBridge rules, dashboard |
| Lab 9–12 | Workbook exercises (reliability, DR, monitoring, automation) |

Archived AWS hands-on labs (HA, monitoring, automation) remain in [`_archive/`](../_archive/) for reference.
