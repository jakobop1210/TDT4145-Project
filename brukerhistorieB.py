import sqlite3

con = sqlite3.connect('jernbane.db')
cursor = con.cursor()

# Legge inn operatør SJ
cursor.execute('''INSERT INTO Operatør VALUES ("SJ")''')

# Legge inn togruter i databasen
cursor.execute('''INSERT INTO Togrute VALUES (1, 1, "SJ")''')
cursor.execute('''INSERT INTO Togrute VALUES (2, 1, "SJ")''')
cursor.execute('''INSERT INTO Togrute VALUES (3, 0, "SJ")''')

# Opprette sittevogn og seter
cursor.execute('''INSERT INTO Sittevogn VALUES (1, " SJ-sittevogn-1", 1, 3, 4, "SJ", 1)''')
cursor.execute('''INSERT INTO Sittevogn VALUES (2, " SJ-sittevogn-1", 2, 3, 4, "SJ", 1)''')
cursor.execute('''INSERT INTO Sittevogn VALUES (3, " SJ-sittevogn-1", 1, 3, 4, "SJ", 2)''')
cursor.execute('''INSERT INTO Sittevogn VALUES (4, " SJ-sittevogn-1", 1, 3, 4, "SJ", 3)''')

# Legge inn sete 1 til sete 12 i hver vogn
for vognID in range(1, 5):
    for seteNr in range(1, 13):
        cursor.execute(f'''INSERT INTO Sete VALUES ({seteNr}, {vognID})''')
  
# Opprette sovevogn og kupéer
cursor.execute('''INSERT INTO Sovevogn VALUES (5, 'SJ-sovevogn-1', 2, 4, 'SJ', 2)''')
cursor.execute('''INSERT INTO Kupee VALUES (1, 5)''')
cursor.execute('''INSERT INTO Kupee VALUES (2, 5)''')
cursor.execute('''INSERT INTO Kupee VALUES (3, 5)''')
cursor.execute('''INSERT INTO Kupee VALUES (4, 5)''')


# Opprette togrutetabell StasjonerIRute. Antar at ankomsttid er 5 min før oppgitt klokkeslett i oppgaven,
# og at avgangstid er oppgitt tid. For siste stasjon antar vi at ankomsttid er oppgitt tid. 

# Togrute 1
cursor.execute('''INSERT INTO StasjonerIRute VALUES ("Trondheim", 1, NULL, "07:49", 1)''')
cursor.execute('''INSERT INTO StasjonerIRute VALUES ("Steinkjer", 1, "09:46", "09:51", 2)''')
cursor.execute('''INSERT INTO StasjonerIRute VALUES ("Mosjøen", 1, "13:15", "13:20", 3)''')
cursor.execute('''INSERT INTO StasjonerIRute VALUES ("Mo i Rana", 1, "14:26", "14:31", 4)''')
cursor.execute('''INSERT INTO StasjonerIRute VALUES ("Fauske", 1, "16:44", "16:49", 5)''')
cursor.execute('''INSERT INTO StasjonerIRute VALUES ("Bodø", 1, "17:34", NULL, 6)''')

# Togrute 2
cursor.execute('''INSERT INTO StasjonerIRute VALUES ("Trondheim", 2, NULL, "23:05", 1)''')
cursor.execute('''INSERT INTO StasjonerIRute VALUES ("Steinkjer", 2, "00:52", "00:57", 2)''')
cursor.execute('''INSERT INTO StasjonerIRute VALUES ("Mosjøen", 2, "04:36", "04:41", 3)''')
cursor.execute('''INSERT INTO StasjonerIRute VALUES ("Mo i Rana", 2, "05:50", "05:55", 4)''')
cursor.execute('''INSERT INTO StasjonerIRute VALUES ("Fauske", 2, "08:14", "08:19", 5)''')
cursor.execute('''INSERT INTO StasjonerIRute VALUES ("Bodø", 2, "09:05", NULL, 6)''')

# Togrute 3
cursor.execute('''INSERT INTO StasjonerIRute VALUES ("Mo i Rana", 3, NULL, "08:11", 1)''')
cursor.execute('''INSERT INTO StasjonerIRute VALUES ("Mosjøen", 3, "09:09", "09:14", 2)''')
cursor.execute('''INSERT INTO StasjonerIRute VALUES ("Steinkjer", 3, "12:26", "12:31", 3)''')
cursor.execute('''INSERT INTO StasjonerIRute VALUES ("Trondheim", 3, "14:13", NULL, 4)''')

# Opprette TogruteForekomst for 3 og 4 april 2023
cursor.execute('''INSERT INTO Togruteforekomst VALUES ('2023-04-03', 1)''')
cursor.execute('''INSERT INTO Togruteforekomst VALUES ('2023-04-04', 1)''')
cursor.execute('''INSERT INTO Togruteforekomst VALUES ('2023-04-03', 2)''')
cursor.execute('''INSERT INTO Togruteforekomst VALUES ('2023-04-04', 2)''')
cursor.execute('''INSERT INTO Togruteforekomst VALUES ('2023-04-03', 3)''')
cursor.execute('''INSERT INTO Togruteforekomst VALUES ('2023-04-04', 3)''')

con.commit()