#!/usr/bin/env python3
import requests
import sys

team = sys.argv[1]

url = f"http://10.0.{team}.13:31134"  # simple endpoint that lists models
try:
    r = requests.get(url, timeout=3)
    if r.status_code == 200:
        # print("Ollama is running ✅")
        exit(0)
    else:
        # print(f"Ollama responded with status {r.status_code} ❌")
        exit(1)
except requests.exceptions.RequestException as e:
    # print(f"Ollama is not running ❌: {e}")
    exit(1)

