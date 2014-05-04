-- needed for channelmonitor_pm.py since 29.01.2014
-- modbus do channels to be controlled by a local application (control.py by default).
-- reporting to monitor happens via adichannels! this table only deals with channel control, without attention to service names or members. 
-- actual channel writes will be done when difference is found between values here and in adichannels table.
-- siin puudub viide teenusele?

PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE aochannels(mba,regadd,bootvalue,value,ts,rule,desc,comment,mbi integer); -- one line per register bit (coil). 15 columns.  NO ts???

-- INSERT INTO "aochannels" VALUES('1','400','','1','','','counter simulating ao','test',0); -- ao kirj test 
-- INSERT INTO "aochannels" VALUES('1','401','','1','','','counter simulating ao','test',0); -- ao kirj test member2

CREATE UNIQUE INDEX do_mbareg on 'aochannels'(mba,regadd); -- you need to put a name to the channel even if you do not plan to report it

-- the rule number column is provided just in case some application needs them. should be uniquely indexed!
-- NB but register addresses and bits can be on different lines, to be members of different services AND to be controlled by different rules!!!
-- virtual channels are also possible - these are defined with dir 2 in adichannels.

COMMIT;
