import sqlite3
import hjelpefunksjoner
from datetime import datetime, timedelta

con = sqlite3.connect('jernbane.db')
cursor = con.cursor()

def finnTogruter():
    """
        Henter ut intput for startstasjon, sluttstasjon, dato og klokkeslett ved å kalle inputfunksjonene.
        Finner alle togruter fra startstasjon til sluttstasjon etter klokkeslett for oppgitt dato,
        og for alle klokkeslett dagen etter. Printer ut resultatet i terminalen. 
    """
    print("Vennligst fyll ut ønsket startstasjon")
    stasjoner = hjelpefunksjoner.startOgSluttStasjonsInput()
    print(stasjoner[0], stasjoner[1])
    dato = hjelpefunksjoner.datoInput()
    klokkeslett = hjelpefunksjoner.klokkeslettInput()

    rows = finnTogruterPåDato(stasjoner, dato, klokkeslett)
 
    if not rows:
        print(f'''Det finnes ingen togruter som går mellom {stasjoner[0]} og {stasjoner[1]} den {dato} etter kl {klokkeslett}, eller den {dato + timedelta(days=1)}''')
    for row in rows:
        print(f'''Tognr {row[0]} går fra {stasjoner[0]} kl {row[1]} og ankommer {stasjoner[1]} kl {row[2]} den {row[3]}''')


def finnTogruterPåDato(stasjoner, dato, klokkeslett):
    """ 
        I SECLECT-delen settes Dato til + 1 dag hvis valgt startStasjon har avgangstid som er 
        mindre enn avgangstiden for togruten sin startstasjon, da dette betyr at togruten går over to datoer.
        I WHERE-delen så sjekkes det samme som i SELECT-delen to ganger, for å se om Dato (evt oppdatert)
        er lik dato og avgangstid >= klokkeslett, eller bare lik datoDagEtter. 
        Videre sjekkes det for at startStasjon og sluttStasjon er riktig i forhold til brukerinput. 
        Tilsutt sjekkes det for at togruten går riktig vei, 
        da må startStasjon sitt StasjonNr må være mindre enn sluttStasjon sitt StasjonsNr 
        Parameters:
            stasjoner (array): List med valgt start- og sluttstasjon
            dato (str): Datoen brukeren skal reise
            klokkelsett (str): klokkeslettet som brukeren har valgt 
        Returns:
            type (list): List med alle togruter som går mellom valgte stasjoner på valgt dato og klokkeslett
    """
    
    return cursor.execute("""
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
            "dato": dato, "datoDagEtter": dato + timedelta(days=1), "startStasjon": stasjoner[0], 
            "sluttStasjon": stasjoner[1], "klokkeslett": klokkeslett
        }).fetchall()


con.commit()

if __name__ == "__main__":
    finnTogruter()
