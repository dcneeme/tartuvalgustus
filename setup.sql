-- new pic, android, srik airmonitor
PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE setup(register,value,ts,desc,comment); -- desc jaab UI kaudu naha,  comment on enda jaoks. ts on muutmise aeg s, MIKS mitte mba, reg value? setup muutuja reg:value...
-- techbase 3g router / linux controller npe9400
 
-- R... values will only be reported during channelconfiguration()

INSERT INTO 'setup' VALUES('S400','http://www.itvilla.ee','','supporthost','for pull, push cmd');
INSERT INTO 'setup' VALUES('S401','upload.php','','requests.post','for push cmd');
INSERT INTO 'setup' VALUES('S402','Basic cHlhcHA6QkVMYXVwb2E=','','authorization header','for push cmd');
INSERT INTO 'setup' VALUES('S403','support/pyapp/$mac','','upload/dnload directory','for pull and push cmd'); --  $mac will be replaced by wlan mac

-- INSERT INTO 'setup' VALUES('SIP','10.0.0.0','','lan/wlan ip address',''); -- used by srik airmonitor display

INSERT INTO 'setup' VALUES('S512','test','','location','');
-- INSERT INTO 'setup' VALUES('S514','195.222.15.51','','syslog server ip address','local broadcast in use if empty or 0.0.0.0 or 255.255.255.255'); -- port is fixed to udp 514
INSERT INTO 'setup' VALUES('S514','','','syslog server ip address','local broadcast in use if empty or 0.0.0.0 or 255.255.255.255'); -- port is fixed to udp 514.

-- ioplaadi setup
-- INSERT INTO 'setup' VALUES('W1.270','48','','ref ja pw luba',''); -- NEW PIC. 
-- INSERT INTO 'setup' VALUES('W1.271','0','','DI XOR 0000','inversioon'); -- NEW PIC. DI inversion bitmap. 0=hi active, 1=low active
-- INSERT INTO 'setup' VALUES('W1.272','0','','powerup mode','do on startup 0x0000'); -- starmani jaoks koik releed off startimisel / EI MOIKA??

-- INSERT INTO 'setup' VALUES('W1.275','6162','','ANA bitmap','2 tk di'); --  uus pic, 2 tk di  00011000 MBS

-- INSERT INTO 'setup' VALUES('W1.276','180','','usbreset powerup protection','60 s'); -- usbreset powerup protection
-- INSERT INTO 'setup' VALUES('W1.276','50000','','usbreset powerup protection','60 s'); -- resetti ei tee. AGA 0 jatab pidevalt resettima!
-- INSERT INTO 'setup' VALUES('W1.277','5','','usbreset pulse','pikkus 5s'); -- usbreset droid , et jouks veidigi laadida pideva resettimisega
-- INSERT INTO 'setup' VALUES('W1.278','50000','','button pulse len','180 s viide'); -- seda resetti pole linuxi korral vaja
-- INSERT INTO 'setup' VALUES('W1.279','5','','button pulse','5 s'); -- buttonpulse 5 s pulse , useless for linux



CREATE UNIQUE INDEX reg_setup on 'setup'(register);
COMMIT;
