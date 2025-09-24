#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2020 Google LLC
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     https://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import http.server
import os
import urllib.parse
import json

CRED_FILE = "/tmp/credentials.json"

class HealthzHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # Get auth url
        if self.path == '/auth':
            # show form
            html = b"""
            <html><body>
                <h2>Update Credentials</h2>
                <form method="POST" action="/auth">
                    Username: <input type="text" name="username"><br>
                    Password: <input type="password" name="password"><br>
                    <input type="submit" value="Submit">
                </form>
            </body></html>
            """
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.send_header("Content-length", str(len(html)))
            self.end_headers()
            self.wfile.write(html)
            return
        
        # Get health of healthcheck
        if self.path != '/healthz':
            self.send_response(404)
            self.send_header("Content-length", "0")
            self.end_headers()
            return

        content = b'err'
        try:
            with open('/tmp/healthz', 'rb') as fd:
                content = fd.read().strip()
        except:
            pass
        self.send_response(200 if content == b'ok' else 400)
        self.send_header("Content-type", "text/plain")
        self.send_header("Content-length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

        # Return credentials for healthcheck
        if self.path == '/creds':
            # return current credentials as JSON (for debugging / healthcheck.py)
            if os.path.exists(CRED_FILE):
                with open(CRED_FILE, "r") as f:
                    creds = f.read().encode()
            else:
                creds = b'{}'
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Content-length", str(len(creds)))
            self.end_headers()
            self.wfile.write(creds)
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        if self.path == '/auth':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length).decode()
            data = urllib.parse.parse_qs(body)

            # username = data.get("username", [""])[0]
            password = data.get("password", [""])[0]

            # store creds in JSON file
            with open(CRED_FILE, "w") as f:
                json.dump({"password": password}, f)

            response = f"Stored credentials!".encode()
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.send_header("Content-length", str(len(response)))
            self.end_headers()
            self.wfile.write(response)
            return

        self.send_response(404)
        self.end_headers()

httpd = http.server.HTTPServer(('', 45281), HealthzHandler)
httpd.serve_forever()
