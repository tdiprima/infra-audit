# 🛡️ Infrastructure Audit CLI ⚙️

![](infra-audit.png)

## Problem

Linux and macOS servers often drift from security best practices over time. Misconfigurations go unnoticed, packages fall behind, and small issues compound into real vulnerabilities.

## Solution

`infra-audit` scans a host and reports security and reliability issues in seconds. It checks SSH configuration, firewall status, Docker security, disk and memory health, zombie processes, exposed secrets, and outdated packages.

## Example Output

```
$ infra-audit scan
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
git clone https://github.com/tdiprima/infra-audit.git
cd infra-audit
uv sync
source .venv/bin/activate
pip install -e .
```

## Usage

Run all checks:

```bash
infra-audit scan
```

Output as JSON for CI/CD pipelines:

```bash
infra-audit scan --json
```

Pipe into `jq` for filtering:

```bash
infra-audit scan --json | jq '.[] | select(.status != "pass")'
```

<br>
