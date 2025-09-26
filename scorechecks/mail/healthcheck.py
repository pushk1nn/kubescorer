#!/usr/bin/env python3
import sys
from smtplib import SMTP

team = sys.argv[1]

host = f"10.0.{team}.17"

with SMTP(host) as smtp:
    smtp.noop()
    exit(0)
exit(1)