"""SSH security checks."""

import logging
import os

from infra_audit.utils import make_result, PASS, WARN, FAIL

logger = logging.getLogger(__name__)

SSHD_CONFIG = "/etc/ssh/sshd_config"


def _read_sshd_config():
    """Read sshd_config and return its contents, or None if unreadable."""
    if not os.path.isfile(SSHD_CONFIG):
        return None
    try:
        with open(SSHD_CONFIG, "r") as fh:
            return fh.read()
    except PermissionError:
        logger.warning("Cannot read %s (permission denied)", SSHD_CONFIG)
        return None


def _find_directive(config_text, directive):
    """Return the last uncommented value for a given sshd directive."""
    value = None
    for line in config_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#") or not stripped:
            continue
        parts = stripped.split()
        if len(parts) >= 2 and parts[0].lower() == directive.lower():
            value = parts[1].lower()
    return value


def check_ssh_root_login():
    """Check whether SSH root login is disabled."""
    config = _read_sshd_config()
    if config is None:
        return make_result(
            "ssh_root_login", WARN, "Cannot read sshd_config"
        )

    value = _find_directive(config, "PermitRootLogin")
    if value in (None, "prohibit-password", "no"):
        return make_result(
            "ssh_root_login", PASS, "SSH root login disabled"
        )
    return make_result(
        "ssh_root_login", FAIL, f"SSH root login is set to '{value}'"
    )


def check_ssh_password_auth():
    """Check whether SSH password authentication is disabled."""
    config = _read_sshd_config()
    if config is None:
        return make_result(
            "ssh_password_auth", WARN, "Cannot read sshd_config"
        )

    value = _find_directive(config, "PasswordAuthentication")
    if value == "no":
        return make_result(
            "ssh_password_auth", PASS, "SSH password authentication disabled"
        )
    status = FAIL if value == "yes" else WARN
    display = value if value else "not set (defaults vary)"
    return make_result(
        "ssh_password_auth", status,
        f"SSH password authentication: {display}"
    )
