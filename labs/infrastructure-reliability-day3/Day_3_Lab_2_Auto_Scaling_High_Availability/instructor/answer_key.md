# Lab 2 — Answer Key (Instructor)

Use this to verify student submissions (screenshots or live console review). All resources must be in **`us-east-1`** inside VPC **`Lab1-VPC`**.

---

## Prerequisites (Lab 1 + Step 1)

| Resource | Expected value |
|----------|----------------|
| VPC | `Lab1-VPC` · 10.0.0.0/16 · Available |
| `Public-Subnet-A` | us-east-1a · 10.0.1.0/24 · Public-RT · Lab 1 NAT only |
| `Public-Subnet-B` | us-east-1b · 10.0.6.0/24 · Public-RT · ALB (Step 1D) |
| `Public-Subnet-C` | us-east-1c · 10.0.5.0/24 · Public-RT · ALB |
| `Private-Subnet-B` | us-east-1b · 10.0.2.0/24 · Private-RT |
| `Private-Subnet-C` | us-east-1c · 10.0.4.0/24 · Private-RT |
| `Web-SG` | HTTP:80 from 0.0.0.0/0 · SSH:22 from student IP/32 |
| NAT | `Lab1-NAT` in Public-Subnet-A · Private-RT route 0.0.0.0/0 → NAT |

---

## Step 2 — Launch Template

| Field | Expected value |
|-------|----------------|
| Name | `WebServer-LT` |
| Default version | 1 |
| Auto Scaling guidance | Enabled |
| AMI | Amazon Linux 2023 |
| Instance type | t2.micro |
| Security group | Web-SG |
| User data | Bash script installing httpd + custom index.html |

---

## Step 3 — Target Group

| Field | Expected value |
|-------|----------------|
| Name | `ASG-TG` |
| Target type | instance |
| Protocol / port | HTTP / 80 |
| VPC | Lab1-VPC |
| Health check path | `/` |
| Success codes | 200 |
| Healthy / unhealthy threshold | 2 / 2 |
| Interval / timeout | 10s / 5s |

---

## Step 4–5 — Application Load Balancer

| Field | Expected value |
|-------|----------------|
| Name | `ASG-ALB` |
| Type | application |
| Scheme | internet-facing |
| State | active |
| Subnets | Public-Subnet-B + Public-Subnet-C (us-east-1b + us-east-1c) |
| Security group | Web-SG |
| Listener | HTTP:80 → forward to ASG-TG |
| DNS name | `ASG-ALB-*.us-east-1.elb.amazonaws.com` |

---

## Step 6 — Auto Scaling Group

| Field | Expected value |
|-------|----------------|
| Name | `WebServer-ASG` |
| Launch template | WebServer-LT (version 1) |
| Min / desired / max | 2 / 2 / 6 |
| Subnets | Private-Subnet-B + Private-Subnet-C |
| Target group | ASG-TG attached |
| Health check type | ELB |
| Scaling policy | `Scale-on-CPU` · target tracking · CPU 70% · warmup 60s |
| Instance tag | Name = WebServer-ASG on instances |

---

## Steps 7–8 — Running instances and health

| Check | Expected |
|-------|----------|
| Running instances | 2 |
| ASG Activity | Successful launch events |
| Target group registered | 2 targets |
| Target health | Both healthy in **us-east-1b** and **us-east-1c** (not **unused**) |

**Common failure:** One AZ healthy, other **unused** or instance restart loop → ALB subnets must be **`Public-Subnet-B` + `Public-Subnet-C`**, not A+C.
| AZ spread | Different AZs (typically 1b and 1c) |

---

## Step 9 — Load balancer test

| Check | Expected |
|-------|----------|
| Browser HTTP 200 | Demo page with Instance ID, AZ, Private IP |
| Load distribution | Instance ID may change on refresh |

---

## Steps 10–13 — Auto healing

| Check | Expected |
|-------|----------|
| After terminate one instance | ASG Activity shows replacement launch |
| Target group | Returns to 2 healthy targets |
| Recovery time | Typically 2–8 minutes · document actual measured time |

Student should document three timestamps and calculated recovery time.

---

## Step 14 — Optional scaling (bonus)

| Check | Expected (if attempted) |
|-------|-------------------------|
| Sustained CPU >70% | ASG Activity shows scale-out (desired > 2) |
| Max instances | Never exceeds 6 |

---

## Grading rubric (suggested)

| Criteria | Points |
|----------|--------|
| Prerequisites: subnets in 2 AZs + Web-SG + NAT route | 10 |
| Launch template with user data | 10 |
| Target group with correct health checks | 10 |
| ALB active, cross-AZ, listener to ASG-TG | 15 |
| ASG: capacity 2/2/6, private subnets, ELB health | 20 |
| Two healthy targets + browser test screenshot | 15 |
| Terminate + auto-heal + recovery time documented | 20 |
| **Total** | **100** |

Deduct 5 points if region is not us-east-1. Deduct 10 if Lab 2 resources not torn down when required.

---

## Bonus question answer

Target tracking scale-out adds instances until CPU approaches 70%, up to **maximum 6**. After traffic drops, scale-in removes extras but never below **minimum 2**.

---

## Troubleshooting quick answers

| Student report | Instructor response |
|----------------|---------------------|
| Targets unhealthy 5+ min | User data failed — check `/tmp/setup.log` via SSM if available; verify NAT route |
| ALB 503 | No healthy targets — wait or fix user data |
| ASG launch failure | Activity tab shows cause — often missing subnet or SG |
| Only 1 instance after terminate | Wait 3 min; check Activity for errors |
