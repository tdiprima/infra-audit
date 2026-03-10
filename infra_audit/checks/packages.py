"""Package freshness checks."""

import logging
import platform
import shutil
from pathlib import Path

from infra_audit.utils import PASS, WARN, make_result, run_command

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
    """Check for upgradable packages via the host's package manager."""
    manager = _detect_linux_package_manager()
    if manager == "apt":
        return _check_apt_packages()
    if manager == "dnf":
        return _check_dnf_packages()
    if manager == "yum":
        return _check_yum_packages()

    return make_result(
        "outdated_packages", WARN, "No supported package manager found"
    )


def _check_apt_packages():
    """Check for upgradable packages via apt."""
    stdout, _, rc = run_command(["apt", "list", "--upgradable"], timeout=60)
    if rc == 0:
        upgradable = [
            line for line in stdout.splitlines()
            if line.strip() and "[upgradable" in line.lower()
        ]
        count = len(upgradable)
        if count > 0:
            names = [line.split("/")[0] for line in upgradable]
            logger.info("Outdated packages: %s", ", ".join(names))
        if count == 0:
            return make_result(
                "outdated_packages", PASS, "All packages up to date (apt)"
            )
        return make_result(
            "outdated_packages", WARN,
            f"{count} package(s) outdated (apt)"
        )
    return make_result(
        "outdated_packages", WARN, "Unable to check updates (apt)"
    )


def _check_dnf_packages():
    """Check for upgradable packages via dnf."""
    stdout, _, rc = run_command(["dnf", "check-update", "--quiet"], timeout=60)
    if rc in (0, 100):
        updates = [
            line for line in stdout.splitlines()
            if line.strip() and not line.startswith("Obsoleting")
        ]
        count = len(updates)
        if count == 0:
            return make_result(
                "outdated_packages", PASS, "All packages up to date (dnf)"
            )
        return make_result(
            "outdated_packages", WARN,
            f"{count} package(s) outdated (dnf)"
        )
    return make_result(
        "outdated_packages", WARN, "Unable to check updates (dnf)"
    )


def _check_yum_packages():
    """Check for upgradable packages via yum."""
    stdout, _, rc = run_command(["yum", "check-update", "--quiet"], timeout=60)
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
        "outdated_packages", WARN, "Unable to check updates (yum)"
    )


def _detect_linux_package_manager():
    """Detect the most likely package manager for this Linux host."""
    has_apt = shutil.which("apt") is not None
    has_dnf = shutil.which("dnf") is not None
    has_yum = shutil.which("yum") is not None

    os_ids = _read_os_release_ids()

    # Strong distro markers first.
    if Path("/etc/debian_version").exists():
        if has_apt:
            return "apt"
    if Path("/etc/redhat-release").exists():
        if has_dnf:
            return "dnf"
        if has_yum:
            return "yum"

    debian_like = {"debian", "ubuntu", "linuxmint", "pop", "kali"}
    rhel_like = {
        "rhel", "fedora", "centos", "rocky", "almalinux",
        "ol", "amzn",
    }

    if os_ids.intersection(debian_like):
        if has_apt:
            return "apt"
    if os_ids.intersection(rhel_like):
        if has_dnf:
            return "dnf"
        if has_yum:
            return "yum"

    # Generic fallback if distro hints are missing.
    if has_apt:
        return "apt"
    if has_dnf:
        return "dnf"
    if has_yum:
        return "yum"

    return None


def _read_os_release_ids():
    """Read ID and ID_LIKE values from /etc/os-release."""
    ids = set()
    try:
        with open("/etc/os-release", "r", encoding="utf-8") as fh:
            for raw_line in fh:
                line = raw_line.strip()
                if line.startswith("ID="):
                    ids.add(line.split("=", 1)[1].strip().strip('"').lower())
                elif line.startswith("ID_LIKE="):
                    values = line.split("=", 1)[1].strip().strip('"').lower()
                    ids.update(values.split())
    except OSError:
        return ids
    return ids


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
