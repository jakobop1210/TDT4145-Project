import sqlite3

con = sqlite3.connect('jernbane.db')
cursor = con.cursor()

togruteforekomster = cursor.execute('''SELECT * FROM TogruteForekomst''')

for togruteforekomst in togruteforekomster:   
    for i in range(1, 13):
        cursor.execute('''INSERT INTO BillettSete(OrdreNr, Dato, TogruteID, SeteNr, VognID) VALUES (NULL, :Dato, :TogruteID, :SeteNr, :VognID)''', 
                       {'Dato': togruteforekomst[0], 'TogruteID': togruteforekomst[1], 'SeteNr': i, 'VognID': "NULL"}) #PROBLEM AT VOGNID ER NULL


#Finn ledige seter (billetter) på en del-togrute
# - Betyr: Finn alle ledige seter for delstrekningene for alle del-togrutene
#   -> Antar at det kun skal vises billetter som er ledige hele del-togruten

def finn_ledige_seter():
    startstasjon = ""
    sluttstasjon = ""
    dato = "2023-04-03"


    #FINN ALLE TOGRUTEFOREKOMSTENE SOM INNEHOLDER START OG SLUTTSTASJONEN
    cursor.execute('''
        SELECT * 
        FROM TogruteForekomst AS trf
        WHERE trf.TogruteID IN (
            SELECT sir.TogruteID
            FROM StasjonerIRute AS sir INNER JOIN JernbaneStasjon AS startstasjon ON (sir.JernbanestasjonNavn = startstasjon.Navn)
            WHERE startstasjon.Navn = 'Trondheim' AND  sir.TogruteID IN (
                SELECT DISTINCT sir2.TogruteID
                FROM StasjonerIRute sir2 INNER JOIN JernbaneStasjon AS sluttstasjon ON (sir2.JernbanestasjonNavn = sluttstasjon.Navn)
                WHERE sir2.TogruteID = sir.TogruteID AND sluttstasjon.Navn = 'Fauske'
            )
        )
    ''')
                
    ## HVORDAN GJØR VI DET MED BILLETTER? ALLE BILLETTER MÅ JO OPPRETTES PÅ FORHÅND
    cursor.execute('INSERT INTO KundeOrdre VALUES ()')


con.commit()



#Lite problem: Vite om stasjoner er i en togrute. Da må du hente ut alle stasjonene