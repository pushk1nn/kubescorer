#!/usr/bin/env python3
import requests
import json
import sys

url = ""

try:
    team = sys.argv[1]
    # with open("/tmp/credentials.json", "r") as f:
    #     creds = json.loads(f.read())
    #     url = creds.get("username")
except:
    exit(1)
 
response = requests.get(f"http://100.65.{team}.213", timeout=5)

if response.status_code == 200:
    exit(0)
exit(1)