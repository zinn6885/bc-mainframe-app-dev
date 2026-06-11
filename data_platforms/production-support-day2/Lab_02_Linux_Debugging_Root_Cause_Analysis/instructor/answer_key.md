# Lab 2 — Answer Key (Instructor)

**Mock solution:** [lab2_solution.xlsx](lab2_solution.xlsx)

---

## Live EC2 — expected fix flow

```bash
systemctl status payment-processor     # failed
sudo journalctl -u payment-processor -n 50   # port 8080 in use
sudo ss -tulpn | grep 8080             # python3 PID (e.g. 2523)
pgrep -af rogue-process.py             # /opt/rogue-process.py
sudo kill -9 <PID>
sudo systemctl reset-failed payment-processor
sudo systemctl restart payment-processor
systemctl is-active payment-processor  # active
```

**Do not use** `pkill -f rogue-process.py` — it can kill the student's SSH shell. Use `kill -9 <PID>` only.

---

## Mock — investigation log answers

| Step | Key finding |
|------|-------------|
| 1–3 | Service down; port 8080 conflict |
| 4–5 | PID 9876 — legacy `old-process` |
| 6–9 | Kill process; service `active (running)` |

---

## 5 Whys root cause

Incomplete runbook and missing validation step after migration.

---

## RCA timeline

09:00 failed → 09:05 logs → 09:10 PID found → 09:12 fixed → 09:15 verified (**15 min** downtime)

---

## Common mistakes

| Mistake | Fix |
|---------|-----|
| `ss` without `sudo` | PID hidden — use `sudo ss -tulpn` |
| Broad `pkill` | Kills SSH session — use `kill -9 <PID>` |
| Skip `reset-failed` | Run before restart after failed unit |
| RCA stops at port conflict | Root cause is runbook/process gap |
