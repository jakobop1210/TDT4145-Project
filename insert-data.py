import sqlite3
con = sqlite3.connect('jernbane.db')
cursor = con.cursor()

cursor.execute('''INSERT INTO Banestrekning VALUES ('Test1', 'Energi', 3, 'TestStart', 'TestSlutt')''')
con.commit()