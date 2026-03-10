"""CLI entry point for infra-audit."""

import json
import logging
import os
import sys

import click

from infra_audit.checks import ALL_CHECKS
from infra_audit.utils import PASS, WARN, FAIL

LOG_LEVEL = os.environ.get("INFRA_AUDIT_LOG_LEVEL", "WARNING").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.WARNING),
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)

STATUS_ICONS = {
    PASS: "\u2714",  # check mark
    WARN: "\u26a0",  # warning sign
    FAIL: "\u2718",  # cross mark
}


@click.group()
@click.version_option(version="0.1.0", prog_name="infra-audit")
def cli():
    """Audit Linux/macOS servers for security and reliability issues."""


@cli.command()
@click.option("--json-output", "--json", "output_json", is_flag=True,
              help="Output results as JSON for CI/CD integration.")
def scan(output_json):
    """Run all audit checks against the current host."""
    results = []
    for check_fn in ALL_CHECKS:
        try:
            result = check_fn()
            results.append(result)
        except Exception as exc:
            logging.getLogger(__name__).error(
                "Check %s failed: %s", check_fn.__name__, exc
            )
            results.append({
                "name": check_fn.__name__,
                "status": WARN,
                "message": f"Check error: {exc}",
            })

    if output_json:
        _print_json(results)
    else:
        _print_human(results)

    has_fail = any(r["status"] == FAIL for r in results)
    sys.exit(1 if has_fail else 0)


def _print_human(results):
    """Print results in human-readable format."""
    for result in results:
        icon = STATUS_ICONS.get(result["status"], "?")
        click.echo(f"{icon} {result['message']}")


def _print_json(results):
    """Print results as JSON."""
    click.echo(json.dumps(results, indent=2))


def main():
    """Entry point called by the console script."""
    cli()


if __name__ == "__main__":
    main()
