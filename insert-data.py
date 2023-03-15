import sqlite3
con = sqlite3.connect('jernbane.db')
cursor = con.cursor()

cursor.execute('''INSERT INTO Banestrekning VALUES ('Test1', 'Energi', 3, 'TestStart', 'TestSlutt')''')
con.commit()

# Brukerhistorie A 


# Brukerhistorie B 

# Brukerhistorie C 
def togruterInnomStasjon(ukedag):
    #cursor.execute("SELECT * FROM  WHERE navn =:navn", {"navn" = ukedag})
   # row = cursor.fetchall()
   # print("First row from table person:")
    #print(row)

# Brukerhistorie D 

# Brukerhistorie E 

# Brukerhistorie F 

# Brukerhistorie G
 
# Brukerhistorie H 

