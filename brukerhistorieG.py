import brukerhistorieD
import hjelpefunksjoner
import sqlite3
con = sqlite3.connect('jernbane.db')
cursor = con.cursor()

def finnLedigeSeterOgKjop():
    """
    Hovedfunksjon for programmet. Lar brukeren se alle ledige billetter på en dato og så kjøpe dem
    """

    kundeNr = userLogin()

    #FINN ALLE TOGRUTEFOREKOMSTENE SOM INNEHOLDER START OG SLUTTSTASJONEN OG DATOEN
    stasjoner = hjelpefunksjoner.startOgSluttStasjonsInput()
    startstasjon = stasjoner[0]
    sluttstasjon = stasjoner[1]
    dato = hjelpefunksjoner.datoInput()
    togruter = brukerhistorieD.finnTogruterPåDato([startstasjon, sluttstasjon], dato, '00:00')

    #FINN ALLE LEDIGE SETER PÅ DELETOGRUTENE (delstrekningene mellom start og sluttstasjon)
    count = 1

    ledigeSeterForSitte = dict()
    ledigeSeterForSove = dict()
    print()
    for togruteforekomst in togruter:
        print(f"Ledige plasser for togrute {count} den {togruteforekomst[-1]} kl {togruteforekomst[1]} fra {startstasjon} til {sluttstasjon}:") #Kanskje importe en funksjon fra en annen brukerhistorie for å finne start og sluttstasjon for togrute
    
        responseSeter = cursor.execute('''
            SELECT DISTINCT tr.TogruteID, sv.NrIVognOppsett, sv.VognID, s.SeteNr
            FROM ((Togrute AS tr INNER JOIN SitteVogn AS sv ON (tr.TogruteID = sv.TogruteID)) 
                INNER JOIN Sete AS s ON (sv.VognID = s.VognID)) 
                INNER JOIN Togruteforekomst AS trf ON (tr.TogruteID = trf.TogruteID)
            WHERE trf.Dato = :Dato 
                AND tr.TogruteID = :TogruteID 
                AND (SeteNr, s.VognID) NOT IN (
                    SELECT DISTINCT bs.SeteNr, bs.VognID
                    FROM BillettSete AS bs INNER JOIN DelstrekningForSete AS dfs ON (bs.BillettID = dfs.BillettID)
                    WHERE bs.TogruteID = :TogruteID 
                        AND bs.Dato = :Dato 
                        AND OrdreNr IS NOT NULL 
                        AND dfs.DelstrekningsID IN ( 
                            SELECT ds1.DelstrekningsID
                            FROM Delstrekning as ds1
                            WHERE ds1.DelstrekningsID >=  (
                                SELECT ds.DelstrekningsID
                                FROM (((Togrute AS tr INNER JOIN StasjonerIRute AS sir ON (tr.TogruteID = sir.TogruteID)) 
                                    INNER JOIN JernbaneStasjon as js ON (sir.JernbanestasjonNavn = js.Navn)) 
                                    INNER JOIN Delstrekning AS ds ON (js.Navn = ds.StartStasjon)) 
                                WHERE tr.TogruteID = :TogruteID AND ds.StartStasjon = :StartStasjon
                            )
                        AND DelstrekningsID <= (
                            SELECT DelstrekningsID
                            FROM (((Togrute AS tr INNER JOIN StasjonerIRute AS sir ON (tr.TogruteID = sir.TogruteID)) 
                                INNER JOIN JernbaneStasjon as js ON (sir.JernbanestasjonNavn = js.Navn)) 
                                INNER JOIN Delstrekning AS ds ON (js.Navn = ds.StartStasjon)) 
                            WHERE tr.TogruteID = :TogruteID AND ds.SluttStasjon = :SluttStasjon
                        )
                    )
            ) 
        ''', {'TogruteID': togruteforekomst[0], 'Dato': togruteforekomst[-1], 'StartStasjon': startstasjon, 'SluttStasjon': sluttstasjon}).fetchall()

        #Print alle ledige setene per vogn
        vognNrIOppsett = list(set([x[1] for x in responseSeter]))
        antall_vogner = len(vognNrIOppsett)
        for vognIdx in range(int(antall_vogner)):
            ledige_seter_i_vogn = []
            for sete in responseSeter: 
                if int(sete[1]) == vognNrIOppsett[vognIdx]:
                    ledige_seter_i_vogn.append(str(sete[-1]))
                    sitteKey = (str(count)+str(vognNrIOppsett[vognIdx])) #Identifiserer ved en kombinasjon av togruteID og vognNrIoppsett
                    ledigeSeterForSitte[sitteKey] = ledigeSeterForSitte[sitteKey] + [int(sete[-1])] if sitteKey in ledigeSeterForSitte else [int(sete[-1])]
            responsStreng = f"Ledige seter i vogn {vognNrIOppsett[vognIdx]}: {', '.join(ledige_seter_i_vogn)}" if len(ledige_seter_i_vogn) > 0 else "Ingen ledige seter"
            print(responsStreng)

        #print(f"Ledige kupeer for togrute {count} den {togruteforekomst[-1]} kl {togruteforekomst[1]} fra {startstasjon} til {sluttstasjon}:")
        responseKupeer = cursor.execute('''
            SELECT DISTINCT sv.NrIVognOppsett, k.KupeeNr, sv.VognID
            FROM ((Togrute AS tr INNER JOIN SoveVogn AS sv ON (tr.TogruteID = sv.TogruteID)) INNER JOIN Kupee AS k ON (sv.VognID = k.VognID)) INNER JOIN Togruteforekomst AS trf ON (tr.TogruteID = trf.TogruteID)
            WHERE trf.Dato = :Dato AND tr.TogruteID = :TogruteID AND (KupeeNr, k.VognID) NOT IN (
                SELECT bk.KupeeNr, bk.VognID
                FROM BillettKupee AS bk
                WHERE bk.TogruteID = :TogruteID AND bk.Dato = :Dato AND OrdreNr IS NOT NULL
            ) 
        ''', {'TogruteID': togruteforekomst[0], 'Dato': togruteforekomst[-1]}).fetchall()

        #Print alle ledige kupeer per vogn
        harLedig = False
        vognNrIOppsett = list(set([x[0] for x in responseKupeer]))
        antall_vogner = len(vognNrIOppsett)
        for vognIdx in range(int(antall_vogner)):
            ledige_seter_i_vogn = []
            for kupee in responseKupeer:
                if int(kupee[0] == vognNrIOppsett[vognIdx]):
                    harLedig = True
                    soveKey = (str(count)+str(vognNrIOppsett[vognIdx]))
                    ledigeSeterForSove[soveKey] = ledigeSeterForSove[soveKey] + [int(kupee[1])] if soveKey in ledigeSeterForSove else [int(kupee[1])]
                    ledige_seter_i_vogn.append(str(kupee[1]))
        responsStreng = f"Ledige kupeer i vogn {vognNrIOppsett[vognIdx]}: {', '.join(ledige_seter_i_vogn)}" if harLedig > 0 else "Ingen ledige kupeer"
        print(responsStreng)
        print()
        count += 1

    #KJØP BILLETTER
    print()
    typeBillett = velgTypeBillett() 

    print("Vennligst velg hvilken billett du vil kjøpe:")
    valgtTogrute, valgtTogruteNr = velgTogruteNr(togruter, ledigeSeterForSitte, ledigeSeterForSove, typeBillett) 

    cursor.execute('''
        INSERT INTO KundeOrdre (Dag, tid, KundeNr, Dato, TogruteID) VALUES (:Dato, :Tid, :KundeNr, :Dato, :TogruteID)
    ''', {'Dato': dato, 'Tid': dato, 'KundeNr': kundeNr, 'TogruteID': valgtTogrute[0]}).fetchall()
    ordreID = cursor.lastrowid

    valgteSeter = dict()
    if (typeBillett == "1"):
        while True:
            valgtSeteNr, valgtVognNr = velgSitteBillett(ordreID, valgtTogrute[0], valgtTogrute[-1], startstasjon, sluttstasjon, ledigeSeterForSitte, valgtTogruteNr, valgteSeter)
            valgteSeter[valgtVognNr] = valgteSeter[valgtTogruteNr] + [valgtSeteNr] if valgtTogruteNr in valgteSeter else [valgtSeteNr]
            if (input(f"Vil du kjøpe flere sittebilletter for togrute {valgtTogrute[0]}? (j/n): ").lower() == "n"):
                break
    elif (typeBillett == "2"):
        velgKupeebillett(ordreID, valgtTogrute[0], valgtTogrute[-1], startstasjon, sluttstasjon, ledigeSeterForSove, valgtTogruteNr)
    else:
        print("Du valgte ikke en gyldig type billett!")

def userLogin():
    """
    Sjekker om oppgitt eposten er registrert i databasen
    return:
        usermail (str): Kundenummeret til kunden som logget inn med eposten
    """
    usermail = input("Logg inn med din epost: ").lower()
    allUserEmails = cursor.execute('''SELECT KundeNr, Epost FROM Kunde''').fetchall()
    for email in allUserEmails:
        if usermail == email[1].lower():
            print("Du er logget inn!")
            print()
            return email[0]
    else:
        print("Velg en gyldig epost!")
        return userLogin()
    
def velgTypeBillett():
    """
    Validerer at brukeren velger en gyldig type billett (type 1 eller tpye 2)
    Returns:
        type (int): Type billett brukeren valgte
    """
    type = input("Vennligst velg hvilken type billett du vil kjøpe: Sittebillett (1), Kupeebillett (2) ")
    if type == "1" or type == "2":
        return type
    else:
        print("Du valgte ikke en gyldig type billett!")
        return velgTypeBillett()

def velgTogruteNr(togruter, ledigeSeterForSitte, ledigeSeterForSove, typeBillett): #problem: kan velge togrute som har null kupeer
    """
    Validerer at brukeren velger et gyldig togrute nummer

    Parameters:
        togruter (list): Liste med alle togruter som passerer gjennom valgte stasjoner
    Returns:
        togruteNr (int): Togrute nummeret brukeren valgte
    """
    togruteNr = input("Velg et togrute nummer: ")
   
    if int(togruteNr) < 1 or int(togruteNr) > len(togruter):
        print("Velg et gyldig togrute nummer!")
        return velgTogruteNr(togruter, ledigeSeterForSitte, ledigeSeterForSove, typeBillett)
    else:
        if int(typeBillett) == 2: # Passer på at brukeren velger et togrute som har kupeer
            gyldigeTogruteNr = [str(x[0]) for x in ledigeSeterForSove.keys()]
            if togruteNr not in gyldigeTogruteNr:
                print("Velg et gyldig togrute nummer!")
                return velgTogruteNr(togruter, ledigeSeterForSitte, ledigeSeterForSove, typeBillett)
        else: # Passer på at brukeren velger et togrute som har sittebilletter
            gyldigeTogruteNr = [str(x[0]) for x in ledigeSeterForSitte.keys()]
            if togruteNr not in gyldigeTogruteNr:
                print("Velg et gyldig togrute nummer!")
                return velgTogruteNr(togruter, ledigeSeterForSitte, ledigeSeterForSove, typeBillett)
        return togruter[int(togruteNr)-1], togruteNr

def velgSitteBillett(ordreID, TogruteID, dato, startstasjon, sluttstasjon, ledigeSeterForSitte, valgtTogruteNr, valgteSeter):
    """
    Finner hvilken vogn og sete som brukeren vil kjøpe og lager en bestilling basert på dette

    Parameters:
        ordreID (int): ID-en til ordren som skal opprettes
        TogruteID (int): ID-en til togruten som skal opprettes
        dato (str): Datoen brukeren skal reise
        startstasjon (str): Navnet på startstasjonen
        sluttstasjon (str): Navnet på sluttstasjonen
        ledigeSeterForSitte (dict): Dictionary med alle ledige seter for sittebilletter
        valgtTogruteNr (int): Togrute nummeret brukeren valgte
        valgteSeter (dict): Dictionary med alle seter som er valgt av brukeren tidligere
    Returns:
    """
    valgtVognNr = input("Velg vogn nummer: ")

    #Finner alle ledige seter for valgt vogn og togrute
    vognKey = str(valgtTogruteNr) + str(valgtVognNr)
    
    if vognKey not in ledigeSeterForSitte: #sjekker om oppgitt vogn er tilgjengelig
        print("Velg et gyldig vogn nummer!")
        return velgSitteBillett(ordreID, TogruteID, dato, startstasjon, sluttstasjon, ledigeSeterForSitte, valgtVognNr, valgteSeter)
    seteNr = input("Velg sete nummer: ")
    
    if int(seteNr) not in ledigeSeterForSitte[vognKey]: #sjekker om oppgitt sete er tilgjengelig for oppgitt vogn
        print()
        print("Setenummeret var ikke gyldig! Velg er gyldig vognnummer og setenummer på nytt:")
        print(ledigeSeterForSitte[vognKey])
        return velgSitteBillett(ordreID, TogruteID, dato, startstasjon, sluttstasjon, ledigeSeterForSitte, valgtVognNr, valgteSeter)
    if int(valgtVognNr) in valgteSeter.keys():
        if int(seteNr) in valgteSeter[int(valgtVognNr)]:
            print("Du har allerede valgt dette setet!")
            return velgSitteBillett(ordreID, TogruteID, dato, startstasjon, sluttstasjon, ledigeSeterForSitte, valgtVognNr, valgteSeter)
    korresponderendeVognID = cursor.execute('''
        SELECT VognID
        FROM SitteVogn NATURAL JOIN Togrute
        WHERE TogruteID = :TogruteID AND NrIVognOppsett = :NrIVognOppsett
    ''', {'TogruteID': TogruteID, 'NrIVognOppsett': valgtVognNr}).fetchone()[0]

    cursor.execute(''' 
        INSERT INTO BillettSete(OrdreNr, Dato, TogruteID, SeteNr, VognID, StartStasjon, SluttStasjon) VALUES (:OrdreNr, :Dato, :TogruteID, :SeteNr, :VognID, :StartStasjon, :SluttStasjon)
    ''', {'OrdreNr': ordreID, 'Dato': dato, 'TogruteID': TogruteID, 'SeteNr': seteNr, 'VognID': korresponderendeVognID, 'StartStasjon': startstasjon, 'SluttStasjon': sluttstasjon})
    BillettID = cursor.lastrowid

    #Finner alle delstrekningene som inngår i reisen fra startstasjon til sluttstasjon
    delstrekninger = cursor.execute('''
        SELECT DelstrekningsID
        FROM Delstrekning
        WHERE DelstrekningsID >=  (
            SELECT DelstrekningsID
            FROM (((Togrute AS tr INNER JOIN StasjonerIRute AS sir ON (tr.TogruteID = sir.TogruteID)) 
                 INNER JOIN JernbaneStasjon as js ON (sir.JernbanestasjonNavn = js.Navn)) 
                 INNER JOIN Delstrekning AS ds ON (js.Navn = ds.StartStasjon)) 
            WHERE tr.TogruteID = :TogruteID AND ds.StartStasjon = :startStasjon
            )
        AND DelstrekningsID <= (
            SELECT DelstrekningsID
            FROM (((Togrute AS tr INNER JOIN StasjonerIRute AS sir ON (tr.TogruteID = sir.TogruteID)) 
                 INNER JOIN JernbaneStasjon as js ON (sir.JernbanestasjonNavn = js.Navn)) 
                INNER JOIN Delstrekning AS ds ON (js.Navn = ds.StartStasjon)) 
            WHERE tr.TogruteID = :TogruteID AND ds.SluttStasjon = :sluttStasjon
            )
    ''', {'TogruteID': TogruteID, 'startStasjon': startstasjon, 'sluttStasjon': sluttstasjon}).fetchall()

    for delstrekning in delstrekninger:
        cursor.execute('''
            INSERT INTO DelstrekningForSete(BillettID, DelstrekningsID) VALUES (:BillettID, :DelstrekningsID)
        ''', {'BillettID': BillettID, 'DelstrekningsID': delstrekning[0]})

    print("Sete bestilt!")
    return int(seteNr), int(valgtVognNr)

def velgKupeebillett(ordreID, TogruteID, dato, startstasjon, sluttstasjon, ledigeSeterForSove, valgtTogruteNr):
    """
    Finner hvilken vogn og kupee som brukeren vil kjøpe og lager en bestilling basert på det.

    Parameters: 
        ordreID (int): ID-en til ordren som skal opprettes
        togruteID (int): ID-en til togruten som skal kjøpes billett til
        dato (str): Datoen brukeren skal reise
        startstasjon (str): Navnet på stasjonen som toget starter på
        sluttstasjon (str): Navnet på stasjonen som toget ender på
        ledigeSeterForSove (dict): En dictionary med alle ledige kupeer for sovevogner
        valgtTogruteNr (int): Togrute nummeret brukeren valgte
    Returns:
    """
    valgtVognNr = input("Velg vogn nummer: ")
    vognKey = str(valgtTogruteNr) + str(valgtVognNr)
    if vognKey not in ledigeSeterForSove: #Sjekker om vognnummeret er lik en av nummerene til vognene som er sovevogner
        print("Velg et gyldig vogn nummer!")
        return velgKupeebillett(ordreID, TogruteID, dato, startstasjon, sluttstasjon, ledigeSeterForSove, valgtTogruteNr)
    kupeeNr = input("Velg kupée nummer: ")
    if int(kupeeNr) not in ledigeSeterForSove[vognKey]: #Sjekker om kupéenummeret er gyldig for den valgte vognen
        print("Velg et gyldig kupée nummer!")
        return velgKupeebillett(ordreID, TogruteID, dato, startstasjon, sluttstasjon, ledigeSeterForSove, valgtTogruteNr)
    antallSenger = input("Hvor mange senger vil du ha? ")

    korresponderendeVognID = cursor.execute('''
        SELECT VognID
        FROM SoveVogn NATURAL JOIN Togrute
        WHERE TogruteID = :TogruteID AND NrIVognOppsett = :NrIVognOppsett
    ''', {'TogruteID': TogruteID, 'NrIVognOppsett': valgtVognNr}).fetchone()[0]

    #Sjekker om kunden bestiller en eller to senger i en kupée
    if int(antallSenger) == 2:
        cursor.execute(''' 
            INSERT INTO BillettKupee (SengeNr, OrdreNr, Dato, TogruteID, KupeeNr, VognID, StartStasjon, SluttStasjon) VALUES 
            (1, :OrdreNr, :Dato, :TogruteID, :KupeeNr, :VognID, :StartStasjon, :SluttStasjon),
            (2, :OrdreNr, :Dato, :TogruteID, :KupeeNr, :VognID, :StartStasjon, :SluttStasjon);
        ''', {'OrdreNr': ordreID, 'Dato': dato, 'TogruteID': TogruteID, 'KupeeNr': kupeeNr, 'VognID': korresponderendeVognID, 'StartStasjon': startstasjon, 'SluttStasjon': sluttstasjon})
        print("Din ordre er bestilt!")
    else:
        cursor.execute(''' 
            INSERT INTO BillettKupee (SengeNr, OrdreNr, Dato, TogruteID, KupeeNr, VognID, StartStasjon, SluttStasjon) VALUES (:SengeNr, :OrdreNr, :Dato, :TogruteID, :KupeeNr, :VognID, :StartStasjon, :SluttStasjon)
        ''', {'SengeNr':1, 'OrdreNr': ordreID, 'Dato': dato, 'TogruteID': TogruteID, 'KupeeNr': kupeeNr, 'VognID': korresponderendeVognID, 'StartStasjon': startstasjon, 'SluttStasjon': sluttstasjon})
        print("Din ordre er bestilt!")

if __name__ == "__main__":
    finnLedigeSeterOgKjop()

con.commit()