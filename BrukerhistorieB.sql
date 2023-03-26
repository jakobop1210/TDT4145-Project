-- Opprette Operatør-tabellen
INSERT INTO Operatør VALUES ('SJ');

-- Legge inn togruter i databasen
INSERT INTO Togrute VALUES 
    (1, 1, 'SJ'),
    (2, 1, 'SJ'),
    (3, 0, 'SJ');

-- Opprette sittevogn og seter
INSERT INTO Sittevogn(Navn, NrIVognOppsett, AntallRader, SeterPerRad, OperatørNavn, TogruteID) VALUES 
    ('SJ-sittevogn-1', 1, 3, 4, 'SJ', 1),
    ('SJ-sittevogn-1', 2, 3, 4, 'SJ', 1),
    ('SJ-sittevogn-1', 1, 3, 4, 'SJ', 2),
    ('SJ-sittevogn-1', 1, 3, 4, 'SJ', 3);

-- Legge inn sete 1 til sete 12 i hver vogn
INSERT INTO Sete VALUES 
    (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (8, 1), (9, 1), (10, 1), (11, 1), (12, 1),
    (1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2), (8, 2), (9, 2), (10, 2), (11, 2), (12, 2),
    (1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (7, 3), (8, 3), (9, 3), (10, 3), (11, 3), (12, 3),
    (1, 4), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4), (8, 4), (9, 4), (10, 4), (11, 4), (12, 4);

-- Opprette sovevogn og kupéer
INSERT INTO Sovevogn(Navn, NrIVognOppsett, AntallKupeer, OperatørNavn, TogruteID) VALUES ('SJ-sovevogn-1', 2, 4, 'SJ', 2);
INSERT INTO Kupee VALUES 
    (1, 5),
    (2, 5),
    (3, 5),
    (4, 5);


-- Opprette togrutetabell StasjonerIRute. Antar at ankomsttid er 5 min før oppgitt klokkeslett i oppgaven,
-- og at avgangstid er oppgitt tid. For siste stasjon antar vi at ankomsttid er oppgitt tid. 

-- Togrute 1
INSERT INTO StasjonerIRute VALUES 
    ("Trondheim", 1, NULL, "07:49", 1),
    ("Steinkjer", 1, "09:46", "09:51", 2),
    ("Mosjøen", 1, "13:15", "13:20", 3),
    ("Mo i Rana", 1, "14:26", "14:31", 4),
    ("Fauske", 1, "16:44", "16:49", 5),
    ("Bodø", 1, "17:34", NULL, 6);

-- Togrute 2
INSERT INTO StasjonerIRute VALUES 
    ("Trondheim", 2, NULL, "23:05", 1),
    ("Steinkjer", 2, "00:52", "00:57", 2),
    ("Mosjøen", 2, "04:36", "04:41", 3),
    ("Mo i Rana", 2, "05:50", "05:55", 4),
    ("Fauske", 2, "08:14", "08:19", 5),
    ("Bodø", 2, "09:05", NULL, 6);

-- Togrute 3
INSERT INTO StasjonerIRute VALUES 
    ("Mo i Rana", 3, NULL, "08:11", 1),
    ("Mosjøen", 3, "09:09", "09:14", 2),
    ("Steinkjer", 3, "12:26", "12:31", 3),
    ("Trondheim", 3, "14:13", NULL, 4);

-- Legge inn data i  Ukedager-tabellen. NB! Tilhører egentlig brukerhistorie C, 
-- men står her for å kunne kjøre C flere ganger uten å måtte kommentere ut denne koden
INSERT INTO Ukedager VALUES (1, 'Mandag');
INSERT INTO Ukedager VALUES (1, 'Tirsdag');
INSERT INTO Ukedager VALUES (1, 'Onsdag');
INSERT INTO Ukedager VALUES (1, 'Torsdag');
INSERT INTO Ukedager VALUES (1, 'Fredag');
INSERT INTO Ukedager VALUES (3, 'Mandag');
INSERT INTO Ukedager VALUES (3, 'Tirsdag');
INSERT INTO Ukedager VALUES (3, 'Onsdag');
INSERT INTO Ukedager VALUES (3, 'Torsdag');
INSERT INTO Ukedager VALUES (3, 'Fredag');
INSERT INTO Ukedager VALUES (2, 'Mandag');
INSERT INTO Ukedager VALUES (2, 'Tirsdag');
INSERT INTO Ukedager VALUES (2, 'Onsdag');
INSERT INTO Ukedager VALUES (2, 'Torsdag');
INSERT INTO Ukedager VALUES (2, 'Fredag');
INSERT INTO Ukedager VALUES (2, 'Lørdag');
INSERT INTO Ukedager VALUES (2, 'Søndag');

   
