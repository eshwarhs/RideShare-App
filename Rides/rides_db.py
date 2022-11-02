import sqlite3

con = sqlite3.connect("rides.db")
con.execute('''PRAGMA foreign_keys = ON;''')
con.execute('''CREATE TABLE RIDES(rideid INTEGER PRIMARY KEY AUTOINCREMENT, created_by TEXT NOT NULL, time_stamp NUMERIC NOT NULL ,source INTEGER NOT NULL,destination INTEGER NOT NULL,FOREIGN KEY (created_by) REFERENCES USERS(username) ON DELETE CASCADE);''')
con.execute('''CREATE TABLE RIDEPOOL(rideid INTEGER NOT NULL,username TEXT NOT NULL, FOREIGN KEY (username) REFERENCES USERS(username) ON DELETE CASCADE);''')

con.close()