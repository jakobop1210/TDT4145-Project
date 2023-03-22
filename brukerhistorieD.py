import re
import sqlite3
from datetime import datetime, timedelta

con = sqlite3.connect('jernbane.db')
cursor = con.cursor()

def finnTogruter():
    # Spør brukeren om input for stasjonsnavn, dato og klokkeslett
    print("Vennligst fyll ut ønsket startstasjon")
    stasjoner = stasjonsInput()
    dato = datoInput().date()
    datoDagEtter = dato + timedelta(days=1)
    klokkeslett = klokkeslettInput()
    
    # Finner TogruteID'en for Togruter som går mellom oppgitt start- og sluttstasjon,
    # på oppgitt dato etter oppgitt klokkeslett
    togruter = cursor.execute("""
        SELECT Togrute.TogruteID, startStasjonIRute.Avgangstid,  sluttStasjonIRute.Ankomsttid, Dato
        FROM Togrute
        JOIN StasjonerIRute AS startStasjonIRute ON Togrute.TogruteID = startStasjonIRute.TogruteID
        JOIN StasjonerIRute AS sluttStasjonIRute ON Togrute.TogruteID = sluttStasjonIRute.TogruteID
        JOIN TogruteForekomst ON Togrute.TogruteID = TogruteForekomst.TogruteID
        WHERE (Dato = :dato OR Dato = :datoDagEtter)
        AND startStasjonIRute.JernbanestasjonNavn = :startStasjon
        AND sluttStasjonIRute.JernbanestasjonNavn = :sluttStasjon
		    AND startStasjonIRute.StasjonsNr < SluttStasjonIRute.StasjonsNr
        AND startStasjonIRute.Avgangstid >= :klokkeslett
		    ORDER BY Dato, startStasjonIRute.Avgangstid
        """, {"dato": dato, "datoDagEtter": datoDagEtter, "startStasjon": stasjoner[0], "sluttStasjon": stasjoner[1], "klokkeslett": klokkeslett})
    rows = togruter.fetchall()

    for row in rows:
        print(f'''Tognr {row[0]} går fra {stasjoner[0]} kl {row[1]} og ankommer {stasjoner[1]} kl {row[2]} den {row[3]}''')


con.commit()

# Henter inn bruker input for start- og sluttstasjon, og validerer input'en
def stasjonsInput():
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
        stasjonsInput()
    elif startStasjon == sluttStasjon:
        print("Kan ikke ha samme start- og sluttstasjon, prøv igjen")
        stasjonsInput()

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
