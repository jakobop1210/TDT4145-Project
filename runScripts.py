import sqlite3

con = sqlite3.connect('jernbane.db')
cursor = con.cursor()

# Kjøre brukerhistorieA.sql script
with open('brukerhistorieA.sql', 'r') as f:
    script = f.read()
cursor.executescript(script)

# Kjøre brukerhistorieB.sql script
with open('brukerhistorieB.sql', 'r') as f:
    script = f.read()
cursor.executescript(script)

# Kjøre brukerhistorieF.sql script
with open('brukerhistorieF.sql', 'r') as f:
    script = f.read()

cursor.executescript(script)


con.commit()

con.close()