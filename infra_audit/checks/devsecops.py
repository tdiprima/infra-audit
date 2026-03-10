"""DevSecOps checks: exposed .env files, open ports."""

import logging
import os
import platform

from infra_audit.utils import PASS, WARN, make_result, run_command

logger = logging.getLogger(__name__)

COMMON_WEB_DIRS = [
    "/var/www",
    "/srv",
    "/opt",
]


def check_exposed_env_files():
    """Look for .env files in common web-serving directories."""
    found = []
    for base_dir in COMMON_WEB_DIRS:
        if not os.path.isdir(base_dir):
            continue
        for root, _dirs, files in os.walk(base_dir):
            for fname in files:
                if fname == ".env":
                    found.append(os.path.join(root, fname))

    if not found:
        return make_result(
            "exposed_env_files", PASS,
            "No .env files found in common web directories"
        )
    return make_result(
        "exposed_env_files", WARN,
        f"Found {len(found)} exposed .env file(s): {', '.join(found[:5])}"
    )


def check_open_ports():
    """List listening TCP ports and flag unexpected ones."""
    system = platform.system()

    if system == "Linux":
        stdout, _, rc = run_command(["ss", "-tlnp"])
    elif system == "Darwin":
        # lsof -iTCP -sTCP:LISTEN -nP
        stdout, _, rc = run_command(["lsof", "-iTCP", "-sTCP:LISTEN", "-nP"])
    else:
        return make_result(
            "open_ports", WARN,
            f"Open port check not supported on {system}"
        )

    if rc != 0:
        return make_result("open_ports", WARN, "Cannot list listening ports")

    # Count listening entries (skip header)
    lines = [line for line in stdout.splitlines()[1:] if line.strip()]
    count = len(lines)

    if count == 0:
        return make_result("open_ports", PASS, "No listening TCP ports found")
    return make_result(
        "open_ports", WARN,
        f"{count} listening TCP port(s) detected"
    )
