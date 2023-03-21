import sqlite3

con = sqlite3.connect('jernbane.db')
cursor = con.cursor()

def finn_ledige_seter():
    startstasjon = "Trondheim"
    sluttstasjon = "Bodø"
    dato = "2023-04-03"


    #FINN ALLE TOGRUTEFOREKOMSTENE SOM INNEHOLDER START OG SLUTTSTASJONEN
    response = cursor.execute('''
        SELECT * 
        FROM TogruteForekomst AS trf
        WHERE trf.TogruteID IN (
            SELECT sir.TogruteID
            FROM StasjonerIRute AS sir INNER JOIN JernbaneStasjon AS startstasjon ON (sir.JernbanestasjonNavn = startstasjon.Navn)
            WHERE startstasjon.Navn = :startstasjon AND  sir.TogruteID IN (
                SELECT DISTINCT sir2.TogruteID
                FROM StasjonerIRute sir2 INNER JOIN JernbaneStasjon AS sluttstasjon ON (sir2.JernbanestasjonNavn = sluttstasjon.Navn)
                WHERE sir2.TogruteID = sir.TogruteID AND sluttstasjon.Navn = :sluttstasjon
            )
        )
    ''', {'startstasjon': startstasjon, 'sluttstasjon': sluttstasjon}).fetchall()

    #FINN ALLE LEDIGE SETER PÅ DELETOGRUTENE
    for togruteforekomst in response:
        print()
        print(f"Ledige seter for togrute {togruteforekomst[1]} den {togruteforekomst[0]}:") #Kanskje importe en funksjon fra en annen brukerhistorie for å finne start og sluttstasjon for togrute
        
        responseSeter = cursor.execute('''
            SELECT DISTINCT tr.TogruteID, sv.NrIVognOppsett, s.SeteNr
            FROM ((Togrute AS tr INNER JOIN SitteVogn AS sv ON (tr.TogruteID = sv.TogruteID)) INNER JOIN Sete AS s ON (sv.VognID = s.VognID)) INNER JOIN Togruteforekomst AS trf ON (tr.TogruteID = trf.TogruteID)
            WHERE trf.Dato = :Dato AND tr.TogruteID = :TogruteID AND (SeteNr, s.VognID) NOT IN (
                SELECT bs.SeteNr, bs.VognID
                FROM BillettSete AS bs
                WHERE bs.TogruteID = :TogruteID AND bs.Dato = :Dato AND OrdreNr IS NOT NULL
            ) 
        ''', {'TogruteID': togruteforekomst[1], 'Dato': togruteforekomst[0]}).fetchall()

        #Print alle ledige setene per vogn
        antall_vogner = len(set([x[1] for x in responseSeter]))
        for vognIdx in range(1, int(antall_vogner) + 1):
            ledige_seter_i_vogn = []
            for sete in responseSeter:
                if int(sete[1]) == vognIdx:
                    ledige_seter_i_vogn.append(str(sete[-1]))
            responsStreng = f"Ledige seter i vogn {vognIdx}: {', '.join(ledige_seter_i_vogn)}" if len(ledige_seter_i_vogn) > 0 else "Ingen ledige seter"
            print(responsStreng)
                    
    #FINN ALLE LEDIGE KUPEER PÅ DELETOGRUTENE
    for togruteforekomst in response:
        print()
        print(f"Ledige kupeer for togrute {togruteforekomst[1]} den {togruteforekomst[0]}:")
        responseKupeer = cursor.execute('''
            SELECT DISTINCT sv.NrIVognOppsett, k.KupeeNr
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
                if int(kupee[0] == ekteVognIdx):
                    harLedig = True
                    ledige_seter_i_vogn.append(str(kupee[-1]))
        responsStreng = f"Ledige kupeer i vogn {ekteVognIdx}: {', '.join(ledige_seter_i_vogn)}" if harLedig > 0 else "Ingen ledige kupeer"
        print(responsStreng)

    #KJØP BILLETTER
    print()
    typeBillett = input("Vennligst velg hvilken type billett du vil kjøpe: (1) Sittebillett, (2) Kupeebillett")

    print("Vennligst velg hvilken billett du vil kjøpe:")
    togrutenr = input("Velg et togrute nummer: ")
    cursor.execute('''
        INSERT INTO KundeOrdre (Dag, tid, KundeID, Dato, TogruteID) VALUES (:Dato, :Tid, :KundeID, :Dato, :TogruteID)
    ''', {'Dato': dato, 'Tid': dato, 'KundeID': 1, 'TogruteID': togrutenr}).fetchall()
    ordreID = cursor.lastrowid 

    if (typeBillett == "1"):
        velgSitteBillett(ordreID, togrutenr)
    elif (typeBillett == "2"):
        velgKupeebillett(ordreID, togrutenr)
    else:
        print("Du valgte ikke en gyldig type billett!")

def velgSitteBillett(ordreID, togrutenr):
    billettDato = input("Velg dato for billetten: ")
    vognNr = input("Velg vogn nummer: ")
    seteNr = input("Velg sete nummer: ")
    cursor.execute(''' 
        INSERT INTO BillettSete (OrdreNr, Dato, TogruteID, SeteNr, VognID) VALUES (:OrdreNr, :Dato, :TogruteID, :SeteNr, :VognID)
    ''', {'OrdreNr': ordreID, 'Dato': billettDato, 'TogruteID': togrutenr, 'SeteNr': seteNr, 'VognID': vognNr})

    print("Din ordre er bestilt!")
            

def velgKupeebillett(ordreID, togrutenr):
    billettDato = input("Velg dato for billetten: ")
    vognNr = input("Velg vogn nummer: ")
    kupeeNr = input("Velg sete nummer: ")
    antallSenger = input("Hvor mange senger vil du ha?")
    if antallSenger == 2:
        cursor.execute(''' 
            INSERT INTO BillettKupee (OrdreNr, Dato, TogruteID, KupeeNr, VognID) VALUES (:OrdreNr, :Dato, :TogruteID, :SeteNr, :VognID)
        ''', {'OrdreNr': ordreID, 'Dato': billettDato, 'TogruteID': togrutenr, 'KupeeNrs': kupeeNr, 'VognID': vognNr})
        cursor.execute(''' 
            INSERT INTO BillettKupee (OrdreNr, Dato, TogruteID, KupeeNr, VognID) VALUES (:OrdreNr, :Dato, :TogruteID, :SeteNr, :VognID)
        ''', {'OrdreNr': ordreID, 'Dato': billettDato, 'TogruteID': togrutenr, 'KupeeNrs': kupeeNr, 'VognID': vognNr})
        print("Din ordre er bestilt!")
    else:
        cursor.execute(''' 
            INSERT INTO BillettKupee (OrdreNr, Dato, TogruteID, SeteNr, VognID) VALUES (:OrdreNr, :Dato, :TogruteID, :SeteNr, :VognID)
        ''', {'OrdreNr': ordreID, 'Dato': billettDato, 'TogruteID': togrutenr, 'SeteNr': kupeeNr, 'VognID': vognNr})
        print("Din ordre er bestilt!")
        
            
    

    ####                                                                    ####
    #### MANGLER STØTTE FOR KUPEER, BRUKERINNLOGGING OG VALDIERING AV INPUT ####
    ####                                                                    ####   
    # - Må kunne kjøpe 1/2 senger i kupeen

finn_ledige_seter()

con.commit()


# import brukerhistorieE
# brukerhistorieE.print_something()


