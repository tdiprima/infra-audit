<!-- # Infrastructure Audit CLI -->

![](infra-audit.png)

## Problem

Linux and macOS servers often drift from security best practices over time. Misconfigurations go unnoticed, packages fall behind, and small issues compound into real vulnerabilities.

## Solution

`infra-audit` scans a host and reports security and reliability issues in seconds. It checks SSH configuration, firewall status, Docker security, disk and memory health, zombie processes, exposed secrets, and outdated packages.

## Example Output

```
$ infra_audit scan
✔ SSH root login disabled
✔ SSH password authentication disabled
✔ Firewall active (ufw)
⚠ 5 listening TCP port(s) detected
✔ Disk usage normal: 35%
✔ Memory usage normal: 54%
✔ No zombie processes
⚠ systemctl not available (non-systemd host)
✔ Docker socket permissions OK
✔ No Docker daemon.json found
✔ No .env files found in common web directories
⚠ 3 package(s) outdated (apt)
```

## Installation

```bash
git clone https://github.com/your-username/infra-audit.git
cd infra-audit
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Usage

Run all checks:

```bash
sudo infra_audit scan
```

Output as JSON for CI/CD pipelines:

```bash
sudo infra_audit scan --json
```

Pipe into `jq` for filtering:

```bash
sudo infra_audit scan --json | jq '.[] | select(.status != "pass")'
```

## Email Reports

Set environment variables to have the scan result emailed after each run:

| Variable | Required | Description |
|---|---|---|
| `INFRA_AUDIT_EMAIL_TO` | Yes | Recipient(s), comma-separated |
| `INFRA_AUDIT_EMAIL_FROM` | No | Sender address (default: `infra-audit@<hostname>`) |
| `INFRA_AUDIT_SMTP_HOST` | No | SMTP server (default: `localhost`) |
| `INFRA_AUDIT_SMTP_PORT` | No | SMTP port (default: `25`) |
| `INFRA_AUDIT_SMTP_USER` | No | SMTP username |
| `INFRA_AUDIT_SMTP_PASSWORD` | No | SMTP password |
| `INFRA_AUDIT_SMTP_TLS` | No | Enable STARTTLS: `true`/`false` (default: `false`) |

Example using Gmail (with an [App Password](https://myaccount.google.com/apppasswords)):

```bash
export INFRA_AUDIT_EMAIL_TO=you@example.com
export INFRA_AUDIT_SMTP_HOST=smtp.gmail.com
export INFRA_AUDIT_SMTP_PORT=587
export INFRA_AUDIT_SMTP_TLS=true
export INFRA_AUDIT_SMTP_USER=you@gmail.com
export INFRA_AUDIT_SMTP_PASSWORD=your-app-password
sudo -E infra_audit scan
```

## Scheduled Monthly Reports (cron)

**1. Store secrets in a protected env file:**

```bash
sudo nano /etc/infra-audit.env   # add the INFRA_AUDIT_* vars above
sudo chmod 600 /etc/infra-audit.env
```

**2. Add a cron entry** (`sudo crontab -e` or `/etc/cron.d/infra-audit`):

```cron
# Run at 06:00 on the 1st of every month
0 6 1 * *  root  set -a && . /etc/infra-audit.env && set +a && /path/to/infra-audit/run.sh
```

**3. Allow passwordless sudo for the venv Python binary** (`sudo visudo`):

```
your-user ALL=(ALL) NOPASSWD: /path/to/infra-audit/.venv/bin/python
```

**4. Test before relying on it:**

```bash
sudo env -i $(cat /etc/infra-audit.env | xargs) /path/to/infra-audit/run.sh
```

## Logging

Set `INFRA_AUDIT_LOG_FILE` to append all output to a file:

```bash
export INFRA_AUDIT_LOG_FILE=/var/log/infra-audit.log
```

Set `INFRA_AUDIT_LOG_LEVEL` to control verbosity (`DEBUG`, `INFO`, `WARNING`):

```bash
export INFRA_AUDIT_LOG_LEVEL=INFO
```

<br>
