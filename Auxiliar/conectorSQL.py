# -*- coding: utf-8 -*-
import pyodbc 

server = 'fernandogasparjr.ddns.net,4713\\SQLSERVER'
db1 = 'TurboBet'
uname = 'TurboBet'
pword = '<(*_3pkloZ!6pIse'

conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    f'SERVER={server};'
    f'DATABASE={db1};'
    f'UID={uname};'
    f'PWD={pword}'
)
