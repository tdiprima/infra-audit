#!/bin/bash
# infra-audit runner — safe for interactive use and cron.
#
# Environment variables:
#   INFRA_AUDIT_LOG_FILE   Path to append log output (default: no file, stdout only)
#   INFRA_AUDIT_EMAIL_TO   Recipient(s) — if set, Python will email the report
#
# All other INFRA_AUDIT_* vars are passed through to the Python CLI.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="$SCRIPT_DIR/.venv/bin/python"
TIMESTAMP="$(date '+%Y-%m-%d %H:%M:%S')"

log() {
    local msg="[$TIMESTAMP] $*"
    echo "$msg"
    if [[ -n "${INFRA_AUDIT_LOG_FILE:-}" ]]; then
        echo "$msg" >> "$INFRA_AUDIT_LOG_FILE"
    fi
}

if [[ ! -x "$PYTHON" ]]; then
    echo "ERROR: virtualenv not found at $SCRIPT_DIR/.venv — run: python3 -m venv .venv && pip install -e ." >&2
    exit 2
fi

log "Starting infra-audit scan on $(hostname)"

# Capture output so we can log it and still let it flow to stdout/cron's mailer.
if [[ -n "${INFRA_AUDIT_LOG_FILE:-}" ]]; then
    sudo -E "$PYTHON" -m infra_audit.cli scan 2>&1 | tee -a "$INFRA_AUDIT_LOG_FILE"
    EXIT_CODE="${PIPESTATUS[0]}"
else
    sudo -E "$PYTHON" -m infra_audit.cli scan
    EXIT_CODE=$?
fi

log "Scan complete (exit code: $EXIT_CODE)"
exit "$EXIT_CODE"
