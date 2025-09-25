#!/usr/bin/env python3
import socket
import sys

team = sys.argv[1]

WINRM_HOST = f"10.0.{team}.15"
WINRM_PORT = 5985

# Open TCP socket
with socket.create_connection((WINRM_HOST, WINRM_PORT), timeout=5) as sock:
    # Minimal HTTP request to WinRM service
    http_req = (
        "POST /wsman HTTP/1.1\r\n"
        f"Host: {WINRM_HOST}\r\n"
        "Content-Length: 0\r\n"
        "Connection: Close\r\n"
        "\r\n"
    )
    sock.sendall(http_req.encode())

    # Read response
    data = sock.recv(1024).decode(errors="ignore")
    if "HTTP/1.1 401" in data and "WWW-Authenticate" in data:
        exit(0)  # success, WinRM is alive
    exit(1)
