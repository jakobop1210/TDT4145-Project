import sqlite3
con = sqlite3.connect('jernbane.db')
cursor = con.cursor()

# Brukerhistorie C 

# Legge inn data i  Ukedager-tabellen
#hverdager = ["Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag"]
#alleDager = ["Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag", "Lørdag", "Søndag"]
#
#for i in hverdager:
#    cursor.execute(f'''INSERT INTO Ukedager VALUES (1, '{i}')''')
#    cursor.execute(f'''INSERT INTO Ukedager VALUES (3, '{i}')''')
#for i in alleDager:
#    cursor.execute(f'''INSERT INTO Ukedager VALUES (2, '{i}')''')


def togruterInnomStasjon(ukedag, stasjonsNavn):
    togruterInnomStasjonPåUkedag = cursor.execute("""
        SELECT Togrute.TogruteID 
        FROM Togrute INNER JOIN Ukedager
             ON Togrute.TogruteID = Ukedager.TogruteID
        WHERE Ukedager.Ukedag = :ukedag AND Togrute.TogruteID IN (
            SELECT TogruteID
            FROM Togrute NATURAL JOIN StasjonerIRute
            WHERE StasjonerIRute.JernbanestasjonNavn = :stasjonsNavn
        )
        """, {"ukedag": ukedag, "stasjonsNavn": stasjonsNavn})
    
    rows = togruterInnomStasjonPåUkedag.fetchall()
    print(f"Togrutene som går innom {stasjonsNavn} {ukedag}")
    for row in rows:
        print(row)

togruterInnomStasjon("Lørdag", "Bodø")



con.commit()


