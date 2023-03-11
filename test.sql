


CREATE TABLE InneholderStrekning(
  BaneStrekningsNavn TEXT NOT NULL,
  DelstrekningsID TEXT NOT NULL,
  CONSTRAINT is_pk PRIMARY KEY (BaneStrekningsNavn, DelstrekningsID),
  CONSTRAINT BaneStrekningsNavn_fk FOREIGN KEY BaneStrekningsNavn REFERENCES BaneStrekning ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT DelstrekningsID_fk FOREIGN KEY DelstrekningsID REFERENCES DelStrekning ON UPDATE CASCADE ON DELETE CASCADE
)

CREATE TABLE Delstrekning(
  DelstrekningsID text NOT null, 
  Sportype text, 
  Lengde text, 
  StartStasjon text, 
  SluttStasjon text,
  CONSTRAINT ds_pk PRIMARY KEY DelstrekningsID,
  CONSTRAINT StartS_fk FOREIGN KEY StartStasjon REFERENCES JernbaneStasjon ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT SluttS_fk FOREIGN KEY SluttStasjon REFERENCES JernbaneStasjon ON UPDATE CASCADE ON DELETE CASCADE
)

CREATE TABLE JernbaneStasjon(
  Navn text not NULL, 
  Moh text,
  CONSTRAINT jbs_pk PRIMARY KEY Navn,
)


CREATE TABLE StasjonerIRute(
  JernbanestasjonNavn text not NULL, 
  TogruteID text, 
  Ankomsttid text, 
  Avgangstid text,
  CONSTRAINT jbsn_fk FOREIGN key JernbaneStasjonNavn REFERENCES JernbaneStasjon on UPDATE CASCADE on UPDATE DELETE,
  CONSTRAINT trid_fk FOREIGN key TogruteID REFERENCES Togrute on UPDATE CASCADE on UPDATE DELETE,


  )

CREATE TABLE Operatør(
  Navn text not NULL,
  CONSTRAINT ONavn_pk PRIMARY KEY Navn,
)

CREATE TABLE Togrute(
  TogruteID text not NULL, 
  Hovedretning text, 
  OperatørNavn text, 
  VognOppsettID,
  Ukedager text, --? Hvordan får vi frem at dette er en flerverdi nøkkel?
  CONSTRAINT tr_pk PRIMARY KEY TogruteID,
  CONSTRAINT OperatørNavn_fk FOREIGN key OperatørNavn REFERENCES Operatør on UPDATE CASCADE on UPDATE DELETE,
  CONSTRAINT VognOppsettID_fk FOREIGN key VognOppsettID REFERENCES VognOppsett on UPDATE CASCADE on UPDATE DELETE,
  )

-- CREATE TABLE Ukedager(
--   TogruteID text not null, 
--   ,
--   CONSTRAINT TogruteID PRIMARY KEY TogruteID
--   )
-- TogruteID er fremmednøkkel mot togrute

CREATE TABLE TogruteForekomst(
  Dato text , 
  TogruteID text,
  CONSTRAINT togruteID_fk FOREIGN KEY TogruteID REFERENCES Togrute on UPDATE CASCADE on DELETE CASCADE,
  )


--? Hva skjer med denne egt?
CREATE TABLE DelstrekningErReservert(
  DelstrekningsID text not null, 
  OrdreNr text, 
  SeteNr integer, 
  VognTypeNavn text,
  CONSTRAINT DelstrekningsID_fk FOREIGN KEY DelstrekningsID REFERENCES Delstrekning on UPDATE CASCADE on DELETE CASCADE,
  CONSTRAINT OrdreNr_fk FOREIGN KEY OrdreNr REFERENCES KundeOrdre on UPDATE CASCADE on DELETE CASCADE,
  CONSTRAINT DelstrekningsID_fk FOREIGN KEY DelstrekningsID REFERENCES Delstrekning on UPDATE CASCADE on DELETE CASCADE,
  )
-- DelstrekningsID er fremmednøkkel mot Delstrekning
-- OrdreNr er fremmednøkkel mot KundeOrdre
-- SeteNr og VognTypeNavn er fremmednøkler mot Sete

CREATE TABLE KundeOrdre(
  OrdreNr text not null, 
  Dag text, 
  Tid text, 
  AntallBilletter integer, 
  KundeID text, 
  Dato text, 
  TogruteID text
  CONSTRAINT OrdreNr_pk PRIMARY KEY OrdreNr,
  CONSTRAINT TogruteID_fk FOREIGN KEY TogruteID REFERENCES TogruteForekomst on UPDATE CASCADE on DELETE CASCADE,
  CONSTRAINT Dato_fk FOREIGN KEY Dato REFERENCES TogruteForekomst on UPDATE CASCADE on DELETE CASCADE,
  )

-- KundeID er fremmednøkkel mot Kunde
-- Dato og TogruteID er fremmednøkler mot TogruteForekomst

CREATE TABLE Billetter(
  BillettID text not null, 
  type text, 
  OrdreNr text,
  CONSTRAINT BillettID_pk PRIMARY KEY BillettID,
  CONSTRAINT OrdreNr_fk FOREIGN KEY OrdreNr REFERENCES KundeOrdre on UPDATE CASCADE on DELETE CASCADE,
  )
-- BillettID er primærnøkkel
-- Type beskriver hvilken superklasse Billetten er
-- OrdreNr er fremmednøkkel til KundeOrdre


CREATE TABLE BillettKupée(
  OrdreNr, 
  KupéeNr, 
  VognTypeNavn, 
  AntallSenger
  )
OrdreNr er fremmednøkkel mot KundeOrdre
KupéeNr og VognTypeNavn er fremmednøkler mot Kupée

CREATE TABLE Kunde(
  KundeNr text not null, 
  Navn text, 
  E-post text, 
  Tlf * multiple VALUES,
  CONSTRAINT KundeNr_pk PRIMARY KEY KundeNr,
  )

CREATE TABLE VognOppsett(
  VognOppsettID text not null,
  CONSTRAINT VognOppsettID_pk PRIMARY KEY VognOppsettID,

  )

CREATE TABLE HarVogn(
  VongOppsettID text, 
  VognTypeNavn text, 
  OppsettNr text
  )
  
VognOppsettID er fremmednøkkel mot VognOppsett
VognTypeNavn er fremmednøkkel mot VognType

CREATE TABLE HarVognType(
  OperatørNavn text not null, 
  VognNavn text,
  CONSTRAINT OperatørNavn_fk FOREIGN KEY OperatørNavn REFERENCES Operatør on UPDATE CASCADE on DELETE CASCADE,
  CONSTRAINT VognNavn_fk FOREIGN KEY VognNavn REFERENCES VognType on UPDATE CASCADE on DELETE CASCADE,
  )
OperatørNavn er fremmednøkkel mot Operatør
--? Hvordan gjør vi dette??
VognNavn er fremmednøkkel mot sovevogn eller sittevogn, da vogntype-tabellen ikke finnes. 

CREATE TABLE Sovevogn(
  Navn text not null, 
  AntallKupéer integer,
  CONSTRAINT Navn_pk PRIMARY KEY Navn,
  )

CREATE TABLE Sittevogn(
  Navn text not null, 
  AntallRader integer, 
  SeterPerRad integer,
  CONSTRAINT Navn_pk PRIMARY KEY Navn,

  )

CREATE TABLE Seng(
  SengNr integer not NULL, 
  VognTypeNavn text, 
  BillettID text,
  CONSTRAINT SengNr_pk PRIMARY KEY SengNr, --? Hva gjør vi her?
  CONSTRAINT VognTypeNavn_fk FOREIGN KEY VognTypeNavn REFERENCES VognType on UPDATE CASCADE on DELETE CASCADE,
  CONSTRAINT BillettID_fk FOREIGN KEY BillettID REFERENCES Billetter on UPDATE CASCADE on DELETE CASCADE,


  )
SengNr er delvis nøkkel for seng
VognTypeNavn er fremmednøkkel til Sovevogn
BillettID er fremmednøkkel mot Billetter

CREATE TABLE Sete(
  SeteNr integer not NULL, 
  VognTypeNavn text, 
  BillettID text,
  CONSTRAINT SeteNr_pk PRIMARY KEY SeteNr, --? Hva gjør vi her?
  CONSTRAINT VognTypeNavn_fk FOREIGN KEY VognTypeNavn REFERENCES VognType on UPDATE CASCADE on DELETE CASCADE,
  CONSTRAINT BillettID_fk FOREIGN KEY BillettID REFERENCES Billetter on UPDATE CASCADE on DELETE CASCADE,
  )
SeteNr er delvis nøkkel for sete
VognTypeNavn er fremmednøkkel mot Sittevogn
BillettID er fremmednøkkel mot Billetter

