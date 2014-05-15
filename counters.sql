-- counters as modbus registers, several (2,3 or 4) registers can be combined to increase the counter size
-- member is the order of the values in multivalue messages. x1,x2 and y1,y2 define the linear conversion from raw to value
-- power calculation based on increment is possible in adition to cumulative readings. behavior depends on config

-- CONFIG BIT MEANINGS
-- # 1 - below outlo warning, 4 
-- # 2 - below outlo critical, 8 - above outhi critical
-- # 4 - above outhi warning
-- # 8   above outhi critical

-- 16 - immediate notification on status change (USED FOR STATE FROM POWER)
-- 32 - value limits to status inversion  - voimaldab anda YHTE kollast/punast ala, naiteks tanavavalgustuse jaoks  
-- 64 - power flag
-- 128 - state from power flag
-- 256 - notify on 10% value change (not only limit crossing that becomes activated by 5 or 10)
-- 512 - do not report at all, for internal usage
-- counters are normally located in 2 registers 
-- comment used for read group defining, speeds up reading
 
PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
-- ts is time when count was changed. without change ts is not updated! block is off_tout for on/off state detection
CREATE TABLE counters(mba,regadd,val_reg,member,cfg,x1,x2,y1,y2,outlo,outhi,avg,block,raw,value,status,ts,desc,comment,wcount INTEGER,mbi integer);
-- INSERT INTO "counters" VALUES('1','400','E1CW','1','0','0','1000','0','1000','','','2','100','','','','','en tarve Wh','c1.400-405',-2,0); -- fiider 1 faas 1
-- INSERT INTO "counters" VALUES('1','402','E1CW','2','0','0','1000','0','1000','','','2','100','','','','','en tarve Wh','c1.400-405',-2,0); -- fiider 1 faas 2
-- INSERT INTO "counters" VALUES('1','404','E1CW','3','0','0','1000','0','1000','','','2','100','','','','','en tarve Wh','c1.400-405',-2,0); -- fiider 1 faas 3
-- techbase MSW ja LSW on vahetuses! sama jama kui barionetil.

-- INSERT INTO "counters" VALUES('1','406','E2CW','1','0','0','1000','0','1000','','','2','100','','','','','en tarve Wh','c1.406-411',-2,0); -- fiider 2 faas 1
-- INSERT INTO "counters" VALUES('1','408','E2CW','2','0','0','1000','0','1000','','','2','100','','','','','en tarve Wh','c1.406-411',-2,0); -- fiider 2 faas 2
-- INSERT INTO "counters" VALUES('1','410','E2CW','3','0','0','1000','0','1000','','','2','100','','','','','en tarve Wh','c1.406-411',-2,0); -- fiider 2 faas 3

-- allpool normaalne ioplaat
INSERT INTO "counters" VALUES('1','400','E1CW','1','0','0','1000','0','1000','','','2','100','','','','','en tarve Wh','c1.400-405',2,1); -- fiider 1 faas 1
INSERT INTO "counters" VALUES('1','402','E1CW','2','0','0','1000','0','1000','','','2','100','','','','','en tarve Wh','c1.400-405',2,1); -- fiider 1 faas 1
INSERT INTO "counters" VALUES('1','404','E1CW','3','0','0','1000','0','1000','','','2','100','','','','','en tarve Wh','c1.400-405',2,1); -- fiider 1 faas 1

INSERT INTO "counters" VALUES('1','406','E2CW','1','0','0','1000','0','1000','','','2','100','','','','','en tarve Wh','c1.400-405',2,1); -- fiider 1 faas 1
INSERT INTO "counters" VALUES('1','408','E2CW','2','0','0','1000','0','1000','','','2','100','','','','','en tarve Wh','c1.400-405',2,1); -- fiider 1 faas 1
INSERT INTO "counters" VALUES('1','410','E2CW','3','0','0','1000','0','1000','','','2','100','','','','','en tarve Wh','c1.400-405',2,1); -- fiider 1 faas 1


-- INSERT INTO "counters" VALUES('14','1','E1CW','1','0','0','1000','0','1000','','','2','100','','','','','en tarve Wh','c1.400-405',2,1); -- fiider 1 faas 1
-- INSERT INTO "counters" VALUES('14','3','E1CW','2','0','0','1000','0','1000','','','2','100','','','','','en tarve Wh','c1.400-405',2,1); -- fiider 1 faas 2
-- INSERT INTO "counters" VALUES('14','5','E1CW','3','0','0','1000','0','1000','','','2','100','','','','','en tarve Wh','c1.400-405',2,1); -- fiider 1 faas 3

-- INSERT INTO "counters" VALUES('15','1','E2CW','1','0','0','1000','0','1000','','','2','100','','','','','en tarve Wh','c1.406-411',2,1); -- fiider 2 faas 1
-- INSERT INTO "counters" VALUES('15','3','E2CW','2','0','0','1000','0','1000','','','2','100','','','','','en tarve Wh','c1.406-411',2,1); -- fiider 2 faas 2
-- INSERT INTO "counters" VALUES('15','5','E2CW','3','0','0','1000','0','1000','','','2','100','','','','','en tarve Wh','c1.406-411',2,1); -- fiider 2 faas 3

-- INSERT INTO "counters" VALUES('17','1','E3CW','1','0','0','1000','0','1000','','','2','30','','','','','en tarve Wh','c3.1-6',2,1); -- fiider 3 faas 1
-- INSERT INTO "counters" VALUES('17','3','E3CW','2','0','0','1000','0','1000','','','2','30','','','','','en tarve Wh','c3.1-6',2,1); -- fiider 3 faas 2
-- INSERT INTO "counters" VALUES('17','5','E3CW','3','0','0','1000','0','1000','','','2','30','','','','','en tarve Wh','c3.1-6',2,1); -- fiider 3 faas 3

-- INSERT INTO "counters" VALUES('3','1','E4W','1','0','0','1000','0','1000','','','','','','','','','en tarve Wh','c3.1-6',2,1); -- fiider 4 faas 1
-- INSERT INTO "counters" VALUES('3','3','E4W','2','0','0','1000','0','1000','','','','','','','','','en tarve Wh','c3.1-6',2,1); -- fiider 4 faas 2
-- INSERT INTO "counters" VALUES('3','5','E4W','3','0','0','1000','0','1000','','','','','','','','','en tarve Wh','c3.1-6',2,1); -- fiider 4 faas 3

-- block kasutame off thresholdi etteandmiseks sekundites (kui nii kaua uusi imp ei tule siis on off)
-- voimused faaside kaupa et igale oma threshold anda
-- INSERT INTO "counters" VALUES('14','1','P11W','1','357','0','1','0','3600','1000','2200','2','30','','','','','en tarve Wh','',2,1); -- fiider 1 faas 1 W, keeluaken 2
-- ioplaat
INSERT INTO "counters" VALUES('1','400','P11W','1','357','0','1','0','3600','1000','2200','2','30','','','','','en tarve Wh','',2,1); -- fiider 1 faas 1 W, keeluaken 2
INSERT INTO "counters" VALUES('','','P11W','2','','0','1','0','3600','','','2','100','','1000','','','abijoon Wh','',2,0); -- fiider 1 faas 1 W, keskm 2
INSERT INTO "counters" VALUES('','','P11W','3','','0','1','0','3600','','','2','100','','2000','','','abijoon Wh','',2,0); -- fiider 1 faas 1 W, keskm 2
-- INSERT INTO "counters" VALUES('14','3','P12W','1','357','0','1','0','3600','1000','2200','2','30','','','','','en tarve Wh','',2,1); -- fiider 1 faas 2 W, keeluaken 2
INSERT INTO "counters" VALUES('1','402','P12W','1','357','0','1','0','3600','1000','2200','2','30','','','','','en tarve Wh','',2,1); -- fiider 1 faas 2 W, keeluaken 2
INSERT INTO "counters" VALUES('','','P12W','2','','0','1','0','3600','','','2','100','','1000','','','abijoon Wh','',2,0); -- fiider 1 faas 1 W, keskm 2
INSERT INTO "counters" VALUES('','','P12W','3','','0','1','0','3600','','','2','100','','2000','','','abijoon Wh','',2,0); -- fiider 1 faas 1 W, keskm 2
-- INSERT INTO "counters" VALUES('14','5','P13W','1','357','0','1','0','3600','200','2200','2','30','','','','','en tarve Wh','',2,1); -- fiider 1 faas 3 W, keeluaken 2
INSERT INTO "counters" VALUES('1','404','P13W','1','357','0','1','0','3600','200','2200','2','30','','','','','en tarve Wh','',2,1); -- fiider 1 faas 3 W, keeluaken 2
INSERT INTO "counters" VALUES('','','P13W','2','','0','1','0','3600','','','2','100','','200','','','abijoon Wh','',2,0); -- fiider 1 faas 1 W, keskm 2
INSERT INTO "counters" VALUES('','','P13W','3','','0','1','0','3600','','','2','100','','2200','','','abijoon Wh','',2,0); -- fiider 1 faas 1 W, keskm 2

-- INSERT INTO "counters" VALUES('15','1','P21W','1','357','0','1','0','3600','1000','2200','2','30','','','','','en tarve Wh','',2,1); -- fiider 2 faas 1 W, keeluaken 2
INSERT INTO "counters" VALUES('1','406','P21W','1','357','0','1','0','3600','1000','2200','2','30','','','','','en tarve Wh','',2,1); -- fiider 2 faas 1 W, keeluaken 2
INSERT INTO "counters" VALUES('','','P21W','2','','0','1','0','3600','','','2','100','','1000','','','abijoon Wh','',2,0); -- fiider 2 faas 1 W, keskm 2
INSERT INTO "counters" VALUES('','','P21W','3','','0','1','0','3600','','','2','100','','2000','','','abijoon Wh','',2,0); -- fiider 2 faas 1 W, keskm 2
-- INSERT INTO "counters" VALUES('15','3','P22W','1','357','0','1','0','3600','1000','2200','2','30','','','','','en tarve Wh','',2,1); -- fiider 2 faas 2 W, keeluaken 2
INSERT INTO "counters" VALUES('1','408','P22W','1','357','0','1','0','3600','1000','2200','2','30','','','','','en tarve Wh','',2,1); -- fiider 2 faas 2 W, keeluaken 2
INSERT INTO "counters" VALUES('','','P22W','2','','0','1','0','3600','','','2','100','','1000','','','abijoon Wh','',2,0); -- fiider 2 faas 1 W, keskm 2
INSERT INTO "counters" VALUES('','','P22W','3','','0','1','0','3600','','','2','100','','2000','','','abijoon Wh','',2,0); -- fiider 2 faas 1 W, keskm 2
-- INSERT INTO "counters" VALUES('15','5','P23W','1','357','0','1','0','3600','200','2200','2','30','','','','','en tarve Wh','',2,1); -- fiider 2 faas 3 W, keeluaken 2
INSERT INTO "counters" VALUES('1','410','P23W','1','357','0','1','0','3600','200','2200','2','30','','','','','en tarve Wh','',2,1); -- fiider 2 faas 3 W, keeluaken 2
INSERT INTO "counters" VALUES('','','P23W','2','','0','1','0','3600','','','2','100','','200','','','abijoon Wh','',2,0); -- fiider 2 faas 1 W, keskm 2
INSERT INTO "counters" VALUES('','','P23W','3','','0','1','0','3600','','','2','100','','2200','','','abijoon Wh','',2,0); -- fiider 2 faas 1 W, keskm 2

-- INSERT INTO "counters" VALUES('17','1','P31W','1','357','0','1','0','3600','1000','2200','2','30','','','','','en tarve Wh','',2,1); -- fiider 3 faas 1 W, keeluaken 2
-- INSERT INTO "counters" VALUES('1','412','P31W','1','357','0','1','0','3600','1000','2200','2','30','','','','','en tarve Wh','',2,1); -- fiider 3 faas 1 W, keeluaken 2
-- INSERT INTO "counters" VALUES('','','P31W','2','','0','1','0','3600','','','2','100','','1000','','','abijoon Wh','',2,0); -- fiider 3 faas 1 W, keskm 2
INSERT INTO "counters" VALUES('','','P31W','3','','0','1','0','3600','','','2','100','','2000','','','abijoon Wh','',2,0); -- fiider 3 faas 1 W, keskm 2
-- INSERT INTO "counters" VALUES('17','3','P32W','1','357','0','1','0','3600','1000','2200','2','30','','','','','en tarve Wh','',2,1); -- fiider 3 faas 2 W, keeluaken 2
-- INSERT INTO "counters" VALUES('1','414','P32W','1','357','0','1','0','3600','1000','2200','2','30','','','','','en tarve Wh','',2,1); -- fiider 3 faas 2 W, keeluaken 2
-- INSERT INTO "counters" VALUES('','','P32W','2','','0','1','0','3600','','','2','100','','1000','','','abijoon Wh','',2,0); -- fiider 3 faas 1 W, keskm 2
-- INSERT INTO "counters" VALUES('','','P32W','3','','0','1','0','3600','','','2','100','','2000','','','abijoon Wh','',2,0); -- fiider 3 faas 1 W, keskm 2
-- INSERT INTO "counters" VALUES('17','5','P33W','1','357','0','1','0','3600','200','2200','2','30','','','','','en tarve Wh','',2,1); -- fiider 3 faas 3 W, keeluaken 2
-- INSERT INTO "counters" VALUES('1','416','P33W','1','357','0','1','0','3600','200','2200','2','30','','','','','en tarve Wh','',2,1); -- fiider 3 faas 3 W, keeluaken 2
-- INSERT INTO "counters" VALUES('','','P33W','2','','0','1','0','3600','','','2','100','','200','','','abijoon Wh','',2,0); -- fiider 3 faas 1 W, keskm 2
-- INSERT INTO "counters" VALUES('','','P33W','3','','0','1','0','3600','','','2','100','','2200','','','abijoon Wh','',2,0); -- fiider 3 faas 1 W, keskm 2

-- automaatselt tuleks abijoonte value votta pohiliikme min ja max seest... aga kuidas viidata?
 
-- faasid koos, ilma thresholdita
-- INSERT INTO "counters" VALUES('1','400','P1W','1','64','0','1','0','3600','','','2','100','','','','','en tarve Wh','c1.400-405',-2,0); -- fiider 1 faas 1 W, keskm 2
-- INSERT INTO "counters" VALUES('1','402','P1W','2','64','0','1','0','3600','','','2','100','','','','','en tarve Wh','c1.400-405',-2,0); -- fiider 1 faas 2 W
-- INSERT INTO "counters" VALUES('1','404','P1W','3','64','0','1','0','3600','','','2','100','','','','','en tarve Wh','c1.400-405',-2,0); -- fiider 1 faas 3 W

-- INSERT INTO "counters" VALUES('1','406','P2W','1','64','0','1','0','3600','','','2','100','','','','','en tarve Wh','c1.400-405',-2,0); -- fiider 2 faas 1 W, keskm 2
-- INSERT INTO "counters" VALUES('1','408','P2W','2','64','0','1','0','3600','','','2','100','','','','','en tarve Wh','c1.400-405',-2,0); -- fiider 2 faas 2 W
-- INSERT INTO "counters" VALUES('1','410','P2W','3','64','0','1','0','3600','','','2','100','','','','','en tarve Wh','c1.400-405',-2,0); -- fiider 2 faas 3 W

-- INSERT INTO "counters" VALUES('17','1','P3W','1','357','0','1','0','3600','1000','2200','2','30','','','','','en tarve Wh','c1.400-405',2,1); -- fiider 3 faas 1 W, 
-- INSERT INTO "counters" VALUES('17','3','P3W','2','357','0','1','0','3600','1000','1800','2','30','','','','','en tarve Wh','c1.400-405',2,1); -- fiider 3 faas 2 W
-- INSERT INTO "counters" VALUES('17','5','P3W','3','357','0','1','0','3600','1000','1800','2','30','','','','','en tarve Wh','c1.400-405',2,1); -- fiider 3 faas 3 W

-- INSERT INTO "counters" VALUES('1','400','R1W','1','148','0','1','0','1','0','0','','10','','','','','en tarve on/off','c1.400-405',-2,0); -- ON OFF , IMMEDIATE NOTIF
-- INSERT INTO "counters" VALUES('1','402','R1W','2','148','0','1','0','1','0','0','','10','','','','','en tarve on/off','c1.400-405',-2,0); -- ON OFF , IMMEDIATE NOTIF
-- INSERT INTO "counters" VALUES('1','404','R1W','3','148','0','1','0','1','0','0','','10','','','','','en tarve on/off','c1.400-405',-2,0); -- ON OFF , IMMEDIATE NOTIF

-- INSERT INTO "counters" VALUES('1','406','R2W','1','148','0','1','0','1','0','0','','10','','','','','en tarve on/off','c1.400-405',-2,0); -- ON OFF , IMMEDIATE NOTIF
-- INSERT INTO "counters" VALUES('1','408','R2W','2','148','0','1','0','1','0','0','','10','','','','','en tarve on/off','c1.400-405',-2,0); -- ON OFF , IMMEDIATE NOTIF
-- INSERT INTO "counters" VALUES('1','410','R2W','3','148','0','1','0','1','0','0','','10','','','','','en tarve on/off','c1.400-405',-2,0); -- ON OFF , IMMEDIATE NOTIF

-- ioplaat
INSERT INTO "counters" VALUES('1','400','R1W','1','148','0','1','0','1','0','0','','30','','','','','en tarve on/off','',2,1); -- ON OFF , IMMEDIATE NOTIF
INSERT INTO "counters" VALUES('1','402','R1W','2','148','0','1','0','1','0','0','','30','','','','','en tarve on/off','',2,1); -- ON OFF , IMMEDIATE NOTIF
INSERT INTO "counters" VALUES('1','404','R1W','3','148','0','1','0','1','0','0','','30','','','','','en tarve on/off','',2,1); -- ON OFF , IMMEDIATE NOTIF

INSERT INTO "counters" VALUES('1','406','R2W','1','148','0','1','0','1','0','0','','30','','','','','en tarve on/off','',2,1); -- ON OFF , IMMEDIATE NOTIF
INSERT INTO "counters" VALUES('1','408','R2W','2','148','0','1','0','1','0','0','','30','','','','','en tarve on/off','',2,1); -- ON OFF , IMMEDIATE NOTIF
INSERT INTO "counters" VALUES('1','410','R2W','3','148','0','1','0','1','0','0','','30','','','','','en tarve on/off','',2,1); -- ON OFF , IMMEDIATE NOTIF


-- INSERT INTO "counters" VALUES('14','1','R1W','1','148','0','1','0','1','0','0','','10','','','','','en tarve on/off','',2,1); -- ON OFF , IMMEDIATE NOTIF
-- INSERT INTO "counters" VALUES('14','3','R1W','2','148','0','1','0','1','0','0','','10','','','','','en tarve on/off','',2,1); -- ON OFF , IMMEDIATE NOTIF
-- INSERT INTO "counters" VALUES('14','5','R1W','3','148','0','1','0','1','0','0','','10','','','','','en tarve on/off','',2,1); -- ON OFF , IMMEDIATE NOTIF

-- INSERT INTO "counters" VALUES('15','1','R2W','1','148','0','1','0','1','0','0','','10','','','','','en tarve on/off','',2,1); -- ON OFF , IMMEDIATE NOTIF
-- INSERT INTO "counters" VALUES('15','3','R2W','2','148','0','1','0','1','0','0','','10','','','','','en tarve on/off','',2,1); -- ON OFF , IMMEDIATE NOTIF
-- INSERT INTO "counters" VALUES('15','5','R2W','3','148','0','1','0','1','0','0','','10','','','','','en tarve on/off','',2,1); -- ON OFF , IMMEDIATE NOTIF

-- INSERT INTO "counters" VALUES('17','1','R3W','1','148','0','1','0','1','0','0','','10','','','','','en tarve on/off','',2,1); -- ON OFF , IMMEDIATE NOTIF
-- INSERT INTO "counters" VALUES('17','3','R3W','2','148','0','1','0','1','0','0','','10','','','','','en tarve on/off','',2,1); -- ON OFF , IMMEDIATE NOTIF
-- INSERT INTO "counters" VALUES('17','5','R3W','3','148','0','1','0','1','0','0','','10','','','','','en tarve on/off','',2,1); -- ON OFF , IMMEDIATE NOTIF


-- INSERT INTO "counters" VALUES('14','1','R11V','1','640','0','1','0','1','0','0','','10','','0','','','internal state on/off','',2,1); -- ON OFF , IMMEDIATE NOTIF
-- INSERT INTO "counters" VALUES('14','3','R12V','1','640','0','1','0','1','0','0','','10','','0','','','internal state on/off','',2,1); -- ON OFF , IMMEDIATE NOTIF
-- INSERT INTO "counters" VALUES('14','5','R13V','1','640','0','1','0','1','0','0','','10','','0','','','internal state on/off','',2,1); -- ON OFF , IMMEDIATE NOTIF

-- INSERT INTO "counters" VALUES('15','1','R21V','1','640','0','1','0','1','0','0','','10','','0','','','internal state on/off','',2,1); -- ON OFF , IMMEDIATE NOTIF
-- INSERT INTO "counters" VALUES('15','3','R22V','1','640','0','1','0','1','0','0','','10','','0','','','internal state on/off','',2,1); -- ON OFF , IMMEDIATE NOTIF
-- INSERT INTO "counters" VALUES('15','5','R23V','1','640','0','1','0','1','0','0','','10','','0','','','internal state on/off','',2,1); -- ON OFF , IMMEDIATE NOTIF

-- INSERT INTO "counters" VALUES('17','1','R31V','1','640','0','1','0','1','0','0','','10','','0','','','internal state on/off','',2,1); -- ON OFF , IMMEDIATE NOTIF
-- INSERT INTO "counters" VALUES('17','3','R32V','1','640','0','1','0','1','0','0','','10','','0','','','internal state on/off','',2,1); -- ON OFF , IMMEDIATE NOTIF
-- INSERT INTO "counters" VALUES('17','5','R33V','1','640','0','1','0','1','0','0','','10','','0','','','internal state on/off','',2,1); -- ON OFF , IMMEDIATE NOTIF
-- value algseis ei tohi '' olla! neid eelmisi ei saada! R11S ei toimi, kasuta R11V jne!

-- sama mbi, mba, regadd read taidetakse yhekorraga!

-- wcount -2 is for barionet, lsw msw order weird. normally 2 for msw, lsw. can be 1 or 4 as well.

-- power to be counted based on raw reading increment and time between the readings.
-- P1W is sending W for electricity and gas consumption. cannot be negative or more than 15 / 30 kW
-- INSERT INTO "counters" VALUES('1','410','P1W','1','16','0','500','0','3600000','0','20000','2','','','','','','el voimus, 500 imp=3600 kWs','max 15kW 25A kaitsmete korral?',-2);
-- INSERT INTO "counters" VALUES('1','412','P1W','2','16','0','100','0','33732000','0','30000','2','','','','','','gaasi voimsus kv alusel, 100 imp=33732000 Ws','max 30kW?',-2);

CREATE UNIQUE INDEX co_regmember on 'counters'(val_reg,member);
COMMIT;

