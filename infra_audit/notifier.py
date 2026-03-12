"""Email notification for infra-audit scan results.

Reads all configuration from environment variables so no secrets are
stored in code or config files.

Required:
    INFRA_AUDIT_EMAIL_TO      Comma-separated recipient list

Optional:
    INFRA_AUDIT_EMAIL_FROM    Sender address (default: infra-audit@<hostname>)
    INFRA_AUDIT_SMTP_HOST     SMTP server   (default: localhost)
    INFRA_AUDIT_SMTP_PORT     SMTP port     (default: 25)
    INFRA_AUDIT_SMTP_USER     SMTP username (default: none)
    INFRA_AUDIT_SMTP_PASSWORD SMTP password (default: none)
    INFRA_AUDIT_SMTP_TLS      Use STARTTLS  (default: false)
"""

import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)


def _count_by_status(results, status):
    return sum(1 for r in results if r["status"] == status)


def _build_body(results):
    """Build a plain-text report body from scan results."""
    lines = ["Infrastructure Audit Report", "=" * 40, ""]
    for r in results:
        lines.append(f"[{r['status'].upper():4s}] {r['name']}: {r['message']}")
    lines.append("")
    lines.append(
        f"Summary: {_count_by_status(results, 'pass')} pass  "
        f"{_count_by_status(results, 'warn')} warn  "
        f"{_count_by_status(results, 'fail')} fail"
    )
    return "\n".join(lines)


def send_report(results, hostname):
    """Send the audit report via SMTP if INFRA_AUDIT_EMAIL_TO is set.

    Does nothing (and does not raise) if the env var is absent.
    Raises on SMTP errors so the caller can log and handle them.
    """
    to_addr = os.environ.get("INFRA_AUDIT_EMAIL_TO", "").strip()
    if not to_addr:
        logger.debug("INFRA_AUDIT_EMAIL_TO not set; skipping email.")
        return

    from_addr = os.environ.get("INFRA_AUDIT_EMAIL_FROM", f"infra-audit@{hostname}")
    smtp_host = os.environ.get("INFRA_AUDIT_SMTP_HOST", "localhost")
    smtp_port = int(os.environ.get("INFRA_AUDIT_SMTP_PORT", "25"))
    smtp_user = os.environ.get("INFRA_AUDIT_SMTP_USER", "")
    smtp_password = os.environ.get("INFRA_AUDIT_SMTP_PASSWORD", "")
    use_tls = os.environ.get("INFRA_AUDIT_SMTP_TLS", "false").lower() == "true"

    fail_count = _count_by_status(results, "fail")
    warn_count = _count_by_status(results, "warn")
    subject = f"[infra-audit] {hostname} — {fail_count} FAIL, {warn_count} WARN"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg.attach(MIMEText(_build_body(results), "plain"))

    recipients = [addr.strip() for addr in to_addr.split(",")]

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
            server.ehlo()
            if use_tls:
                server.starttls()
                server.ehlo()
            if smtp_user and smtp_password:
                server.login(smtp_user, smtp_password)
            server.sendmail(from_addr, recipients, msg.as_string())
        logger.info(
            "Audit report emailed",
            extra={"event": "email_sent", "recipients": to_addr, "host": hostname},
        )
    except smtplib.SMTPException as exc:
        logger.error(
            "Failed to send audit report email: %s",
            exc,
            extra={"event": "email_failed", "host": hostname},
        )
        raise
