import brukerhistorieD
from datetime import datetime, timedelta
import sqlite3
con = sqlite3.connect('jernbane.db')
cursor = con.cursor()

def finn_ledige_seter():
    """
    Hovedfunksjon for programmet. Lar brukeren se alle ledige billetter på en dato og så kjøpe dem
    """

    kundeNr = userLogin()
    dato = input("Velg dato (YYYY-MM-DD): ")

    startstasjon = "Steinkjer"
    sluttstasjon = "Bodø"
    # dato = "2023-04-03"

    #FINN ALLE TOGRUTEFOREKOMSTENE SOM INNEHOLDER START OG SLUTTSTASJONEN OG DATOEN
    response = cursor.execute('''
        SELECT * 
        FROM TogruteForekomst AS trf
        WHERE trf.Dato = :dato AND trf.TogruteID IN (
            SELECT sir.TogruteID
            FROM StasjonerIRute AS sir INNER JOIN JernbaneStasjon AS startstasjon ON (sir.JernbanestasjonNavn = startstasjon.Navn)
            WHERE startstasjon.Navn = :startstasjon AND  sir.TogruteID IN (
                SELECT DISTINCT sir2.TogruteID
                FROM StasjonerIRute sir2 INNER JOIN JernbaneStasjon AS sluttstasjon ON (sir2.JernbanestasjonNavn = sluttstasjon.Navn)
                WHERE sir2.TogruteID = sir.TogruteID AND sluttstasjon.Navn = :sluttstasjon
            )
        )
    ''', {'startstasjon': startstasjon, 'sluttstasjon': sluttstasjon, 'dato': dato}).fetchall()
    print(response) #[('2023-04-03', 1), ('2023-04-03', 2)]
    datoT = datetime.strptime(dato, "%Y-%m-%d").date()
    togruter = brukerhistorieD.finnTogruterPåDato([startstasjon, sluttstasjon], datoT, '00:00')

    #FINN ALLE LEDIGE SETER PÅ DELETOGRUTENE (delstrekningene mellom start og sluttstasjon)
    gyldigeTogruteNrForSitte = set()
    gyldigeSeteNr = dict()
    for togruteforekomst in togruter:
        print()
        print(f"Ledige seter for togrute {togruteforekomst[0]} den {togruteforekomst[-1]} fra {startstasjon} til {sluttstasjon}:") #Kanskje importe en funksjon fra en annen brukerhistorie for å finne start og sluttstasjon for togrute
        
        responseSeter = cursor.execute('''
            SELECT DISTINCT tr.TogruteID, sv.NrIVognOppsett, s.SeteNr
            FROM ((Togrute AS tr INNER JOIN SitteVogn AS sv ON (tr.TogruteID = sv.TogruteID)) INNER JOIN Sete AS s ON (sv.VognID = s.VognID)) INNER JOIN Togruteforekomst AS trf ON (tr.TogruteID = trf.TogruteID)
            WHERE trf.Dato = :Dato AND tr.TogruteID = :TogruteID AND (SeteNr, s.VognID) NOT IN (
                SELECT DISTINCT bs.SeteNr, bs.VognID
                FROM BillettSete AS bs INNER JOIN DelstrekningForSete AS dfs ON (bs.BillettID = dfs.BillettID)
                WHERE bs.TogruteID = :TogruteID AND bs.Dato = :Dato AND OrdreNr IS NOT NULL AND dfs.DelstrekningsID IN ( 
                        SELECT ds1.DelstrekningsID
                        FROM Delstrekning as ds1
                        WHERE ds1.DelstrekningsID >=  (
                            SELECT ds.DelstrekningsID
                            FROM (((Togrute AS tr INNER JOIN StasjonerIRute AS sir ON (tr.TogruteID = sir.TogruteID)) INNER JOIN JernbaneStasjon as js ON (sir.JernbanestasjonNavn = js.Navn)) INNER JOIN Delstrekning AS ds ON (js.Navn = ds.StartStasjon)) 
                            WHERE tr.TogruteID = :TogruteID AND ds.StartStasjon = :StartStasjon
                        )
                        AND DelstrekningsID <= (
                            SELECT DelstrekningsID
                            FROM (((Togrute AS tr INNER JOIN StasjonerIRute AS sir ON (tr.TogruteID = sir.TogruteID)) INNER JOIN JernbaneStasjon as js ON (sir.JernbanestasjonNavn = js.Navn)) INNER JOIN Delstrekning AS ds ON (js.Navn = ds.StartStasjon)) 
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
                    gyldigeTogruteNrForSitte.add(sete[0])
                    gyldigeSeteNr[vognIdx] = gyldigeSeteNr[vognIdx] + [sete[-1]] if vognIdx in gyldigeSeteNr else [sete[-1]]
                    ledige_seter_i_vogn.append(str(sete[-1]))
            responsStreng = f"Ledige seter i vogn {vognIdx}: {', '.join(ledige_seter_i_vogn)}" if len(ledige_seter_i_vogn) > 0 else "Ingen ledige seter"
            print(responsStreng)

    #FINN ALLE LEDIGE KUPEER PÅ DELETOGRUTENE
    gyldigeTogruteNrForSove = set()
    gyldigeKupeeNr = dict()
    kupeeDict = {}
    for togruteforekomst in response:
        print()
        print(f"Ledige kupeer for togrute {togruteforekomst[1]} den {togruteforekomst[0]} fra {startstasjon} til {sluttstasjon}:")
        responseKupeer = cursor.execute('''
            SELECT DISTINCT sv.NrIVognOppsett, k.KupeeNr, sv.VognID
            FROM ((Togrute AS tr INNER JOIN SoveVogn AS sv ON (tr.TogruteID = sv.TogruteID)) INNER JOIN Kupee AS k ON (sv.VognID = k.VognID)) INNER JOIN Togruteforekomst AS trf ON (tr.TogruteID = trf.TogruteID)
            WHERE trf.Dato = :Dato AND tr.TogruteID = :TogruteID AND (KupeeNr, k.VognID) NOT IN (
                SELECT bk.KupeeNr, bk.VognID
                FROM BillettKupee AS bk
                WHERE bk.TogruteID = :TogruteID AND bk.Dato = :Dato AND OrdreNr IS NOT NULL
            ) 
        ''', {'TogruteID': togruteforekomst[1], 'Dato': togruteforekomst[0]}).fetchall()

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
                    gyldigeTogruteNrForSove.add(togruteforekomst[1])
                    gyldigeKupeeNr[ekteVognIdx] = gyldigeKupeeNr[ekteVognIdx] + [kupee[-2]] if ekteVognIdx in gyldigeKupeeNr else [kupee[-2]]
                    ledige_seter_i_vogn.append(str(kupee[1]))
        responsStreng = f"Ledige kupeer i vogn {ekteVognIdx}: {', '.join(ledige_seter_i_vogn)}" if harLedig > 0 else "Ingen ledige kupeer"
        print(responsStreng)

    #KJØP BILLETTER
    print()
    typeBillett = velgTypeBillett() 

    print("Vennligst velg hvilken billett du vil kjøpe:")
    togrutenr = velgTogruteNr(gyldigeTogruteNrForSitte, gyldigeTogruteNrForSove, typeBillett) 

    cursor.execute('''
        INSERT INTO KundeOrdre (Dag, tid, KundeNr, Dato, TogruteID) VALUES (:Dato, :Tid, :KundeNr, :Dato, :TogruteID)
    ''', {'Dato': dato, 'Tid': dato, 'KundeNr': kundeNr, 'TogruteID': togrutenr}).fetchall()
    ordreID = cursor.lastrowid

    if (typeBillett == "1"):
        while True:
            velgSitteBillett(ordreID, togrutenr, dato, gyldigeSeteNr, startstasjon, sluttstasjon)
            if (input(f"Vil du kjøpe flere sittebilletter for togrute {togrutenr}? (j/n): ").lower() == "n"):
                break
    elif (typeBillett == "2"):
        velgKupeebillett(ordreID, togrutenr, dato, kupeeDict, gyldigeKupeeNr)
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

def velgTogruteNr(gydligTogruteNrForSitte, gydligTogruteNrForSove, typeBillett):
    """
    Validerer at brukeren velger et gyldig togrute nummer

    Parameters:
        gydligTogruteNrForSitte (list): En liste med gyldige togrute nummer for sittevogner
        gydligTogruteNrForSove (list): En liste med gyldige togrute nummer for kupeevogner
        typeBillett (int): Type billett brukeren valgte
    Returns:
        togruteNr (int): Togrute nummeret brukeren valgte
    """
    togruteNr = input("Velg et togrute nummer: ")
    if typeBillett == "1":
        if int(togruteNr) in list(gydligTogruteNrForSitte):
            return togruteNr
        else:
            print("Velg et gyldig togrute nummer!")
            return velgTogruteNr(gydligTogruteNrForSitte, gydligTogruteNrForSove, typeBillett)
    else:
        if int(togruteNr) in list(gydligTogruteNrForSove):
            return togruteNr
        else:
            print("Velg et gyldig togrute nummer!")
            return velgTogruteNr(gydligTogruteNrForSitte, gydligTogruteNrForSove, typeBillett)

def velgSitteBillett(ordreID, togrutenr, dato, startstasjon, sluttstasjon):
    """
    Finner hvilken vogn og sete som brukeren vil kjøpe og lager en bestilling basert på dette

    Parameters:
        ordreID (int): ID-en til ordren som skal opprettes
        togrutenr (int): ID-en til togruten som skal kjøpes billett til
        gyldigeSeteNr (dict): En dictionary som inneholder hvilke seter som er ledige i hvilke vogner
    Returns:
    """
    vognNr = input("Velg vogn nummer: ")
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

    gyldigeVognNr = cursor.execute('''
        SELECT DISTINCT sv.VognID
        FROM ((Togrute AS tr INNER JOIN SitteVogn AS sv ON (tr.TogruteID = sv.TogruteID)) INNER JOIN Sete AS s ON (sv.VognID = s.VognID)) INNER JOIN Togruteforekomst AS trf ON (tr.TogruteID = trf.TogruteID)
        WHERE tr.TogruteID = :TogruteID AND trf.Dato = :Dato 
    ''', {'Dato': dato, 'TogruteID': togrutenr}).fetchall()
    gyldigeVognNr = [x[0] for x in gyldigeVognNr]

    # billettDato = input("Velg dato for billetten: ") ###SJEKKER IKKE DENNE ENDA
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


def velgKupeebillett(ordreID, togrutenr, dato, kupeeDict, gyldigeKupeeNr):
    """
    Finner hvilken vogn og kupee som brukeren vil kjøpe og lager en bestilling basert på det.

    Parameters: 
        ordreID (int): ID-en til ordren som skal opprettes
        togrutenr (int): Togrute nummeret som brukeren har valgt
        kupeeDict (dict): En dictionary som kan oversette nummeret til vognen (relativt til toget) til vognID-en
        gyldigeKupeeNr (dict): En dictionary som inneholder hvilke kupéer som er ledige i hver vogn
    Returns:
    """
    # billettDato = input("Velg dato for billetten: ")
    vognNr = input("Velg vogn nummer: ")
    if int(vognNr) not in gyldigeKupeeNr: #Sjekker om vognnummeret er lik en av nummerene til vognene som er sovevogner
        print("Velg et gyldig vogn nummer!")
        return velgKupeebillett(ordreID, togrutenr, dato, kupeeDict, gyldigeKupeeNr)
    kupeeNr = input("Velg kupée nummer: ")
    if int(kupeeNr) not in gyldigeKupeeNr[int(vognNr)]: #Sjekker om kupéenummeret er gyldig for den valgte vognen
        print("Velg et gyldig kupée nummer!")
        return velgKupeebillett(ordreID, togrutenr, dato, kupeeDict, gyldigeKupeeNr)
    antallSenger = input("Hvor mange senger vil du ha? ")
    vognID = kupeeDict[str(dato) + str(togrutenr) + str(vognNr)]

    #Sjekker om kunden bestiller en eller to senger i en kupée
    if antallSenger == 2:
        cursor.execute(''' 
            INSERT INTO BillettKupee (SengeNr, OrdreNr, Dato, TogruteID, KupeeNr, VognID) VALUES (1, :OrdreNr, :Dato, :TogruteID, :KupeeNr, :VognID);
        ''', {'OrdreNr': ordreID, 'Dato': dato, 'TogruteID': togrutenr, 'KupeeNr': kupeeNr, 'VognID': vognID})
        con.commit()
        cursor.execute(''' 
            INSERT INTO BillettKupee (SengeNr, OrdreNr, Dato, TogruteID, KupeeNr, VognID) VALUES (2, :OrdreNr, :Dato, :TogruteID, :KupeeNr, :VognID);
        ''', {'OrdreNr': ordreID, 'Dato': dato, 'TogruteID': togrutenr, 'KupeeNr': kupeeNr, 'VognID': vognID})
        con.commit()
        print("Din ordre er bestilt!")
    else:
        cursor.execute(''' 
            INSERT INTO BillettKupee (SengeNr, OrdreNr, Dato, TogruteID, KupeeNr, VognID) VALUES (:SengeNr, :OrdreNr, :Dato, :TogruteID, :KupeeNr, :VognID)
        ''', {'SengeNr':1, 'OrdreNr': ordreID, 'Dato': dato, 'TogruteID': togrutenr, 'KupeeNr': kupeeNr, 'VognID': vognID})
        print("Din ordre er bestilt!")
    

def finnTogruterPåDato(stasjoner, dato, klokkeslett):
    # I SECLECT-delen settes Dato til + 1 dag hvis valgt startStasjon har avgangstid som er 
    # mindre enn avgangstiden for togruten sin startstasjon, da dette betyr at togruten går over to datoer.
    # I WHERE-delen så sjekkes det samme som i SELECT-delen to ganger, for å se om Dato (evt oppdatert)
    # er lik dato og avgangstid >= klokkeslett, eller bare lik datoDagEtter. 
    # Videre sjekkes det for at startStasjon og sluttStasjon er riktig i forhold til brukerinput. 
    # Tilsutt sjekkes det for at togruten går riktig vei, 
    # da må startStasjon sitt StasjonNr må være mindre enn sluttStasjon sitt StasjonsNr 
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


    ####                                                                    
    #### MANGLER: VALDIERING AV INPUT, MULIGHET TIL Å KJØPE FLERE SETEBILLETTER
    ####                                                                       
    # - Må kunne kjøpe 1/2 senger i kupeen
    # - kan velge billettype 2 og så togrute 1 - det burde ikke gå
    # - kan kun bestille flere setebilletter for samme togrute nummer (togruteID) - FAIR
    # - Håndterer ikke ordentlig når man velger et sete som er reservert - FIXED
    # - Validering av kupeebilletter er kanskje ikke helt riktig 

if __name__ == "__main__":
    finn_ledige_seter()

con.commit()