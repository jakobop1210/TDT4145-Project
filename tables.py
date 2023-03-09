import sqlite3

con = sqlite3.connect('jernbane.db')
cursor = con.cursor()
cursor.execute(''' 
    CREATE TABLE Banestrekning (
        Navn VARCHAR(30) NOT NULL,
        Fremdriftsenergi VARCHAR(30),
        AntallStasjoner INTEGER,
        StartStasjon VARCHAR(30),
        SluttStasjon VARCHAR(30),
        CONSTRAINT bs_pk PRIMARY KEY (Navn),
        CONSTRAINT start_fk FOREIGN KEY (StartStasjon) REFERENCES JernbaneStasjon(Navn) ON UPDATE CASCADE ON DELETE CASCADE,
        CONSTRAINT slutt_fk FOREIGN KEY (SluttStasjon) REFERENCES JernbaneStasjon(Navn) ON UPDATE CASCADE ON DELETE CASCADE
    );
''')
#Kan fremmednøkkel være Null her?