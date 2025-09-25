#!/usr/bin/env python3
import socket
import sys

team = sys.argv[1]

OPENFIRE_HOST = f"10.0.{team}.16"   # change to server IP if remote
OPENFIRE_PORT = 5222          # default XMPP port


# Open TCP socket
with socket.create_connection((OPENFIRE_HOST, OPENFIRE_PORT), timeout=5) as sock:
    # Send minimal XMPP opening stream
    xmpp_open = (
        "<?xml version='1.0'?>"
        f"<stream:stream to='{OPENFIRE_HOST}' "
        "xmlns='jabber:client' "
        "xmlns:stream='http://etherx.jabber.org/streams' "
        "version='1.0'>"
    )
    sock.sendall(xmpp_open.encode())

    # Try to read response
    data = sock.recv(1024).decode(errors="ignore")
    if "<stream:stream" in data or "<stream:features" in data:
        exit(0)
    exit(1)
