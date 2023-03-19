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
        SELECT Togrute.TogruteID, Togrute.OperatorNavn
        FROM Togrute INNER JOIN Ukedager
             ON Togrute.TogruteID = Ukedager.TogruteID
        WHERE Ukedager.Ukedag = :ukedag AND Togrute.TogruteID IN (
            SELECT TogruteID
            FROM Togrute NATURAL JOIN StasjonerIRute
            WHERE StasjonerIRute.JernbanestasjonNavn = :stasjonsNavn
        )
        """, {"ukedag": ukedag, "stasjonsNavn": stasjonsNavn})
    rows = togruterInnomStasjonPåUkedag.fetchall()
    
    
    for row in rows:
        startstasjon = cursor.execute("""
            SELECT JernbanestasjonNavn, Avgangstid
            FROM StasjonerIRute
            WHERE TogruteID = :row AND Ankomsttid IS NULL
        """, {"row": row[0]})

        startstasjonForTogrute = startstasjon.fetchall()

        sluttstasjon = cursor.execute("""
            SELECT JernbanestasjonNavn, Ankomsttid
            FROM StasjonerIRute
            WHERE TogruteID = :row AND Avgangstid IS NULL
        """, {"row": row[0]})

        sluttstasjonForTogrute = startstasjon.fetchall()

        print(f'''Togruten med id: {row[0]} og operatør {row[1]}, 
går innom {stasjonsNavn} på {ukedag}er. 
Den starter fra {startstasjonForTogrute[0][0]} kl {startstasjonForTogrute[0][1]}, 
og ankommer {sluttstasjonForTogrute[0][0]} kl {sluttstasjonForTogrute[0][1]}''')

togruterInnomStasjon("Lørdag", "Bodø")


con.commit()


