-- DC58888-2 tartuvalguistsus . comment asemel dsp_id! srik??

-- CONF BITS
-- # 1 - value 1 = warningu (values can be 0 or 1 only)
-- # 2 - value 1 = critical, 
-- # 4 - value inversion 
-- # 8 - value to status inversion
-- # 16 - immediate notification on value change (whole multivcalue service will be (re)reported)
-- # 32 - this channel is actually a writable coil output, not a bit from the register (takes value 0000 or FF00 as value to be written, function code 05 instead of 06!)
--     when reading coil, the output will be in the lowest bit, so 0 is correct as bit value

-- if 2 lowest bits are 0 then status is not following value and must be set programmatically

-- # block sending. 1 = read, but no notifications to server. 2=do not even read, temporarely register down or something...

PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;

CREATE TABLE dichannels(mba,regadd,bit,val_reg,member,cfg,block,value,status,ts_chg,chg,desc,dsp_id,ts_msg,type integer,mbi integer); -- ts_chg is update toime (happens on change only), ts_msg =notif
-- mis on dsp_id?? type?? kuidagi kaudselt naitab h voi i starmanis. mbi on index. mb[mbi] jaoks
-- value is bit value 0 or 1, to become a member value with or without inversion
-- status values can be 0..3, depending on cfg. member values to service value via OR (bigger value wins)
-- if newvalue is different from value, write will happen. do not enter newvalues for read only register related rows.
-- type is for category flagging, 0=do, 1 = di, 2=ai, 3=ti. use only 0 and 1 in this table

-- controlled outputs, following dochannels bit values. outputs will not change if they are not followed here!
INSERT INTO "dichannels" VALUES('1','1','0','LES','1','0','0','0','0','0','','USER_LED','20','',0,0); -- kollane LED side ok

INSERT INTO "dichannels" VALUES('1','100','0','LRW','1','17','0','0','0','0','','contactor','20','',0,0); -- valgustuse relee olek
INSERT INTO "dichannels" VALUES('','','0','LRW','2','17','0','0','0','0','','lokaalne andur','20','',0,0); -- juhtsignaalid OR
INSERT INTO "dichannels" VALUES('','','0','LRW','3','17','0','0','0','0','','kalender','20','',0,0); -- 
INSERT INTO "dichannels" VALUES('','','0','LRW','4','17','0','0','0','0','','kaugjuhtimine','20','',0,0); -- 
-- siin tuleks midagi valja moelda et kui relee olek ei klapi teiste ORTiga, siis status 2 kuidagi kuhugi!

INSERT INTO "dichannels" VALUES('1','200','0','BRS','1','18','0','0','0','0','','door','20','',0,0); -- uks di1

INSERT INTO "dichannels" VALUES('1','201','0','LSW','1','16','0','0','0','0','','L sens1','20','',0,0); -- lighting sensor bin di2
INSERT INTO "dichannels" VALUES('','','0','LSW','2','16','0','0','1','0','','Lsens2','20','',0,0); -- lighting sensor analogue to bin
INSERT INTO "dichannels" VALUES('','','0','LSW','3','16','0','0','1','0','','Lsens selector','0','',0,0); -- lighting sensor selector, 1=analogue

INSERT INTO "dichannels" VALUES('1','202','0','PWS','1','18','0','0','0','0','','AC power','20','',0,0); -- toide di3

-- jargmised teenused on meelespidamiseks, kas selle faasiga on asi korras
INSERT INTO "dichannels" VALUES('','','','F1W','1','18','0','0','1','0','','feeder1 phase 1','20','',0,0); -- on failure. both value and status calculated based on energy!
INSERT INTO "dichannels" VALUES('','','','F1W','2','18','0','0','1','0','','feeder1 phase 2','20','',0,0); -- on failure. both value and status calculated based on energy!
INSERT INTO "dichannels" VALUES('','','','F1W','3','18','0','0','1','0','','feeder1 phase 3','20','',0,0); -- on failure. both value and status calculated based on energy!

INSERT INTO "dichannels" VALUES('','','','F2W','1','18','0','0','1','0','','feeder2 phase 1','20','',0,0); -- on failure. both value and status calculated based on energy!
INSERT INTO "dichannels" VALUES('','','','F2W','2','18','0','0','1','0','','feeder2 phase 2','20','',0,0); -- on failure. both value and status calculated based on energy!
INSERT INTO "dichannels" VALUES('','','','F2W','3','18','0','0','1','0','','feeder2 phase 3','20','',0,0); -- on failure. both value and status calculated based on energy!

INSERT INTO "dichannels" VALUES('','','','F3W','1','18','0','0','1','0','','feeder3 phase 1','20','',0,0); -- on failure. both value and status calculated based on energy!
INSERT INTO "dichannels" VALUES('','','','F3W','2','18','0','0','1','0','','feeder3 phase 2','20','',0,0); -- on failure. both value and status calculated based on energy!
INSERT INTO "dichannels" VALUES('','','','F3W','3','18','0','0','1','0','','feeder3 phase 3','20','',0,0); -- on failure. both value and status calculated based on energy!

INSERT INTO "dichannels" VALUES('','','','F4W','1','18','0','0','1','0','','feeder4 phase 1','20','',0,0); -- on failure. both value and status calculated based on energy!
INSERT INTO "dichannels" VALUES('','','','F4W','2','18','0','0','1','0','','feeder4 phase 2','20','',0,0); -- on failure. both value and status calculated based on energy!
INSERT INTO "dichannels" VALUES('','','','F4W','3','18','0','0','1','0','','feeder4 phase 3','20','',0,0); -- on failure. both value and status calculated based on energy!

INSERT INTO "dichannels" VALUES('','','','F5W','1','18','0','0','1','0','','feeder5 phase 1','20','',0,0); -- on failure. both value and status calculated based on energy!
INSERT INTO "dichannels" VALUES('','','','F5W','2','18','0','0','1','0','','feeder5 phase 2','20','',0,0); -- on failure. both value and status calculated based on energy!
INSERT INTO "dichannels" VALUES('','','','F5W','3','18','0','0','1','0','','feeder5 phase 3','20','',0,0); -- on failure. both value and status calculated based on energy!

-- INSERT INTO "dichannels" VALUES('','','','F11S','1','18','0','0','1','0','','feeder1 phase 1','20','',0,0); -- off on failure. both value and status calculated based on energy!
-- INSERT INTO "dichannels" VALUES('','','','F12S','1','18','0','0','1','0','','feeder1 phase 2','20','',0,0); -- off on failure. both value and status calculated based on energy!
-- INSERT INTO "dichannels" VALUES('','','','F13S','1','18','0','0','1','0','','feeder1 phase 3','20','',0,0); -- off on failure. both value and status calculated based on energy!

-- INSERT INTO "dichannels" VALUES('','','','F21S','1','18','0','0','1','0','','feeder2 phase 1','20','',0,0); -- off on failure. both value and status calculated based on energy!
-- INSERT INTO "dichannels" VALUES('','','','F22S','1','18','0','0','1','0','','feeder2 phase 2','20','',0,0); -- off on failure. both value and status calculated based on energy!
-- INSERT INTO "dichannels" VALUES('','','','F23S','1','18','0','0','1','0','','feeder2 phase 3','20','',0,0); -- off on failure. both value and status calculated based on energy!

-- INSERT INTO "dichannels" VALUES('','','','F31S','1','18','0','0','1','0','','feeder3 phase 1','20','',0,0); -- off on failure. both value and status calculated based on energy!
-- INSERT INTO "dichannels" VALUES('','','','F32S','1','18','0','0','1','0','','feeder3 phase 2','20','',0,0); -- off on failure. both value and status calculated based on energy!
-- INSERT INTO "dichannels" VALUES('','','','F33S','1','18','0','0','1','0','','feeder3 phase 3','20','',0,0); -- off on failure. both value and status calculated based on energy!

CREATE UNIQUE INDEX di_regmember on 'dichannels'(val_reg,member); -- mbi, mba jne voivad korduda! teenuste liikmed!
-- NB bits and registers are not necessarily unique!

COMMIT;
