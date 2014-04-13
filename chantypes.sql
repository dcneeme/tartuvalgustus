-- devices attached to the modbusRTU or modbusTCP network accessible to droid controller
BEGIN TRANSACTION; 
CREATE TABLE 'chantypes'(num integer,type integer,name,descr); -- ebables using mixed rtu and tcp inputs
INSERT INTO 'chantypes' VALUES(1,2,'AI','analogue inputs from holding registers');
INSERT INTO 'chantypes' VALUES(2,3,'1W','1wire sensors from holding register');
INSERT INTO 'chantypes' VALUES(3,1,'DI','binary inputs from holding registers'); 
INSERT INTO 'chantypes' VALUES(4,0,'DO','binary outputs from holding registers');
INSERT INTO 'chantypes' VALUES(0,4,'CO','counters from holding registers'); -- not visible as type, use for di subtype only

INSERT INTO 'chantypes' VALUES(5,10,'AI','analogue inputs from input registers'); -- bit kaaluga 8 pysti input reg korral!
INSERT INTO 'chantypes' VALUES(6,11,'1W','1wire sensors from input register');
INSERT INTO 'chantypes' VALUES(7,9,'DI','binary inputs from input registers'); 
INSERT INTO 'chantypes' VALUES(8,8,'DO','binary outputs from input registers');
INSERT INTO 'chantypes' VALUES(9,12,'','counters from input registers'); --

-- INSERT INTO 'chantypes' VALUES(5,0,'DO','counters on binary inputs'); 

CREATE UNIQUE INDEX num_chantypes on 'chantypes'(num); -- chantype ordering numbers must be unique
CREATE UNIQUE INDEX type_chantypes on 'chantypes'(type); -- chantype types must be unique
-- CREATE UNIQUE INDEX name_chantypes on 'chantypes'(name); -- chantype names must be unique ??

COMMIT;
    