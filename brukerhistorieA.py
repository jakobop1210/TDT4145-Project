import sqlite3

con = sqlite3.connect('jernbane.db')
cursor = con.cursor()

# Legge inn jernbanestasjoner for Nordlandsbanen
cursor.execute('''INSERT INTO Jernbanestasjon VALUES ("Trondheim", 5.1)''')
cursor.execute('''INSERT INTO Jernbanestasjon VALUES ("Steinkjer", 3.6)''')
cursor.execute('''INSERT INTO Jernbanestasjon VALUES ("Mosjøen", 6.8)''')
cursor.execute('''INSERT INTO Jernbanestasjon VALUES ("Mo i Rana", 3.5)''')
cursor.execute('''INSERT INTO Jernbanestasjon VALUES ("Fauske", 34)''')
cursor.execute('''INSERT INTO Jernbanestasjon VALUES ("Bodø", 4.1)''')

# Legge inn delstrekninger for Nordlandsbanen
cursor.execute('''INSERT INTO Delstrekning VALUES (1, 1, 120, "Trondheim", "Steinkjer")''')
cursor.execute('''INSERT INTO Delstrekning VALUES (2, 0, 280, "Steinkjer", "Mosjøen")''')
cursor.execute('''INSERT INTO Delstrekning VALUES (3, 0, 90, "Mosjøen", "Mo i Rana")''')
cursor.execute('''INSERT INTO Delstrekning VALUES (4, 0, 170, "Mo i Rana", "Fauske")''')
cursor.execute('''INSERT INTO Delstrekning VALUES (5, 0, 60, "Fauske", "Bodø")''')

# Opprette Nordlandsbanen
cursor.execute('''INSERT INTO Banestrekning VALUES ("Nordlandsbanen", "Diesel", 6, "Trondheim", "Bodø")''')

# InneholderDelstrekning
cursor.execute('''INSERT INTO InneholderStrekning VALUES ("Nordlandsbanen", 1)''')
cursor.execute('''INSERT INTO InneholderStrekning VALUES ("Nordlandsbanen", 2)''')
cursor.execute('''INSERT INTO InneholderStrekning VALUES ("Nordlandsbanen", 3)''')
cursor.execute('''INSERT INTO InneholderStrekning VALUES ("Nordlandsbanen", 4)''')
cursor.execute('''INSERT INTO InneholderStrekning VALUES ("Nordlandsbanen", 5)''')

con.commit()