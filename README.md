# Email Sending Tool

Python script to send personalized bulk emails using a Gmail app password.

> Use this only for recipients who have given permission (opt-in).

## Features
- Send to any number of contacts from CSV (`email,name`)
- Personalized greeting using recipient name
- Multiple template variants (different tone/wording)
- Delay between sends to reduce SMTP throttling risk

## Setup
1. Install Python 3.10+
2. Create Gmail app password:
   - Google Account -> Security -> 2-Step Verification -> App passwords
3. Create recipients CSV using this format:

```csv
email,name
creator1@example.com,Rahul
creator2@example.com,Priya
```

You can copy `recipients.sample.csv`.

## Usage
```bash
python3 sender.py \
  --sender-email yourmail@gmail.com \
  --app-password "xxxx xxxx xxxx xxxx" \
  --recipients-csv recipients.sample.csv \
  --delay-seconds 2
```

## CSV columns
- `email` (required)
- `name` (optional; fallback: `there`)

## Run tests
```bash
python3 -m unittest discover -s tests -v
```

## Notes
- Gmail has daily sending limits; keep volume reasonable.
- If you need advanced tracking/unsubscribe handling, use a proper email provider (SES, SendGrid, Mailgun, etc.).
