"""System health checks: disk, memory, zombies, failed services."""

import logging
import shutil
from contextlib import suppress

from infra_audit.utils import FAIL, PASS, WARN, make_result, run_command

logger = logging.getLogger(__name__)

DISK_WARN_PERCENT = 80
DISK_FAIL_PERCENT = 90
MEM_WARN_PERCENT = 85
MEM_FAIL_PERCENT = 95


def check_disk_usage():
    """Check root partition disk usage."""
    total, used, _free = shutil.disk_usage("/")
    percent = (used / total) * 100

    if percent >= DISK_FAIL_PERCENT:
        return make_result(
            "disk_usage", FAIL,
            f"Disk usage critical: {percent:.0f}%"
        )
    if percent >= DISK_WARN_PERCENT:
        return make_result(
            "disk_usage", WARN,
            f"Disk usage high: {percent:.0f}%"
        )
    return make_result(
        "disk_usage", PASS,
        f"Disk usage normal: {percent:.0f}%"
    )


def check_memory_usage():
    """Check system memory usage."""
    stdout, _, rc = run_command(["free", "-m"])
    if rc == 0:
        return _parse_free_output(stdout)

    # macOS fallback
    stdout, _, rc = run_command(["vm_stat"])
    if rc == 0:
        return _parse_vm_stat(stdout)

    return make_result("memory_usage", WARN, "Cannot determine memory usage")


def _parse_free_output(stdout):
    """Parse Linux 'free -m' output."""
    for line in stdout.splitlines():
        if line.lower().startswith("mem:"):
            parts = line.split()
            if len(parts) >= 3:
                total = int(parts[1])
                used = int(parts[2])
                if total > 0:
                    percent = (used / total) * 100
                    return _memory_result(percent)
    return make_result("memory_usage", WARN, "Could not parse memory info")


def _parse_vm_stat(stdout):
    """Parse macOS 'vm_stat' output to estimate memory usage."""
    # page_size = 16384  # default on Apple Silicon; 4096 on Intel
    stats = {}
    for line in stdout.splitlines():
        if "page size of" in line:
            with suppress(ValueError, IndexError):
                int(line.split()[-2])
        elif ":" in line:
            key, _, val = line.partition(":")
            try:
                stats[key.strip()] = int(val.strip().rstrip("."))
            except ValueError:
                continue

    free_pages = stats.get("Pages free", 0)
    active = stats.get("Pages active", 0)
    inactive = stats.get("Pages inactive", 0)
    speculative = stats.get("Pages speculative", 0)
    wired = stats.get("Pages wired down", 0)

    total = free_pages + active + inactive + speculative + wired
    used = active + wired
    if total > 0:
        percent = (used / total) * 100
        return _memory_result(percent)
    return make_result("memory_usage", WARN, "Could not parse vm_stat")


def _memory_result(percent):
    """Return a result based on memory usage percentage."""
    if percent >= MEM_FAIL_PERCENT:
        return make_result(
            "memory_usage", FAIL,
            f"Memory usage critical: {percent:.0f}%"
        )
    if percent >= MEM_WARN_PERCENT:
        return make_result(
            "memory_usage", WARN,
            f"Memory usage high: {percent:.0f}%"
        )
    return make_result(
        "memory_usage", PASS,
        f"Memory usage normal: {percent:.0f}%"
    )


def check_zombie_processes():
    """Check for zombie processes."""
    stdout, _, rc = run_command(["ps", "aux"])
    if rc != 0:
        return make_result("zombie_processes", WARN, "Cannot list processes")

    zombies = [
        line for line in stdout.splitlines()
        if len(line.split()) > 7 and line.split()[7] == "Z"
    ]
    count = len(zombies)
    if count == 0:
        return make_result("zombie_processes", PASS, "No zombie processes")
    return make_result(
        "zombie_processes", WARN,
        f"{count} zombie process(es) found"
    )


def check_service_failures():
    """Check for failed systemd services."""
    # sudo systemctl --failed --no-pager --no-legend
    stdout, _, rc = run_command(["systemctl", "--failed", "--no-pager", "--no-legend"])
    if rc != 0:
        return make_result(
            "service_failures", WARN,
            "systemctl not available (non-systemd host)"
        )
    failed = [line for line in stdout.splitlines() if line.strip()]
    count = len(failed)
    if count == 0:
        return make_result("service_failures", PASS, "No failed services")
    return make_result(
        "service_failures", FAIL,
        f"{count} failed service(s)"
    )
