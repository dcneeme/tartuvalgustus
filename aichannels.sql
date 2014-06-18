-- airmonitor_srik jaoks! comment asemel dsp_id. tugipinge 4v, 1 kvant = 1 mv! reg270=0030

-- analogue values and temperatures channel definitions for android-based automation controller 
-- x1 ja x2 for input range, y1 y2 for output range. conversion based on 2 points x1,y1 and y1,y2. x=raw, y=value.
-- avg defines averaging strength, has effect starting from 2

-- # CONFIGURATION BITS
-- # siin ei ole tegemist ind ja grp teenuste eristamisega, ind teenused konfitakse samadel alustel eraldi!
-- # konfime poolbaidi vaartustega, siis hex kujul hea vaadata. vanem hi, noorem lo!
-- # x0 - alla outlo ikka ok, 0x - yle outhi ikka ok 
-- # x1 - alla outlo warning, 1x - yle outhi warning
-- # x2 - alla outlo critical, 2x - yle outhi critical
-- # x3 - alla outlo ei saada, 3x - yle outhi ei saada
-- #      8x ei saada monitooringusse?


-- x1 x2 y1 y2 values needed also for virtual setup values, where no linear conversions is needed. use 0 100 0 100 not to convert
-- block kasutada grupeerimiseks, polleritesse?

PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
-- drop table aichannels; -- remove the old one

CREATE TABLE aichannels(mba,regadd,val_reg,member,cfg,x1,x2,y1,y2,outlo,outhi,avg,block,raw,value,status,ts,desc,dsp_id,type integer,mbi integer); -- type vt chantypes
-- type is for category flagging, 0=do, 1 = di, 2=ai, 3=ti. use only 2 and 3 in this table (4=humidity, 5=co2?)
-- INSERT INTO "aichannels" VALUES('1','600','T1W','1','17','0','80','0','50','50','500','1','','','110','0','','temp calc','100',2,0); -- temp sensor ait
-- INSERT INTO "aichannels" VALUES('','','T1W','2','0','0','100','0','100','0','','1','','0','150','0','','temp channel 2','',4,0); -- min warntemp sensor near hum sensor
-- INSERT INTO "aichannels" VALUES('','','T1W','3','0','0','100','0','100','0','','1','','0','330','0','','temp channel 3','',4,0); -- max warn

-- INSERT INTO "aichannels" VALUES('1','501','LAW','1','0','0','600','0','100','10','20','2','','00','0','0','','','',3,0); -- ai3, valgusandur analogue npe, 2uA/lx, 10k
INSERT INTO "aichannels" VALUES('1','2','LAW','1','0','0','600','0','100','10','20','2','','00','0','0','','','',3,1); -- ioplaat test

-- npe ai on umbes 3.45 mV kvandile. 4,11V= 1189 kvanti. see vastab 200 lx, ehk jagamine 6:1
INSERT INTO "aichannels" VALUES('','','LAW','2','0','0','100','0','100','0','','1','','0','10','0','','','',3,0); -- ai3, valgusandur threshold on
INSERT INTO "aichannels" VALUES('','','LAW','3','0','0','100','0','100','0','','1','','0','20','0','','','',3,0); -- ai3, valgusadnur threshold off

INSERT INTO "aichannels" VALUES('1','3','BTW','1','17','0','100','0','1000','0','600','3','','','110','0','','battery voltage','',3,1); -- akupinge npe
-- 4 v umbes 1189, vastab aga 12v akupingele, seega korruta adc valjund kymnega. 
INSERT INTO "aichannels" VALUES('','','BTW','2','0','0','100','0','100','0','','1','','0','0','0','','batt temp limit','',3,0); -- just a line on the graph
INSERT INTO "aichannels" VALUES('','','BTW','3','0','0','100','0','100','0','','1','','0','600','0','','batt temp limit','',3,0); -- just a line on the graph

-- INSERT INTO "aichannels" VALUES('1','502','T1W','1','0','143','358','200','1250','20','','3','','','110','0','','','',3,0); -- ai 2, temperatuur npe tc1047a
INSERT INTO "aichannels" VALUES('1','4','T1W','1','0','143','358','200','1250','20','','3','','','110','0','','','',3,1); -- ai 2, temperatuur npe tc1047a ioplaat
INSERT INTO "aichannels" VALUES('','','T1W','2','0','0','1000','0','1000','20','','3','','','-150','0','','','',3,0); -- ai 2, temperatuur
INSERT INTO "aichannels" VALUES('','','T1W','3','0','0','1000','0','1000','20','','3','','','550','0','','','',3,0); -- ai 2, temperatuur


-- INSERT INTO "aichannels" VALUES('1','503','A3V','1','0','0','100','0','100','0','','1','','0','20','0','','','',3,0); -- ai4


CREATE UNIQUE INDEX ai_regmember on 'aichannels'(val_reg,member); -- every service member only once
COMMIT;
