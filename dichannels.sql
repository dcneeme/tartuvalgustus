-- DC58888-2 tartuvalguistsus . comment asemel dsp_id! srik??

-- CONF BITS
-- # 1 - value 1 = warningu (values can be 0 or 1 only)
-- # 2 - value 1 = critical, 
-- # 4 - value inversion 
-- # 8 - value to status inversion
-- # 16 - immediate notification on value change (whole multivcalue service will be (re)reported)
-- # 32 - this channel is actually a writable coil output, not a bit from the register (takes value 0000 or FF00 as value to be written, function code 05 instead of 06!)
--     when reading coil, the output will be in the lowest bit, so 0 is correct as bit value

-- # block sending. 1 = read, but no notifications to server. 2=do not even read, temporarely register down or something...

PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;

CREATE TABLE dichannels(mba,regadd,bit,val_reg,member,cfg,block,value,status,ts_chg,chg,desc,dsp_id,ts_msg,type integer); -- ts_chg is update toime (happens on change only), ts_msg =notif
-- mis on dsp_id??
-- value is bit value 0 or 1, to become a member value with or without inversion
-- status values can be 0..3, depending on cfg. member values to service value via OR (bigger value wins)
-- if newvalue is different from value, write will happen. do not enter newvalues for read only register related rows.
-- type is for category flagging, 0=do, 1 = di, 2=ai, 3=ti. use only 0 and 1 in this table

-- controlled outputs, following dochannels bit values. outputs will not change if they are not followed here!
-- INSERT INTO "dichannels" VALUES('1','0','0','R1S','1','17','0','0','1','0','','lighting state','20','',0); -- valgustuse relee olek
INSERT INTO "dichannels" VALUES('1','100','0','R1S','1','17','0','0','1','0','','lighting state','20','',0); -- valgustuse relee olek
INSERT INTO "dichannels" VALUES('1','206','0','BRS','1','17','0','0','1','0','','door','20','',0); -- uks di7

-- INSERT INTO "dichannels" VALUES('','','8','MOS','1','17','0','0','1','0','','mon state','21','',0); -- mon olek
-- INSERT INTO "dichannels" VALUES('','','8','USS','1','17','0','0','1','0','','usb state','22','',0); -- usb olek
-- INSERT INTO "dichannels" VALUES('','','8','WLS','1','17','0','0','1','0','','wlan state','23','',0); -- wlan olek

CREATE UNIQUE INDEX di_regmember on 'dichannels'(val_reg,member);
-- NB bits and registers are not necessarily unique!

COMMIT;
