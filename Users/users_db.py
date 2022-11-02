import sqlite3

con = sqlite3.connect("users.db")
con.execute('''PRAGMA foreign_keys = ON;''')
con.execute('''CREATE TABLE USERS(username TEXT PRIMARY KEY,password TEXT NOT NULL);''')

con.close()