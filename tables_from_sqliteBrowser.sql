CREATE TABLE Banestrekning ( 
        Navn TEXT NOT NULL,
        Fremdriftsenergi TEXT,
        AntallStasjoner INTEGER,
        StartStasjon TEXT,
        SluttStasjon TEXT,
        CONSTRAINT Banestrekning_pk PRIMARY KEY (Navn),
        CONSTRAINT start_fk FOREIGN KEY (StartStasjon) REFERENCES JernbaneStasjon(Navn) ON UPDATE CASCADE ON DELETE CASCADE,
        CONSTRAINT slutt_fk FOREIGN KEY (SluttStasjon) REFERENCES JernbaneStasjon(Navn) ON UPDATE CASCADE ON DELETE CASCADE
)

CREATE TABLE Delstrekning (
	DelstrekningsID INTEGER NOT NULL,
	Sportype INTEGER,
	Lengde INTEGER,
	StartStasjon TEXT,
	SluttStasjon TEXT,
	CONSTRAINT delstrekning_pk PRIMARY KEY (DelstrekningsID),
	CONSTRAINT start_fk FOREIGN KEY (StartStasjon) REFERENCES JernbaneStasjon(Navn) ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT slutt_fk FOREIGN KEY (StartStasjon) REFERENCES JernbaneStasjon(Navn) ON UPDATE CASCADE ON DELETE CASCADE
)

CREATE TABLE DelstrekningErReservert (
	DelstrekningsID INTEGER NOT NULL,
	OrdreNr INTEGER NOT NULL,
	CONSTRAINT reservert_pk PRIMARY KEY (DelstrekningsID, OrdreNr),
	CONSTRAINT delstreking_fk FOREIGN KEY (DelstrekningsID) REFERENCES Delstrekning(DelstrekningsID) ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT ordre_fk FOREIGN KEY (OrdreNr) REFERENCES KundeOrdre(OrdreNr) ON UPDATE CASCADE ON DELETE CASCADE
)

CREATE TABLE InneholderStrekning (
	BanestrekningsNavn TEXT NOT NULL,
	DelstrekningsID TEXT NOT NULL,
	CONSTRAINT inneholderStrekning_pk PRIMARY KEY (BanestrekningsNavn, DelstrekningsID),
	CONSTRAINT banestreknings_fk FOREIGN KEY (BanestrekningsNavn) REFERENCES Banestrekning(Navn) ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT delstrekning_fk FOREIGN KEY (DelstrekningsID) REFERENCES Delstrekning(DelstrekningsID) ON UPDATE CASCADE ON DELETE CASCADE
)

CREATE TABLE JernbaneStasjon (
	Navn TEXT NOT NULL,
	Moh REAL,
	CONSTRAINT stasjon_pk PRIMARY KEY (Navn)
)

CREATE TABLE KundeOrdre(
	OrdreNr INTEGER NOT NULL,
	Dag date,
	tid TEXT,
	AntallBilletter INTEGER, 
	KundeID INTEGER, 
	Dato date, 
	TogruteID INTEGER,
	CONSTRAINT kundeOrdre_pk PRIMARY KEY (OrdreNr),
	CONSTRAINT kunde_fk FOREIGN KEY (KundeID) REFERENCES Kunde(KundeID) ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT togruteforekomst_fk FOREIGN KEY (Dato, TogruteID) REFERENCES TogruteForekomst(Dato, TogruteID) ON UPDATE CASCADE ON DELETE CASCADE
)

CREATE TABLE Kunde (
	KundeNr INTEGER NOT NULL,
	Navn TEXT,
	Epost TEXT,
	Tlf TEXT,
	CONSTRAINT kunde_pk PRIMARY KEY (KundeNr)
)

CREATE TABLE Operatør(
	Navn TEXT NOT NULL,
	CONSTRAINT operator_pk PRIMARY KEY (Navn)
)

CREATE TABLE Seng (
	VognTypeNavn TEXT NOT NULL,
	SengNr INTEGER NOT NULL,
	BillettID INTEGER,
	CONSTRAINT seng_pk PRIMARY KEY (VognTypeNavn, SengNr)
	CONSTRAINT vongtype_fk FOREIGN KEY (VognTypeNavn) REFERENCES Sovevogn(Navn) ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT billett_fk FOREIGN KEY (BillettID) REFERENCES Billetter(BillettID) ON UPDATE CASCADE ON DELETE CASCADE
)

CREATE TABLE Sete (
	SeteNr INTEGER NOT NULL,
	VognTypeNavn TEXT NOT NULL,
	CONSTRAINT sete_pk PRIMARY KEY (VognTypeNavn, SeteNr),
	CONSTRAINT vogntype_fk FOREIGN KEY (VognTypeNavn) REFERENCES Sittevogn(Navn) ON UPDATE CASCADE ON DELETE CASCADE
)

CREATE TABLE Sittevogn (
	Navn TEXT NOT NULL,
	AntallRader INTEGER,
	SeterPerRad INTEGER,
	CONSTRAINT sittevogn_pk PRIMARY KEY (Navn)
)

CREATE TABLE Sovevogn (
	Navn TEXT NOT NULL,
	AntallKupeer INTEGER,
	CONSTRAINT sovevogn_pk PRIMARY KEY (Navn)
)

CREATE TABLE StasjonerIRute (
	JernbanestasjonNavn	TEXT NOT NULL,
	TogruteID	INTEGER NOT NULL,
	Ankomsttid	time,
	Avgangstid	time,
	CONSTRAINT stasjonIRute_pk PRIMARY KEY(JernbanestasjonNavn,TogruteID),
	CONSTRAINT togrute_fk FOREIGN KEY(TogruteID) REFERENCES Togrute(TogruteID) ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT stasjon_fk FOREIGN KEY(JernbanestasjonNavn) REFERENCES JernbaneStasjon(Navn) ON UPDATE CASCADE ON DELETE CASCADE
)

CREATE TABLE Togrute (
	TogruteID	INTEGER NOT NULL,
	Hovedretning	INTEGER,
	OperatorNavn	TEXT,
	VognOppsettID	INTEGER,
	CONSTRAINT togrute_pk PRIMARY KEY(TogruteID),
	CONSTRAINT vongOppsett_fk FOREIGN KEY(VognOppsettID) REFERENCES VognOppsett(VognOppsettID) ON UPDATE CASCADE ON DELETE SET NULL,
	CONSTRAINT operator_fk FOREIGN KEY(OperatorNavn) REFERENCES Operator(Navn) ON UPDATE CASCADE ON DELETE CASCADE
)

CREATE TABLE TogruteForekomst(
	Dato date NOT NULL,
	TogruteID INTEGER NOT NULL,
	CONSTRAINT forekomst_pk PRIMARY KEY (Dato, TogruteID)
	CONSTRAINT togrute_fk FOREIGN KEY (TogruteID) REFERENCES Togrute(TogruteID) ON UPDATE CASCADE ON DELETE CASCADE
)

CREATE TABLE Ukedager (
	TogruteID INTEGER NOT NULL,
	Ukedag TEXT NOT NULL,
	CONSTRAINT ukedag_pk PRIMARY KEY (TogruteID, Ukedag),
	CONSTRAINT togrute_fk FOREIGN KEY (TogruteID) REFERENCES Togrute(TogruteID) ON UPDATE CASCADE ON DELETE CASCADE
)

CREATE TABLE VognOppsett (
	VognOppsettID INTEGER NOT NULL,
	CONSTRAINT vognOppsett_pk PRIMARY KEY (VognOppsettID)
)

CREATE TABLE HarVogn (
	VognOppsettID INTEGER NOT NULL, 
	VognTypeNavn TEXT NOT NULL, 
	OppsettNr INTEGER,
	CONSTRAINT harVogn_pk PRIMARY KEY (VognOppsettID, VognTypeNavn),
	CONSTRAINT vognOppsett_fk FOREIGN (VognOppsettID) KEY REFERENCES VognOppsett(VognOppsettID) ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT sittevogn_fk FOREIGN KEY (VognTypeNavn) REFERENCES Sittevogn(Navn) ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT sovevogn_fk FOREIGN KEY (VognTypeNavn) REFERENCES Sovevogn(Navn) ON UPDATE CASCADE ON DELETE CASCADE
)

CREATE TABLE HarVognType (
	OperatørNavn TEXT NOT NULL, 
	VognTypeNavn TEXT NOT NULL,
	CONSTRAINT harVognType_pk PRIMARY KEY (OperatørNavn, VognTypeNavn),
	CONSTRAINT sittevogn_fk FOREIGN KEY (VognTypeNavn) REFERENCES Sittevogn(Navn) ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT sovevogn_fk FOREIGN KEY (VognTypeNavn) REFERENCES Sovevogn(Navn) ON UPDATE CASCADE ON DELETE CASCADE
)r

CREATE TABLE Kupee (
	KupeeNr INTEGER NOT NULL,
	VognTypeNavn TEXT NOT NULL,
	CONSTRAINT kupee_pk PRIMARY KEY (KupeeNr, VognTypeNavn),
	CONSTRAINT vogntype_fk FOREIGN KEY (VognTypeNavn) REFERENCES Sovevogn(Navn) ON UPDATE CASCADE ON DELETE SET NULL
)

CREATE TABLE BillettKupee (
	OrdreNr INTEGER NOT NULL,
	KupeeNr INTEGER NOT NULL,
	VognTypeNavn TEXT NOT NULL, 
	HarBestiltSeng1 INTEGER, 
	HarBestiltSeng2 INTEGER,
	CONSTRAINT billettKupee_pk PRIMARY KEY (OrdreNr, KupeeNr, VognTypeNavn),
	CONSTRAINT ordre_fk FOREIGN KEY (OrdreNr) REFERENCES KundeOrdre(OrdreNr) ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT kupee_fk FOREIGN KEY (KupeeNr) REFERENCES Kupee(KupeeNr) ON UPDATE CASCADE ON DELETE CASCADE
)

CREATE TABLE BillettSeteDelstrekning(
  DelstrekningsID INTEGER NOT NULL,
  OrdreNr INTEGER NOT NULL,
  SeteNr INTEGER NOT NULL,
  VognTypeNavn TEXT NOT NULL,
  CONSTRAINT BillettSeteDelstrekning_pk PRIMARY KEY (DelstrekningsID, OrdreNr, SeteNr, VognTypeNavn),
  CONSTRAINT Delstrekning_fk FOREIGN KEY (DelstrekningsID) REFERENCES Delstrekning(DelstrekningsID) ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT Sete_fk FOREIGN KEY (SeteNr, VognTypeNavn) REFERENCES Sete(SeteNr, VognTypeNavn) ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT sittevogn_fk FOREIGN KEY (VognTypeNavn) REFERENCES SitteVogn(Navn) ON UPDATE CASCADE ON DELETE CASCADE
)