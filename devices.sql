-- devices attached to the modbusRTU or modbusTCP network
BEGIN TRANSACTION; 
-- count0..count3 are channel counts for do, do, ai an 1wire.

CREATE TABLE 'devices'(num integer,rtuaddr integer,tcpaddr,status integer,name,location,descr,count0 integer,count1 integer,count2 integer,count3 integer); -- ebables using mixed rtu and tcp inputs

INSERT INTO 'devices' VALUES(1,1,'127.0.0.1:502',0,'techbase','outdoor','linux kontroller',8,8,8,8); -- the same as for barionet, fixed addresses for system devices
-- INSERT INTO 'devices' VALUES(2,2,'127.0.0.1:10502',0,'counter 3 chan','outdoor','itvilla',0,0,0,0);
-- INSERT INTO 'devices' VALUES(3,3,'127.0.0.1:10502',0,'counter 3chan','outdoor','itvilla',0,0,0,0);
 
CREATE UNIQUE INDEX num_devices on 'devices'(num); -- device ordering numbers must be unique
CREATE UNIQUE INDEX addr_devices on 'devices'(rtuaddr,tcpaddr); -- device addresses must be unique

COMMIT;
    