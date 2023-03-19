import sqlite3
from datetime import datetime, timedelta


con = sqlite3.connect('jernbane.db')
cursor = con.cursor()

def make_datetime(date_str, time_str):
    if not time_str:
        return None
    dt = datetime.strptime(date_str + ' ' + time_str, '%Y-%m-%d %H:%M')
    return dt

startstajon = "Trondheim"
sluttstasjon = "Mo i Rana"
tid = "07:50"
dato = "2023-04-03"
request_datetime = make_datetime(dato, tid)
dato_obj = datetime.strptime(dato, '%Y-%m-%d')
dato_obj_pluss1 = dato_obj + timedelta(days=1)
dato_obj = dato_obj.strftime('%Y-%m-%d')
dato_obj_pluss1 = dato_obj_pluss1.strftime('%Y-%m-%d')

klokkeslett = ""

####NB GJØR OM F-STRING TIL INJECTION SIKKER LØSNING ETTERPÅ
response = cursor.execute(f''' 
    SELECT  sir.JernbanestasjonNavn, trf.Dato, tr.TogruteID, sir.Ankomsttid, sir.Avgangstid
    FROM (TogruteForekomst AS trf NATURAL JOIN Togrute AS tr) INNER JOIN StasjonerIRute AS sir ON (tr.TogruteID = sir.TogruteID)
    WHERE (trf.Dato = '2023-04-03' OR trf.Dato = '2023-04-04')
''')
#ANTAGELSER:
# - Antar at de vil ha toruter som går før oppgitt tidspunkt
# - Antar at "mellom to stasjoner" betyr at de to stasjonene er i togruten slik at kunden kan komme seg fra start til slutt
# - Antar at startstasjonen sin avgangstid må være større (etter) tid hvis {basertPåAvgangstid = true}


rows = response.fetchall()
stasjoner_i_forekomst = dict()
for row in rows:
    delstasjon = list(row)
    ankomst_datetime = make_datetime(delstasjon[1], delstasjon[-2])
    print(ankomst_datetime)
    key = row[1] + "." + str(row[2])
    # if ankomst_datetime < request_datetime: #hvis ankomstdatetime er none så
    #     continue

    # if row[4] > tid: #Hvis avgangstidspunkt er etter 'tid' for den stasjonen så kan den legges til
    if key in stasjoner_i_forekomst:
        stasjoner_i_forekomst[key] = stasjoner_i_forekomst[key] + [[row[0]]]
    else:
        stasjoner_i_forekomst[key] = [row[0]]
    print(row)
print(stasjoner_i_forekomst)

# for forekomst in stasjoner_i_forekomst:
#     if (startstajon in forekomst) and (sluttstasjon in forekomst):
#         print(forekomst)


# x = make_datetime('2023-01-01', '07:50')
# y = make_datetime('2023-01-01', '07:49')
# print(x > y)

con.commit()


#Resultat: togruteID, startstasjon, ankomststart, sluttstasjon, ankomstslutt
