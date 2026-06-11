# Lab 3 — Setup Files

Optional helper files for Steps 3 and 4. Copy to the EC2 instance with `scp` — see [instructions.md](../instructions.md).

| File | Use |
|------|-----|
| `cloudwatch_agent_config.json` | CloudWatch agent configuration |
| `send_metrics.sh` | Custom metrics script (ServiceHealth, ResponseTimeMs) |
| `lab3_put_metric_data_policy.json` | IAM inline policy for instructor — allows `put-metric-data` in Step 4 |
| `build_lab3_workbooks.py` | Regenerate `template/lab3_starter.xlsx` and `instructor/lab3_solution.xlsx` |

**Region:** `us-east-1`

```bash
python setup/build_lab3_workbooks.py
```
