"""Firewall status checks."""

import logging
import platform

from infra_audit.utils import run_command, make_result, PASS, WARN, FAIL

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


def _check_linux_firewall():
    """Check Linux firewall via ufw or iptables."""
    stdout, _, rc = run_command(["ufw", "status"])
    if rc == 0:
        if "active" in stdout.lower():
            return make_result("firewall", PASS, "Firewall active (ufw)")
        return make_result("firewall", FAIL, "Firewall inactive (ufw)")

    stdout, _, rc = run_command(["iptables", "-L", "-n"])
    if rc == 0:
        rule_lines = [
            line for line in stdout.splitlines()
            if line and not line.startswith("Chain") and not line.startswith("target")
        ]
        if rule_lines:
            return make_result("firewall", PASS, "Firewall rules found (iptables)")
        return make_result("firewall", WARN, "iptables present but no rules configured")

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
