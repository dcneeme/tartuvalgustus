-- DC6888 tartu valgustus. ts ts_chg asemel!

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
-- voiks loobuda type kasutamisest! siin voetud regtype kasutusele dsp_id asemele.

CREATE TABLE dichannels(mba,regadd,bit,val_reg,member,cfg,block,value,status,ts,chg,desc,regtype,ts_msg,type integer,mbi integer); -- ts_chg is update toime (happens on change only), ts_msg =notif
-- mis on dsp_id?? type?? kuidagi kaudselt naitab h voi i starmanis. mbi on index. mb[mbi] jaoks
-- value is bit value 0 or 1, to become a member value with or without inversion
-- status values can be 0..3, depending on cfg. member values to service value via OR (bigger value wins)
-- if newvalue is different from value, write will happen. do not enter newvalues for read only register related rows.
-- type is for category flagging, 0=do, 1 = di, 2=ai, 3=ti. use only 0 and 1 in this table

-- controlled outputs, following dochannels bit values. outputs will not change if they are not followed here!
-- INSERT INTO "dichannels" VALUES('1','1','0','LES','1','0','0','0','0','0','','USER_LED','h','',0,0); -- kollane LED side ok

INSERT INTO "dichannels" VALUES('1','0','8','LRW','1','17','0','0','0','0','','contactor do1','h','',0,0); -- valgustuse relee olek npe juhtimisel
INSERT INTO "dichannels" VALUES('','','0','LRW','2','17','0','0','0','0','','lokaalne andur','s','',0,0); -- juhtsignaalid bin OR anal
INSERT INTO "dichannels" VALUES('','','0','LRW','3','17','0','0','0','0','','kalender','s','',0,0); -- 
INSERT INTO "dichannels" VALUES('','','0','LRW','4','17','0','0','0','0','','kaugjuhtimine','s!','',0,0); -- kui siin 1 kaivitab kontaktori nagu ka lok voi kal
-- siin tuleks midagi valja moelda et kui relee olek ei klapi teiste ORiga, siis status 2 kuidagi kuhugi!

INSERT INTO "dichannels" VALUES('','','0','VPW','1','17','0','0','0','0','','VPN olek (1 on, 0 off, 2 jama)','s','',0,0); -- vpn status siia
INSERT INTO "dichannels" VALUES('','','0','VPW','2','17','0','0','0','0','','lokaalne vpn vajadus','s','',0,0); -- lokaalne loogika luba
INSERT INTO "dichannels" VALUES('','','0','VPW','3','17','0','0','0','0','','kaugjuhtimine','s!','',0,0); -- man kaugelt luba

INSERT INTO "dichannels" VALUES('1','1','5','BRS','1','18','0','0','0','0','','door','h','',0,0); -- uks ai6 as DI

INSERT INTO "dichannels" VALUES('1','1','7','LSW','1','17','0','0','0','0','','L sens1','h','',0,0); -- lighting sensor bin ai8 in DI mode 
INSERT INTO "dichannels" VALUES('','','0','LSW','2','17','0','0','1','0','','Lsens2','s','',0,0); -- lighting sensor analogue as binary
INSERT INTO "dichannels" VALUES('','','0','LSW','3','16','0','0','1','0','','Lsens selector','s!','',0,0); -- lighting sensor selector, 1=analogue

INSERT INTO "dichannels" VALUES('1','202','0','PWS','1','18','0','0','0','0','','AC power','h','',0,0); -- toide di3 npe
-- INSERT INTO "dichannels" VALUES('1','1','6','PWS','1','18','0','0','0','0','','AC power','h','',0,0); -- toide ai7 as DI

-- jargmised teenused on meelespidamiseks, kas selle faasiga on asi korras
INSERT INTO "dichannels" VALUES('','','','F1W','1','18','0','0','1','0','','feeder1 phase 1','s','',0,0); -- on failure. both value and status calculated based on energy!
INSERT INTO "dichannels" VALUES('','','','F1W','2','18','0','0','1','0','','feeder1 phase 2','s','',0,0); -- on failure. both value and status calculated based on energy!
INSERT INTO "dichannels" VALUES('','','','F1W','3','18','0','0','1','0','','feeder1 phase 3','s','',0,0); -- on failure. both value and status calculated based on energy!

INSERT INTO "dichannels" VALUES('','','','F2W','1','18','0','0','1','0','','feeder2 phase 1','s','',0,0); -- on failure. both value and status calculated based on energy!
INSERT INTO "dichannels" VALUES('','','','F2W','2','18','0','0','1','0','','feeder2 phase 2','s','',0,0); -- on failure. both value and status calculated based on energy!
INSERT INTO "dichannels" VALUES('','','','F2W','3','18','0','0','1','0','','feeder2 phase 3','s','',0,0); -- on failure. both value and status calculated based on energy!

INSERT INTO "dichannels" VALUES('','','','F3W','1','18','0','0','1','0','','feeder3 phase 1','s','',0,0); -- on failure. both value and status calculated based on energy!
INSERT INTO "dichannels" VALUES('','','','F3W','2','18','0','0','1','0','','feeder3 phase 2','s','',0,0); -- on failure. both value and status calculated based on energy!
INSERT INTO "dichannels" VALUES('','','','F3W','3','18','0','0','1','0','','feeder3 phase 3','s','',0,0); -- on failure. both value and status calculated based on energy!

-- INSERT INTO "dichannels" VALUES('','','','F4W','1','18','0','0','1','0','','feeder4 phase 1','s','',0,0); -- on failure. both value and status calculated based on energy!
-- INSERT INTO "dichannels" VALUES('','','','F4W','2','18','0','0','1','0','','feeder4 phase 2','s','',0,0); -- on failure. both value and status calculated based on energy!
-- INSERT INTO "dichannels" VALUES('','','','F4W','3','18','0','0','1','0','','feeder4 phase 3','s','',0,0); -- on failure. both value and status calculated based on energy!

-- INSERT INTO "dichannels" VALUES('','','','F5W','1','18','0','0','1','0','','feeder5 phase 1','s','',0,0); -- on failure. both value and status calculated based on energy!
-- INSERT INTO "dichannels" VALUES('','','','F5W','2','18','0','0','1','0','','feeder5 phase 2','s','',0,0); -- on failure. both value and status calculated based on energy!
-- INSERT INTO "dichannels" VALUES('','','','F5W','3','18','0','0','1','0','','feeder5 phase 3','s','',0,0); -- on failure. both value and status calculated based on energy!

CREATE UNIQUE INDEX di_regmember on 'dichannels'(val_reg,member); -- mbi, mba jne voivad korduda! teenuste liikmed!
-- NB bits and registers are not necessarily unique!

COMMIT;
