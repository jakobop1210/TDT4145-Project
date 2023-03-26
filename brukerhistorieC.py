import sqlite3
import hjelpefunksjoner

con = sqlite3.connect('jernbane.db')
cursor = con.cursor()
 
def finnTogruter():
    """
        Henter ut intput for jernbanestasjon og ukedag ved å kalle inputfunksjonene, 
        finner deretter alle togruter som går innom oppgitt stasjon på oppgitt ukedag.
        Sjekker tilslutt om valgt stasjon er siste stasjon i ruten, hvis ikke så må avgangstiden bli funnet. 
    """
    print("Vennligst fyll ut ønsket stasjon")
    stasjon = hjelpefunksjoner.stasjonsInput()
    ukedag = hjelpefunksjoner.ukedagInput()
    alleTogruter = finnTogruterInnomStasjon(stasjon, ukedag)

    if not alleTogruter:
        print("Ingen togruter går innom denne stasjonen på denne ukedagen")
    else:
        for row in alleTogruter:
            if (stasjon == row[3]):
                print(
                    f'''Togrute nr {row[0]} fra {row[2]} til {row[3]} kjører innom {stasjon} på {ukedag}er kl {row[4]}.''')
            else:
                stasjonsTidspunkt = cursor.execute("""
                    SELECT Avgangstid
                    FROM StasjonerIRute
                    WHERE TogruteID = :row AND JernbanestasjonNavn = :stasjonsNavn
                """, {"row": row[0], "stasjonsNavn": stasjon})
                avgangstid = stasjonsTidspunkt.fetchall()[0][0]
                print(
                    f'''Togrute nr {row[0]} fra {row[2]} til {row[3]} kjører innom {stasjon} på {ukedag}er kl {avgangstid}.''')

def finnTogruterInnomStasjon(stasjon, ukedag):
    """
        I WHERE-delen sjekkes det for om valgt stasjon sin ankomsttid er mindre enn togruten sin avgangstid, 
        isåfall går toget innom den stasjonen dagen etter, og Ukedag må endres til neste dag. 
        Videre sjekkes det at StartStasjonIRute og SluttStasjonIRute sin ankomsttid og avgangsstid 
        er NULL for å finne riktige start- og sluttstasjoner for togruten. 
        Tilslutt sjekkes det for at oppgitt stasjon av bruker finnes i den togruten. 
        Parameters:
            stasjon (str): Valgt jernbanestasjon av bruker
            ukedag (str): Ukedagen brukeren skal få opp togruter for
        Returns:
            type (list): Liste med alle togruter som går innom valgt stasjon på valgt ukedag
    """
    return cursor.execute("""
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
        )""", {"ukedag": ukedag, "stasjonsNavn": stasjon}).fetchall()


if __name__ == "__main__":
    finnTogruter()

con.commit()
