#!/usr/bin/env python3
import requests
import json

url = ""

try:
    with open("/tmp/credentials.json", "r") as f:
        creds = json.loads(f.read())
        url = creds.get("username")
except:
    exit(1)
 
response = requests.get(f"https://{url}.com", timeout=5)

if response.status_code == 200:
    exit(0)
exit(1)