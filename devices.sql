-- devices attached to the modbusRTU or modbusTCP network
BEGIN TRANSACTION; 
-- count0..count3 are channel counts for di, do, ai an 1wire. aga counterid???

CREATE TABLE 'devices'(num integer,rtuaddr integer,tcpaddr,mbi integer,name,location,descr,count0 integer,count1 integer,count2 integer,count3 integer); -- ebables using mixed rtu and tcp inputs

-- INSERT INTO 'devices' VALUES(1,1,'127.0.0.1:502',0,'techbase','','linux kontroller',7,4,4,8); -- from server 
INSERT INTO 'devices' VALUES(1,1,'npe_udpio',0,'techbase','','linux kontroller',7,4,4,8); --  using socat
-- INSERT INTO 'devices' VALUES(1,1,'/dev/ttyAPP0',0,'olinuxino','','linux kontroller',7,4,4,8); --  using  uart or rs485

-- INSERT INTO 'devices' VALUES(2,33,'127.0.0.1:1502',1,'counter','','loendimoodul 1',0,0,0,0); -- 
-- INSERT INTO 'devices' VALUES(2,1,'/dev/ttyS3',1,'npe rs485','','tecbase',7,4,4,8); -- tegelikult mba miski muu, aga slave eraldi kirjeldada voib

-- INSERT INTO 'devices' VALUES(3,28,'127.0.0.1:1502',1,'counter','','loendimoodul 2',0,0,0,0);
-- INSERT INTO 'devices' VALUES(4,30,'127.0.0.1:1502',1,'counter','','loendimoodul 3',0,0,0,0);

 
CREATE UNIQUE INDEX num_devices on 'devices'(num); -- device ordering numbers must be unique
CREATE UNIQUE INDEX addr_devices on 'devices'(rtuaddr,tcpaddr); -- device addresses must be unique

COMMIT;
    
