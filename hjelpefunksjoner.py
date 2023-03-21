
import datetime
import re
from sqlite3 import Cursor
import sqlite3

con = sqlite3.connect('jernbane.db')
cursor = con.cursor()

alleDager = ["Mandag", "Tirsdag", "Onsdag",
             "Torsdag", "Fredag", "Lørdag", "Søndag"]


def getUserID():
    email = input("Skriv in email: ")

    if not email:
        print("Ugyldig email. Prøv igjen")
        return getUserID()

    return email


def klokkeslettInput():
    klokkeslett = input("Klokkeslett (for.eks 16:45): ")
    if re.match(r'^([0-1][0-9]|[2][0-3]):([0-5][0-9])$', klokkeslett) and datetime.strptime(klokkeslett, "%H:%M"):
        return klokkeslett
    print("Ikke gyldig klokkeslett, prøv igjen")
    return klokkeslettInput()


def datoInput():
    dato = input("Dato (for.eks 2023-04-20): ")
    try:
        dato = datetime.strptime(dato, "%Y-%m-%d")
        print(dato)
        return dato
    except:
        print("Ikke gyldig dato, prøv igjen")
        return datoInput()


def stasjonsInput():
    startStasjonInput = input("Startstasjon: ")
    sluttStasjonInput = input("Sluttstasjon: ")

    # Sørge for at bruk av små og store bokstaver ikke påvirker input'en
    startStasjon = ' '.join([x.capitalize() if len(
        x) > 1 else x.lower() for x in startStasjonInput.split()])
    sluttStasjon = ' '.join([x.capitalize() if len(
        x) > 1 else x.lower() for x in sluttStasjonInput.split()])

    # Finner alle jernbanestasjoner i databasen
    jernbanestasjoner = cursor.execute("SELECT Navn FROM Jernbanestasjon")
    alleStasjonsNavn = jernbanestasjoner.fetchall()

    # Kaller funksjonen på nytt hvis inputen er ugyldig
    if (startStasjon and sluttStasjon) not in [navn[0] for navn in alleStasjonsNavn]:
        print("Ikke gyldig jernbanestasjoner, prøv igjen")
        stasjonsInput()
    elif startStasjon == sluttStasjon:
        print("Kan ikke ha samme start- og sluttstasjon, prøv igjen")
        stasjonsInput()

    return [startStasjon, sluttStasjon]


con.commit()


def ukedagInput():
    ukedag = input("Ukedag: ").capitalize()
    if ukedag not in alleDager:
        print("Ikke gyldig ukedag, prøv igjen")
        ukedagInput()
    return ukedag
