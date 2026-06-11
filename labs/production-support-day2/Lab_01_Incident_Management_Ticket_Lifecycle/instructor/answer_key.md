# Lab 1: Incident Management and Ticket Lifecycle — Instructor Answer Key

**Solution workbook:** [lab1_solution.xlsx](lab1_solution.xlsx)

---

## Expected Escalation Decisions (Step 9)

| Ticket | Priority | Decision | Reasoning |
|--------|----------|----------|-----------|
| INC-002 | P2 | Escalate to L2 after 15 minutes | P2 SLA requires L1→L2 escalation if not resolved in 15 min. 8-second response time needs L2 investigation. |
| INC-003 | P3 | Stay at L1, resolve within 24 hours | P3 gives L1 up to 1 hour before escalation needed. Missing column is low impact, can be handled by L1. |

---

## Expected Resolution Timeline (INC-001)

| Event | Time | SLA Met? |
|-------|------|----------|
| Ticket created | 09:00 | - |
| Escalated to L2 | 09:05 (5 min) | ✅ Within 5 min SLA |
| Issue fixed | 09:12 (12 min total) | ✅ Within 1 hour SLA |
| Ticket closed | After user verification | ✅ Complete |

---

## Bonus Challenge Answer

**Scenario:** A P1 ticket was fixed in 10 minutes, but no one updated the ticket status for 2 hours.

**Question:** Did this violate SLA? Why?

**Answer:**

> Yes. SLA measures time to *resolution*, not just time to fix. The 2-hour delay in updating the ticket means reporting would show a 2+ hour resolution time. Best practice: update ticket immediately after fix.

---

## Common Mistakes to Watch For

| Mistake | Correction |
|---------|------------|
| Setting INC-001 as P2 or P3 | Payment failure with no workaround = P1 critical outage |
| Not escalating P1 within 5 minutes | Escalation Rules clearly state 5 min for P1 |
| Forgetting root cause documentation | L2 must document what caused the issue |
| Closing without resolution category | Every closed ticket needs a resolution category |
| Escalating P3 immediately | P3 gives L1 1 hour before escalation needed |

---

## Instructor Notes

### Setup Requirements

- Ensure participants have Excel or Google Sheets access
- Estimated time: 20–25 minutes

### Delivery Tips

- Demonstrate the first 3 steps live before participants begin
- Emphasize that P1 means CRITICAL — no workaround
- Use the bonus challenge as a discussion starter about SLA compliance

### Common Questions

**Q:** Can I use different category names?  
**A:** Yes, but keep them logical (e.g., "Payments" instead of "Payment API")

**Q:** What if my Excel doesn't have column letters?  
**A:** Go to View → Show → Headings (check this box)

**Q:** Does the exact wording of descriptions matter?  
**A:** Close enough is fine — focus on understanding the concepts
