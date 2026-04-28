#!/usr/bin/env python3
"""
Bulk personalized email sender using Gmail app password.

Safety note: Use only with recipients who opted in to receive your emails.
"""

from __future__ import annotations

import argparse
import csv
import random
import smtplib
import ssl
import time
from dataclasses import dataclass
from email.message import EmailMessage
from pathlib import Path
from typing import Iterable


TEMPLATE_VARIANTS = [
    (
        "Creator Support for Your Content",
        """Hello {name}, good morning,

We are the Sarkvission marketing team. If you're a creator, we're here to support your growth.

We can help with:
- Video editing
- Script support
- Thumbnail design
- Logo design

Portfolio / Site:
https://thesarkvission.web.app/

Thanks,
Sarkvission Team
""",
    ),
    (
        "We Can Help You Grow Your Creator Brand",
        """Hello {name},

Good morning! We are from Sarkvission's marketing team.

If you are a content creator, we'd love to help you with creative services like editing, scripting, thumbnail design, and logo design.

Take a quick look here:
https://thesarkvission.web.app/

Thank you,
Sarkvission Team
""",
    ),
    (
        "Support Services for Creators",
        """Hi {name},

Hope you're doing great. We're Sarkvission marketing team, and we help creators with quality content support.

Our services include editing, script writing support, thumbnail design, and logo design.

Website:
https://thesarkvission.web.app/

Regards,
Sarkvission Team
""",
    ),
]


@dataclass
class Recipient:
    email: str
    name: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send personalized bulk emails.")
    parser.add_argument("--sender-email", required=True, help="Your Gmail address.")
    parser.add_argument("--app-password", required=True, help="Gmail app password.")
    parser.add_argument(
        "--recipients-csv",
        required=True,
        type=Path,
        help="CSV with headers: email,name",
    )
    parser.add_argument(
        "--delay-seconds",
        type=float,
        default=2.0,
        help="Delay between emails to avoid hitting provider limits.",
    )
    parser.add_argument(
        "--smtp-host", default="smtp.gmail.com", help="SMTP host (default Gmail)."
    )
    parser.add_argument("--smtp-port", type=int, default=465, help="SMTP SSL port")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview messages without sending emails.",
    )
    return parser.parse_args()


def load_recipients(csv_path: Path) -> list[Recipient]:
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    recipients: list[Recipient] = []
    with csv_path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        required_cols = {"email", "name"}
        if not reader.fieldnames or not required_cols.issubset(set(reader.fieldnames)):
            raise ValueError("CSV must contain headers: email,name")

        for row in reader:
            email = (row.get("email") or "").strip()
            name = (row.get("name") or "").strip() or "there"
            if not email:
                continue
            recipients.append(Recipient(email=email, name=name))

    if not recipients:
        raise ValueError("No valid recipients found in CSV.")
    return recipients


def build_message(sender_email: str, recipient: Recipient, variant_idx: int) -> EmailMessage:
    subject, template = TEMPLATE_VARIANTS[variant_idx]

    msg = EmailMessage()
    msg["From"] = sender_email
    msg["To"] = recipient.email
    msg["Subject"] = subject
    msg.set_content(template.format(name=recipient.name))
    return msg


def choose_variants(count: int) -> Iterable[int]:
    for i in range(count):
        yield i % len(TEMPLATE_VARIANTS)


def send_bulk_emails(
    sender_email: str,
    app_password: str,
    recipients: list[Recipient],
    smtp_host: str,
    smtp_port: int,
    delay_seconds: float,
    dry_run: bool,
) -> None:
    variants = list(choose_variants(len(recipients)))
    random.shuffle(variants)

    if dry_run:
        print("[DRY RUN] No email will be sent. Previewing generated messages:\n")
        for recipient, variant_idx in zip(recipients, variants, strict=True):
            msg = build_message(sender_email, recipient, variant_idx)
            print(f"To: {recipient.email} | Subject: {msg['Subject']}")
            print(msg.get_content())
            print("-" * 60)
        return

    context = ssl.create_default_context()
    sent = 0
    with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context) as smtp:
        smtp.login(sender_email, app_password)
        for recipient, variant_idx in zip(recipients, variants, strict=True):
            msg = build_message(sender_email, recipient, variant_idx)
            smtp.send_message(msg)
            sent += 1
            print(f"[{sent}/{len(recipients)}] Sent to {recipient.email}")
            time.sleep(delay_seconds)

    print(f"\nDone: sent {sent} emails.")


def main() -> None:
    args = parse_args()
    recipients = load_recipients(args.recipients_csv)
    send_bulk_emails(
        sender_email=args.sender_email,
        app_password=args.app_password,
        recipients=recipients,
        smtp_host=args.smtp_host,
        smtp_port=args.smtp_port,
        delay_seconds=args.delay_seconds,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
