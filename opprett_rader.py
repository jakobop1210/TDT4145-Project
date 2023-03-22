
import sqlite3
con = sqlite3.connect('jernbane.db')
cursor = con.cursor()


cursor.execute(
    '''INSERT INTO KundeOrdre VALUES (4, 'Mandag','05:00',1,'2023-04-03',1)''')
cursor.execute(
    '''INSERT INTO KundeOrdre VALUES (2, 'Mandag','05:00',1,'2023-04-03',2)''')
cursor.execute(
    '''INSERT INTO KundeOrdre VALUES (3, 'Mandag','05:00',1,'2023-04-03',3)''')


# kundeEmailer = cursor.execute('''
#     Select Epost from kunde
# ''').fetchall()

# kundeEmailer = [email[0] for email in kundeEmailer]
# print(kundeEmailer)


con.commit()
