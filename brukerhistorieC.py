import sqlite3
con = sqlite3.connect('jernbane.db')
cursor = con.cursor()

# Brukerhistorie C 

# Legge inn data i  Ukedager-tabellen
#hverdager = ["Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag"]
alleDager = ["Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag", "Lørdag", "Søndag"]
#
#for i in hverdager:
#    cursor.execute(f'''INSERT INTO Ukedager VALUES (1, '{i}')''')
#    cursor.execute(f'''INSERT INTO Ukedager VALUES (3, '{i}')''')
#for i in alleDager:
#    cursor.execute(f'''INSERT INTO Ukedager VALUES (2, '{i}')''')


def finnTogruterInnomStasjon():
    # Spør brukeren om input for stasjonsnavn og ukedag
    print("Vennligst fyll ut ønsket stasjon")
    stasjon = stasjonsInput()
    ukedag = ukedagInput()

    # Finner TogruteID'en og operatørnavn for Togruter som går på oppgitt ukedag innom oppgitt stasjon
    togruterInnomStasjon = cursor.execute("""
        SELECT Togrute.TogruteID, Togrute.OperatorNavn
        FROM Togrute INNER JOIN Ukedager
             ON Togrute.TogruteID = Ukedager.TogruteID
        WHERE Ukedager.Ukedag = :ukedag AND Togrute.TogruteID IN (
            SELECT TogruteID
            FROM Togrute NATURAL JOIN StasjonerIRute
            WHERE StasjonerIRute.JernbanestasjonNavn = :stasjonsNavn
        )
        """, {"ukedag": ukedag, "stasjonsNavn": stasjon})
    rows = togruterInnomStasjon.fetchall()
    
    # Looper gjennom alle TogruteID'er fra spørringen over
    for row in rows:
        # Finner startstasjon for spesifikk TogruteID
        startstasjon = cursor.execute("""
            SELECT JernbanestasjonNavn
            FROM StasjonerIRute
            WHERE TogruteID = :row AND Ankomsttid IS NULL
        """, {"row": row[0]})

        startstasjonForTogrute = startstasjon.fetchall()

        # Finner sluttstasjon for spesifikk TogruteID
        sluttstasjon = cursor.execute("""
            SELECT JernbanestasjonNavn, Ankomsttid
            FROM StasjonerIRute
            WHERE TogruteID = :row AND Avgangstid IS NULL
        """, {"row": row[0]})

        sluttstasjonForTogrute = sluttstasjon.fetchall()

        # Finner tidspunktet Togruten går innom stasjonen oppgitt av brukeren 
        if (stasjon == sluttstasjonForTogrute[0][0]):
            innomStasjonTidspunkt = sluttstasjonForTogrute[0][1]
        else: 
            stasjonsTidspunkt = cursor.execute("""
                SELECT Avgangstid
                FROM StasjonerIRute
                WHERE TogruteID = :row AND JernbanestasjonNavn = :stasjonsNavn
            """, {"row": row[0], "stasjonsNavn": stasjon})

            innomStasjonTidspunkt = stasjonsTidspunkt.fetchall()[0][0]

        # Printer resultatet til terminalen
        print(f'''Togrute nr {row[0]} fra {startstasjonForTogrute[0][0]} til {sluttstasjonForTogrute[0][0]} kjører innom {stasjon} på {ukedag}er kl {innomStasjonTidspunkt}.''')

# Henter inn bruker input for jernbanestasjon, og validrer input'en
def stasjonsInput():
    stasjonInput = input("Jernbanestasjon: ")
    # Sørge for at bruk av små og store bokstaver ikke påvirker input'en
    stasjon = ' '.join([x.capitalize() if len(x) > 1 else x.lower() for x in stasjonInput.split()]) 

    # Finner alle jernbanestasjoner i databasen
    jernbanestasjoner = cursor.execute("SELECT Navn FROM Jernbanestasjon")
    alleStasjonsNavn = jernbanestasjoner.fetchall()

    # Kaller funksjonen på nytt hvis inputen er ugyldig
    if stasjon  not in [navn[0] for navn in alleStasjonsNavn]:
        print("Ikke gyldig jernbanestasjon, prøv igjen")
        stasjonsInput()
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


