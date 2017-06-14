import time
import sqlite3
import pandas.io.sql as sql

todaysd = time.strftime("%d_%m_%Y_")
con = sqlite3.connect("housingthing.db")
table = sql.read_sql('select * from housing', con)
table.to_csv("housing{0}".format(todaysd)+'.csv')

table2 = sql.read_sql('select * from jobs', con)

table2.to_csv("jobs{0}".format(todaysd)+'.csv')
