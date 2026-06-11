# Lab 3 — Instructor Package

**Estimated setup time:** 15–20 minutes (after Lab 2 is complete)  
**Region:** US East (N. Virginia) — `us-east-1`

---

## Before class

1. Complete **Lab 2** setup — EC2 running, students can SSH, `payment-processor` fixed.
2. Follow **[AWS_LAB3_SETUP.md](AWS_LAB3_SETUP.md)** — attach IAM role for CloudWatch metrics.
3. Walk through **[instructions.md](../instructions.md)** yourself once to verify console paths and commands.
4. Distribute to students: EC2 public IP, `.pem` key, region (`us-east-1`).

---

## Materials

| File | Purpose |
|------|---------|
| [AWS_LAB3_SETUP.md](AWS_LAB3_SETUP.md) | Pre-lab IAM and instructor verification checklist |
| [answer_key.md](answer_key.md) | Expected calculations and sample postmortem |
| [lab3_solution.xlsx](lab3_solution.xlsx) | Completed reference workbook (all 7 sheets filled) |
| [../template/lab3_starter.xlsx](../template/lab3_starter.xlsx) | Student starter (labels and blanks on all sheets) |
| [../setup/build_lab3_workbooks.py](../setup/build_lab3_workbooks.py) | Regenerate starter and solution workbooks |

To rebuild workbooks: `python setup/build_lab3_workbooks.py`

---

## Student guide

[../instructions.md](../instructions.md) — Steps 1–14 (AWS Console + SSH + Excel)
