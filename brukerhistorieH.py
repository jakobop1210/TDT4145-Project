import sqlite3
import datetime

con = sqlite3.connect('jernbane.db')
cursor = con.cursor()

def find_time():
    current_time = datetime.datetime.now()
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

    print(current_date)
    print(current_clock_time)

    return current_date, current_clock_time

    
def fremtidige_reiser():
    brukerID = getUserID()
    current_date, current_clock_time = find_time()

    res = cursor.execute(
        '''
        SELECT
	Kunde.Navn,
	KundeOrdre.OrdreNr,
	BillettDato,
	BillettTogruteID,
	StartStasjon,
	SluttStasjon,
	StasjonerIRute.Avgangstid
FROM
	Kunde
	INNER JOIN KundeOrdre ON Kunde.KundeNr == KundeOrdre.KundeID
	INNER JOIN (
		SELECT
			OrdreNr AS AlleOrderer,
			TogruteID AS BillettTogruteID,
			Dato AS BillettDato,
			StartStasjon,
			SluttStasjon
		FROM
			BillettSete
	UNION
	SELECT
		OrdreNr AS AlleOrderer,
		TogruteID AS BillettTogruteID,
		Dato AS BillettDato,
		StartStasjon,
		SluttStasjon
	FROM
		BillettKupee) 
		
		ON KundeOrdre.OrdreNr == AlleOrderer
		
		INNER JOIN TogruteForekomst on (BillettDato == TogruteForekomst.Dato and BillettTogruteID == TogruteForekomst.TogruteID)
		
		INNER JOIN Togrute ON TogruteForekomst.TogruteID == Togrute.TogruteID
		
		INNER JOIN StasjonerIRute on (StasjonerIRute.TogruteID == Togrute.TogruteID and  StasjonerIRute.JernbanestasjonNavn == StartStasjon)
		
		WHERE Kunde.KundeNr == :brukerID and (BillettDato > :current_date or (BillettDato == :current_date and StasjonerIRute.Avgangstid > :current_clock_time))
		'''
    ,{'brukerID': brukerID, 'current_date': current_date, 'current_clock_time': current_clock_time})
    allTickets = res.fetchall()

    output_string = ""

    for ticket in allTickets:
        output_string += f"Your ticket {ticket[0]} for a travel the {ticket[2]}\nOrderNumber: {ticket[1]}  From {ticket[4]} To  {ticket[5]} \N{HOURGLASS} Departure: {ticket[6]}\n\n"

    
    print(output_string)
	 

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

    if not list:
        print("Ugyldig email, prøv på nytt.")
        return getUserID()

    return str(list[0][0])

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

fremtidige_reiser()

con.commit()