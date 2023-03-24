import sqlite3
import datetime
from datetime import datetime, timedelta
con = sqlite3.connect('jernbane.db')
cursor = con.cursor()

def find_time():
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

def datoInput():
    dato = input("Dato (for.eks 2023-04-03): \n\n")
    try:
        dato = datetime.strptime(dato, "%Y-%m-%d")
        return dato
    except:
        print("Ikke gyldig dato, prøv igjen")
        return datoInput()

def tidspunktInput():
    tidspunkt = input("Tidspunkt (for.eks 12:30): \n\n")
    try:
        tidspunkt = datetime.strptime(tidspunkt, "%H:%M")
        return tidspunkt
    except:
        print("Ikke gyldig tidspunkt, prøv igjen")
        return tidspunktInput()
    
def user_time():
    date = datoInput().date()
    time = str(tidspunktInput().time())[:-3]
    return date, time

def main():
    bruker = getUser()
    print(f"Velkommen {bruker[1]}\n\n Epost: {bruker[2]}, Telefon: {bruker[3]}, BrukerID: {bruker[0]}\n")
    fremtidige_reiser(bruker[0])
    
def fremtidige_reiser(brukerID:str):
    own_time_or_date = input("Vil du se fremtidige reiser basert på tidspunktet nå, eller et spesifikt tidspunkt? (nå[n]/egendefinert[e]): \n\n")
    if own_time_or_date.lower() == "e":
        current_date, current_clock_time = user_time()
    elif own_time_or_date.lower() == "n":
        current_date, current_clock_time = find_time()
    else:
        print("Ugyldig input, prøv igjen")
        return fremtidige_reiser(brukerID)
    
    print(f"Reiser etter {current_date} {current_clock_time}\N{HOURGLASS}\n")

    res = cursor.execute(
        '''
        SELECT Kunde.Navn, KundeOrdre.OrdreNr, BillettDato, 
        BillettTogruteID, StartStasjon, SluttStasjon, 
        StasjonerIRute.Avgangstid
FROM
	Kunde
	INNER JOIN KundeOrdre ON Kunde.KundeNr == KundeOrdre.KundeID
	INNER JOIN (
		SELECT
			OrdreNr AS AlleOrderer,TogruteID AS BillettTogruteID,Dato AS BillettDato,StartStasjon,SluttStasjon
		FROM
			BillettSete
	UNION
	  SELECT
		  OrdreNr AS AlleOrderer,TogruteID AS BillettTogruteID,Dato AS BillettDato,StartStasjon,SluttStasjon
	  FROM
		  BillettKupee) 
		
		ON KundeOrdre.OrdreNr == AlleOrderer
		
		INNER JOIN TogruteForekomst on 
      (BillettDato == TogruteForekomst.Dato and BillettTogruteID == TogruteForekomst.TogruteID)
		
		INNER JOIN Togrute ON 
      TogruteForekomst.TogruteID == Togrute.TogruteID
		
		INNER JOIN StasjonerIRute on 
      (StasjonerIRute.TogruteID == Togrute.TogruteID and  StasjonerIRute.JernbanestasjonNavn == StartStasjon)
		
		WHERE Kunde.KundeNr == :brukerID and 
      (BillettDato > :current_date or (BillettDato == :current_date and StasjonerIRute.Avgangstid > :current_clock_time))
		
    ''',{'brukerID': brukerID, 'current_date': current_date, 'current_clock_time': current_clock_time})
    allTickets = res.fetchall()

    output_string = ""

    for ticket in allTickets:
        output_string += f"Traveler: {ticket[0]} Date: {ticket[2]}\nOrderNumber: {ticket[1]}  From '{ticket[4]}' To  '{ticket[5]}'  Departure: '{ticket[6]}'\N{HOURGLASS}\n\n"

    
    print(output_string)
	 

def getUser():
    '''
        Henter brukerID basert på email til en bruker. Spør på nytt om bruker ikke finnes.
    '''
    email = input("Skriv in email('ctrl + c' to quit): ")

    if not email or len(email) < 2:
        print("Ugyldig email. Prøv igjen")
        return getUser()

    userID = cursor.execute('''
        SELECT *
        from kunde
        WHERE Epost == :email
    ''',{'email': email})
    list = userID.fetchall()

    if not list:
        print("Ugyldig email, prøv på nytt.")
        return getUser()

    return list[0]

def ankomst_avgangstider(stasjon_navn: list):
    output = []
    for stasjon in stasjon_navn:
        output.append(ankomst_avgangstider_single(stasjon))
    return output

def ankomst_avgangstider_single(stasjon_navn:str):
    capitalized_navn = stasjon_navn.capitalize()
    response = cursor.execute('''
        SELECT Ankomsttid, Avgangstid, JernbanestasjonNavn
        FROM Togrute inner JOIN StasjonerIRute on Togrute.TogruteID == StasjonerIRute.TogruteID
        WHERE
	JernbanestasjonNavn == :stasjon_navn
    ''',{'stasjon_navn': capitalized_navn})
    tider = response.fetchall()

    # print(tider)

    # if not tider:
    #     print("Ugyldig stasjon, prøv på nytt.")
    #     return ankomst_avgangstider()
    return tider

main()

con.commit()