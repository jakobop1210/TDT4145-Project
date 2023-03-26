import brukerhistorieD
import hjelpefunksjoner
from datetime import datetime, timedelta
import sqlite3
con = sqlite3.connect('jernbane.db')
cursor = con.cursor()

def finn_ledige_seter():
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
    togruterID = [togrute[0] for togrute in togruter]

    #FINN ALLE LEDIGE SETER PÅ DELETOGRUTENE (delstrekningene mellom start og sluttstasjon)
    count = 1

    kupeeDict = {}
    for togruteforekomst in togruter:
        print()
        print(f"Ledige seter for togrute {count} den {togruteforekomst[-1]} kl {togruteforekomst[1]} fra {startstasjon} til {sluttstasjon}:") #Kanskje importe en funksjon fra en annen brukerhistorie for å finne start og sluttstasjon for togrute
    
        responseSeter = cursor.execute('''
            SELECT DISTINCT tr.TogruteID, sv.NrIVognOppsett, s.SeteNr
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
        antall_vogner = len(set([x[1] for x in responseSeter]))
        for vognIdx in range(1, int(antall_vogner) + 1):
            ledige_seter_i_vogn = []
            for sete in responseSeter:
                if int(sete[1]) == vognIdx:
                    ledige_seter_i_vogn.append(str(sete[-1]))
            responsStreng = f"Ledige seter i vogn {vognIdx}: {', '.join(ledige_seter_i_vogn)}" if len(ledige_seter_i_vogn) > 0 else "Ingen ledige seter"
            print(responsStreng)

        print()
        print(f"Ledige kupeer for togrute {count} den {togruteforekomst[-1]} kl {togruteforekomst[1]} fra {startstasjon} til {sluttstasjon}:")
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
        antall_vogner = len(set([x[0] for x in responseKupeer]))
        harLedig = False
        for vognIdx in range(int(antall_vogner)):
            ekteVognIdx = list(set([x[0] for x in responseKupeer]))[vognIdx]
            ledige_seter_i_vogn = []
            for kupee in responseKupeer:
                kupeeKey = str(togruteforekomst[0]) + str(togruteforekomst[1]) + str(kupee[0]) #Unik key for hver vogn som inneholder kupee
                if kupeeKey not in kupeeDict:
                    kupeeDict[kupeeKey] = kupee[-1]
                if int(kupee[0] == ekteVognIdx):
                    harLedig = True
                    ledige_seter_i_vogn.append(str(kupee[1]))
        responsStreng = f"Ledige kupeer i vogn {ekteVognIdx}: {', '.join(ledige_seter_i_vogn)}" if harLedig > 0 else "Ingen ledige kupeer"
        print(responsStreng)
        count += 1
    #FINN ALLE LEDIGE KUPEER PÅ DELETOGRUTENE
    #for togruteforekomst in togruter:

    #KJØP BILLETTER
    print()
    typeBillett = velgTypeBillett() 

    print("Vennligst velg hvilken billett du vil kjøpe:")
    valgtTogrute = velgTogruteNr(togruter) 

    cursor.execute('''
        INSERT INTO KundeOrdre (Dag, tid, KundeNr, Dato, TogruteID) VALUES (:Dato, :Tid, :KundeNr, :Dato, :TogruteID)
    ''', {'Dato': dato, 'Tid': dato, 'KundeNr': kundeNr, 'TogruteID': valgtTogrute[0]}).fetchall()
    ordreID = cursor.lastrowid

    if (typeBillett == "1"):
        while True:
            velgSitteBillett(ordreID, valgtTogrute[0], valgtTogrute[-1], startstasjon, sluttstasjon)
            if (input(f"Vil du kjøpe flere sittebilletter for togrute {valgtTogrute[0]}? (j/n): ").lower() == "n"):
                break
    elif (typeBillett == "2"):
        velgKupeebillett(ordreID, valgtTogrute[0], valgtTogrute[-1], kupeeDict, startstasjon, sluttstasjon)
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
    type = input("Vennligst velg hvilken type billett du vil kjøpe: (1) Sittebillett, (2) Kupeebillett ")
    if type == "1" or type == "2":
        return type
    else:
        print("Du valgte ikke en gyldig type billett!")
        return velgTypeBillett()

def velgTogruteNr(togruter):
    """
    Validerer at brukeren velger et gyldig togrute nummer

    Parameters:
       gyldIDArr (Array): Liste med alle togruteID'er som kan velges
    Returns:
        togruteNr (int): Togrute nummeret brukeren valgte
    """

    togruteNr = input("Velg et togrute nummer: ")
   
    if int(togruteNr) < 1 or int(togruteNr) > len(togruter):
        print("Velg et gyldig togrute nummer!")
        return velgTogruteNr(togruter)
    else:
        return togruter[int(togruteNr)-1]

def velgSitteBillett(ordreID, togrutenr, dato, startstasjon, sluttstasjon):
    """
    Finner hvilken vogn og sete som brukeren vil kjøpe og lager en bestilling basert på dette

    Parameters:
        ordreID (int): ID-en til ordren som skal opprettes
        togrutenr (int): ID-en til togruten som skal kjøpes billett til
        dato (str): Datoen brukeren skal reise
        startstasjon (str): Navnet på startstasjonen
        sluttstasjon (str): Navnet på sluttstasjonen
    Returns:
    """
    vognNr = input("Velg vogn nummer: ")

    #Finner alle ledige seter for valgt vogn og togrute
    gyldigeSeteNr = cursor.execute('''
        SELECT DISTINCT s.SeteNr
        FROM ((Togrute AS tr INNER JOIN SitteVogn AS sv ON (tr.TogruteID = sv.TogruteID)) INNER JOIN Sete AS s ON (sv.VognID = s.VognID)) INNER JOIN Togruteforekomst AS trf ON (tr.TogruteID = trf.TogruteID)
        WHERE tr.TogruteID = :TogruteID AND trf.Dato = :Dato AND s.SeteNr NOT IN (
            SELECT bs.SeteNr
            FROM BillettSete AS bs INNER JOIN Sittevogn AS sv2 ON (bs.VognID = sv2.VognID)
            WHERE bs.Dato = :Dato AND bs.TogruteID = :TogruteID AND sv2.NrIVognOppsett = :NrIVognOppsett
        )
    ''', {'Dato': dato, 'TogruteID': togrutenr, 'NrIVognOppsett': vognNr}).fetchall()
    gyldigeSeteNr = [x[0] for x in gyldigeSeteNr]
    print("HER")
    print(gyldigeSeteNr)

    gyldigeVognNr = cursor.execute('''
        SELECT DISTINCT sv.NrIVognOppsett
        FROM ((Togrute AS tr INNER JOIN SitteVogn AS sv ON (tr.TogruteID = sv.TogruteID)) INNER JOIN Sete AS s ON (sv.VognID = s.VognID)) INNER JOIN Togruteforekomst AS trf ON (tr.TogruteID = trf.TogruteID)
        WHERE tr.TogruteID = :TogruteID AND trf.Dato = :Dato 
    ''', {'Dato': dato, 'TogruteID': togrutenr}).fetchall()
    gyldigeVognNr = [x[0] for x in gyldigeVognNr]

    if int(vognNr) not in gyldigeVognNr: #sjekker om oppgitt vogn er tilgjengelig
        print("Velg et gyldig vogn nummer!")
        return velgSitteBillett(ordreID, togrutenr, dato, startstasjon, sluttstasjon)
    seteNr = input("Velg sete nummer: ")
    if int(seteNr) not in gyldigeSeteNr: #sjekker om oppgitt sete er tilgjengelig for oppgitt vogn
        print("Velg et gyldig sete nummer!")
        return velgSitteBillett(ordreID, togrutenr, dato, startstasjon, sluttstasjon)
    cursor.execute(''' 
        INSERT INTO BillettSete (OrdreNr, Dato, TogruteID, SeteNr, VognID, StartStasjon, SluttStasjon) VALUES (:OrdreNr, :Dato, :TogruteID, :SeteNr, :VognID, :StartStasjon, :SluttStasjon)
    ''', {'OrdreNr': ordreID, 'Dato': dato, 'TogruteID': togrutenr, 'SeteNr': seteNr, 'VognID': vognNr, 'StartStasjon': startstasjon, 'SluttStasjon': sluttstasjon})
    BillettID = cursor.lastrowid

    #Finner alle delstrekningene som inngår i reisen fra startstasjon til sluttstasjon
    delstrekninger = cursor.execute('''
        SELECT DelstrekningsID
        FROM Delstrekning
        WHERE DelstrekningsID >=  (
            SELECT DelstrekningsID
            FROM (((Togrute AS tr INNER JOIN StasjonerIRute AS sir ON (tr.TogruteID = sir.TogruteID)) INNER JOIN JernbaneStasjon as js ON (sir.JernbanestasjonNavn = js.Navn)) INNER JOIN Delstrekning AS ds ON (js.Navn = ds.StartStasjon)) 
            WHERE tr.TogruteID = :TogruteID AND ds.StartStasjon = :startStasjon
            )
        AND DelstrekningsID <= (
            SELECT DelstrekningsID
            FROM (((Togrute AS tr INNER JOIN StasjonerIRute AS sir ON (tr.TogruteID = sir.TogruteID)) INNER JOIN JernbaneStasjon as js ON (sir.JernbanestasjonNavn = js.Navn)) INNER JOIN Delstrekning AS ds ON (js.Navn = ds.StartStasjon)) 
            WHERE tr.TogruteID = :TogruteID AND ds.SluttStasjon = :sluttStasjon
            )
    ''', {'TogruteID': togrutenr, 'startStasjon': startstasjon, 'sluttStasjon': sluttstasjon}).fetchall()

    for delstrekning in delstrekninger:
        cursor.execute('''
            INSERT INTO DelstrekningForSete(BillettID, DelstrekningsID) VALUES (:BillettID, :DelstrekningsID)
        ''', {'BillettID': BillettID, 'DelstrekningsID': delstrekning[0]})

    print("Sete bestilt!")

def velgKupeebillett(ordreID, togrutenr, dato, kupeeDict, startstasjon, sluttstasjon):
    """
    Finner hvilken vogn og kupee som brukeren vil kjøpe og lager en bestilling basert på det.

    Parameters: 
        ordreID (int): ID-en til ordren som skal opprettes
        togrutenr (int): Togrute nummeret som brukeren har valgt
        kupeeDict (dict): En dictionary som kan oversette nummeret til vognen (relativt til toget) til vognID-en
        gyldigeKupeeNr (dict): En dictionary som inneholder hvilke kupéer som er ledige i hver vogn
        startstasjon (str): Navnet på stasjonen som toget starter på
        sluttstasjon (str): Navnet på stasjonen som toget ender på
    Returns:
    """
    vognNr = input("Velg vogn nummer: ")

    gyldigeVognNr = cursor.execute('''
        SELECT DISTINCT sv.NrIVognOppsett
        FROM ((Togrute AS tr INNER JOIN Sovevogn AS sv ON (tr.TogruteID = sv.TogruteID)) INNER JOIN Kupee AS k ON (sv.VognID = k.VognID)) INNER JOIN Togruteforekomst AS trf ON (tr.TogruteID = trf.TogruteID)
        WHERE tr.TogruteID = :TogruteID AND trf.Dato = :Dato      
    ''', {'Dato': dato, 'TogruteID': togrutenr}).fetchall()
    gyldigeVognNr = [x[0] for x in gyldigeVognNr]

    #Finner hvilke kupeer som er ledige for den vognen for valgt togtur
    gyldigeKupeeNr = cursor.execute(''' 
        SELECT DISTINCT k.Kupeenr
        FROM ((Togrute AS tr INNER JOIN Sovevogn AS sv ON (tr.TogruteID = sv.TogruteID)) INNER JOIN Kupee AS k ON (sv.VognID = k.VognID)) INNER JOIN Togruteforekomst AS trf ON (tr.TogruteID = trf.TogruteID)
        WHERE tr.TogruteID = :TogruteID AND trf.Dato = :Dato AND k.KupeeNr NOT IN (
                SELECT bk.KupeeNr
                FROM BillettKupee AS bk INNER JOIN Sovevogn AS sv2 ON (bk.VognID = sv2.VognID)
                WHERE bk.Dato = :Dato AND bk.TogruteID = :TogruteID AND sv2.NrIVognOppsett = :NrIVognOppsett
        )
    ''', {'Dato': dato, 'TogruteID': togrutenr, 'NrIVognOppsett': vognNr}).fetchall()
    gyldigeKupeeNr = [x[0] for x in gyldigeKupeeNr]

    if int(vognNr) not in gyldigeVognNr: #Sjekker om vognnummeret er lik en av nummerene til vognene som er sovevogner
        print("Velg et gyldig vogn nummer!")
        return velgKupeebillett(ordreID, togrutenr, dato, kupeeDict, startstasjon, sluttstasjon)
    kupeeNr = input("Velg kupée nummer: ")
    if int(kupeeNr) not in gyldigeKupeeNr: #Sjekker om kupéenummeret er gyldig for den valgte vognen
        print("Velg et gyldig kupée nummer!")
        return velgKupeebillett(ordreID, togrutenr, dato, kupeeDict, startstasjon, sluttstasjon)
    antallSenger = input("Hvor mange senger vil du ha? ")
    vognID = kupeeDict[str(dato) + str(togrutenr) + str(vognNr)]

    #Sjekker om kunden bestiller en eller to senger i en kupée
    if antallSenger == 2:
        cursor.execute(''' 
            INSERT INTO BillettKupee (SengeNr, OrdreNr, Dato, TogruteID, KupeeNr, VognID, StartStasjon, SluttStasjon) VALUES 
            (1, :OrdreNr, :Dato, :TogruteID, :KupeeNr, :VognID, :StartStasjon, :SluttStasjon),
            (2, :OrdreNr, :Dato, :TogruteID, :KupeeNr, :VognID, :StartStasjon, :SluttStasjon);
        ''', {'OrdreNr': ordreID, 'Dato': dato, 'TogruteID': togrutenr, 'KupeeNr': kupeeNr, 'VognID': vognID, 'StartStasjon': startstasjon, 'SluttStasjon': sluttstasjon})
        print("Din ordre er bestilt!")
    else:
        cursor.execute(''' 
            INSERT INTO BillettKupee (SengeNr, OrdreNr, Dato, TogruteID, KupeeNr, VognID, StartStasjon, SluttStasjon) VALUES (:SengeNr, :OrdreNr, :Dato, :TogruteID, :KupeeNr, :VognID, :StartStasjon, :SluttStasjon)
        ''', {'SengeNr':1, 'OrdreNr': ordreID, 'Dato': dato, 'TogruteID': togrutenr, 'KupeeNr': kupeeNr, 'VognID': vognID, 'StartStasjon': startstasjon, 'SluttStasjon': sluttstasjon})
        print("Din ordre er bestilt!")


    ### MANGLER 
    # - Må kunne kjøpe 2 senger i kupeen - funker ikke
    # - kan velge billettype 2 og så togrute 1 - det burde ikke gå?
    # - kan kun bestille flere setebilletter for samme togrute nummer (togruteID) - FAIR
    # - Håndterer ikke ordentlig når man velger et sete som er reservert - FIXED

if __name__ == "__main__":
    finn_ledige_seter()

con.commit()