import sqlite3

con = sqlite3.connect('jernbane.db')
cursor = con.cursor()

# Legge inn 
# Opprette TogruteForekomst for 3 og 4 april 2023
cursor.execute('''INSERT INTO Togruteforekomst VALUES 
    ('2023-04-03', 1),
    ('2023-04-04', 1),
    ('2023-04-03', 2),
    ('2023-04-04', 2),
    ('2023-04-03', 3),
    ('2023-04-04', 3)''')

con.commit()