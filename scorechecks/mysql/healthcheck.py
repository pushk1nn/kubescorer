#!/usr/bin/env python3
import mysql.connector  
import sys

team = sys.argv[1]

cnx = mysql.connector.connect(user='netrunner', password='ChangeMe123!',
                              host=f'10.0.{team}.12', connection_timeout=3)

conn_status = cnx.is_connected()
cnx.close()

if conn_status:
    exit(0)
exit(1)