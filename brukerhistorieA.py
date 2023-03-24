import sqlite3

con = sqlite3.connect('jernbane.db')
cursor = con.cursor()

# Legge inn jernbanestasjoner for Nordlandsbanen
cursor.execute('''INSERT INTO Jernbanestasjon VALUES 
    ("Trondheim", 5.1),
    ("Steinkjer", 3.6),
    ("Mosjøen", 6.8),
    ("Mo i Rana", 3.5),
    ("Fauske", 34),
    ("Bodø", 4.1)''')

# Legge inn delstrekninger for Nordlandsbanen
cursor.execute('''INSERT INTO Delstrekning(Sportype, Lengde, StartStasjon, SluttStasjon) VALUES 
    (1, 120, "Trondheim", "Steinkjer"),
    (0, 280, "Steinkjer", "Mosjøen"),
    (0, 90, "Mosjøen", "Mo i Rana"),
    (0, 170, "Mo i Rana", "Fauske"),
    (0, 60, "Fauske", "Bodø")''')

# Opprette Nordlandsbanen
cursor.execute('''INSERT INTO Banestrekning VALUES ("Nordlandsbanen", "Diesel", 6, "Trondheim", "Bodø")''')

# InneholderDelstrekning
cursor.execute('''INSERT INTO InneholderStrekning VALUES 
    ("Nordlandsbanen", 1),
    ("Nordlandsbanen", 2),
    ("Nordlandsbanen", 3),
    ("Nordlandsbanen", 4),
    ("Nordlandsbanen", 5)''')

con.commit()