import sqlite3
con = sqlite3.connect('jernbane.db')
cursor = con.cursor()

# Brukerhistorie C

# Legge inn data i  Ukedager-tabellen
#hverdager = ["Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag"]
alleDager = ["Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag", "Lørdag", "Søndag"]

# for i in hverdager:
#    cursor.execute(f'''INSERT INTO Ukedager VALUES (1, '{i}')''')
#    cursor.execute(f'''INSERT INTO Ukedager VALUES (3, '{i}')''')
# for i in alleDager:
#    cursor.execute(f'''INSERT INTO Ukedager VALUES (2, '{i}')''')

def finnTogruterInnomStasjon():
    # Spør brukeren om input for stasjonsnavn og ukedag
    print("Vennligst fyll ut ønsket stasjon")
    stasjon = stasjonsInput()
    ukedag = ukedagInput()

    # I WHERE-delen sjekkes det for om valgt stasjon sin ankomsttid er mindre enn togruten sin avgangstid, 
    # isåfall går toget innom den stasjonen dagen etter, og Ukedag må endres til neste dag. 
    # Videre sjekkes det at StartStasjonIRute og SluttStasjonIRute sin ankomsttid og avgangsstid 
    # er NULL for å finne riktige start- og sluttstasjoner for togruten. 
    # Tilslutt sjekkes det for at oppgitt stasjon av bruker finnes i den togruten. 
    togruterInnomStasjon = cursor.execute("""
        SELECT Togrute.TogruteID, Togrute.OperatorNavn, StartstasjonIRute.JernbanestasjonNavn, 
               SluttStasjonIRute.JernbanestasjonNavn, SluttStasjonIRute.Ankomsttid
        FROM Togrute NATURAL JOIN Ukedager
             INNER JOIN StasjonerIRute AS StartStasjonIRute ON Togrute.TogruteID = StartStasjonIRute.TogruteID
             INNER JOIN StasjonerIRute AS SluttStasjonIRute ON Togrute.TogruteID = SluttStasjonIRute.TogruteID
        WHERE 
            ((CASE WHEN startStasjonIRute.Avgangstid > (
                SELECT Ankomsttid
                FROM Togrute AS Tog2 NATURAL JOIN StasjonerIRute 
                WHERE Togrute.TogruteID = Tog2.TogruteID AND JernbanestasjonNavn = :stasjonsNavn
            )
            THEN 
                CASE Ukedag
                    WHEN 'Mandag' THEN 'Tirsdag'
                    WHEN 'Tirsdag' THEN 'Onsdag'
                    WHEN 'Onsdag' THEN 'Torsdag'
                    WHEN 'Torsdag' THEN 'Fredag'
                    WHEN 'Fredag' THEN 'Lørdag'
                    WHEN 'Lørdag' THEN 'Søndag'
                    WHEN 'Søndag' THEN 'Mandag'
                END
            ELSE Ukedag END) = :ukedag 
            AND StartStasjonIRute.Ankomsttid IS NULL
            AND SluttStasjonIRute.Avgangstid IS NULL
            AND Togrute.TogruteID IN (
                SELECT TogruteID
                FROM Togrute NATURAL JOIN StasjonerIRute
                WHERE StasjonerIRute.JernbanestasjonNavn = :stasjonsNavn
            )
        )""", {"ukedag": ukedag, "stasjonsNavn": stasjon})
    
    rows = togruterInnomStasjon.fetchall()

    # Hvis spørringen er tom finnes det ingen togruter
    if not rows:
        print("Ingen togruter går innom denne stasjonen på denne ukedagen")
    else:
        # Looper gjennom alle TogruteID'er fra spørringen over
        for row in rows:
            # Hvis oppgitt stasjon er siste stasjon i ruten
            if (stasjon == row[3]):
                print(
                    f'''Togrute nr {row[0]} fra {row[2]} til {row[3]} kjører innom {stasjon} på {ukedag}er kl {row[4]}.''')
            # Hvis oppgitt stasjon ikke er siste stasjon i ruten må avgangstiden bli funnet
            else:
                stasjonsTidspunkt = cursor.execute("""
                    SELECT Avgangstid
                    FROM StasjonerIRute
                    WHERE TogruteID = :row AND JernbanestasjonNavn = :stasjonsNavn
                """, {"row": row[0], "stasjonsNavn": stasjon})
                avgangstid = stasjonsTidspunkt.fetchall()[0][0]
                print(
                    f'''Togrute nr {row[0]} fra {row[2]} til {row[3]} kjører innom {stasjon} på {ukedag}er kl {avgangstid}.''')

# Henter inn bruker input for jernbanestasjon, og validrer input'en
def stasjonsInput():
    while True:
        stasjonInput = input("Jernbanestasjon: ")
        # Sørge for at bruk av små og store bokstaver ikke påvirker input'en
        stasjon = ' '.join([delNavn.capitalize() if len(delNavn) > 1 else delNavn.lower() for delNavn in stasjonInput.split()])

        # Finner alle jernbanestasjoner i databasen
        jernbanestasjoner = cursor.execute("SELECT Navn FROM Jernbanestasjon")
        alleStasjonsNavn = jernbanestasjoner.fetchall()

        # Kaller funksjonen på nytt hvis inputen er ugyldig
        if stasjon not in [navn[0] for navn in alleStasjonsNavn]:
            print("Ikke gyldig jernbanestasjon, prøv igjen")
        else:
            return stasjon

# Henter inn bruker input for ukedag, og validrer input'en
def ukedagInput():
    ukedag = input("Ukedag: ").capitalize()
    if ukedag not in alleDager:
        print("Ikke gyldig ukedag, prøv igjen")
        ukedagInput()
    return ukedag


finnTogruterInnomStasjon()

con.commit()
