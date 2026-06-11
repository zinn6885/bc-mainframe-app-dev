# EC2 Setup Screenshots — Lab 2 & Lab 3

Reference screenshots for launching and connecting to the training EC2 instance using the **AWS Console** and **EC2 Instance Connect** (browser terminal).

> **Excluded from this set:** Windows PowerShell SSH setup, WSL setup, Winsock/DNS troubleshooting, and local PEM key permission fixes. Participants should use **EC2 Instance Connect** instead of local SSH.

---

## Screenshot manifest (8 files)

Place restored or re-captured images in this folder using these exact names:

| # | Filename | AWS step |
|---|----------|----------|
| 1 | `Lab02_Step_0.1_Launch_EC2_Name_and_AMI.png` | EC2 → Launch instance → name + Amazon Linux 2023 AMI |
| 2 | `Lab02_Step_0.2_Launch_EC2_Instance_Type_and_Key.png` | Instance type (e.g. `t3.micro`) + create/download key pair |
| 3 | `Lab02_Step_0.3_Launch_EC2_Network_and_Storage.png` | VPC/subnet defaults + 8–20 GB gp3 root volume |
| 4 | `Lab02_Step_0.4_Launch_EC2_Review_and_Launch.png` | Review summary → **Launch instance** |
| 5 | `Lab02_Step_0.5_EC2_Instance_Running.png` | Instances list — state **Running**, status checks **2/2** |
| 6 | `Lab02_Step_0.6_Edit_Security_Group_Outbound.png` | Security group — allow outbound HTTPS (for Atlas + pip) |
| 7 | `Lab02_Step_0.7_EC2_Instance_Connect_Button.png` | Instance selected → **Connect** → **EC2 Instance Connect** tab |
| 8 | `Lab02_Step_0.8_EC2_Instance_Connect_Terminal.png` | Browser terminal open as `ec2-user@…` |

---

## Original filenames (before rename)

These were captured on **2026-06-08** in **us-east-1** and renamed in the parent `Lab Screenshots` folder. They were removed during lab cleanup and must be **re-captured or restored from backup**:

| Restored name (use above) | Original capture file |
|---------------------------|------------------------|
| `Lab02_Step_0.1_Launch_EC2_Name_and_AMI.png` | `screencapture-us-east-1-console-aws-amazon-ec2-home-2026-06-08-21_41_45.png` |
| `Lab02_Step_0.2_Launch_EC2_Instance_Type_and_Key.png` | `screencapture-us-east-1-console-aws-amazon-ec2-home-2026-06-08-23_22_55.png` |
| `Lab02_Step_0.3_Launch_EC2_Network_and_Storage.png` | `screencapture-us-east-1-console-aws-amazon-ec2-home-2026-06-08-21_44_12.png` |
| `Lab02_Step_0.4_Launch_EC2_Review_and_Launch.png` | `Screenshot 2026-06-08 214515.png` |
| `Lab02_Step_0.5_EC2_Instance_Running.png` | `screencapture-us-east-1-console-aws-amazon-ec2-home-2026-06-08-21_45_47.png` |
| `Lab02_Step_0.6_Edit_Security_Group_Outbound.png` | `screencapture-us-east-1-console-aws-amazon-ec2-home-2026-06-08-23_02_25.png` |
| `Lab02_Step_0.7_EC2_Instance_Connect_Button.png` | `Lab02_Step_1.1_Launch_EC2_Training_Lab.png` (renamed) |
| `Lab02_Step_0.8_EC2_Instance_Connect_Terminal.png` | `Screenshot 2026-06-08 232856.png` |

---

## Intentionally excluded (do not restore)

| Filename | Reason |
|----------|--------|
| `Lab02_Step_1.1_Fix_SSH_Key_Permissions_Windows.png` | Local Windows SSH — not used |
| `Lab02_Step_1.1_WSL_Environment_Setup.png` | WSL — not used |
| `Lab02_Step_1.1_SSH_Connect_Attempt_WSL.png` | WSL SSH — not used |
| `Lab02_Step_1.1_WSL_Network_Troubleshooting.png` | WSL network debug — not used |
| `Lab02_Step_1.1_Reset_Winsock_IP_Stack.png` | Windows network fix — not used |
| `Lab02_Step_1.1_Flush_DNS_Check_HyperV.png` | Windows network fix — not used |
| `Lab02_Step_1.1_Verify_SSH_Key_PEM.png` | Local PEM key — optional; Instance Connect preferred |

---

## Quick restore check

```bash
ls "Lab Screenshots/EC2_Setup"/Lab02_Step_0.*.png | wc -l
# Expected: 8
```
