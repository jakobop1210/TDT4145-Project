import sqlite3
import re

def registrer_kunde():
    con = sqlite3.connect('jernbane.db')
    cursor = con.cursor()

    print("Vennligst fyll ut informasjonen under")
    navn = input("Navn: ")
    epost = input("E-post: ")
    regex = re.match(r'^[A-Za-z0-9]+\@[A-Za-z]+(\.[A-Za-z]+)?\.[A-Za-z]+$', epost)
    if not bool(regex):
        print()
        print("Vennligst velg en gyldig mail")
        print()
        registrer_kunde()
        return

    tlf = input("Telefonnummer: ")
    if len(tlf) != 8:
        print()
        print("Vennligst velg et gyldig telefonnummer med åtte siffer")
        print()
        registrer_kunde()
        return

    cursor.execute('''INSERT INTO Kunde(Navn, Epost, Tlf) VALUES (:navn, :epost, :tlf)''', 
                   {'navn': navn, 'epost': epost, 'tlf': tlf})

    con.commit()
    print("Du er nå registrert!")

registrer_kunde()
