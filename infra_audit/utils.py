"""Utility functions for infra-audit checks."""

import logging
import subprocess

logger = logging.getLogger(__name__)

PASS = "pass"
WARN = "warn"
FAIL = "fail"


def run_command(args, timeout=30):
    """Run a shell command safely and return stdout, stderr, returncode.

    Args:
        args: List of command arguments (no shell=True to avoid injection).
        timeout: Seconds before the command is killed.

    Returns:
        Tuple of (stdout, stderr, returncode). Returns empty strings and
        returncode -1 if the command is not found or times out.
    """
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.stdout, result.stderr, result.returncode
    except FileNotFoundError:
        logger.debug("Command not found: %s", args[0])
        return "", f"{args[0]}: command not found", -1
    except subprocess.TimeoutExpired:
        logger.warning("Command timed out: %s", " ".join(args))
        return "", "command timed out", -1


def make_result(name, status, message):
    """Create a standardized check result dict.

    Args:
        name: Short name for the check.
        status: One of PASS, WARN, FAIL.
        message: Human-readable description of the finding.

    Returns:
        Dict with keys: name, status, message.
    """
    return {"name": name, "status": status, "message": message}
