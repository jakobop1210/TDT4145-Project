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

CREATE TABLE BillettKupee (
	BillettID INTEGER NOT NULL, 
	OrdreNr INTEGER, 
	Dato date, 
	TogruteID INTEGER, 
	KupeeNr INTEGER, 
	VognID INTEGER
	CONSTRAINT billettKupee_pk PRIMARY KEY (BillettID),
	CONSTRAINT kundeOrdre_fk FOREIGN KEY (OrdreNr) REFERENCES KundeOrdre(OrdreNr) ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT togruteForekomst_fk FOREIGN KEY (Dato, TogruteID) REFERENCES TogruteForekomst(Dato, TogruteID) ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT sete_fk FOREIGN KEY (KupeeNr, VognID) REFERENCES Kupee(KupeeNr, VognID) ON UPDATE CASCADE ON DELETE CASCADE
)

CREATE TABLE BillettSete (
	BillettID INTEGER NOT NULL, 
	OrdreNr INTEGER, 
	Dato date, 
	TogruteID INTEGER, 
	SeteNr INTEGER, 
	VognID INTEGER
	CONSTRAINT billettKupee_pk PRIMARY KEY (BillettID),
	CONSTRAINT kundeOrdre_fk FOREIGN KEY (OrdreNr) REFERENCES KundeOrdre(OrdreNr) ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT togruteForekomst_fk FOREIGN KEY (Dato, TogruteID) REFERENCES TogruteForekomst(Dato, TogruteID) ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT sete_fk FOREIGN KEY (SeteNr, VognID) REFERENCES Sete(Setenr, VognID) ON UPDATE CASCADE ON DELETE CASCADE
)

CREATE TABLE Operatør(
	Navn TEXT NOT NULL,
	CONSTRAINT operator_pk PRIMARY KEY (Navn)
)

CREATE TABLE Sittevogn (
	VognID INTEGER NOT NULL,
	AntallRader INTEGER,
	SeterPerRad INTEGER,
	OperatørNavn TEXT,
	VognOppsettID INTEGER,
	CONSTRAINT sittevogn_pk PRIMARY KEY (VognID)
	CONSTRAINT operatør_fk FOREIGN KEY (OperatørNavn) REFERENCES Operatør(Navn) ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT vognOppsett_fk FOREIGN KEY (VognOppsettID) REFERENCES VognOppsett(VognOppsettID) ON UPDATE CASCADE ON DELETE SET NULL
)

CREATE TABLE Sete (
	SeteNr INTEGER NOT NULL,
	VognID TEXT NOT NULL,
	CONSTRAINT sete_pk PRIMARY KEY (SeteNr, VognID),
	CONSTRAINT vogntype_fk FOREIGN KEY (VognID) REFERENCES Sittevogn(VognID) ON UPDATE CASCADE ON DELETE CASCADE
)

CREATE TABLE DelstrekningForSete (
	BillettID INTEGER NOT NULL, 
	DelstrekningsID INTEGER NOT NULL,
	CONSTRAINT delstrekningForSete_pk PRIMARY KEY (BillettID, DelstrekningsID),
	CONSTRAINT billett_fk FOREIGN KEY (BillettID) REFERENCES BillettSete(BillettID) ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT DelstrekningsID FOREIGN KEY (DelstrekningsID) REFERENCES Delstrekning(DelstrekningsID) ON UPDATE CASCADE ON DELETE CASCADE
)

CREATE TABLE Sovevogn (
	VognID INTEGER NOT NULL,
	AntallKupeer INTEGER,
	OperatørNavn TEXT,
	VognOppsettID INTEGER,
	CONSTRAINT sovevogn_pk PRIMARY KEY (VognID),
	CONSTRAINT operatør_fk FOREIGN KEY (OperatørNavn) REFERENCES Operatør(Navn) ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT vognOppsett_fk FOREIGN KEY (VognOppsettID) REFERENCES VognOppsett(VognOppsettID) ON UPDATE CASCADE ON DELETE SET NULL
)

CREATE TABLE Kupee (
	KupeeNr INTEGER NOT NULL,
	VognID INTEGER NOT NULL,
	CONSTRAINT kupee_pk PRIMARY KEY (KupeeNr, VognID),
	CONSTRAINT sovevogn_fk FOREIGN KEY (VognID) REFERENCES Sovevogn(VognID) ON UPDATE CASCADE ON DELETE SET NULL
)

CREATE TABLE VognOppsett (
	VognOppsettID INTEGER NOT NULL,
	CONSTRAINT vognOppsett_pk PRIMARY KEY (VognOppsettID)
)




-- CREATE TABLE BillettKupee (
-- 	OrdreNr INTEGER NOT NULL,
-- 	KupeeNr INTEGER NOT NULL,
-- 	VognID INTEGER NOT NULL, 
-- 	HarBestiltSeng1 INTEGER, 
-- 	HarBestiltSeng2 INTEGER,
-- 	CONSTRAINT billettKupee_pk PRIMARY KEY (OrdreNr, KupeeNr, VognID),
-- 	CONSTRAINT ordre_fk FOREIGN KEY (OrdreNr) REFERENCES KundeOrdre(OrdreNr) ON UPDATE CASCADE ON DELETE CASCADE,
-- 	CONSTRAINT kupee_fk FOREIGN KEY (KupeeNr, VognID) REFERENCES Kupee(KupeeNr, VognID) ON UPDATE CASCADE ON DELETE CASCADE
-- )

-- CREATE TABLE BillettDelstrekningForOrdreAvSete (
-- 	DelstrekningsID INTEGER NOT NULL, 
-- 	OrdreNr INTEGER NOT NULL,
-- 	CONSTRAINT billettForOrdreAvSete_pk PRIMARY KEY (DelstrekningsID, OrdreNr),
-- 	CONSTRAINT delstreknings_fk FOREIGN KEY DelstrekningsID REFERENCES Delstrekning(DelstrekningsID) ON UPDATE CASCADE ON DELETE CASCADE,
-- 	CONSTRAINT ordre_fk FOREIGN KEY OrdreNr REFERENCES KundeOrdre(OrdreNr) ON UPDATE CASCADE ON DELETE CASCADE
-- )

-- CREATE TABLE BillettSete(
-- 	OrdreNr INTEGER NOT NULL, 
-- 	SeteNr INTEGER NOT NULL, 
-- 	VognID INTEGER NOT NULL,
-- 	CONSTRAINT billettSete_pk PRIMARY KEY (OrdreNr, SeteNr, VognID),
-- 	CONSTRAINT kundeOrdre_fk FOREIGN KEY (OrdreNr) REFERENCES KundeOrdre(OrdreNr) ON UPDATE CASCADE ON DELETE CASCADE,
-- 	CONSTRAINT sete_fk FOREIGN KEY (SeteNr, VognID) REFERENCES Sete(SeteNr, VognID) ON UPDATE CASCADE ON DELETE CASCADE
-- )

