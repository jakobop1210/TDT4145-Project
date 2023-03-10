import sqlite3

con = sqlite3.connect('jernbane.db')
cursor = con.cursor()
cursor.execute(''' 
    CREATE TABLE Banestrekning (
        Navn TEXT NOT NULL,
        Fremdriftsenergi TEXT,
        AntallStasjoner INTEGER,
        StartStasjon TEXT,
        SluttStasjon TEXT,
        CONSTRAINT bs_pk PRIMARY KEY (Navn),
        CONSTRAINT start_fk FOREIGN KEY (StartStasjon) REFERENCES JernbaneStasjon(Navn) ON UPDATE CASCADE ON DELETE CASCADE,
        CONSTRAINT slutt_fk FOREIGN KEY (SluttStasjon) REFERENCES JernbaneStasjon(Navn) ON UPDATE CASCADE ON DELETE CASCADE
    );
''')
# ? Kan fremmednøkkel være Null her?
# ? Hvor lang bør en VARCHAR være? 30?

# CREATE TABLE HarVogn(
# 	VognOppsettID INTEGER NOT NULL,
# 	VognTypeNavn TEXT NOT NULL,
# 	OppsettNr INTEGER,
# 	CONSTRAINT harVogn_pk PRIMARY KEY (VognOppsettID, VognTypeNavn),
# 	CONSTRAINT oppsett_fk FOREIGN KEY (VognOppsettID) REFERENCES VognOppsett(VognOppsettID) ON UPDATE CASCADE ON DELETE CASCADE,
# 	CONSTRAINT vogntype_fk FOREIGN KEY (VognTypeNavn) REFERENCES VognType ....
# )

con.commit()