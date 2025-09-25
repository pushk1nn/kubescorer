#!/usr/bin/env python3
import mysql.connector  
import sys
import json

team = sys.argv[1]

with open('/tmp/credentials.json', 'r') as f:
    data = json.load(f)

password = data["password"]

cnx = mysql.connector.connect(user='netrunner', password=password,
                              host=f'10.0.{team}.12', connection_timeout=3)

conn_status = cnx.is_connected()
cnx.close()

if conn_status:
    exit(0)
exit(1)