import re
import sqlite3
import datetime

# ? For en bruker skal man kunne finne all informasjon om de kjøpene hen har gjort for fremtidige
# ? reiser. Denne funksjonaliteten skal programmeres.


# ? Fremgangsmåte
# finne en kunde med brukerid fra kunde tabellen
# joine med BillettSete og BillettKupee på OrdreNr
# joine den med kundeordre på KundeID for å finne alle ordre til en kunde
#

# uisdahø@gmail.com

# SELECT *

# FROM KundeOrdre as KO
# 	NATURAL JOIN Togrute as TR
# 	NATURAL JOIN TogruteForekomst as TRFK
# 	NATURAL JOIN StasjonerIRute as SIR
	
# where StasjonsNr == 1

'''
SELECT *
FROM KundeOrdre as KO
	NATURAL JOIN Togrute as TR
	NATURAL JOIN TogruteForekomst as TRFK
	NATURAL JOIN StasjonerIRute as SIR
	
where StasjonsNr == 1  and ( KO.KundeNr == 1) and (TRFK.Dato > 2023-04-03 or (TRFK.Dato == 2023-04-03 and SIR.Avgangstid > 10:00) )
'''

'''
        SELECT *
        from kunde  as k natural join KundeOrdre as ko inner join BillettSete as bs on (ko.OrdreNr == bs.OrdreNr)
        WHERE k.KundeNr == :KundeNr and ((ko.Dato < :current_date) or (ko.Dato == :current_date and ko.tid > :current_clock_time))
'''

con = sqlite3.connect('jernbane.db')
cursor = con.cursor()

def fremtidigeReiser():
    KundeNr = getUserID()
    current_time = datetime.datetime.now()
    current_date = f"{current_time.year}-{current_time.month}-{current_time.day}"
    current_clock_time = f"{current_time.hour}:{current_time.second}"
    print(current_date)
    print(current_clock_time)

    req = cursor.execute(
        """
  SELECT *

FROM Kunde
	inner JOIN KundeOrdre on Kunde.KundeNr == KundeOrdre.KundeID
	NATURAL JOIN (SELECT OrdreNr, TogruteID as BillettSeteTogruteID FROM BillettSete UNION SELECT OrdreNr, TogruteID as BillettKupeeTogruteID FROM BillettKupee)
    NATURAL JOIN Togrute as TR
    NATURAL JOIN TogruteForekomst as TRFK
    NATURAL JOIN StasjonerIRute as SIR
 
	WHERE
		Ankomsttid IS NULL and Kunde.KundeNr == 10 and  (Dato > '2023-04-02' or ( Dato == '2023-04-03' or Avgangstid < '08:00'))
        """
        ,{'KundeNr': KundeNr, "current_date" :current_date, "current_clock_time": current_clock_time})
    res = req.fetchall()
    print(res)

# and (TRFK.Dato > :current_date or (TRFK.Dato == :current_date  and SIR.Avgangstid > :current_clock_time) )

# or (ko.Dato == :current_date and ko.Tidspunkt > :current_clock_time)
def getUserID():
    '''
        Henter brukerID basert på email til en bruker. Spør på nytt om bruker ikke finnes.
    '''
    email = input("Skriv in email('ctrl + c' to quit): ")

    if not email or len(email) < 2:
        print("Ugyldig email. Prøv igjen")
        return getUserID()

    userID = cursor.execute('''
        SELECT KundeNr
        from kunde
        WHERE Epost == :email
    ''',{'email': email})
    list = userID.fetchall()
    print(list)

    if not list:
        print("Ugyldig email, prøv på nytt.")
        return getUserID()

    return str(list[0][0])

def brukerBiletter(brukerID:str):
    '''
        Henter alle billetter til en bruker basert på brukerID
    '''
    billetter = cursor.execute('''
        SELECT KundeNr
        from kunde
        WHERE Epost == :email
    ''',{'brukerID': brukerID})
    allTickets = billetter.fetchall()
    print(allTickets)

fremtidigeReiser()
con.commit()