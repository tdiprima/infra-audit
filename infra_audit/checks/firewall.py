"""Firewall status checks."""

import logging
import os
import platform
import shutil

from infra_audit.utils import FAIL, PASS, WARN, make_result, run_command

logger = logging.getLogger(__name__)


def check_firewall_status():
    """Check whether a firewall is active on the system."""
    system = platform.system()

    if system == "Linux":
        return _check_linux_firewall()
    if system == "Darwin":
        return _check_macos_firewall()
    return make_result(
        "firewall", WARN, f"Firewall check not supported on {system}"
    )


def _find_command(name, sbin_paths=("/usr/sbin", "/sbin")):
    """Locate a command by name, checking sbin directories and PATH."""
    for sbin in sbin_paths:
        candidate = os.path.join(sbin, name)
        if os.path.isfile(candidate):
            return candidate
    return shutil.which(name)


def _check_linux_firewall():
    """Check Linux firewall via ufw or iptables."""
    ufw = _find_command("ufw")
    if ufw:
        stdout, stderr, rc = run_command([ufw, "status"])
        if rc == 0:
            if "active" in stdout.lower():
                return make_result("firewall", PASS, "Firewall active (ufw)")
            return make_result("firewall", FAIL, "Firewall inactive (ufw)")
        return make_result(
            "firewall", WARN,
            "ufw found but could not query status (try running as root)"
        )

    iptables = _find_command("iptables")
    if iptables:
        stdout, stderr, rc = run_command([iptables, "-L", "-n"])
        if rc == 0:
            rule_lines = [
                line for line in stdout.splitlines()
                if line and not line.startswith("Chain") and not line.startswith("target")
            ]
            if rule_lines:
                return make_result("firewall", PASS, "Firewall rules found (iptables)")
            return make_result("firewall", WARN, "iptables present but no rules configured")
        return make_result(
            "firewall", WARN,
            "iptables found but could not query rules (try running as root)"
        )

    return make_result("firewall", WARN, "No firewall tool found (ufw/iptables)")


def _check_macos_firewall():
    """Check macOS application firewall status."""
    stdout, _, rc = run_command(
        ["/usr/libexec/ApplicationFirewall/socketfilterfw", "--getglobalstate"]
    )
    if rc == 0 and "enabled" in stdout.lower():
        return make_result("firewall", PASS, "Firewall active (macOS)")
    if rc == 0:
        return make_result("firewall", FAIL, "Firewall disabled (macOS)")
    return make_result("firewall", WARN, "Could not determine macOS firewall status")
