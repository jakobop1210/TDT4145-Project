import sqlite3
import datetime
import hjelpefunksjoner
from datetime import datetime
con = sqlite3.connect('jernbane.db')
cursor = con.cursor()

def find_time():
    '''
    Funksjon som finner tidspunktet nå, og returnerer det i en streng
    
    Returns
        current_date (str): Datoen nå
        current_clock_time (str): Tidspunktet nå
    '''

    current_time = datetime.now()
    hour = current_time.hour
    minute = current_time.minute
    if len(str(current_time.hour))<2:
        hour = "0" + str(current_time.hour)
    if len(str(current_time.minute))<2:
        minute = "0" + str(current_time.minute)
    
    month = current_time.month
    day = current_time.day
    if len(str(current_time.month))<2:
        month = "0" + str(current_time.month)
    if len(str(current_time.day))<2:
        day = "0" + str(current_time.day)


    current_date = f"{current_time.year}-{month}-{day}"
    current_clock_time = f"{hour}:{minute}"
    return current_date, current_clock_time
    
def user_time():
    '''
    Funksjon som lar brukeren velge tidspunktet de vil se fremtidige reiser fra
    
    Returns 
        date (str): Datoen brukeren har valgt
        time (str): Tidspunktet brukeren har valgt
    '''

    date = hjelpefunksjoner.datoInput().date()
    time = str(hjelpefunksjoner.klokkeslettInput())
    print(date, time)
    return date, time

def main():
    '''
    Hovedfunksjonen som kjører hele programmet
    '''
    print("Velkommen til Jernbanesystemet\n")
    bruker = getUser()
    print(f"Velkommen {bruker[1]}\n\n Epost: {bruker[2]}, Telefon: {bruker[3]}, BrukerID: {bruker[0]}\n")
    fremtidige_reiser(bruker[0])
    
def fremtidige_reiser(brukerID:str):
    '''
    Finner fremtidige reiser for en bruker. 
    Finner først alle reiser som brukeren har bestilt, og deretter filtrerer den ut de som har vært.

    Parameters
        brukerID (str): BrukerID til brukeren som skal finne fremtidige reiser
    '''
    own_time_or_date = input("Vil du se fremtidige reiser basert på tidspunktet nå, eller et spesifikt tidspunkt? (nå[n]/egendefinert[e]): \n\n")
    if own_time_or_date.lower() == "e":
        current_date, current_clock_time = user_time()
    elif own_time_or_date.lower() == "n":
        current_date, current_clock_time = find_time()
    else:
        print("Ugyldig input, prøv igjen")
        return fremtidige_reiser(brukerID)
    
    print(f"Reiser etter {current_date} {current_clock_time}\N{HOURGLASS}\n")

    res = cursor.execute('''
        SELECT Kunde.Navn, KundeOrdre.OrdreNr, BillettDato, BillettTogruteID, 
              StartStasjon, SluttStasjon, StasjonerIRute.Avgangstid, Togrute.OperatorNavn
        FROM Kunde NATURAL JOIN KundeOrdre
        	 INNER JOIN (
        		SELECT OrdreNr AS AlleOrderer,TogruteID AS BillettTogruteID, 
                       Dato AS BillettDato,StartStasjon,SluttStasjon
        		FROM BillettSete
        	    UNION
        	    SELECT OrdreNr AS AlleOrderer,TogruteID AS BillettTogruteID, 
                       Dato AS BillettDato,StartStasjon,SluttStasjon
        	    FROM BillettKupee) ON KundeOrdre.OrdreNr = AlleOrderer
        	 INNER JOIN TogruteForekomst ON (BillettDato = TogruteForekomst.Dato AND BillettTogruteID = TogruteForekomst.TogruteID)
        	 INNER JOIN Togrute ON TogruteForekomst.TogruteID = Togrute.TogruteID
        	 INNER JOIN StasjonerIRute ON (StasjonerIRute.TogruteID = Togrute.TogruteID AND StasjonerIRute.JernbanestasjonNavn = StartStasjon)
             WHERE Kunde.KundeNr = :brukerID 
                   AND (BillettDato > :current_date OR (BillettDato = :current_date AND StasjonerIRute.Avgangstid > :current_clock_time))
    ''',{'brukerID': brukerID, 'current_date': current_date, 'current_clock_time': current_clock_time})
    allTickets = res.fetchall()

    output_string = ""

    for ticket in allTickets:
        output_string += f"Traveler: {ticket[0]} Dato: {ticket[2]} Operatør: {ticket[7]} \nOrderNummer: {ticket[1]}  Fra '{ticket[4]}' Til  '{ticket[5]}' Avgangstid: '{ticket[6]}'\N{HOURGLASS}\n\n"
        seteBillettInformasjon = getSeteBillett(ticket[1], brukerID)
        if seteBillettInformasjon:
          for billett in seteBillettInformasjon:
            sete = f"BillettID: {billett[0]} Sete: {billett[1]}  Vogn nummer: {billett[2]}\n"
            output_string += sete
            line = ""
          for i in range(len(sete)):
            line += "-"
          output_string += line + "\n"
            

            
        kupeBillettInformasjon = getKupeebillett(ticket[1], brukerID)
        if kupeBillettInformasjon:
          for billett in kupeBillettInformasjon:
            kup = f"BillettID: {billett[0]} Kupe: {billett[1]} SengeNr: {billett[2]}  Vogn nummer: {billett[3]}\n"
            output_string += kup
            line = ""
          for i in range(len(kup)):
            line += "-"
          output_string += line + "\n"
            
    if not output_string:
        print("Ingen reiser funnet")
        return
    print(output_string)
	 

def getUser():
    '''
        Henter brukerID basert på email til en bruker. Spør på nytt om bruker ikke finnes.

        Returns:
            user (list): En liste med brukerens informasjon
    '''
    email = input("Skriv in email('ctrl + c' to quit): ")

    if not email:
        print("Du kan ikke skrive inn en tom streng. Prøv igjen.")
        return getUser()

    userID = cursor.execute('''
        SELECT *
        from kunde
        WHERE Epost == :email
    ''', {'email': email})
    list = userID.fetchall()

    if not list:
        print("Ugyldig email. Prøv igjen.")
        return getUser()

    return list[0]

def getSeteBillett(ordreNr, brukerID):
    '''
        Henter setebilletter basert på ordrenummer til en bruker. Spør på nytt om billett ikke finnes.

        Returns:
            ticket (list): En liste med billettinformasjon
    '''

    if not ordreNr:
        print("Du kan ikke skrive inn en tom streng. Prøv igjen.")
        return getSeteBillett()

    ticket = cursor.execute('''
    SELECT BillettID, SeteNr, NrIVognOppsett
    FROM KundeOrdre NATURAL JOIN BillettSete
         NATURAL JOIN Sete
         INNER JOIN SitteVogn ON BillettSete.VognID = SitteVogn.VognID
    WHERE KundeOrdre.KundeNr = :brukerID AND OrdreNr = :ordreNr
    ''',{'ordreNr': ordreNr, 'brukerID': brukerID})
    list = ticket.fetchall()
    print(list)

    if not list:
        return []

    return list

def getKupeebillett(ordreNr:str, brukerID:str):
    '''
        Henter kupeebilletter basert på ordrenummer til en bruker. Spør på nytt om billett ikke finnes.

        Returns:
            ticket (list): En liste med billettinformasjon
    '''

    if not ordreNr:
        print("Du kan ikke skrive inn en tom streng. Prøv igjen.")
        return getKupeebillett()

    ticket = cursor.execute('''
      SELECT BillettID, KupeeNr, SengeNr, NrIVognOppsett
      FROM KundeOrdre NATURAL JOIN BillettKupee
           NATURAL JOIN Kupee
           INNER JOIN SoveVogn ON BillettKupee.VognID = SoveVogn.VognID
      WHERE KundeOrdre.KundeNr = :brukerID AND KundeOrdre.OrdreNr = :ordreNr
    ''',{'ordreNr': ordreNr, 'brukerID': brukerID})
    list = ticket.fetchall()

    if not list:
        return []

    return list
main()

con.commit()