"""Docker security checks."""

import json
import logging
from pathlib import Path

from infra_audit.utils import PASS, WARN, make_result

logger = logging.getLogger(__name__)

DOCKER_SOCKET = "/var/run/docker.sock"


def check_docker_socket():
    """Check if the Docker socket is world-readable/writable."""
    if not Path(DOCKER_SOCKET).exists():
        return make_result("docker_socket", PASS, "Docker socket not present")

    try:
        stat = Path(DOCKER_SOCKET).stat()
        mode = stat.st_mode
        # Check if 'other' has read or write permissions
        other_rw = mode & 0o006
        if other_rw:
            return make_result(
                "docker_socket", WARN,
                "Docker socket is world-accessible"
            )
        return make_result("docker_socket", PASS, "Docker socket permissions OK")
    except PermissionError:
        return make_result(
            "docker_socket", WARN,
            "Cannot stat Docker socket (permission denied)"
        )


def check_docker_configs():
    """Check for insecure Docker daemon configuration."""
    daemon_json = "/etc/docker/daemon.json"
    if not Path(daemon_json).is_file():
        return make_result(
            "docker_config", PASS, "No Docker daemon.json found"
        )

    try:
        with open(daemon_json, "r") as fh:
            config = json.load(fh)
    except (PermissionError, json.JSONDecodeError) as exc:
        return make_result(
            "docker_config", WARN,
            f"Cannot parse Docker daemon.json: {exc}"
        )

    issues = []
    if config.get("icc", True) is True:
        issues.append("inter-container communication enabled")
    if config.get("userland-proxy", True) is True:
        issues.append("userland-proxy enabled")
    if not config.get("no-new-privileges", False):
        issues.append("no-new-privileges not set")

    if issues:
        return make_result(
            "docker_config", WARN,
            f"Docker config issues: {'; '.join(issues)}"
        )
    return make_result("docker_config", PASS, "Docker daemon config looks good")
