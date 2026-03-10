"""Package freshness checks."""

import logging
import platform

from infra_audit.utils import run_command, make_result, PASS, WARN

logger = logging.getLogger(__name__)


def check_outdated_packages():
    """Check for outdated system packages."""
    system = platform.system()

    if system == "Linux":
        return _check_linux_packages()
    if system == "Darwin":
        return _check_macos_packages()
    return make_result(
        "outdated_packages", WARN,
        f"Package check not supported on {system}"
    )


def _check_linux_packages():
    """Check for upgradable packages via apt or yum."""
    # Try apt first
    stdout, _, rc = run_command(["apt", "list", "--upgradable"], timeout=60)
    if rc == 0:
        upgradable = [
            line for line in stdout.splitlines()
            if "/" in line and "Listing" not in line
        ]
        count = len(upgradable)
        if count == 0:
            return make_result(
                "outdated_packages", PASS, "All packages up to date (apt)"
            )
        return make_result(
            "outdated_packages", WARN,
            f"{count} package(s) outdated (apt)"
        )

    # Try yum
    stdout, _, rc = run_command(
        ["yum", "check-update", "--quiet"], timeout=60
    )
    if rc in (0, 100):
        updates = [
            line for line in stdout.splitlines()
            if line.strip() and not line.startswith("Obsoleting")
        ]
        count = len(updates)
        if count == 0:
            return make_result(
                "outdated_packages", PASS, "All packages up to date (yum)"
            )
        return make_result(
            "outdated_packages", WARN,
            f"{count} package(s) outdated (yum)"
        )

    return make_result(
        "outdated_packages", WARN, "No supported package manager found"
    )


def _check_macos_packages():
    """Check for outdated Homebrew packages."""
    stdout, _, rc = run_command(["brew", "outdated", "--quiet"], timeout=60)
    if rc != 0:
        return make_result(
            "outdated_packages", WARN, "Homebrew not available"
        )
    outdated = [line for line in stdout.splitlines() if line.strip()]
    count = len(outdated)
    if count == 0:
        return make_result(
            "outdated_packages", PASS, "All Homebrew packages up to date"
        )
    return make_result(
        "outdated_packages", WARN,
        f"{count} Homebrew package(s) outdated"
    )
