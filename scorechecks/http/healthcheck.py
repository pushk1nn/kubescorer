#!/usr/bin/env python3
import requests
import sys

team = sys.argv[1]

response = requests.get(f"http://10.0.{team}.11", timeout=5)
if response.status_code == 200:
	exit(0)
exit(1)