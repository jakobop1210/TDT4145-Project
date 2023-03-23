import re
import sqlite3
from datetime import datetime, timedelta

con = sqlite3.connect('jernbane.db')
cursor = con.cursor()

# Henter ut intput for startstasjon, sluttstasjon, dato og klokkeslett ved å kalle inputfunksjonene.
# Finner alle togruter fra startstasjon til sluttstasjon etter klokkeslett for oppgitt dato,
# og for alle klokkeslett dagen etter. Printer ut resultatet i terminalen. 
def finnTogruter():
    # Spør brukeren om input for stasjonsnavn, dato og klokkeslett
    print("Vennligst fyll ut ønsket startstasjon")
    stasjoner = stasjonsInput()
    print(stasjoner[0], stasjoner[1])
    dato = datoInput().date()
    datoDagEtter = dato + timedelta(days=1)
    print(dato, datoDagEtter)
    klokkeslett = klokkeslettInput()

    # I SECLECT-delen settes Dato til + 1 dag hvis valgt startStasjon har avgangstid som er 
    # mindre enn avgangstiden for togruten sin startstasjon, da dette betyr at togruten går over to datoer.
    # I WHERE-delen så sjekkes det samme som i SELECT-delen to ganger, for å se om Dato (evt oppdatert)
    # er lik dato og avgangstid >= klokkeslett, eller bare lik datoDagEtter. 
    # Videre sjekkes det for at startStasjon og sluttStasjon er riktig i forhold til brukerinput. 
    # Tilsutt sjekkes det for at togruten går riktig vei, 
    # da må startStasjon sitt StasjonNr må være mindre enn sluttStasjon sitt StasjonsNr 
    togruter = cursor.execute("""
        SELECT Tog.TogruteID, startStasjonIRute.Avgangstid, sluttStasjonIRute.Ankomsttid,
            CASE WHEN startStasjonIRute.Avgangstid < (
                SELECT StasjonerIRute.Avgangstid 
                FROM Togrute AS Tog2 NATURAL JOIN StasjonerIRute 
                WHERE Tog.TogruteID = Tog2.TogruteID AND StasjonerIRute.Ankomsttid IS NULL
            )
            THEN DATE(Dato, "+1 day")
            ELSE Dato END AS Dato
        FROM Togrute AS Tog NATURAL JOIN StasjonerIRute AS startStasjonIRute
             INNER JOIN StasjonerIRute AS sluttStasjonIRute ON Tog.TogruteID = sluttStasjonIRute.TogruteID
             INNER JOIN TogruteForekomst ON Tog.TogruteID = TogruteForekomst.TogruteID
        WHERE 
            ((CASE WHEN startStasjonIRute.Avgangstid < (
                SELECT StasjonerIRute.Avgangstid 
                FROM Togrute AS Tog2 NATURAL JOIN StasjonerIRute 
                WHERE Tog.TogruteID = Tog2.TogruteID AND StasjonerIRute.Ankomsttid IS NULL
            )
            THEN DATE(Dato, "+1 day")
            ELSE Dato END = :dato AND startStasjonIRute.Avgangstid >= :klokkeslett)
             OR
            (CASE WHEN startStasjonIRute.Avgangstid < (
                SELECT StasjonerIRute.Avgangstid 
                FROM Togrute AS Tog2 NATURAL JOIN StasjonerIRute 
                WHERE Tog.TogruteID = Tog2.TogruteID AND StasjonerIRute.Ankomsttid IS NULL
            )
            THEN DATE(Dato, "+1 day")
            ELSE Dato END = :datoDagEtter))
            AND startStasjonIRute.JernbanestasjonNavn = :startStasjon
            AND sluttStasjonIRute.JernbanestasjonNavn = :sluttStasjon
		    AND startStasjonIRute.StasjonsNr < SluttStasjonIRute.StasjonsNr   
		ORDER BY Dato, startStasjonIRute.Avgangstid
        """, {
            "dato": dato, "datoDagEtter": datoDagEtter, "startStasjon": stasjoner[0], 
            "sluttStasjon": stasjoner[1], "klokkeslett": klokkeslett
        })

    rows = togruter.fetchall()

    # Hvis spørringen er tom finnes det ingen togruter, ellers printes resultatet
    if not rows:
        print(f'''Det finnes ingen togruter som går mellom {stasjoner[0]} og {stasjoner[1]} den {dato} etter kl {klokkeslett}, eller den {datoDagEtter}''')
    for row in rows:
        print(f'''Tognr {row[0]} går fra {stasjoner[0]} kl {row[1]} og ankommer {stasjoner[1]} kl {row[2]} den {row[3]}''')

con.commit()

# Henter inn bruker input for start- og sluttstasjon, og validerer input'en
def stasjonsInput():
    while True:
        startStasjonInput = input("Startstasjon: ")
        sluttStasjonInput = input("Sluttstasjon: ")

        # Sørge for at bruk av små og store bokstaver ikke påvirker input'en
        startStasjon= ' '.join([x.capitalize() if len(x) > 1 else x.lower() for x in startStasjonInput.split()])
        sluttStasjon = ' '.join([x.capitalize() if len(x) > 1 else x.lower() for x in sluttStasjonInput.split()])   

        # Finner alle jernbanestasjoner i databasen
        jernbanestasjoner = cursor.execute("SELECT Navn FROM Jernbanestasjon")
        alleStasjonsNavn = jernbanestasjoner.fetchall()

        # Kaller funksjonen på nytt hvis inputen er ugyldig
        if (startStasjon and sluttStasjon)  not in [navn[0] for navn in alleStasjonsNavn]:
            print("Ikke gyldig jernbanestasjoner, prøv igjen")
        elif startStasjon == sluttStasjon:
            print("Kan ikke ha samme start- og sluttstasjon, prøv igjen")
        else:
            return [startStasjon, sluttStasjon]

# Henter inn bruker input for dato, og validerer input'en
def datoInput():
    dato = input("Dato (for.eks 2023-04-20): ")
    try:
        dato = datetime.strptime(dato, "%Y-%m-%d")
        return dato
    except:
        print("Ikke gyldig dato, prøv igjen")
        return datoInput()
 
# Henter inn bruker input for klokkeslett, og validerer input'en
def klokkeslettInput():
    klokkeslett = input("Klokkeslett (for.eks 16:45): ")
    if re.match(r'^([0-1][0-9]|[2][0-3]):([0-5][0-9])$', klokkeslett) and datetime.strptime(klokkeslett, "%H:%M"):
        return klokkeslett
    print("Ikke gyldig klokkeslett, prøv igjen")
    return klokkeslettInput()

finnTogruter()
