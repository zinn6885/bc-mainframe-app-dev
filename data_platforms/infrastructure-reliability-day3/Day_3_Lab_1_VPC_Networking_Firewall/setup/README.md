# Lab 1 setup scripts

## test_vpc_lab1.py

Instructor validation script — deploys, validates, or tears down all lab resources programmatically.

```powershell
pip install -r requirements.txt

# Validate student or manual build
python setup/test_vpc_lab1.py --validate-only

# Full automated deploy (costs ~$0.45/hr while NAT + Firewall run)
python setup/test_vpc_lab1.py --deploy --wait-firewall

# Clean up
python setup/test_vpc_lab1.py --teardown
```

See [instructor/AWS_LAB1_SETUP.md](../instructor/AWS_LAB1_SETUP.md) for full usage.
