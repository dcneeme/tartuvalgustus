-- devices attached to the modbusRTU or modbusTCP network
BEGIN TRANSACTION; 
-- count0..count3 are channel counts for di, do, ai an 1wire. aga counterid???

CREATE TABLE 'devices'(num integer,rtuaddr integer,tcpaddr,mbi integer,name,location,descr,count0 integer,count1 integer,count2 integer,count3 integer); -- ebables using mixed rtu and tcp inputs

INSERT INTO 'devices' VALUES(1,1,'127.0.0.1:502',0,'techbase','','linux kontroller',7,4,4,8); -- on npe
-- INSERT INTO 'devices' VALUES(2,14,'127.0.0.1:1502',1,'counter','','loendimoodul 1',0,0,0,0); -- 
-- INSERT INTO 'devices' VALUES(3,15,'127.0.0.1:1502',1,'counter','','loendimoodul 2',0,0,0,0);
-- INSERT INTO 'devices' VALUES(4,17,'127.0.0.1:1502',1,'counter','','loendimoodul 3',0,0,0,0);
INSERT INTO 'devices' VALUES(2,1,'127.0.0.1:1502',1,'counter','','dc5888',8,8,8,0); -- dc5888 8 loendikanalit adr 1

-- INSERT INTO 'devices' VALUES(1,1,'10.0.0.121:502',0,'techbase','','linux kontroller',7,4,4,8); -- from server 
-- INSERT INTO 'devices' VALUES(2,14,'10.0.0.121:1502',1,'counter','','loendimoodul 1',0,0,0,0); -- 
-- INSERT INTO 'devices' VALUES(3,15,'10.0.0.121:1502',1,'counter','','loendimoodul 2',0,0,0,0);
-- INSERT INTO 'devices' VALUES(4,17,'10.0.0.121:1502',1,'counter','','loendimoodul 3',0,0,0,0);

 
CREATE UNIQUE INDEX num_devices on 'devices'(num); -- device ordering numbers must be unique
CREATE UNIQUE INDEX addr_devices on 'devices'(rtuaddr,tcpaddr); -- device addresses must be unique

COMMIT;
    