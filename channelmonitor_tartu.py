# This Python file uses the following encoding: utf-8 
# see http://www.python.org/dev/peps/pep-0263/

# this script is 1) constantly updating the channel tables according to the modbus register content; 2) sending messages to the central server;
# 3) listening commands and new setup values from the central server; 4) comparing the dochannel values with actual do values in dichannels table and writes to eliminate  the diff.
# currently supported commands: REBOOT, VARLIST, pull, sqlread, run

APVER='channelmonitor_tartu.py 23.03.2014'  # linux and python3 -compatible. # OBSOLETE ! use droidcontroller/channelmonitor_pm.py now!

# 23.06.2013 based on channelmonitor3.py
# 25.06.2013 added push cmd, any (mostly sql or log) file from d4c directory to be sent into pyapp/mac on itvilla.ee, this SHOULD BE controlled by setup.sql - NOT YET!
# 28.06.2013 checking modbusproxy before slave registers and tcperr increase. stop and recreate db if proxy running but slave inaccessible.
# 02.07.2013 first check reg 255:0 1
# 08.07.2013 added some register reads from modbusproxy, incl uuid and simserial. no battery data reading yet. chk proxy version first?
# 09.07.2013 syslog broadcast
# 10.07.2013 check age before reporting to mon, stale data not to be sent!
# 16.07.2013 added mbproxy watchdog init 120s to reboot in case of tcp comm loss
# 20.07.2013 fixed missing di renotifications (failed filtering attempt). added some voice messages (on reboot and channel problems). release candidate.
   #  main loop speak is ok, but errors and ending mesages later do not function for some reason!
   #    20.07.2013 broadcast based on wlan ip, works also with hotspot (but that goes off with reboot). ssid dp, passwd hvvpumpla
# 22.07.2013 toggle wlan (but not hotspot). subprocess has problems on android!!! use droid.toggle() instead
# 23.07.2013 airplane mode off
# 25.07.2013 fixing gsm signal level to -120 if <-114
# 26.07.2013 eelmise fix.. -120 gBm
# 18.08.2013 counters fix, only last svc was sent to buff2server
# 30.08.2013 finished di and ai age check, svc not to be reported if stale
# 09.09.2013 fixed a few minor problems in dichannel_bits(). restored also PVW and T1W reporting, lost for a while for unknown reason. NO logging from now on!!!
# 08.10.2013 log msg read_aichannels added for debugging
# 08.11.2013 trying to get logcat dump in case of usb connectivity loss (on exit from running state)
# 23.11.2013 logcat dump works using call. do not attempt to recreate sqlite tables any more if USB state si not 0 (OK).
# 25.11.2013 removed path from logcat dump filename. FULLREBOOT su - s reboot in addition to 666 DEAD
# 25.11.2013 removed proxy 666 dead usage, kept subexec su - c reboot (impossible  to give the first grant to python if proxy reboot is used as well)
# 08.12.2013 started modifications for olinuxino and python3.
# 09.12.2013 udp comm fixed, .encode for python3 str was needed. still working with android too.
# 12.12.2013 added cmd:logcat,0  to get gzipped logcat report any time
# 16.12.2013 do 7 and do8 as commLED and gsm_pwr,  use dochannels for bitwise output control (no need for set coil then). added function setbit_dochannels()
# 18.12.2013  carrying on with above... dictionaries in write_dochannels()
# 19.12.2013  carrying on with above... outputs functional for commLED and gsmPWR
# 20.12.2013 have put sql tables into memory. problem with setup chg & dump!
# 21.12.2013 setup dump ok. outputs ok. use usbpower delay 100 for linux. make sure the files setnetwork.sh, network.conf, getnetwork.sh are in d4c directory for archlinux.
# 22.12.2013 syslog server address controlled by S514 now in setup.sql.
# 23.12.2013 android and linux behavior differ related to di/do sync!
# 24.12.2013 fixed output flapping behavior after gsmbreak, add bit changes one after another. use previous output not the powerup value. fixed channelconfig().
# 25.12.2013 stopped log pushing on usb disconnect. removed chmod + x from within pull(). stopped recreating databases on modbus failures (tables in memory since 20.12).
# 26.12.2013 replaces traceback() with +str(sys.exc_info()[1]) to be printed and syslogged. counters restored based on counters table, taking svc member, x2,y2 into account.
# 26.12.2013 the same version backupped as rescue executable. changed AVS to 2 there!                            
# 28.12.2013 kick flight mode temporarely on at 20 and 40 s with failing udp send (it may help to restore connectivity, has done so in manual tests! also for wlan.)
# 29.12.2013 AVS:2 fix to AVS:0
# 01.01.2014 added BTW, BCW, BVW services via aichannels (battTemperature, BattCharge, BattVoltage)
# 04.01.2014 run,dbREcreate not needed any more, disabled. cmd:RMLOG added.
# 06.01.2014 cmd:free,path  added, returns free space for d4c in ERV response
# 07.01.2013 a few small things
# 08.01.2014 moved to droid/droidcontroller/channelmonitor_pm.py, using modules in subdirectory droid/droidcontroller/droidcontroller. JAMA?
# 15.01.2014 lisatud syslog raw ai ytlemiseks print(msg jarele)  
# 27.01.2014 muudetud fullreboot ja gsmpwr timeout aegu, linuxi vajadusi arvestades. fulreboot 900 s, gsmpwr 300. 5v reset ara parem kasuta, max viide vaid 255 s! cmd:GSMBREAK added.
# 29.01.2014 fullreboot if proxy lost. no stop on android if no proxy present to restart. fullreboot only on full battery, to avoid locked xperia screen on boot... 
# 29.01.2014 analogue registers were writable via setup, now also via aochannels, that can be updated via svc in aichannels. V1W for example. for starman. use aochannels.sql!
# 03.02.2014 cmd:REBOOT ebaonnestub nyyd, kui proxystate ei ole 0! fullreboot on ikka voimalik. pandud hvv kp6. aochannels.sql vajalik!!!
# 04.02.2014 tegelikult 03.02 sony vigane mac ..112233 likvideeritud, voib esineda kui wlan enne reboot off! sellest oli abi hvv kp6 elustamisel
# ### 05.02.2014 change the getsetnetwork part!! vt starmani lahendust!!!
# 09.02.2014 statuse parandus ai signaalide jaoks
# 07.03.2014 techbase npe support. ttyS3 = rs485
#++++++++++
# 23.03.2014 tartu valgustuse versioon. getset_network asemele get_network()
# 24.03.2014 sqlite probleem techbase peal. katsetada ramdiski. ei aidanud. samas onm mingi rs485 jama ka...
# 30.03.2014 traceback maha. miks sqlite3 transaction error? ainult npe peal, kus vanem sqlite3 versioon (ehk oli see aeg, kus oli vaja pysaqlite?). deferred transaction ka ei aita.
#   proovida olinuxino sqlitet? kah ju arm..
  
# PROBLEMS and TODO
# ### 05.02.2014 change the getsetnetwork part!! vt starmani lahendust!!!

# inserting to sent2server has problems. skipping it for now, no local log therefore.
# add UCV, UCS (gsmUptime)
# free space monitoring should be added.


#modbusproxy registers / Only one register can be read  or write at time (registers are sometimes long)
#000-099 ModbusProxy information
        #0:x - ModbuProxy long version string <app version>.<commit seq>-<branch>-<short sha1>
#100-199 ModbusProxy configuration
        #100:x - SL4A USB connected autostart script name
        #101:x - SL4A ModbusProxy service autostart script name
#200-299 ModbusProxy log and counters
        #200:1 - USB status
#300-399 Phone information
        #300:8 - UUID
        #301:x - device ID
        #302:x - SIM serial number
        #303:x - line1number (phone number if stored on SIM)
        #304:1 - cell RSSI - returns 0 on sony xperia!!!
        #305:1 - WiFi RSSI     / returns ffc0 if very close to ap
        #310:3 - wlan0 MAC address     / ok, ex
        #313:2 - wlan0 IPv4 address



# ### procedures ######################


def read_long(mba, reg, len): # read multiple registers to form one resulting value. no good for barionet counters (with wrong order)!
    result = client.read_holding_registers(address=reg, count=len, unit=mba)
    if (isinstance(result, ReadHoldingRegistersResponse)):
        t = 0
        for i in range(0, len, 1):
            t = (t << 16) + result.registers[i]
        return t
    else:
        return -1 # assuming no negative result normally



def subexec(exec_cmd,submode): # submode 0 returns exit code, submode 1 returns output of a subprocess, like a shell script or command
    # seems to work on linux, but NOT on android with python 2.6!!!
    #for wifi, try this:
    #droid.toggleWifiState(True) # On
    #print droid.checkWifiState().result
    #droid.toggleWifiState(False) # Off
    #proc=subprocess.Popen([exec_cmd], shell=True, stdout=DEVNULL, stderr=DEVNULL)
    if submode == 0: # return exit status, 0 or more
        #proc=subprocess.Popen([exec_cmd], shell=True, stdout=DEVNULL, stderr=DEVNULL)
        #proc=subprocess.Popen(exec_cmd, shell=True, stdout=DEVNULL, stderr=DEVNULL)
        returncode=subprocess.call(exec_cmd) # ootab kuni lopetab
        #proc.wait()
        return returncode  # return just the subprocess exit code
    else: # return everything from sdout
        proc=subprocess.Popen([exec_cmd], shell=True, stdout=subprocess.PIPE)
        result = proc.communicate()[0]
        #proc.wait()
        return result


def sqlread(table): # drops table and reads from file table.sql that must exist
    global conn1tables, conn3tables,conn4tables
    Cmd='drop table if exists '+table
    filename=table+'.sql' # the file to read from
    try:
        sql = open(filename).read()
    except:
        msg='FAILURE in sqlread: '+str(sys.exc_info()[1]) # aochannels ei pruugi olemas olla alati!
        print(msg)
        syslog(msg)
        #traceback.print_exc()
        time.sleep(1)
        return 1

    try:
        if table in conn1tables:
            conn1.execute(Cmd) # drop the table if it exists
            conn1.executescript(sql) # read table into database
            conn1.commit()
        if table in conn3tables:
            conn3.execute(Cmd)
            conn3.executescript(sql) # read table into database
            conn3.commit()
        if table in conn4tables:
            conn4.execute(Cmd)
            conn4.executescript(sql) # read table into database
            conn4.commit()
        msg='sqlread: successfully (dropped and) read the table '+table
        print(msg)
        syslog(msg)
        time.sleep(0.5)
        return 0
    except:
        msg='sqlread: '+str(sys.exc_info()[1])
        print(msg)
        syslog(msg)
        #traceback.print_exc()
        time.sleep(1)
        return 1



def read_batt(): # read modbus proxy registers regarding battery. no parameters. output should go into sql tables to get reported!
    i=0
    global BattVoltage, BattTemperature, BattStatus, BattPlugged, BattHealth, BattCharge
    try:
        result = client.read_holding_registers(address=350, count=7, unit=255) # battery data
        BattVoltage=result.registers[6] # mV
        BattTemperature=result.registers[5] # ddegC
        BattStatus=result.registers[4] # 2 charging, 3 disch, 5 full, 4 not ch, 1 unknown
        BattPlugged=result.registers[3] # 2 = plugged USB.
        BattHealth=result.registers[2] # 2 good, 4 dead, 3 heat, 7 cold, 1 unknown, 6 unknown failure
        BattCharge=result.registers[1] # 0..100
        msg='read_batt: Voltage '+str(BattVoltage)+', Temperature '+str(BattTemperature)+', Status '+str(BattStatus)+', Health '+str(BattHealth)+', Plugged '+str(BattPlugged)+', Charge '+str(BattCharge)
    except:
        msg='read_batt: FAILURE - not supported by this modbusproxy version?'
        return 1
    syslog(msg)


def read_proxy(what): # read modbus proxy registers, wlan mac most importantly. start only if tcp conn already exists! parameter 'all' or anything
    global mac, USBstate, USBuptime, PhoneUptime, ProxyUptime, WLANip, ProxyVersion, UUID, SIMserial, stop, logaddr, loghost, logport, GSMlevel, WLANlevel, OSTYPE, ts_proxygot
    i=0
    tmparray=[]
    WLANoldip=WLANip
    WLANip=''
    SIMserial=''
    USBnewState=0

    try:
        result = client.read_holding_registers(address=313, count=2, unit=255) # wlan ip
        for i in range(2):
            if WLANip != '': # WLANip != '':
                WLANip=WLANip+'.'
                
            #if i == 1: # second half
                #loghost=WLANip+str(result.registers[i]/256)+'.255'
            WLANip = WLANip+str(result.registers[i]/256)+'.'+str(result.registers[i]&255)

        if WLANoldip != WLANip:
            msg='read_proxy: WLAN ip changed from '+WLANoldip+' to '+WLANip+', broadcast to '+loghost
            print(msg)
            syslog(msg) # debug
            #if OSTYPE == 'android':
                #droid.ttsSpeak('wireless ip has changed, broadcast to '+loghost) # broadcast / syslog controlled by S514
            #logaddr=(loghost,logport) # global variable change

        result = client.read_holding_registers(address=200, count=1, unit=255) # USB state. 1 = running, disconnected
        USBnewState=result.registers[0]
        if USBnewState != USBstate and USBstate == 1: # was running but not any more, save logcat dump
            msg="lost USB running state!"
        #    msg="logcat dump to be saved due to USB not running any more" # peaks kohe teavitama!
            print(msg)
            syslog(msg)
            time.sleep(1)
        #    resultcode=logcat_dumpsend() # trying to dump and push logcat content on usb disconnect
        #    if resultcode == 0:
        #        print('logcat dump successfully sent')
                
        USBstate=USBnewState

        msg='read_proxy: ProxyState '+str(ProxyState)+', USBstate '+str(USBstate) # 0 and 1 ok
        print(msg) # debug
        syslog(msg) # debug
        #syslog(msg) # debug

        if ProxyState == 0: # proxy ok
            if USBstate == 1:
                USBuptime=int(read_long(255,205,4)/1000) # USBuptime in s, result - 1 if error
            else:
                USBuptime=0
        else: # no proxy
            msg='proxy not responsive for '+str(ts - ts_proxygot)+' seconds'
            print(msg)
            syslog(msg)
            USBuptime=0

        PhoneUptime=int(read_long(255,360,4)/1000)
        ProxyUptime=int(read_long(255,201,4)/1000)
        GSMlevel=client.read_holding_registers(address=304, count=1, unit=255).registers[0]*2-113 # 0..31, 99? converted to dBm read one at the time! -115=flight_mode!
        WLANlevel=client.read_holding_registers(address=305, count=1, unit=255).registers[0]-65536  # converted to negative number. read one at the time!
        if WLANlevel > 0 or WLANlevel < -114:  # -115 means flight mode. can be also -200 or -9999.
            WLANlevel=-120 # means off to me.
            #msg='fixing WLANlevel to '+str(WLANlevel)
            #print(msg)
            #syslog(msg)
        
        ts_proxygot=ts # last successful proxy reading, means proxy is up
        #msg='ts_proxygot '+str(int(ts_proxygot)) # debug
        #print(msg) # debug
        #syslog(msg) # debug
        msg='phoneup '+str(PhoneUptime)+', proxyup '+str(ProxyUptime)+', gsm '+str(GSMlevel)+', wlan '+str(WLANlevel) # levels dBm
        #syslog(msg) # debug
        print(msg)

        if what != 'all':  # enough what we've read above for regular reading #########################
            return 0

        ProxyVersion = read_hexstring(255,0,11) # 44 characters or emtpy

        UUID = read_hexstring(255,300,8) # 32 char hex string
        msg='proxyversion '+ProxyVersion+', uuid '+UUID
        syslog(msg) # debug

        mac = read_hexstring(255,310,3).upper() # mas as 12 character hex string, initial try
        msg='read_proxy: mac='+mac
        syslog(msg) # debug
        if OSTYPE == 'android':
            while len(mac) != 12 or mac == '000000000000' or '112233' in mac: # invalid mac ...112233 in sony xperia after reboot when wlan was off before reboot
                msg='invalid mac, switching wireless on and off'
                print(msg)
                syslog(msg)
                droid.ttsSpeak(msg)
                droid.toggleWifiState(True)
                time.sleep(10)
                if droid.checkWifiState().result == True:
                    droid.ttsSpeak('wireless activated')
                    mac = read_hexstring(255,310,3).upper() # mas as 12 character hex string
                    droid.toggleWifiState(False)
                else:
                    droid.ttsSpeak('wireless did not activate for some reason')
                time.sleep(8)

            msg='got the correct mac '+mac
            print(msg)
            syslog(msg)
            droid.ttsSpeak('got the mac address ending with '+mac[-4:])

        result = client.read_holding_registers(address=302, count=10, unit=255) # sim serial
        if result.registers[0] != '0':
            #syslog('simdec: '+repr(result.registers))
            for i in range(10):
                if (result.registers[i]/256) == 0:
                    SIMserial=SIMserial+'F'
                else:
                    SIMserial=SIMserial+chr(result.registers[i]/256)
                if (result.registers[i]&255) == 0:
                    SIMserial=SIMserial+'F'
                else:
                    SIMserial=SIMserial+chr(result.registers[i]&255)
            syslog('simserial: '+SIMserial)
        else:
            syslog('simserial read FAILED: '+repr(result.registers))
        # add here to add more to read for 'all'


        
        return 0
    except: 
        msg='proxy read failing for '+str(int(ts - ts_proxygot))+' seconds'  # : '+str(sys.exc_info()[1])
        print(msg)
        syslog(msg)
        return 1


def read_hexstring(mba,regaddr,regcount): # read from modbus register as hex string
    i=0
    output=''
    try:
        result = client.read_holding_registers(address=regaddr, count=regcount, unit=mba) # wlan mac
        for i in range(regcount):
            output = output + format("%04x" % result.registers[i])
    except: # Exception,err:
        msg='error reading modbus registers: '+str(sys.exc_info()[1])
        #traceback.print_exc()
        syslog(msg)
        print(msg)

    return output # hex string with lenghth 4 x count or empty



def channelconfig(): # register settings read, write to slaves if needed, report to mon server
    # on android assuming the proxy connection is ok, tested before (ProxyState == 0)
    global tcperr,inumm,ts,sendstring #,MBsta # not yet used, add handling
    mba=0
    register=''
    value=0
    regok=0
    mba_array=[]

    try:
        Cmd4="BEGIN IMMEDIATE TRANSACTION" # conn4 for setup
        conn4.execute(Cmd4)
        Cmd4="select register,value from setup"
        cursor4.execute(Cmd4) # read setup variables into cursor
        
        for row in cursor4:
            regok=0
            msg='setup record '+str(repr(row))
            print(msg)
            syslog(msg)
            register=row[0] # contains W<mba>.<regadd> or R<mba>.<regadd>
            # do not read value here, can be string as well
                
            if '.' in register: # dot is needed
                try:
                    mba=int(register[1:].split('.')[0])
                    regadd=int(register[1:].split('.')[1])
                    msg='going to read and set (if needed) register '+register+' at mba '+str(mba)+', regadd '+str(regadd)+' to '+format("%04x" % value)
                    regok=1
                except:
                    msg='invalid mba and/or register data for '+register
                print(msg)
                syslog(msg)

                if regok == 1:
                    try:
                        if row[1] != '':
                            value=int(float(row[1])) # setup value from setup table
                        else:
                            msg='empty value for register '+register+', assuming 0!'
                            value=0
                            print(msg)
                            syslog(msg)
                        
                        result = client.read_holding_registers(address=regadd, count=1, unit=mba) # actual value currently in slave modbus register
                        tcpdata = result.registers[0]
                        if register[0] == 'W': # writable
                            if tcpdata == value: # the actual value verified
                                msg=msg+' - setup register value already OK, '+str(value)
                                print(msg)
                                syslog(msg)
                                #prepare data for the monitoring server
                                #sendstring=sendstring+"W"+str(mba)+"."+str(regadd)+":"+str(tcpdata)+"\n"  # register content reported as decimal
                            else:
                                msg='CHANGING config in mba '+str(mba)+' regadd '+str(regadd)+' from '+format("%04x" % tcpdata)+' to '+format("%04x" % value)
                                time.sleep(0.1) # successive sending without delay may cause failures!
                                try:
                                    client.write_register(address=regadd, value=value, unit=mba) # only one regiter to write here
                                    respcode=0 #write_register(mba,regadd,value,0) # write_register sets MBsta[] as well
                                    #prepare data for the monitoring server = NOT HERE!
                                    #sendstring=sendstring+"W"+str(mba)+"."+str(regadd)+":"+str(value)+"\n"  # data just written, not verified! 
                                except:
                                    msg='error writing modbus register: '+str(sys.exc_info()[1])
                                    syslog(msg)
                                    print(msg)
                                    respcode=1
                                    #traceback.print_exc()
                                if respcode != 0:
                                    msg=msg+' - write_register() PROBLEM!'
                                    time.sleep(1)
                                    #return 1 # continue with others!
                            print(msg)
                            syslog(msg)
                            #sys.stdout.flush()

                        else: # readable only
                            msg='updating setup with read-only configuration data from mba.reg '+str(mba)+'.'+str(regadd)
                            print(msg)
                            syslog(msg)
                            Cmd4="update setup set value='"+str(tcpdata)+"' where register='"+register+"'"
                            conn4.execute(Cmd4)
                            #send the actual data to the monitoring server
                            #sendstring=sendstring+"R"+str(mba)+"."+str(regadd)+":"+str(tcpdata)+"\n"  # register content reported as decimal

                    except: 
                        msg=' - could not read the modbus register mba.reg '+str(mba)+'.'+str(regadd)+' '+str(sys.exc_info()[1])
                        print(msg)
                        syslog(msg)
                        #traceback.print_exc()
                        #syslog('err: '+repr(err))
                        time.sleep(1)
                        return 1

                    time.sleep(0.1) # delay between registers

        conn4.commit()            
        #udpsend(inumm,int(ts)) # sending to the monitoring server - not here, use report_setup() for this!
    except:
        msg='channelconfig FAILURE, '+str(sys.exc_info()[1])
        print(msg)
        syslog(msg)
        #traceback.print_exc()
        #syslog('err: '+repr(err))
    sys.stdout.flush()
    time.sleep(0.5)
    return 0




def write_aochannels(): # synchronizes AI registers with data in aochannels table
    #print('write_aochannels start') # debug
    # and use write_register() write modbus registers  to get the desired result (all ao channels must be also defined in aichannels table!)
    global inumm,ts,ts_inumm,mac,tcpdata,tcperr #,MBsta
    respcode=0
    mba=0 # lokaalne siin
    omba=0 # previous value
    val_reg=''
    desc=''
    value=0
    word=0 # 16 bit register value
    #comment=''
    mcount=0
    #Cmd1=''
    #Cmd3=''
    #Cmd4=''
    ts_created=ts # selle loeme teenuse ajamargiks

    try:
        Cmd3="BEGIN IMMEDIATE TRANSACTION" # conn3, kogu selle teenustegrupiga (aichannels) tegelemine on transaction - read only, no need...
        conn3.execute(Cmd3)

        # 0      1   2    3        4      5    6      7
        #mba,regadd,bit,bootvalue,value,rule,desc,comment

        Cmd3="select aochannels.mba,aochannels.regadd,aochannels.value from aochannels left join aichannels on aochannels.mba = aichannels.mba AND aochannels.regadd = aichannels.regadd where aochannels.value != aichannels.value" # 
        # the command above retrieves mba, regadd and value where values do not match in aichannels and aochannels 
        #print "Cmd3=",Cmd3
        cursor3.execute(Cmd3)

        for row in cursor3: # got mba, regadd and value for coils that need to be updated / written
            regadd=0
            mba=0

            if row[0] != '':
                mba=int(row[0]) # must be a number
            if row[1] != '':
                regadd=int(row[1]) # must be a number
            if row[1] != '':
                value=int(row[2]) # 0 or 1 to be written
            msg='write_aochannels: going to write value '+str(value)+' to register mba.regadd '+str(mba)+'.'+str(regadd) 
            print(msg)
            syslog(msg)

            try:
                client.write_register(address=regadd, value=value, unit=mba)
                respcode=0 
            except:
                respcode=1

            MBsta[mba]=respcode
            if respcode == 0: # success
                MBerr[mba]=0

            else:
                MBerr[mba]=MBerr[mba]+1 # increase error count
                if respcode ==2:
                    print('problem with coil',mba,regadd,value,'writing!')

        conn3.commit()  # dicannel-bits transaction end

    except:
        print('problem with aochannel - aichannel sync! '+str(sys.exc_info()[1]))
        #traceback.print_exc()
        syslog('problem with aochannel - aichannel sync!')
        sys.stdout.flush()

    #conn3.commit() # transaction end, perhaps not even needed - 2 reads, no writes...
    return 0
    # write_aochannels() end. FRESHENED DICHANNELS TABLE VALUES AND CGH BITS (0 TO SEND, 1 TO PROCESS)

    

def write_dochannels(): # synchronizes DO bits (output channels) with data in dochannels table, using actual values checking via output records in dichannels table
    #print('write_dochannels start') # debug
    # find out which do channels need to be changed based on dichannels and dochannels value differencies
    # and use write_register() write modbus registers (not coils) to get the desired result (all do channels must be also defined as di channels in dichannels table!)
    global inumm,ts,ts_inumm,mac,tcpdata,tcperr #,MBsta
    respcode=0
    mba=0 # lokaalne siin
    omba=0 # previous value
    val_reg=''
    desc=''
    value=0
    word=0 # 16 bit register value
    #comment=''
    mcount=0
    #Cmd1=''
    #Cmd3=''
    #Cmd4=''
    ts_created=ts # selle loeme teenuse ajamargiks

    try:
        Cmd3="BEGIN IMMEDIATE TRANSACTION" # conn3, kogu selle teenustegrupiga (aichannels) tegelemine on transaction - read only, no need...
        conn3.execute(Cmd3)

        # 0      1   2    3        4      5    6      7
        #mba,regadd,bit,bootvalue,value,rule,desc,comment

        # write coils first
        Cmd3="select dochannels.mba,dochannels.regadd,dochannels.value from dochannels left join dichannels on dochannels.mba = dichannels.mba AND dochannels.regadd = dichannels.regadd AND dochannels.bit = dichannels.bit where dochannels.value != dichannels.value and (dichannels.cfg & 32) group by dochannels.mba,dochannels.regadd " # coils only here, 100..115
        # the command above retrieves mba, regadd and value for coils where bit values do not match in dichannels and dochannels 
        #print "Cmd3=",Cmd3
        cursor3.execute(Cmd3)

        for row in cursor3: # got mba, regadd and value for coils that need to be updated / written
            regadd=0
            mba=0

            if row[0] != '':
                mba=int(row[0]) # must be a number
            if row[1] != '':
                regadd=int(row[1]) # must be a number
            if row[1] != '':
                value=int(row[2]) # 0 or 1 to be written
            print('going to write as a coil register mba,regadd,value',mba,regadd,value) # temporary

            try:
                client.write_register(address=reg, value=value, unit=mba)
                respcode=0 # write_register(mba,regadd,value,1+2*tcpmode)
            except:
                respcode=1

            MBsta[mba]=respcode
            if respcode == 0: # success
                MBerr[mba]=0

            else:
                MBerr[mba]=MBerr[mba]+1 # increase error count
                if respcode ==2:
                    print('problem with coil',mba,regadd,value,'writing!')

        #conn3.commit()  # dicannel-bits transaction end

    except:
        print('problem with dochannel grp select!')
        sys.stdout.flush()

    # end coil writing


    # write do register(s?) now. take values from dichannels and replace the bits found in dochannels. missing bits are zeroes.
    # take powerup values and replace the bit values in dochannels to get the new do word
    # only write the new word if the bits in dochannel are not equal to the corresponding bits in dichannels
    Cmd3="select dochannels.mba,dochannels.regadd,dochannels.bit,dochannels.value,dichannels.value from dochannels left join dichannels on dochannels.mba = dichannels.mba AND dochannels.regadd = dichannels.regadd AND dochannels.bit = dichannels.bit where round(dochannels.value) != round(dichannels.value) and not(dichannels.cfg & 32) group by dochannels.mba,dochannels.regadd,dochannels.bit"  # find changes only
    # without round() 1 != 1.0 !
    #Cmd3="select dochannels.mba,dochannels.regadd,dochannels.bit,dochannels.value,dichannels.value from dochannels left join dichannels on dochannels.mba = dichannels.mba AND dochannels.regadd = dichannels.regadd AND dochannels.bit = dichannels.bit group by dochannels.mba,dochannels.regadd,dochannels.bit" # mba,reg,bit,dovalue, divalue changed or not
    # the command above retrieves mba, regadd that need to be written as 16 bit register
    # this solution should work for multiple modbus addresses and different regiosters. first cmd is for write on change only, the second is for debugging, always write!
    #print(Cmd3)
    try:
        cursor3.execute(Cmd3)
        mba_array=[]
        mba_dict={} # close to json nested format [mba[reg[bit,ddo,di]]]
        reg_dict={}
        bit_dict={}
        for row in cursor3: # got sorted by mba,regadd,bit values for bits that need to be updated / written
            tmp_array=[]
            #print('got something from dochannels-dichannels left join') # debug 
            regadd=0
            mba=0
            bit=0
            di_value=0
            do_value=0
            syslog('change in output needed for mba,regadd,bit '+str(int(float(row[0])))+", "+str(int(float(row[1])))+", "+str(int(float(row[2])))+' from value '+str(int(float(row[4])))+' to '+str(int(float(row[3]))))
            try:
                mba=int(float(row[0])) # must be number
                regadd=int(float(row[1])) # must be a number. 0..255
                bit=(int(float(row[2]))) # bit 0..15
                tmp_array.append(int(float(row[3])))  # do_value=int(row[3]) # 0 or 1 to be written
                tmp_array.append(int(float(row[4]))) # di_value=int(row[4]) # 0 or 1 to be written
                bit_dict.update({bit : tmp_array}) # regadd:[bit,do,di] dict member
                reg_dict.update({regadd : bit_dict})
            except:
                msg='failure in creating tmp_array '+repr(tmp_array)+' '+str(sys.exc_info()[1])
                print(msg)
                syslog(msg)
                #traceback.print_exc()
                
            mba_dict.update({mba : reg_dict})
            #print('reg_dict',reg_dict,'mba_dict',mba_dict) # debug
            
            if mba != omba:  #  and omba != 0: # next mba, write register using omba now!
                mba_array.append(mba) # mba values in array
                omba=mba
                
        # dictionaries ready, let's process
        for mba in mba_dict.keys(): # this key is string!
            print('finding outputs for mba,regadd',mba,regadd)
            for regadd in reg_dict.keys(): # chk all output registers defined in dochannels table
                
                word=client.read_holding_registers(address=regadd, count=1, unit=mba).registers[0] # find the current output word to inject the bitwise changes
                
                #if regadd == 0: # for do W272_dict member defines initial state according to mba
                #    try:
                #        word=W272_dict[mba] # power-up value
                #        #print('power up setup for mba',mba,format("%04x" % word)) # debug 
                #    except:
                #        msg='power up state for mba '+str(mba)+' NOT SET! chk reg 272'
                #        syslog(msg)
                #        print(msg)
                #        traceback.print_exc()
                #else:
                #    #print('output regadd for mba',regadd,mba) #debug
                #    word = 0 # not DO register
                # 
                
                print('value of the output',mba,regadd,'before change',format("%04x" % word)) # debug
                
                for bit in bit_dict.keys():
                    print('do di bit,[do,di]',bit,bit_dict[bit]) # debug
                    word2=bit_replace(word,bit,bit_dict[bit][0]) # changed the necessary bit. can't reuse / change word directly!
                    word=word2
                    syslog('modified by bit '+str(bit)+' value '+str(bit_dict[bit][0])+' word '+format("%04x" % word)) # debug
                #print('going to write a register mba,regadd,with modified word - ',mba,regadd,format("%04x" % word)) # temporary

                try: #
                    client.write_register(address=regadd, value=word, unit=mba)
                    respcode=0 # write_register(mba,regadd,word,2*tcpmode)
                    msg='output written - mba,regadd,value '+str(mba)+' '+str(regadd)+' '+format("%04x" % word)
                except:
                    msg='FAILED writing register '+str(mba)+'.'+str(regadd)+' '+str(sys.exc_info()[1])
                    print(msg)
                    syslog(msg)
                    #traceback.print_exc()
                    respcode=1

                syslog(msg)
                print(msg)

                if respcode == 0: # ok
                    MBerr[mba]=0
                else:
                    MBerr[mba]=MBerr[mba]+1
                    print('problem with register',mba,regadd,value,'writing!')
            
            omba=mba # to detect mba change. valuse in array mbs_array
                
    except:
        msg='problem with dichannel grp select in write_do_channels! '+str(sys.exc_info()[1])
        print(msg)
        syslog(msg)
        #traceback.print_exc() # debug
        sys.stdout.flush()
        time.sleep(1)
        return 1

    conn3.commit() # transaction end, perhaps not even needed - 2 reads, no writes...
    return 0
    # write_dochannels() end. 
    
    
    


def read_aichannels(): # analogue inputs via modbusTCP, to be executed regularly (about 1..3 s interval). do not send here.
    locstring="" # local
    global inumm,ts,ts_inumm,mac,tcpdata, tcperr
    mba=0 # lokaalne siin
    val_reg=''
    desc=''
    comment=''
    mcount=0
    block=0 # vigade arv
    ts_created=ts # selle loeme teenuse ajamargiks
    value=0

    try:
        Cmd3="BEGIN IMMEDIATE TRANSACTION" # conn3, kogu selle teenustegrupiga (aichannels) tegelemine on transaction
        conn3.execute(Cmd3)

        Cmd3="select val_reg,count(member) from aichannels group by val_reg"
        cursor3.execute(Cmd3)

        for row in cursor3: # services
            lisa='' # vaartuste joru
            val_reg=''
            sta_reg=''
            status=0 # esialgu

            val_reg=row[0] # teenuse nimi
            mcount=int(row[1])
            sta_reg=val_reg[:-1]+"S" # nimi ilma viimase symbolita ja S - statuse teenuse nimi, analoogsuuruste ja temp kohta
            svc_name='' # mottetu komment puhvri reale?
            #print 'reading aichannels values for val_reg',val_reg,'with',mcount,'members' # ajutine
            Cmd3="select * from aichannels where val_reg='"+val_reg+"'" # loeme yhe teenuse kogu info
            #print Cmd3 # ajutine
            cursor3a.execute(Cmd3) # another cursor to read the same table

            for srow in cursor3a: # service members
                #print repr(srow) # debug
                mba=-1 #
                regadd=-1
                member=0
                cfg=0
                x1=0
                x2=0
                y1=0
                y2=0
                outlo=0
                outhi=0
                ostatus=0 # eelmine
                #tvalue=0 # test, vordlus
                oraw=0
                ovalue=0 # previous (possibly averaged) value
                ots=0 # eelmine ts value ja status ja raw oma
                avg=0 # keskmistamistegur, mojub alates 2
                desc=''
                comment=''
                # 0       1     2     3     4   5  6  7  8  9    10     11  12    13  14   15     16  17    18
                #mba,regadd,val_reg,member,cfg,x1,x2,y1,y2,outlo,outhi,avg,block,raw,value,status,ts,desc,comment  # aichannels
                if srow[0] != '':
                    mba=int(srow[0]) # must be int! will be -1 if empty (setpoints)
                if srow[1] != '':
                    regadd=int(srow[1]) # must be int! will be -1 if empty
                val_reg=srow[2] # see on string
                if srow[3] != '':
                    member=int(srow[3])
                if srow[4] != '':
                    cfg=int(srow[4]) # konfibait nii ind kui grp korraga, esita hex kujul hiljem
                if srow[5] != '':
                    x1=int(srow[5])
                if srow[6] != '':
                    x2=int(srow[6])
                if srow[7] != '':
                    y1=int(srow[7])
                if srow[8] != '':
                    y2=int(srow[8])
                if srow[9] != '':
                    outlo=int(srow[9])
                if srow[10] != '':
                    outhi=int(srow[10])
                if srow[11] != '':
                    avg=int(srow[11])  #  averaging strength, values 0 and 1 do not average!
                if srow[12] != '': # block - loendame siin vigu, kui kasvab yle 3? siis enam ei saada
                    block=int(srow[12])  #
                if srow[13] != '': #
                    oraw=int(srow[13])
                if srow[14] != '':
                    ovalue=int(float(srow[14])) # ovalue=int(srow[14])
                if srow[15] != '':
                    ostatus=int(srow[15])
                if srow[16] != '':
                    ots=int(srow[16])
                desc=srow[17]
                comment=srow[18]


                if mba>=0 and mba<256 and regadd>=0 and regadd<65536:  # valid mba and regaddr, let's read to update value in aichannels table
                    msg='reading ai '+str(mba)+'.'+str(regadd)+' for '+val_reg+' m '+str(member) # 'temp skip!'  # ajutine
                    
                    #if respcode == 0: # got  tcpdata as register content. convert to scale.
                    try:
                        result = client.read_holding_registers(address=regadd, count=1, unit=mba)
                        tcpdata = result.registers[0] # reading modbus slave
                        msg=msg+' raw '+str(tcpdata)
                        if mba<5:
                            MBerr[mba]=0

                        if x1 != x2 and y1 != y2: # konf normaalne
                            value=(tcpdata-x1)*(y2-y1)/(x2-x1) # lineaarteisendus
                            value=y1+value

                            #if value == y2: # ebanormaalne analoogsignaali kyllastus
                            #    print 'skipping invalid value, equal to y2',y1
                            #    return 1  # see oli jama!! kp24 hvv naiteks

                            #print 'raw',tcpdata,', ovalue',ovalue, # debug
                            if avg>1 and abs(value-ovalue)<value/2: # keskmistame, hype ei ole suur
                            #if avg>1:  # lugemite keskmistamine vajalik, kusjures vaartuse voib ju ka komaga sailitada!
                                value=((avg-1)*ovalue+value)/avg # averaging
                                msg=msg+', averaged '+str(int(value))
                            else: # no averaging for big jumps
                                if tcpdata == 4096: # this is error result from 12 bit 1wire temperature sensor
                                    value=ovalue # repeat the previous value. should count the errors to raise alarm in the end! counted error result is block, value 3 stps sending.
                                else: # acceptable non-averaged value
                                    msg=msg+', nonavg value '+str(int(value))

                        else:
                            print("val_reg",val_reg,"member",member,"ai2scale PARAMETERS INVALID:",x1,x2,'->',y1,y2,'value not used!')
                            value=0
                            status=3 # not to be sent status=3! or send member as NaN?

                        print(msg) # temporarely off SIIN YTLEB RAW LUGEMI AI jaoks
                        syslog(msg)

                    except: # else: # failed reading register, respcode>0
                        if mba<5:
                            MBerr[mba]=MBerr[mba]+1 # increase error counter
                        print('failed to read ai mb register', mba,regadd,'skipping aichannels table update')
                        return 1 # skipping aichannels update below

                else:
                    value=ovalue # possible setpoint, ovalue from aichannels table, no modbus reading for this
                    status=0
                    #print 'setpoint value',value


                # check the value limits and set the status, acoording to configuration byte cfg bits values
                # use hysteresis to return from non-zero status values
                status=0 # initially for each member
                if value>outhi: # above hi limit
                    if (cfg&4) and status == 0: # warning
                        status=1
                    if (cfg&8) and status<2: # critical
                        status=2
                    if (cfg&12) == 12: #  not to be sent
                        status=3
                        block=block+1 # error count incr
                else: # return with hysteresis 5%
                    if value>outlo and value<outhi-0.05*(outhi-outlo): # value must not be below lo limit in order for status to become normal
                        status=0 # back to normal
                        block=0 # reset error counter

                if value<outlo: # below lo limit
                    if (cfg&1) and status == 0: # warning
                        status=1
                    if (cfg&2) and status<2: # critical
                        status=2
                    if (cfg&3) == 3: # not to be sent, unknown
                        status=3
                        block=block+1 # error count incr
                else: # back with hysteresis 5%
                    if value<outhi and value>outlo+0.05*(outhi-outlo):
                        status=0 # back to normal
                        block=0

                #print 'status for AI val_reg, member',val_reg,member,status,'due to cfg',cfg,'and value',value,'while limits are',outlo,outhi # debug
                #aichannels update with new value and sdatus
                Cmd3="UPDATE aichannels set status='"+str(status)+"', value='"+str(value)+"', ts='"+str(int(ts))+"' where val_reg='"+val_reg+"' and member='"+str(member)+"'" # meelde
                #print Cmd3
                conn3.execute(Cmd3) # kirjutamine
                
        if OSTYPE == 'android':
            try:
                Cmd3="UPDATE aichannels set value='"+str(BattVoltage)+"', ts='"+str(int(ts))+"' where val_reg='BVW' and member='1'"  # battery voltage to svc BVW
                conn3.execute(Cmd3) # write conn3
                Cmd3="UPDATE aichannels set value='"+str(BattCharge)+"', ts='"+str(int(ts))+"' where val_reg='BCW' and member='1'"  # battery charge to svc BCW
                conn3.execute(Cmd3) # write conn3
                Cmd3="UPDATE aichannels set value='"+str(BattTemperature)+"', ts='"+str(int(ts))+"' where val_reg='BTW' and member='1'"  # battery temperature to svc BTW
                conn3.execute(Cmd3) # write conn3
                msg='battery voltage, charge, temperature written into aichannels'
            except:
                msg='failed to update aichannels with battery voltage, charge and temperature'
                pass # if no such row in aichannels
            syslog(msg)
            print(msg)
            
        conn3.commit() # aichannels transaction end
        #conn3a.commit() # cursor3a  transaction end
        return 0

    except:
        msg='PROBLEM with aichannels reading or processing: '+str(sys.exc_info()[1])
        print(msg)
        syslog(msg)
        #traceback.print_exc() # peatub kui sisse jatta
        sys.stdout.flush()
        time.sleep(0.5)

        return 1
    #read_aichannels end



def make_aichannels(): # send the ai service messages to the monitoring server (only if fresh enough, not older than 2xappdelay)
    locstring="" # local
    global inumm,ts,ts_inumm,mac,tcpdata, tcperr, udpport,appdelay
    mba=0 # lokaalne siin
    val_reg=''
    desc=''
    comment=''
    mcount=0
    block=0 # vigade arv
    ts_created=ts # selle loeme teenuse ajamargiks

    try:
        Cmd3="BEGIN IMMEDIATE TRANSACTION" # conn3, kogu selle teenustegrupiga (aichannels) tegelemine on transaction
        conn3.execute(Cmd3)
        conn1.execute(Cmd3) # buff2server

        Cmd3="select val_reg,count(member) from aichannels group by val_reg"
        cursor3.execute(Cmd3)

        for row in cursor3: # services
            val_reg=row[0] # teenuse nimi
            mcount=int(row[1])
            sta_reg=val_reg[:-1]+"S" # nimi ilma viimase symbolita ja S - statuse teenuse nimi, analoogsuuruste ja temp kohta

            if make_aichannel_svc(val_reg,sta_reg) == 0: # successful svc insertion into buff2server
                pass
                print('tried to report svc',val_reg,sta_reg)
            else:
                print('FAILED to report svc',val_reg,sta_reg)
                return 1 #cancel


        conn1.commit() # buff2server transaction end
        conn3.commit() # aichannels transaction end
        #conn3a.commit() # for cursor3a

    except:
        msg='PROBLEM with aichannels reporting '+str(sys.exc_info()[1])
        print(msg)
        syslog(msg)
        #traceback.print_exc()
        sys.stdout.flush()
        time.sleep(0.5)
        return 1




def make_aichannel_svc(val_reg,sta_reg):  # make a single service record based on aichannel members and put it into buff2server
    global inumm,ts,ts_inumm,mac,tcpdata, tcperr, udpport,appdelay
    svc_name='' # mottetu komment puhvri reale?
    status=0 # esialgu
    lisa=''
    #print 'reading aichannels values for val_reg',val_reg,'with',mcount,'members' # ajutine

    Cmd3="select * from aichannels where val_reg='"+val_reg+"'" # loeme yhe teenuse kogu info uuesti
    #print Cmd3 # ajutine
    cursor3a.execute(Cmd3) # another cursor to read the same table

    for srow in cursor3a: # service members
        #print repr(srow) # debug
        mba=-1 #
        regadd=-1
        member=0
        cfg=0
        x1=0
        x2=0
        y1=0
        y2=0
        outlo=0
        outhi=0
        ostatus=0 # eelmine
        #tvalue=0 # test, vordlus
        oraw=0
        ovalue=0 # previous (possibly averaged) value
        ots=0 # eelmine ts value ja status ja raw oma
        mts=0 # max ts, if too old, skip the service reporting
        avg=0 # keskmistamistegur, mojub alates 2
        desc=''
        comment=''
        # 0       1     2     3     4   5  6  7  8  9    10     11  12    13  14   15     16  17    18
        #mba,regadd,val_reg,member,cfg,x1,x2,y1,y2,outlo,outhi,avg,block,raw,value,status,ts,desc,comment  # aichannels
        if srow[0] != '':
            mba=int(srow[0]) # must be int! will be -1 if empty (setpoints)
        if srow[1] != '':
            regadd=int(srow[1]) # must be int! will be -1 if empty
        val_reg=srow[2] # see on string
        if srow[3] != '':
            member=int(srow[3])
        if srow[4] != '':
            cfg=int(srow[4]) # konfibait nii ind kui grp korraga, esita hex kujul hiljem
        if srow[5] != '':
            x1=int(srow[5])
        if srow[6] != '':
            x2=int(srow[6])
        if srow[7] != '':
            y1=int(srow[7])
        if srow[8] != '':
            y2=int(srow[8])
        if srow[9] != '':
            outlo=int(srow[9])
        if srow[10] != '':
            outhi=int(srow[10])
        if srow[11] != '':
            avg=int(srow[11])  #  averaging strength, values 0 and 1 do not average!
        if srow[12] != '': # block - loendame siin vigu, kui kasvab yle 3? siis enam ei saada
            block=int(srow[12])  #
        if srow[13] != '': #
            oraw=int(srow[13])
        if srow[14] != '':
            ovalue=int(float(srow[14]))
        if srow[15] != '':
            ostatus=int(srow[15])
        if srow[16] != '':
            ots=int(srow[16])
        desc=srow[17]
        comment=srow[18]

        if mts < ots:
            mts=ots # latest update to the service must be not too old!

        if mba>=0 and mba<256 and regadd>=0 and regadd<65536:  # valid mba and regaddr, let's read to update value in aichannels table
            print('reporting ai service',val_reg,'member',member,'with value',ovalue)  # ajutine

        #else: # see keeras statuse arvuruse kihva! 9.2.2014 leitud
        #    value=ovalue # possible setpoint, ovalue from aichannels table, no modbus reading for this
        #    status=0
        #    #print 'setpoint value',value


        if ostatus>status:
            status=ostatus
        if status>3:
            msg='make_aichannels_svs() invalid status '+str(status)
            print(msg)
            syslog(msg)

        if lisa != '': # not the first member
            lisa=lisa+' ' # separator between member values
        lisa=lisa+str(ovalue) # adding member values into one string

    # put together final service to buff2server
    Cmd1="INSERT into buff2server values('"+mac+"','"+host+"','"+str(udpport)+"','"+svc_name+"','"+sta_reg+"','"+str(status)+"','"+val_reg+"','"+str(lisa)+"','"+str(int(ts_created))+"','','')"
    #print "ai Cmd1=",Cmd1 # debug
    if (ts-mts  < 2*appdelay): # has been updated lately
        conn1.execute(Cmd1) # write aichannels data into buff2server
    else:
        msg='skipping ai data send (buff2server wr) due to stale aichannels data' # debug
        syslog(msg) # incl syslog
        print(msg)
        return 1

    return 0



def read_dichannel_bits(mba): # binary inputs, bit changes to be found and values in dichannels table updated
# reads 16 bits as di or do channels to be reported to monitoring
# NB the same bits can be of different rows, to be reported in different services. services and their members must be unique
    locstring="" # see on siin lokaalne!
    global inumm,ts,ts_inumm,mac,tcpdata, MBerr,odiword # what if several di extensions??
    #mba=0 # lokaalne siin
    val_reg=''
    desc=''
    comment=''
    mcount=0
    ts_created=ts # timestamp
    ichg=0 # change mask iga mba kohta eraldi koostatav

    try:
        Cmd3="BEGIN IMMEDIATE TRANSACTION" # conn3
        conn3.execute(Cmd3) #

        #Cmd3="select mba,regadd from dichannels group by mba,regadd" # finding di registers to read. usually 1 reg per mb slave.
        Cmd3="select regadd from dichannels where mba='"+str(mba)+"'"  # for one slave only
        cursor3.execute(Cmd3)

        for row in cursor3: # for each mba and regadd (DI register)
            regadd=0
            #mba=0

            #if row[0] != '':
            #    mba=int(row[0]) # must be number
            #if row[1] != '':
            #    regadd=int(row[1]) # must be number
            if row[0] != '':
                regadd=int(row[0]) # must be number

            #mcount=int(row[1])
            if val_reg != val_reg[:-1]+"S": #  only if val_reg does not end with S!
                sta_reg=val_reg[:-1]+"S"
            else:
                sta_reg='' # no status added to the datagram

            svc_name='' # unused?
            #print('reading dichannel register mba,regadd',mba,regadd) # temporary debug
            try: # if respcode == 0: # successful DI register reading - continuous to catch changes! ################################
                result = client.read_holding_registers(address=regadd, count=1, unit=mba) # respcode=read_register(mba,regadd,1) # 1 register at the time, from mb slave
                tcpdata = result.registers[0]  # saab ka bitivaartusi lugeda!
                if mba<5:
                    MBerr[mba]=0
                #print ', result',format("%04x" % tcpdata)
            except:
                #msg='di register '+str(mba)+'.'+str(regadd)+' read FAILURE! no sql update! '+str(sys.exc_info()[1])  # debug
                #print(msg) # debug
                #syslog(msg) # debug
                traceback.print_exc() # debug
                return 1

            Cmd3a="select bit,value from dichannels where mba='"+str(mba)+"' and regadd='"+str(regadd)+"' group by regadd,bit" # loeme koik di kasutusel bitid sellelt registrilt
            try: # now process the data stored into dichannels table
                cursor3a.execute(Cmd3a)

                for srow in cursor3a: # for every mba list the bits in used&to be updated
                    bit=0
                    ovalue=0
                    chg=0 #  bit change flag
                    #mba and regadd are known
                    if srow[0] != '':
                        bit=int(srow[0]) # bit 0..15
                    if srow[1] != '':
                        ovalue=int(float(srow[1])) # bit 0..15
                    value=(tcpdata&2**bit)/2**bit # bit value 0 or 1 instead of 1, 2, 4... / added 06.04
                    #print 'decoded value for bit',bit,value,'was',ovalue

                    # check if outputs must be written
                    if value != ovalue: # change detected, update dichannels value, chg-flag  - saaks ka maski alusel!!!
                        chg=3 # 2-bit change flag, bit 0 to send and bit 1 to process, to be reset separately
                        #ichg=ichg+2**bit # adding up into the change mask
                        msg='DIchannel '+str(mba)+'.'+str(regadd)+' bit '+str(bit)+' change! was '+str(ovalue)+', became '+str(round(value)) # temporary
                        print(msg)
                        syslog(msg)
                        # dichannels table update with new bit values and change flags. no status change here. no update if not changed!
                        Cmd3="UPDATE dichannels set value='"+str(round(value))+"', chg='"+str(chg)+"', ts_chg='"+str(int(ts))+"' where mba='"+str(mba)+"' and regadd='"+str(regadd)+"' and bit='"+str(bit)+"'" # uus bit value ja chg lipp, 2 BITTI!
                    else: # ts_chg used as ts_read now! change detection does not need that  timestamp!
                        Cmd3="UPDATE dichannels set ts_chg='"+str(int(ts))+"' where mba='"+str(mba)+"' and regadd='"+str(regadd)+"' and bit='"+str(bit)+"'" # old value unchanged, use ts_CHG AS TS!
                    print(Cmd3) # debug
                    conn3.execute(Cmd3) # write

            except: # else: # respcode>0
                if mba<5:
                    MBerr[mba]=MBerr[mba]+1 # increase error counter
                    msg='failed to read di register from '+str(mba)+'.'+str(regadd)+' '+str(sys.exc_info()[1])
                    #traceback.print_exc() # debug
                    if MBerr[mba] == 1: # first error
                        print(msg) # di problem (first only)
                        syslog(msg) # di problem (first only)
                return 1

            msg='dichannel register mba.regadd '+str(mba)+'.'+str(regadd)+' read success, value 0x'+format("%04x" % tcpdata)
            #if mba == 255:
            #    print(msg) # temporary debug
        conn3.commit()  # dichannel-bits transaction end
        #conn3a.commit() # cursor3a
        return 0

    except: # Exception,err:  # python3 ei taha seda viimast
        #syslog('err: '+repr(err))
        msg='there was a problem with dichannels data reading or processing! '+str(sys.exc_info()[1])
        syslog(msg)
        print(msg)
        #traceback.print_exc()
        #conn3.commit()  # et transaction rippuma ei jaaks?
        time.sleep(1)
        return 1

# read_dichannel_bits() end. FRESHENED DICHANNELS TABLE VALUES AND CGH BITS (0 TO SEND, 1 TO PROCESS)




def make_dichannels(): # di services into to-be-sent buffer table BUT only when member(s) changed or for renotification AND updated less than 5 s ago
    locstring="" # local
    global inumm,ts,ts_inumm,mac #,tcperr
    mba=0 # local here
    val_reg=''
    desc=''
    comment=''
    mcount=0
    ts_created=ts # timestamp
    #sumstatus=0 # summary status for a service, based on service member statuses
    chg=0 # status change flag with 2 bits in use!
    value=0
    ts_last=0 # last time the service member has been reported to the server
    try:
        Cmd3="BEGIN IMMEDIATE TRANSACTION" # conn3 transaction, dichannels
        conn3.execute(Cmd3) # dichannels
        conn1.execute(Cmd3) # buff2server

        Cmd3="select val_reg,max((chg+0) & 1),min(ts_msg+0) from dichannels where ((chg+0 & 1) and ((cfg+0) & 16)) or ("+str(int(ts))+">ts_msg+"+str(renotifydelay)+") group by val_reg"
        # take into account cfg! not all changes are to be reported immediately! cfg is also for application needs, not only monitoring!
        cursor3.execute(Cmd3)

        for row in cursor3: # services to be processed. either just changed or to be resent
            #lisa='' # string of space-separated values
            val_reg=''
            sta_reg=''
            sumstatus=0 # at first

            val_reg=row[0] # service name
            chg=int(row[1]) # change bitflag here, 0 or 1
            ts_last=int(row[2]) # last reporting time
            if chg == 1: # message due to bichannel state change
                msg='DI service to be reported due to change: '+val_reg
            else:
                msg='DI service '+val_reg+' to be REreported, last reporting was '+str(ts-ts_last)+' s ago' # , ts now=',ts
            print(msg)
            syslog(msg)
            #mcount=int(row[1]) # changed service member count
            sta_reg=val_reg[:-1]+"S" # service status register name


            if make_dichannel_svc(val_reg,sta_reg,chg) != 0: # adds to buff2server if service (with all members) ok
                msg='skipped sending di svc '+val_reg+', possibly due to stalled member data'
                print(msg)

        conn1.commit() # buff2server
        conn3.commit() # dichannels transaction end
        #conn3a.commit() # for cursor3a

    except:
        #traceback.print_exc()
        #syslog('err: '+repr(err))
        msg='there was a problem with make_dichannels()! '+str(sys.exc_info()[1])
        print(msg)
        syslog(msg)

#make_dichannels() lopp




def make_dichannel_svc(val_reg,sta_reg,chg):    # ONE service compiling and buffering into buff2server if ok
    global mac, ts, appdelay
    lisa='' # value string
    sumstatus=0 # status calc
    svc_name='' # unused? but must exist for insertion into buff2server
    Cmd3="select * from dichannels where val_reg='"+val_reg+"' order by member asc" # data for one service ###########
    cursor3a.execute(Cmd3)
    for srow in cursor3a: # ridu tuleb nii palju kui selle teenuse liikmeid, pole oluline milliste mba ja readd vahele jaotatud
        #print 'row in cursor3a',srow # temporary debug
        mba=0 # local here
        regadd=0
        bit=0 #
        member=0
        cfg=0
        ostatus=0 # previous value
        #tvalue=0 # test
        oraw=0
        ovalue=0 # previous or averaged value
        ots=0 # previous update timestamp
        avg=0 # averaging strength, has effect starting from 2
        desc=''
        comment=''
        # 0      1   2     3      4      5     6     7     8    9     10   11   12      13     14
        #(mba,regadd,bit,val_reg,member,cfg,block,value,status,ts_chg,chg,desc,comment,ts_msg,type integer) # dichannels
        if srow[0] != '':
            mba=int(srow[0])
        if srow[1] != '':
            regadd=int(srow[1]) # must be int! can be missing
        if srow[2] != '':
            bit=int(srow[2])
        val_reg=srow[3] #  string
        if srow[4] != '':
            member=int(srow[4])
        if srow[5] != '':
            cfg=int(srow[5]) # configuration byte
        # block?? to prevent sending service with errors. to be added!
        if srow[7] != '':
            value=int(float(srow[7])) # new value
        if srow[8] != '':
            ostatus=int(float(srow[8])) # old status
        if srow[9] != '':
            ots=int(srow[9]) # value ts timestamp

        if (ts-ots > 2*appdelay): # too old data, break! not updated lately
            print('old dichannels bit,ts,ots,age',bit,ts,ots,ts-ots) # debug
            return 1  # stale data, not to be sent!

        desc=srow[11] # description for UI
        comment=srow[11] # comment internal


        #print 'make_dichannel_svc():',val_reg,'member',member,'value before status proc',value,', lisa',lisa  # temporary debug

        if lisa != "": # not the first member any nmore
            lisa=lisa+" "

        # status and inversions according to configuration byte
        status=0 # initially for each member
        if (cfg&4): # value2value inversion
            value=(1^value) # possible member values 0 voi 1
        lisa=lisa+str(value) # adding possibly inverted member value to multivalue string

        if (cfg&8): # value2status inversion
            value=(1^value) # member value not needed any more

        if (cfg&1): # status warning if value 1
            status=value #
        if (cfg&2): # status critical if value 1
            status=2*value

        if status>sumstatus: # summary status is defined by the biggest member sstatus
            sumstatus=status # suurem jaab kehtima

        #print 'make_channel_svc():',val_reg,'member',member,'value after status proc',value,', status',status,', sumstatus',sumstatus,', lisa',lisa  # temporary debug


        #dichannels table update with new chg ja status values. no changes for values! chg bit 0 off! set ts_msg!
        Cmd3="UPDATE dichannels set status='"+str(status)+"', ts_msg='"+str(int(ts))+"', chg='"+str(chg&2)+"' where val_reg='"+val_reg+"' and member='"+str(member)+"'"
        # bit0 from change flag stripped! this is to notify that this service is sent (due to change). may need other processing however.
        #print Cmd3 # di reporting debug
        conn3.execute(Cmd3) # kirjutamine



    # sending service data into buffer table when the loop above is finished - only if they are up to date, according to ts_created
    if sta_reg == val_reg: # only status will be sent!
        val_reg=''
        lisa=''

    #print mac,host,udpport,svc_name,sta_reg,status,val_reg,lisa,ts_created,inumm # temporary
    Cmd1="INSERT into buff2server values('"+mac+"','"+host+"','"+str(udpport)+"','"+svc_name+"','"+sta_reg+"','"+str(sumstatus)+"','"+val_reg+"','"+str(lisa)+"','"+str(int(ts_created))+"','','')"
    #print "di Cmd1=",Cmd1 # debug
    conn1.execute(Cmd1) # write dichannels data into buff2server
    return 0




def read_counters(): # counters, usually 32 bit / 2 registers.
    locstring="" # see on siin lokaalne!
    global inumm,ts,ts_inumm,mac,tcpdata,MBerr #,MBsta
    respcode=0
    mba=0 # lokaalne siin
    val_reg=''
    sta_reg=''
    status=0
    value=0
    lisa=''
    svc_name='' # tegelikult ei kasuta?
    desc=''
    comment=''
    mcount=0
    Cmd1=''
    ts_created=ts # selle loeme teenuse ajamargiks

    try:
        Cmd3="BEGIN IMMEDIATE TRANSACTION" # conn3
        conn3.execute(Cmd3)

        Cmd3="select val_reg,count(member) from counters group by val_reg"
        #print "Cmd3=",Cmd3
        cursor3.execute(Cmd3) # getting services to be read and reported
        for row in cursor3: # possibly multivalue service members
            lisa='' # string to put space-separated values in
            val_reg=''
            sta_reg=''
            status=0 #
            value=0

            val_reg=row[0] # service value register name
            mcount=int(row[1]) # pole vajalik?
            sta_reg=val_reg[:-1]+"S" # status register name
            svc_name='' # unused?
            #print 'reading counter values for val_reg',val_reg,'with',mcount,'members' # temporary
            Cmd3="select * from counters where val_reg='"+val_reg+"'" #
            #print Cmd3 # temporary
            cursor3a.execute(Cmd3)

            for srow in cursor3a: # one row as a result
                #print srow # temporary
                mba=0 # local here
                regadd=0
                member=0
                cfg=0
                x1=0
                x2=0
                y1=0
                y2=0
                outlo=0
                outhi=0
                ostatus=0 # eelmine
                #tvalue=0 # test
                raw=0 # unconverted reading
                oraw=0 # previous unconverted reading
                ovalue=0 # previous converted value
                ots=0
                avg=0 # averaging strength, effective from 2
                desc='' # description for UI
                comment='' # comment internal
                # 0       1     2     3     4   5  6  7  8  9    10     11  12    13   14   15    16  17   18
                #mba,regadd,val_reg,member,cfg,x1,x2,y1,y2,outlo,outhi,avg,block,raw,value,status,ts,desc,comment  # counters
                if srow[0] != '':
                    mba=int(srow[0]) # modbus address
                if srow[1] != '':
                    regadd=int(srow[1]) # must be int! can be missing
                val_reg=srow[2] # string
                if srow[3] != '':
                    member=int(srow[3])
                if srow[4] != '':
                    cfg=int(srow[4]) # config byte
                if srow[5] != '':
                    x1=int(srow[5])
                if srow[6] != '':
                    x2=int(srow[6])
                if srow[7] != '':
                    y1=int(srow[7])
                if srow[8] != '':
                    y2=int(srow[8])
                if srow[9] != '':
                    outlo=int(srow[9])
                if srow[10] != '':
                    outhi=int(srow[10])
                if srow[11] != '':
                    avg=int(srow[11])  #  averaging strenght, effective from 2
                #if srow[12] != '': # block
                #    block=int(srow[12]) # block / error count
                if srow[13] != '': # previous raw reading
                    oraw=int(srow[13])
                if srow[14] != '': # previous converted value
                    ovalue=int(srow[14])
                if srow[15] != '':
                    ostatus=int(srow[15])
                if srow[16] != '':
                    ots=int(srow[16])
                desc=srow[17]
                comment=srow[18]
                wcount=srow[19] # word count - to be used as read_register() param 3

                if mba>=0 and mba<256 and regadd>=0 and regadd<65536:  # legal values for mba and regaddr
                    print('counter',mba,regadd,'for',val_reg,'m',member) #'wcount',wcount)  # debug

                    #MBsta[mba-1]=respcode
                    try: # if respcode == 0: # got tcpdata as counter value
                        result = client.read_holding_registers(address=regadd, count=2, unit=mba) # respcode=read_register(mba,regadd,wcount). 32 bits!
                        if wcount == 2:
                            tcpdata = 65536*result.registers[0]+result.registers[1]
                            print('normal counter',str(mba),str(regadd),'result',tcpdata,'based on',str(result.registers[0]),str(result.registers[1])) # debug
                        else: # barionet, assumably -2
                            tcpdata = 65536*result.registers[1]+result.registers[0]  # wrong word order for counters in barionet!
                            print('barionet counter result',tcpdata,'based on',str(result.registers[1]),str(result.registers[0])) # debug

                        MBerr[mba]=0
                        raw=tcpdata # let's keep the raw
                        value=tcpdata # will be converted later
                        if lisa != '':
                            lisa=lisa+" "

                        # CONFIG BYTE BIT MEANINGS
                        # 1 - below outlo warning,
                        # 2 - below outlo critical,
                        # NB! 3 - not to be sent  if value below outlo
                        # 4 - above outhi warning
                        # 8 - above outhi critical

                        # 16 - to be zeroed regularly, see next bits for when
                        # 32  - midnight if 1, month change if 0
                        # 64 - power to be counted based on count increase and time period between counts
                        # 128 reserv / lsw, msw jarjekord? nagu barix voi nagu android io

                        #kontrolli kas kumulatiivne, nullistuv voi voimsus!
                        if (cfg&16): # power, increment to be calculated! divide increment to time from the last reading to get the power
                            if oraw>0: # last reading seems normal
                                value=raw-oraw # RAW vahe leitud
                                print('counter raw inc',value,) # temporary
                                value=float(value/(ts-ots)) # power reading
                                print('timeperiod',ts-ots,'raw/time',value) # temporary
                                # end special processing for power
                            else:
                                value=0
                                status=3 # not to be sent
                                print('probably first run, no power calc result for',val_reg,'this time! value=0, status=3') # vaartuseks saadame None

                        if x1 != x2 and y1 != y2: # seems like normal input data
                            value=(value-x1)*(y2-y1)/(x2-x1)
                            value=int(y1+value) # integer values to be reported only
                        else:
                            print("read_counters val_reg",val_reg,"member",member,"ai2scale PARAMETERS INVALID:",x1,x2,'->',y1,y2,'conversion not used!')
                            # jaab selline value nagu oli

                        print('counter raw',tcpdata,', value',value,', oraw',oraw,', ovalue',ovalue,', avg',avg,) # the same line continued with next print

                        if avg>1 and abs(value-ovalue)<value/2:  # averaging the readings. big jumps (more than 50% change) are not averaged.
                            value=int(((avg-1)*ovalue+value)/avg) # averaging with the previous value, works like RC low pass filter
                            print(', avg on, counter value',value) # ,'rawdiff',abs(raw-oraw),'raw/2',raw/2
                        else:
                            print(', no avg, counter value becomes',value)


                        # check limits and set statuses based on that
                        # returning to normal with hysteresis, take previous value into account
                        status=0 # initially for each member
                        if value>outhi: # yle ylemise piiri
                            if (cfg&4) and status == 0: # warning if above the limit
                                status=1
                            if (cfg&8) and status<2: # critical if  above the limit
                                status=2
                            if (cfg&12) == 12: # unknown if  above the limit
                                status=3
                        else: # return to normal with hysteresis
                            if value<outhi-0.05*(outhi-outlo):
                                status=0 # normal again

                        if value<outlo: # below lo limit
                            if (cfg&1) and status == 0: # warning if below lo limit
                                status=1
                            if (cfg&2) and status<2: # warning  if below lo limit
                                status=2
                            if (cfg&3) == 3: # unknown  if below lo limit
                                status=3
                        else: # return
                            if value>outlo+0.05*(outhi-outlo):
                                status=0 # normal again

                        print('status for counter svc',val_reg,status,'due to cfg',cfg,'and value',value,'while limits are',outlo,outhi) # debug

                        #if value<ovalue and ovalue < 4294967040: # this will restore the count increase during comm break
                        if value == 0 and ovalue >0: # possible pic reset. perhaps value <= 100?
                            msg='restoring lost content for counter '+str(mba)+'.'+str(regadd)+':2 to become '+str(ovalue)+' again instead of '+str(value)
                            syslog(msg)
                            print(msg)
                            value=ovalue # +value # restoring based on ovalue and new count
                            try:
                                if wcount == 2: # normal counter
                                    #client.write_registers(address=regadd, values=[value&4294901760,value&65535], unit=mba) # f.code 0x10 unsupported!
                                    client.write_register(address=regadd, value=(value&4294901760)/65536, unit=mba) # 0x10 not yet supported! set one by one.
                                    time.sleep(0.1)
                                    client.write_register(address=regadd+1, value=(value&65535), unit=mba) # 0x10 not yet supported!
                                    time.sleep(0.1)
                                else:
                                    if wcount == -2: # barionet counter, MSW must be written first
                                        #client.write_registers(address=regadd, values=[value&65535, value&4294901760], unit=mba) # f.code 0x10 not yet supported!
                                        client.write_register(address=regadd, value=(value&65535), unit=mba)
                                        time.sleep(0.1)
                                        client.write_register(address=regadd+1, value=(value&4294901760)/65536, unit=mba) # which one first for barionet?? chk this
                                        time.sleep(0.1)
                                    else:
                                        print('illegal counter configuration!',mba,regadd,wcount)
                            except:  # restore failed
                                MBerr[mba]=MBerr[mba]+1
                                msg='failed restoring counter register '+str(mba)+'.'+str(regadd)+'\n'+str(sys.exc_info()[1])
                                syslog(msg)
                                print(msg)
                                #traceback.print_exc()

                        #counters table update
                        Cmd3="UPDATE counters set status='"+str(status)+"', value='"+str(value)+"', raw='"+str(raw)+"', ts='"+str(int(ts))+"' where val_reg='"+val_reg+"' and member='"+str(member)+"'"
                        #print 'Cmd3',Cmd3 # temporary debug
                        conn3.execute(Cmd3) # update counters

                        lisa=lisa+str(value) # members together into one string


                    except: # register read failed, respcode>0
                        MBerr[mba]=MBerr[mba]+1
                        msg='failed reading counter register'+str(mba)+'.'+str(regadd)
                        syslog(msg)
                        print(msg)
                        traceback.print_exc()
                else:
                    msg='counters: out of range mba or regadd '+str(mba)+'.'+str(regadd)
                    syslog(msg)
                    print(msg)

            # sending in to buffer
            #print mac,host,udpport,svc_name,sta_reg,status,val_reg,lisa,ts_created,inumm # temporary
            Cmd1="INSERT into buff2server values('"+mac+"','"+host+"','"+str(udpport)+"','"+svc_name+"','"+sta_reg+"','"+str(status)+"','"+val_reg+"','"+str(lisa)+"','"+str(int(ts_created))+"','','')"
            # inum and ts_tried empty at first!
            #print "cnt Cmd1=",Cmd1 # debug
            conn1.execute(Cmd1)



        conn3.commit() # counters transaction end
        #conn3a.commit() # counters cursor3a trans end
        conn1.commit() # buff2server transaction end
        return 0 #respcode

    except: # end reading counters
        msg='problem with counters read or processing: '+str(sys.exc_info()[1])
        print(msg)
        syslog(msg)
        #traceback.print_exc()
        #sys.stdout.flush()
        time.sleep(1)
        return 1

#read_counters end #############




def report_setup(): # send setup data to server via buff2server table as usual.
    locstring="" # local
    global inumm,ts,ts_inumm,mac,host,udpport,TODO,sendstring,W272_dict,loghost,logport,logaddr
    mba=0 # lokaalne siin
    reg=''
    reg_val=''
    Cmd1=''
    Cmd4=''
    ts_created=ts
    svc_name='setup value'
    oldmac=''

    sendstring=sendstring+"AVV:"+APVER+"\nAVS:0\n"  # THIS IS RESCUE VERSION!
    udpsend(inumm,int(ts)) # sending to the monitoring server

    try:
        #Cmd4="BEGIN IMMEDIATE TRANSACTION" # conn4 asetup
        #conn4.execute(Cmd4)
        Cmd1="BEGIN IMMEDIATE TRANSACTION" # conn1 buff2server
        conn1.execute(Cmd1)

        Cmd4="select register,value from setup" # no multimember registers for setup!
        #print(Cmd4) # temporary
        cursor4.execute(Cmd4)

        for row in cursor4: #
            val_reg=''  # string
            reg_val=''  # string
            status=0 # esialgu
            #value=0

            val_reg=row[0] # muutuja  nimi
            reg_val=row[1] # string even if number!
            print(' setup row: ',val_reg,reg_val)

            if val_reg[0] == 'W' and '272' in val_reg: # power up value for do (setup register W1.272 and so on)
                W272_dict.update({int(float(val_reg[1])) : int(float(reg_val))}) # {mba:272value}
                print ('updated W272_dict, became',W272_dict)
                
            if val_reg == 'S514': # syslog ip address
                if reg_val == '0.0.0.0' or reg_val == '':
                    loghost='255.255.255.255' # broadcast
                else:
                    loghost=reg_val
                msg='syslog server address will be updated to '+loghost
                print(msg)
                syslog(msg)
                logaddr=(loghost,logport) # global variable change
                if OSTYPE == 'archlinux':  # change the linux syslog destination address too
                    if subexec(['/etc/syslog-ng/changedest.sh',loghost],0) == 0:
                        msg='linux syslog redirected to '+loghost
                    else:
                        msg='linux syslog redirection to '+loghost+' FAILED!'
                    syslog(msg)
                    print(msg)
            # sending to buffer, no status counterparts! status=''
            Cmd1="INSERT into buff2server values('"+mac+"','"+host+"','"+str(udpport)+"','"+svc_name+"','','','"+val_reg+"','"+reg_val+"','"+str(int(ts_created))+"','','')"
            # panime puhvertabelisse vastuse ootamiseks. inum ja ts+_tried esialgu tyhi! ja svc_name on reserviks! babup vms... # statust ei kasuta!!
            #print "stp Cmd1=",Cmd1 # temporary debug
            conn1.execute(Cmd1)

   
        conn1.commit() # buff2server trans lopp
        conn4.commit() # asetup trans lopp
        msg='setup reported at '+str(int(ts))
        print(msg)
        syslog(msg) # log message to file
        sys.stdout.flush()
        time.sleep(0.5)
        return 0

    except: # setup reading  problem
        msg='setup reporting failure (setup reading problem) '+str(sys.exc_info()[1])
        syslog(msg) # log message to file
        print(msg)
        time.sleep(1)
        return 1

#report_setup lopp#############



def report_channelconfig(): #report *channels cfg part as XYn for each member to avoid need for sql file dump and push
    global mac,host,udpport,ts
    locstring="" # local
    global inumm,ts,ts_inumm,mac,host,udpport,TODO,sendstring #
    mba=0 # lokaalne siin
    reg=''
    regadd=''
    #reg_val=''
    Cmd3=''
    Cmd4=''
    ts_created=ts
    desc=''
    svc_name='' # not needed in fact
    #svc_name='setup value'
    avg=0
    x1=0
    x2=0
    y1=0
    y2=0
    outlo=0
    outhi=0
    cfg=0

    try:
        Cmd3="BEGIN IMMEDIATE TRANSACTION" # conn3 modbus_channels
        conn3.execute(Cmd3)
        Cmd1="BEGIN IMMEDIATE TRANSACTION" # conn1 buff2server
        conn1.execute(Cmd1)

        Cmd3="select mba,regadd,bit,val_reg,member,cfg,desc from dichannels"
        #             0    1     2     3       4     5   6
        cursor3.execute(Cmd3)
        for row in cursor3: # dichannels members to be reported
            if row[0] != '':
                mba=int(row[0])
            if row[1] != '':
                regadd=int(row[1])
            else:
                regadd=0
            if row[2] != '':
                bit=int(row[2])
            val_reg=row[3]
            if row[4] != '':
                member=int(row[4])
            if row[5] != '':
                cfg=int(row[5])
            desc=row[6]
            reg=val_reg[:-1]+str(member) # konfiregister state tabelis sailitamiseks
            reg_val=str(mba)+','+str(regadd)+','+str(bit)+','+str(cfg)+','+desc # comma separated string containing the most important setup values
            #print 'channelreport di reg val',reg,reg_val # debug
            Cmd1="INSERT into buff2server values('"+mac+"','"+host+"','"+str(udpport)+"','"+svc_name+"','','','"+reg+"','"+reg_val+"','"+str(int(ts_created))+"','','')"
            #print "report_channelconfig Cmd1=",Cmd1 # temporary debug
            conn1.execute(Cmd1) # buff2server

        # mba,regadd,val_reg,member,cfg,x1,x2,y1,y2,outlo,outhi,avg,block,raw,value,status,ts,desc
        Cmd3="select mba,regadd,val_reg,member,cfg,x1,x2,y1,y2,outlo,outhi,avg,desc from aichannels"
        #             0      1    2        3     4  5  6  7  8  9     10    11  12
        cursor3.execute(Cmd3)
        for row in cursor3: # aichannels members to be reported
            if row[0] != '':
                mba=int(row[0])
            if row[1] != '':
                regadd=int(row[1])
            else:
                regadd=0
            val_reg=row[2]
            if row[3] != '':
                member=int(row[3])
            if row[4] != '':
                cfg=int(row[4])
            if row[5] != '':
                x1=int(row[5])
            if row[6] != '':
                x2=int(row[6])
            if row[7] != '':
                y1=int(row[7])
            if row[8] != '':
                y2=int(row[8])
            if row[9] != '':
                outlo=int(row[9])
            if row[10] != '':
                outhi=int(row[10])
            if row[11] != '':
                avg=int(row[11])
            desc=row[12]
            reg=val_reg[:-1]+str(member) # konfiregister state tabelis sailitamiseks
            reg_val=str(mba)+','+str(regadd)+','+str(cfg)+','+str(x1)+','+str(x2)+','+str(y1)+','+str(y2)+','+str(outlo)+','+str(outhi)+','+desc # comma separated string containing the most important setup values
            #print 'channelreport ai reg val',reg,reg_val # debug

            Cmd1="INSERT into buff2server values('"+mac+"','"+host+"','"+str(udpport)+"','"+svc_name+"','','','"+reg+"','"+reg_val+"','"+str(int(ts_created))+"','','')"
            #print "report_channelconfig Cmd1=",Cmd1 # temporary debug
            conn1.execute(Cmd1) # buff2server

        conn1.commit()  # buff2server transaction end
        conn3.commit()  # modbus_channels transaction end
        return 0

    except: # channels config reading  problem
        msg='channelconfig reporting problem at '+str(sys.exc_info()[1])
        print(msg)
        syslog(msg) 
        #sys.stdout.flush()
        time.sleep(1)
        return 1




def syslog(msg): # sending out syslog message. previously also appending a line to the log file
    global LOG, ts, logaddr,TCW
    msg=msg+"\n" # add newline to the end
    #print('syslog send to',logaddr) # debug
    
    try: # syslog first
        UDPlogSock.sendto(msg.encode('utf-8'),logaddr)
        if not '255.255.' in logaddr[0] and not '10.0.' in logaddr[0] and not '192.168.' in logaddr[0]: # sending syslog out of local network
            TCW[1]=TCW[1]+len(msg) # udp out increase, payload only
    except:
        pass # kui udp ei toimi, ei toimi ka syslog
        #print 'could NOT send syslog message to '+repr(logaddr)
        #traceback.print_exc()

    
    return 0 # no logging to file except in debug mode! on linux errors go to /root/d4c/appd.log anyway

    try: # file write
        with open(LOG,"a") as f:
            f.write(msg) # writing LOG
        return 0
    except:
        print('logging problem to file ',LOG)
        #traceback.print_exc()
        #sys.stdout.flush()
        time.sleep(1)
        return 1




def unsent():  # delete unsent for too long messages - otherwise the udp messages will contain old key:value duplicates!
    global ts,MONTS,retrydelay
    delcount=0
    mintscreated=ts
    maxtscreated=ts
    try:
        Cmd1="BEGIN IMMEDIATE TRANSACTION"  # buff2server
        conn1.execute(Cmd1)
        #Cmd1="SELECT inum,svc_name,sta_reg,status,val_reg,value,ts_created,ts_tried from buff2server where ts_created+0<"+str(ts+3*renotifydelay) # yle 3x regular notif
        Cmd1="SELECT count(sta_reg),min(ts_created),max(ts_created) from buff2server where ts_created+0+"+str(3*retrydelay)+"<"+str(ts) # yle 3x regular notif
        #print Cmd1 # korjab ka uued sisse!
        cursor1.execute(Cmd1)
        #conn1.commit()
        for rida in cursor1: # only one line for count if any at all
            delcount=rida[0] # int
            if delcount>0: # stalled services found
                #print repr(rida) # debug
                mintscreated=int(rida[1])
                maxtscreated=int(rida[2])
                print(delcount,'services lines waiting ack for',3*retrydelay,'s to be deleted')

                #Cmd1="SELECT inum,svc_name,sta_reg,status,val_reg,value,ts_created,ts_tried from buff2server where ts_created+0+"+str(3*retrydelay)+"<"+str(ts) # debug
                #cursor1.execute(Cmd1) # debug
                #for rida in cursor1: # debug
                #    print repr(rida) # debug

                Cmd1="delete from buff2server where ts_created+0+"+str(3*retrydelay)+"<"+str(ts) # +" limit 10" # limit lisatud 23.03.2014
                conn1.execute(Cmd1)

        Cmd1="SELECT count(sta_reg),min(ts_created),max(ts_created) from buff2server"
        cursor1.execute(Cmd1)
        for rida in cursor1: # only one line for count if any at all
            delcount=rida[0] # int
        if delcount>50: # delete all!
            Cmd1="delete from buff2server"
            conn1.execute(Cmd1)
            msg='deleted '+str(delcount)+' unsent messages from buff2server!'
            print(msg)
            syslog(msg)
        conn1.commit() # buff2server transaction end
        time.sleep(1) # prooviks
    except:
        msg='problem with unsent '+str(sys.exc_info()[1])
        print(msg)
        syslog(msg)
        #traceback.print_exc()
        #sys.stdout.flush()
        time.sleep(1)
        
#unsent() end



def udpmessage(): # udp message creation based on  buff2server data, does the retransmits too if needed.
    # buff2server rows will be deleted and inserted into sent2buffer table based on in: contained in ack message
    # what happens in case of connectivity loss?
    # inumm on global in: to be sent, inum on global in: to be received in ack
    # 16.03.2013 switching off saving to sent2server! does not work and not really needed! logcat usable as replacement.
    # DO NOT SEND IF STATUS == 3! WILL BE DELETED LATER BUT WILL BE VISIBLE THEN...

    #print '----udpmessage start' # debug
    timetoretry=0 # local
    ts_created=0 # local
    svc_count=0 # local
    global sendstring,ts,inumm,ts_inumm  # inumm vaja suurendada enne saatmist, et samaga ei saaks midagi baasi lisada
    locnumm=0 #


    timetoretry=int(ts-retrydelay) # send again services older than that
    #print "udpmessage: timetoretry",timetoretry
    Cmd="BEGIN IMMEDIATE TRANSACTION" # buff2server
    try:
        conn1.execute(Cmd)
    except:
        print('could not start transaction on conn1, buff2server')
        traceback.print_exc()
        
    #Cmd1="DELETE * from buff2server where ts_created+60<"+str(int(ts)) # deleting too old unsent stuff, not deleted by received ack / NOT NEEDED ANY MORE
    #conn1.execute(Cmd)
    # instead of or before deleting the records could be moved to unsent2server table (not existing yet). dumped from there, to be sent later as gzipped sql file

    # limit 30 lisatud 19.06.2013
    Cmd1="SELECT * from buff2server where ts_tried='' or (ts_tried+0>1358756016 and ts_tried+0<"+str(ts)+"+0-"+str(timetoretry)+") AND status+0 != 3 order by ts_created asc limit 30"  # +0 to make it number! use no limit / why?
    #print "send Cmd1=",Cmd1 # debug
    try:
        cursor1.execute(Cmd1)
        for srow in cursor1:
            if svc_count == 0: # on first row let's increase the inumm!
                inumm=inumm+1 # increase the message number / WHY HERE? ACK WILL NOT DELETE THE ROWS!
                if inumm > 65535:
                    inumm=1 # avoid zero for sending
                    ts_inumm=ts # time to set new inumm value
                    print("appmain: inumm increased to",inumm) # DEBUG

            svc_count=svc_count+1
            sta_reg=srow[4]
            status=srow[5]
            val_reg=srow[6]
            value=srow[7]
            ts_created=int(srow[8]) # no decimals needed, .0 always anyway

            if val_reg != '':
                sendstring=sendstring+val_reg+":"+str(value)+"\n"
            if sta_reg != '':
                sendstring=sendstring+sta_reg+":"+str(status)+"\n"

            #lugesime read mis tuleb saata ja muutsime nende ts ning inumm
            #print 'udpmessage on svc',svc_count,sta_reg,status,val_reg,value,ts_created # temporary

            Cmd1="update buff2server set ts_tried='"+str(int(ts))+"',inum='"+str(inumm)+"' where sta_reg='"+sta_reg+"' and status='"+str(status)+"' and ts_created='"+str(ts_created)+"'" # muudame proovimise aega koigil korraga
            #print "update Cmd1=",Cmd1
            conn1.execute(Cmd1)

        if svc_count>0: # there is something (changed services) to be sent!
            #print svc_count,"services using inumm",inumm,"to be sent now, at",ts # debug
            udpsend(inumm,int(ts)) # sending away inside udpmessage()

        Cmd1="SELECT count(mac) from buff2server"  # unsent row (svc member) count in buffer
        cursor1.execute(Cmd1) #
        for srow in cursor1:
            svc_count2=int(srow[0]) # total number of unsent messages

        if svc_count2>30: # do not complain below 30
            print(svc_count2,"SERVICE LINES IN BUFFER waiting for ack from monitoring server")

    except: # buff2server reading unsuccessful. unlikely...
        msg='problem with buff2server read '+str(sys.exc_info()[1])
        print(msg)
        syslog(msg)
        #traceback.print_exc()
        #sys.stdout.flush()
        time.sleep(1)


    conn1.commit() # buff2server transaction end

# udpmessage() end
##################



def udpsend(locnum,locts): # actual udp sending, adding ts to in: for some debugging reason. if locnum==0, then no in: will be sent
    global sendstring,mac,TCW, ts_udpsent, stop, saddr # saddr enne puudus!
    if sendstring == '': # nothing to send
        print('udpsend(): nothing to send!')
        return 1

    if len(mac) != 12:
        print('invalid mac',mac)
        time.sleep(2)
        return 1 # do not send messages with invalid mac

    sendstring="id:"+mac+"\n"+sendstring # loodame, et ts_created on enam-vahem yhine neil teenustel...
    if locnum >0: # in: to be added
        sendstring="in:"+str(locnum)+","+str(locts)+"\n"+sendstring

    #TCW[1]=TCW[1]+len(sendstring) # adding to the outgoing UDP byte counter

    #try: # commLED on when we try to send, no matter successfully or not
        #client.write_register(address=0, value=256*64, unit=1) # so far there are no other than do7 and do8 in use, MSB!  commLED ON
        #client.write_register(address=114, value=100, unit=1)  # short pulse ### test
        #setbit_dochannels(14,1) # bit, value. commLED ON until got udp
    #except:
        #msg='failed to light commLED '+str(sys.exc_info()[1])   # show as one line
        #print(msg)
        #syslog(msg)
        #traceback.print_exc()
        #pass
        
    try:
        sendlen=UDPSock.sendto(sendstring.encode('utf-8'),saddr) # tagastab saadetud baitide arvu
        TCW[1]=TCW[1]+sendlen # traffic counter udp out
        #sendlen=len(sendstring)
        #print "sent len",sendlen,"with in:"+str(locnum),sendstring[:66],"..." #sendstring
        msg='\nsent '+sendstring.replace('\n',' ')   # show as one line
        print(msg)
        syslog(msg)
        sendstring=''
        ts_udpsent=ts # last successful udp send
        
        
    except:
        msg='udp send failure in udpsend() to saddr '+repr(saddr)+', lasting s '+str(int(ts - ts_udpsent)) # cannot send, this means problem with connectivity
        syslog(msg)
        print(msg)
        # make sure flight mode is NOT on, but switch it may help sometimes 
        if OSTYPE == 'android':
            if droid.checkAirplaneMode().result == True:
                droid.toggleAirplaneMode(False)
                droid.ttsSpeak('switched flight mode off')
                time.sleep(10)
            else:
                if ((ts - ts_udpsent > 20) and (ts - ts_udpsent <30)) or ((ts - ts_udpsent > 40) and (ts - ts_udpsent <50)): # comm loss, udp bind problem, cannot send
                    droid.ttsSpeak('trying to switch flight mode to kick radios')
                    droid.toggleAirplaneMode(False) # will fall back on next loop execution
                    time.sleep(10)


def push(filename): # send (gzipped) file to supporthost
    global SUPPORTHOST, mac,TCW
    destinationdirectory = 'support/pyapp/'+mac
    #print 'starting with pushing',filename # debug
    if os.path.isfile(filename):
        pass
    else:
        msg='push: found no file '+filename
        print(msg)
        syslog(msg)
        return 2 # no such file

    if '.gz' in filename or '.tgz' in filename: # packed already
        pass
    else: # lets unpack too
        f_in = open(filename, 'rb')
        f_out = gzip.open(filename+'.gz', 'wb')
        f_out.writelines(f_in)
        f_out.close()
        f_in.close()
        filename = filename+'.gz' # new filename to send
        dnsize=os.stat(filename)[6] # file size to be sent
        msg='the file was gzipped to '+filename+' with size '+str(dnsize) # the original file is kept!
        print(msg)
        syslog(msg)

    try:
        r = requests.post('http://www.itvilla.ee/upload.php',
                            files={'file': open(filename, 'rb')},
                            headers={'Authorization': 'Basic cHlhcHA6QkVMYXVwb2E='},
                            data={'mac': destinationdirectory}
                         )
        print('post response:',r.text) # nothing?
        msg='file '+filename+' with size '+str(dnsize)+' sent to '+destinationdirectory
        syslog(msg)
        print(msg)
        TCW[3]=TCW[3]+dnsize # tcp out inc
        return 0
    except:
        msg='the file '+filename+' was NOT sent to '+destinationdirectory+' '+str(sys.exc_info()[1])
        syslog(msg)
        print(msg)
        #traceback.print_exc()
        return 1




def pull(filename,filesize,start): # uncompressing too if filename contains .gz and succesfully retrieved. start=0 normally. higher with resume.
    global SUPPORTHOST,TCW #
    print('trying to retrieve file '+SUPPORTHOST+'/'+filename+' from byte '+str(start))
    oksofar=1 # success flag
    filename2='' # for uncompressed from the downloaded file
    filepart=filename+'.part' # temporary, to be renamed to filename when complete
    filebak=filename+'.bak'
    dnsize=0 # size of downloaded file
    if start>filesize:
        msg='pull parameters: file '+filename+' start '+str(start)+' above filesize '+str(filesize)
        print(msg)
        syslog(msg)
        return 99 # illegal parameters or file bigger than stated during download resume

    req = 'http://'+SUPPORTHOST+'/'+filename
    pullheaders={'Range': 'bytes=%s-' % (start)} # with requests
    
    msg='trying to retrieve file '+SUPPORTHOST+'/'+filename+' from byte '+str(start)+' using '+repr(pullheaders)
    print(msg)
    syslog(msg)
    try:
        response = requests.get(req, headers=pullheaders) # with python3
        output = open(filepart,'wb')
        output.write(response.content)
        output.close()
    except:
        msg='pull: partial or failed download of temporary file '+filepart+' '+str(sys.exc_info()[1])
        print(msg)
        syslog(msg)
        #traceback.print_exc()
        
    try:
        dnsize=os.stat(filepart)[6]  # int(float(subexec('ls -l '+filename,1).split(' ')[4]))
    except:
        msg='pull: got no size for file '+os.getcwd()+'/'+filepart+' '+str(sys.exc_info()[1])
        print(msg)
        syslog(msg)
        #traceback.print_exc()
        oksofar=0

    if dnsize == filesize: # ok
        msg='pull: file '+filename+' download OK, size '+str(dnsize)
        TCW[2]=TCW[2]+dnsize # adding tcp_in volume to the traffic counter. failed trial not to be counted? partials will add up to the same number anyway.
        print(msg)
        syslog(msg)

        try:
            os.rename(filename, filebak) # keep the previous version if exists
            msg='renamed '+filename+' to '+filebak
        except:
            #traceback.print_exc()
            msg='FAILED to rename '+filename+' to '+filebak+' '+str(sys.exc_info()[1])
            print(msg)
            syslog(msg)
            oksofar=0

        print(msg)
        syslog(msg)

        try:
            os.rename(filepart, filename) #rename filepart to filename2
            msg='renamed '+filepart+' to '+filename
        except:
            msg='FAILED to rename '+filepart+' to '+filename+' '+str(sys.exc_info()[1])
            print(msg)
            syslog(msg)
            oksofar=0
            #traceback.print_exc()
        print(msg)
        syslog(msg)

        if oksofar == 0: # trouble, exit
            return 1

        if '.gz' in filename: # lets unpack too
            filename2=filename.replace('.gz','')
            try:
                os.rename(filename2, filename2+'.bak') # keep the previous versioon if exists
            except:
                #traceback.print_exc()
                pass

            try:
                f = gzip.open(filename,'rb')
                output = open(filename2,'wb')
                output.write(f.read());
                output.close() # file with filename2 created
                #msg='pull: gz file '+filename+' unzipped to '+filename2+', previous file kept as '+filebak
            except:
                os.rename(filename2+'.bak', filename2) # restore the previous versioon if unzip failed
                msg='pull: file '+filename+' unzipping failure, previous file '+filename2+' restored. '+str(sys.exc_info()[1])
                #traceback.print_exc()
                print(msg)
                syslog(msg)
                return 1

        if '.tgz' in filename: # possibly contains a directory
            try:
                f = tarfile.open(filename,'r')
                f.extractall() # extract all into the current directory
                f.close()
                #msg='pull: tgz file '+filename+' successfully unpacked'
            except:
                msg='pull: tgz file '+filename+' unpacking failure! '+str(sys.exc_info()[1])
                #traceback.print_exc()
                print(msg)
                syslog(msg)
                return 1

        # temporarely switching off this chmod feature, failing!!
        #if '.py' in filename2 or '.sh' in filename2: # make it executable, only works with gzipped files!
        #    try:
        #        st = os.stat('filename2')
        #        os.chmod(filename2, st.st_mode | stat.S_IEXEC) # add +x for the owner
        #        msg='made the pulled file executable'
        #        print(msg)
          #      syslog(msg)
         #       return 0
        #    except:
        #        msg='FAILED to make pulled file executable!'
        #        print(msg)
        ##        syslog(msg)
        #        traceback.print_exc()
        #        return 99
        
        return 0
        
    else:
        if dnsize<filesize:
            msg='pull: file '+filename+' received partially with size '+str(dnsize)
            print(msg)
            syslog(msg)
            return 1 # next try will continue 
        else:
            msg='pull: file '+filename+' received larger than unexpected, in size '+str(dnsize)
            TCW[2]=TCW[2]+dnsize # adding tcp_in volume to the traffic counter
            print(msg)
            syslog(msg)
            return 99

# def pull() end. if it was py, reboot should follow. if it was sql, table reread must de done.




def socket_restart(): # close and open tcpsocket
    global tcpaddr, tcpport, tcpsocket, tcperr

    try: # close if opened
        #print 'closing tcp socket'
        tcpsocket.close()
        time.sleep(1)

    except:
        msg='tcp socket was not open '+str(sys.exc_info()[1])
        print(msg)
        syslog(msg)
        #traceback.print_exc() # debug

    # open a new socket
    try:
        print('opening tcp socket to modbusproxy,',tcpaddr, tcpport)
        tcpsocket = socket(AF_INET,SOCK_STREAM) # tcp / must be reopened if pipe broken, no reusage
        #tcpsocket = socket.socket(AF_INET,SOCK_STREAM) # tcp / must be reopened if pipe broken, no reusage
        tcpsocket.settimeout(5) #  conn timeout for modbusproxy. ready defines another (shorter) timeout after sending!
        tcpsocket.connect((tcpaddr, tcpport)) # leave it connected
        msg='modbusproxy (re)connected at '+str(int(ts))
        print(msg)
        sys.stdout.flush()
        syslog(msg) # log message to file
        #tcperr=0
        return 0

    except:
        msg='modbusproxy reconnection failed '+str(sys.exc_info()[1])
        print(msg)
        syslog(msg) # log message to file
        time.sleep(1)
        return 1




def stderr(message): # for android only? from entry.py of mariusz
    #import sys # already imported
    sys.stderr.write('%s\n' % message)




def array2regvalue(array,reg,stamax): # for reporting variables in arrays as message members together with status, for data not found in channel tables
    member=0
    status=0 # based on value members
    if stamax>2:
        stamax=2 # 2 is max allowed status for nagios
    output=reg+':' # string
    for member in range(len(array)): # 0 1 2 3
        if output.split(':')[1] != '': # there are something in sendstring already
            output=output+' '
        output=output+str(array[member])
        #print 'array2regvalue output',output # debug
        if array[member]>status: #
            status=array[member]
    if status>stamax:
        status=stamax #
    output=output+'\n'+reg[:-1]+'S:'+str(status)+'\n'
    return output

    
    
def logcat_dumpsend(): # execute logcat dump and push
    global ts 
    try:
        #filename='/sdcard/sl4a/scripts/d4c/'+str(int(ts))+'.log' # file to dump logcat_last
        filename=str(int(ts))+'.log' # file to dump logcat, without long path
        returncode=subexec(['/system/bin/logcat','-v','time','-df',filename],0) # creates a log file
        # if the resulting file exists, pack and push it
        if returncode == 0:
            returncode=push(filename) # gz is created on the way, includes path!
            if returncode == 0:
                print("file",filename,"successfully pushed")
                os.remove(filename+'.gz') # delete the successfully uploaded gz, no unpacked file left
            else:
                print(" pushing file",filename,"FAILED!")
            time.sleep(6)
            
    except:
        msg='logcat_dumpsend() FAILED: ' +str(sys.exc_info()[1])
        print(msg)
        syslog(msg)
        time.sleep(3)
    
    try:
        os.rename(filename, 'logcat_last.log') # keep the last log only
    except:
        type, value, trace = sys.exc_info()
        #traceback.print_exc()
        print(type,value,trace)
        sys.stdout.flush()
        time.sleep(3)
        
    return returncode


def setbit_dochannels(bit, value, mba = 1, regadd = 0):  # to get set coil functionality. mba and regadd may be skipped if no extensions in use!
    Cmd="update dochannels set value = '"+str(value)+"' where mba='"+str(mba)+"' and regadd='"+str(regadd)+"' and bit='"+str(bit)+"'"
    #print(Cmd) # debug
    try:
        conn3.execute(Cmd)
        conn3.commit()
        msg='output bit '+str(bit)+' set to '+str(value)+' in table dochannels'
        print(msg)
        syslog(msg)
        return 0
    except:
        msg='output bit '+str(bit)+' setting to '+str(value)+' in table dochannels FAILED! '+str(sys.exc_info()[1])
        print(msg)
        syslog(msg)
        return 1


def bit_replace(word,bit,value): # changing word with single bit value
    #print('word to be modified',format("%04x" % word))#bit_replace(255,0,0) # 254
    #bit_replace(255,7,0) # 127
    #bit_replace(0,15,1) # 32k
    #bit_replace(0,7,1) # 128
    #print('bit_replace var: ',format("%04x" % word),bit,value,format("%04x" % ((word & (65535 - 2**bit)) + (value<<bit)))) # debug
    return ((word & (65535 - 2**bit)) + (value<<bit))
    

def get_network(interface):  # check and change if needed mac and ip. FIX parameter to subexec!
    global ts, sendstring, mac
    #mac_ip=subexec(['/root/d4c/getnetwork.sh',interface],1).decode("utf-8").split(' ') # returns [maci, ip] currently in use  # kuidas param anti?? annab vea
    #mac_ip=subexec('/root/d4c/getnetwork.sh',1).decode("utf-8").split(' ') # returns [maci, ip] currently in use
    mac_ip=subexec('./getnetwork.sh',1).decode("utf-8").split(' ') # returns [maci, ip], current directory
    mac_ip[1]=mac_ip[1].split('/')[0] # remove trailing '/24\n' from ip_addr part in this mac_ip tuple
        
    print('mac,ip',repr(mac_ip))
    return mac_ip  #  tuple

    
    
def change_setup(register,value):  # iga muutus omaette transaktsioonina
    global ts
    print('setup change started for',sregister,svalue,', setup_change so far',setup_change)
    sCmd="BEGIN IMMEDIATE TRANSACTION" # setup table. there may be no setup changes, no need for empty transactions
    try:
        conn4.execute(sCmd) # setup transaction start
        sCmd="update setup set value='"+str(svalue)+"', ts='"+str(int(ts))+"' where register='"+sregister+"'" # update only, no insert here!
        print(sCmd)
        syslog(sCmd) # debug
        conn4.execute(sCmd) # table asetup/setup
        conn4.commit() # end transaction
        print('setup change done for',sregister,svalue)
        return 0
    except: #if not succcessful, then not a valid setup message
        msg='setup change problem, possibly the assumed setup register '+sregister+' not found in setup table! '+str(sys.exc_info()[1])
        print(msg)
        syslog(msg)
        time.sleep(1)
        return 1
        


def restore_counter(register,value,counter_row): # counter volumes to be restored - service names and counters should match in counters table!
    msg='going to set counter based on svc '+register+' value '+value+' '+repr(counter_row) # debug
    print(msg) # debug
    syslog(msg)
    readbackfail=0
    
    try:
        mba=int(float(counter_row[0]))
        regadd=int(float(counter_row[1])) # MSW of the counter, number of words defined by wcount
        member=int(float(counter_row[2]))
        wcount=counter_row[3] # integer already in table
        x2=int(float(counter_row[4])) # conversion from
        y2=int(float(counter_row[5])) # conversion to, assuming zero is at zero for both input and output of the conversion
        values=value.split(' ') # array
        print('restore_counter() values '+repr(values)) # debug
        for memb in range(len(values)): # members in value are related to various counters
            #print('restore_counter(): trying to match member '+str(memb+1)) # debug 
            #for w in range(wcount): # possible future improvement, for counter word length above 2
            if memb+1 == member: # member numbering in counters table start from 1, not 0
                value=int((int(float(values[memb])*(x2/y2))&4294901760)/65536)
                msg='restore_counter() word value '+str(value)+' to be written into mba '+str(mba)+' regadd '+str(regadd)
                print(msg)
                syslog(msg)
                client.write_register(address=regadd, value=value, unit=mba) # MSW
                time.sleep(0.1)
                result=client.read_holding_registers(address=regadd+1, count=1, unit=mba)
                realvalue=result.registers[0]
                if realvalue == value:
                    print('MSW OK, value '+str(value)+' (hex '+format("%04x" % realvalue))
                else:
                    print('restore_counter() MSW BAD! got '+str(realvalue)+' (hex '+format("%04x" % realvalue)+') instead of '+str(value))
                    readbackfail=1
                time.sleep(0.1)
                value=int((int(float(values[memb])*(x2/y2)))&65535)
                msg='restore_counter() word value '+str(value)+' to be written into mba '+str(mba)+' regadd '+str(regadd+1)
                print(msg)
                syslog(msg)
                client.write_register(address=regadd+1, value=value, unit=mba) # LSW
                time.sleep(0.1)
                result=client.read_holding_registers(address=regadd+1, count=1, unit=mba)
                realvalue=result.registers[0]
                if realvalue == value:
                    print('LSW OK, value '+str(value)+' (hex '+format("%04x" % realvalue))
                else:
                    print('restore_counter() LSW BAD! got '+str(realvalue)+' (hex '+format("%04x" % realvalue)+') instead of '+str(value))
                    readbackfail=1
                time.sleep(0.1)

                read_counters() # debug test
                
                if readbackfail == 0: # checking the result
                    msg='successfully restored member '+str(member)+' value for counter '+str(mba)+'.'+str(regadd)+' for '+register
                    print(msg)
                    syslog(msg)
                    return 0
                else:
                    msg='value check FAILED after counter '+str(regadd)+' writing!' 
    except:
        #traceback.print_exc()
        msg='FAILED to restore counter for '+register+', '+str(str(sys.exc_info()[1]))
        print(msg) # debug, is this the same as traceback()?
        
    print(msg)
    syslog(msg)
    return 1
    


def report_free(path='./'): #returns free MB and percentage of given fs (can be current fs './' as well)
    info=os.statvfs(path)
    return info[3]*info[1]/1048576,100*info[3]/info[2] # returns free [MB,%]



                                        
# ### procedures end ############################################






# #############################################################
# #################### INIT ###################################
# #############################################################


import time
import datetime

#import sqlite3 # in android
#from pysqlite2 import dbapi2 as sqlite3 # obsolete

import os
import stat
import sys
import traceback
import subprocess
DEVNULL = open(os.devnull, 'wb') # on python 2.x

#import socket
#from socket import AF_INET, SOCK_DGRAM
from socket import *
import string

#import syslog # only for linux, not android (logcat forwarded to external syslog there)
import select
#import urllib2 # requests should be enough
import gzip
import tarfile
import requests # for file upload
#import logging
import glob

#from pymodbus.client.sync import ModbusTcpClient
#from pymodbus.register_read_message import *

host='0.0.0.0' # own ip for udp comm, should always work to send/receive udp data to the server, without socket binding
tcpaddr=''
tcpport=0
tcpmode=1 # if 0, then no tcpmodbus header needed. crc is never needed.
OSTYPE='' # linux or not?

MBsta=[0,0,0,0] # modbus device states (ability to communicate). 1 = crc error, 2=device error, 3=usb error, 4 proxy conn error
MBoldsta=[1,0,0,0] # previous value, begin with no usb conn
MBerr=[0,0,0,0] # counts the consequtive errors for modbus units (slaves)
TCW=[0,0,0,0] # array of communication volumes (UDPin, UDPout, TCPin, TCPout), data in bytes. can be restored from server

lockaddr=('127.0.0.1',44444) # only one instance can bind to it, used for locking!
UDPlockSock = socket(AF_INET,SOCK_DGRAM)
UDPlockSock.settimeout(None)

loghost = '255.255.255.255' # find out the wlan ip and use x.x.x.255 as the syslog server ip for broadcast. should work for hotspot too.
logport=514
logaddr=(loghost,logport) # global variable for syslog()
UDPlogSock = socket(AF_INET,SOCK_DGRAM)
UDPlogSock.settimeout(None) # using for syslog messaging
UDPlogSock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1) # et broadcast lubada

appdelay=30 # 120 # 1s appmain execution interval, reporting all analogue values and counters. NOT DI channels!!

retrydelay=5 # after 5 s resend is possible if row still in buffer
renotifydelay=240 # send again the DI values after that time period even if not changed. but the changed di and do values are sent immediately!

sendstring="" # datagram to be sent
lisa="" # multivalue string member
inumm=1 # datagram number 1..65k
inum=0 # returned datagram number to be used in send buffer cleaning
blocklimit=3 # if block reached this then do not send
TODO='' # signal to remember things to do
tcperr=0
#ts=0 # timestamp s
ts_created=0 # service creation and inserting into buff2server table
ts_tried=0 # timestamp for last send trial
ts_inumm=0 # inumm changed timestamp. to be increased if tyhe same for too long?
setup_change=0 # flag setup change
respcode=0 # return code  0=ok, 1=tmp failure, 2=lost socket
tcpconnfail=0 # flag about proxy conn
ts_interval1=0 # timestamp of trying to restore modbuysproxy conn interval 1
interval1delay=5 # try to restore modbusproxy connection once in this time period if conn lost
stop=0 # reboot flag
LOG=sys.argv[0].replace('.py','.log') # should appear in the current directory
filename='' # for pull()
tablename='' # for sqlread()
filepart=''
dnsize=0
filesize=0
todocode=0 # return code
#pullcode=0 # return code
startnum=0 # file download pointer
pulltry=1 # counter for pull() retries
cfgnum=0 # config retry counter
ts=time.mktime(datetime.datetime.now().timetuple()) #seconds now, with comma
ts_boot=int(ts) # startimise aeg, UPV jaoks
ts_lastappmain=ts # timestamp for last appmain run
ts_lastnotify=ts-200 # force sooner reporting after boot
ts_udpsent=ts # last udp message sent, not received!
ts_udpgot=ts # udp last received
ts_gsmbreak=0
# the timestamps above cannot be 0 initially! some will start full reboot!

mac='000000000000' # initial mac to contact the server in case of no valid setup
odiword=-1 # previous di word, on startup do not use
joru1=''
joru2=''
fore=''
mbcommresult=0 # modbus slave operation result
err_aichannels=0 # error counters to sqlread or even stop and dbREcreate
err_dichannels=0
err_counters=0
err_proxy=0
ProxyState=1 # 0 if connected and responsive
USBstate=255 # 1 if running
USBoldstate=255
USBuptime=0 # readable from modbusproxy
PhoneUptime=0 # readable from modbusproxy
ProxyUptime=0 # readable from modbusproxy
AppUptime=0 # ts_boot alusel, py rakenduse oma
GSMlevel=0 # 0..31, 99?
WLANlevel=0
WLANip=''
ProxyVersion=''
UUID=''
SIMserial=''
BattVoltage=0 # starting from modbusproxy version from 08.07.2013
BattTemperature=0
BattStatus=0
BattPlugged=0
BattHealth=0
BattCharge=0
ts_USBrun=0 # timestamp to start running usb
W272_dict={} # power-on values for modbus slaves. mba:regvalue
gsmbreak=0 # 1 if powerbreak ongoing, do bit 15
ts_proxygot=ts

#from pymodbus.client.sync import ModbusTcpClient as ModbusClient
#from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.register_read_message import *

buf=1024 # udb input
shost="46.183.73.35" # udp listening server - should be configurable! fallback address here?
udpport=44445 # fallback port here?
saddr=(shost,udpport) # mon server
# shost ja udpport voiks ka parameetritega olla.


print("SERVER saddr",saddr,', MODBUSPROXY tcpaddr',tcpaddr,tcpport)

sys.stdout.flush() # to see the print lines above in log
time.sleep(1) # start

tcpwait=2 # alla 0.8 ei tasu, see on proxy tout...  #0.3 # how long to wait for an answer from modbusTCP socket

UDPSock = socket(AF_INET,SOCK_DGRAM)
UDPSock.settimeout(1) # UDPSock.settimeout(0.1) # (0.1) use 1 or more for testing # in () timeout to wait for data from server. defines alsomain loop interval / execution speed!!

host='0.0.0.0' # own ip for udp, should always work, no need for socket binding
addr = (host,udpport) # itself

#database related init
import sqlite3

conn1tables=['buff2server']
conn3tables=['aichannels','dichannels','dochannels','counters','chantypes','devices','aochannels']
conn4tables=['setup']
try:
    conn1= sqlite3.connect(':memory:')  # buffer data from modbus registers, unsent or to be resent
    #  #conn1= sqlite3.connect(':memory:', check_same_thread = False)  # 
    conn3= sqlite3.connect(':memory:')   # modbus register related tables / sometimes locked!!
    #  #conn3a= sqlite3.connect(':memory:', check_same_thread = False)  # one connnection per cursor should be better, see 
             # http://stackoverflow.com/questions/2844267/inserting-rows-while-fetchingfrom-another-table-in-sqlite
    conn4= sqlite3.connect(':memory:')  # setup table, only for update, NO INSERT! 2 s timeout, ends with execution stop.
    #conn1 = sqlite3.connect('/mnt/ramdisk/modbus.db1',2) # proovime failidega, ehk on kiirem kui maluga... 
    #conn3 = sqlite3.connect('/mnt/ramdisk/modbus.db3',2)
    #conn4 = sqlite3.connect('/mnt/ramdisk/modbus.db4',2) 
    #conn1 = sqlite3.connect('./buff2server',2) # proovime failidega, ehk on kiirem kui maluga... 
    #conn3 = sqlite3.connect('./modbus_channels',2)
    #conn4 = sqlite3.connect('./asetup',2) 
except:
    msg=='sqlite connection problem '+str(sys.exc_info()[1])
    print(msg)
    syslog(msg)
    time.sleep(3)

cursor1=conn1.cursor() # cursors to read data from tables
cursor3=conn3.cursor()
cursor3a=conn3.cursor() # the second cursor for the same connection
#cursor3a=conn3a.cursor() # ei saa nii !
cursor4=conn4.cursor()

    


try: # is it android? using modbustcp then
    import android
    droid = android.Android()
    from android_context import Context
    import android_network # android_network.py and android_utils.py must be present!

    import os.path
    from pymodbus.client.sync import ModbusTcpClient as ModbusClient # modbusTCP

    OSTYPE='android'
    
    tcpport=10502 # modbusproxy
    tcpaddr="127.0.0.1" # localhost ip to use for modbusproxy
    client = ModbusClient(host=tcpaddr, port=tcpport)
    
    import BeautifulSoup # ?
    #import gdata.docs.service
    import termios
    os.chdir('/sdcard/sl4a/scripts/d4c')
    
    msg='running on android, current directory '+os.getcwd()
    print(msg)
    syslog(msg)
    
except: # some linux
    tcpport=0 # modbus rtu
    
    if 'ARCH' in os.uname()[2]: # if os.environ['PWD'] == '/root':   # olinuxino 
        OSTYPE='archlinux'
        from pymodbus.client.sync import ModbusSerialClient as ModbusClient # using serial modbusRTU
        client = ModbusClient(method='rtu', stopbits=1, bytesize=8, parity='E', baudrate=19200, timeout=0.3, port='/dev/ttyAPP0') # 0.2 oli vahe, lollistus vahel ja jai lolliks
        
        print('running on archlinux')
        os.chdir('/root/d4c') # OLINUXINO
        
        from droidcontroller.indata import InData
        from droidcontroller.comm_system import CommSystem
        from droidcontroller.comm_modbus import CommModbus
        from droidcontroller.webserver import WebServer
        
        tcpport=0 # using pyserial
        tcpaddr='' # no modbustcp address given
        
    elif 'techbase' in os.environ['HOSTNAME']: # npe
        OSTYPE='techbaselinux'
        # kumb (rtu voi tcp) importida, vajab katsetamist
        from pymodbus.client.sync import ModbusSerialClient as ModbusClient # using serial modbusRTU
        client = ModbusClient(method='rtu', stopbits=1, bytesize=8, parity='E', baudrate=19200, timeout=0.3, port='/dev/ttyS3') # 0.2 oli vahe, lollistus vahel ja jai lolliks
        
    else: # ei ole ei android, arch ega techbase
        #OSTYPE=os.environ['OSTYPE'] #  == 'linux': # running on linux, not android
        OSTYPE='linux' # generic
        from pymodbus.client.sync import ModbusTcpClient as ModbusClient # modbusTCP
        client = ModbusClient(host=tcpaddr, port=tcpport) # TCP
        #client = ModbusClient(method='rtu', stopbits=1, bytesize=8, parity='E', baudrate=19200, timeout=0.2, port='/dev/ttyS0') # change if needed
        
        print('running on generic linux')   # argumente vaja!

        try:
            print(sys.argv[1],sys.argv[2]) # <addr:ip> <sql_dir>
        except:
            print('parameters (socket and sql_dir) needed to run on linux!')
            #traceback.print_exc()
            sys.exit()

        try:
            tcpport=int(sys.argv[1].split(':')[1]) # tcpport=502 # std modbusTCP port # set before
            tcpaddr=sys.argv[1].split(':')[0] # "10.0.0.11" # ip to use for modbusTCP
            print('using',tcpaddr,tcpport)
        except:
            msg='invalid address:port '+tcpaddr+':'+str(tcpport)+'  '+str(sys.exc_info()[1])
            print(msg)
            syslog(msg)
            #traceback.print_exc()
            sys.exit()

        #from sqlite3 import dbapi2 as sqlite3 # in linux
        os.chdir(sys.argv[2]) # ('/srv/scada/acomm/sql')
        print(os.getcwd())
           
            
    
print('current dir',os.getcwd())
#create tables from sql files
for table in conn1tables:
    print('trying to read',table)
    sqlread(table)
for table in conn3tables:
    print('trying to read',table)
    sqlread(table)
for table in conn4tables:
    print('trying to read',table)
    sqlread(table)

#databases are created now, needed for setup handling
#if OSTYPE == 'archlinux':    #mac=getset_network('ether')[0] # get conf and set mac,ip, returns mac and ip in use
#    getset_network('ether') # sets mac too  NO NO!

        
        
try: # is another copy of this script already running?
    UDPlockSock.bind(lockaddr)
    msg='\n'+APVER+' starting at '+str(int(ts))
    syslog(msg)
    print(msg)
    sys.stdout.flush()
    #time.sleep(2)

except: # lock active
    stop=1 # exiting due to lock
    msg='this script will be stopped due to udp lock already active'
    syslog(msg) # log message to file
    print(msg)
    UDPlockSock.close()
    # mark this event into the log



#if tcpport != 0: # modbusTCP
#    client = ModbusClient(host=tcpaddr, port=tcpport)
#else: # modbusRTU
#    client = ModbusClient(method='rtu', stopbits=1, bytesize=8, parity='E', baudrate=19200, timeout=0.2, port='/dev/ttyAPP0')





if stop == 0: # lock ok
    
    #create sqlite connections (while located in sql_dir)
    
    # test if table setup is preset 
    #Cmd='select * from setup'
    #print(Cmd)
    #cursor4.execute(Cmd)
    #for row in cursor4:
    #    print(repr(row))

    # delete unsent rows older than 60 s
    Cmd1="DELETE from buff2server where ts_created+0<"+str(ts)+"-60" # kustutakse koik varem kui ninute tagasi loodud
    conn1.execute(Cmd1)
    Cmd1="SELECT count(sta_reg) from buff2server" # kustutakse koik varem kui ninute tagasi loodud
    cursor1.execute(Cmd1)
    
    for row in cursor1:
        print(row[0],'svc records to be sent currently in buffer')
    time.sleep(1) # buff2server delete old if any
    conn1.commit() # kohe peale execute techbase sqlite jamas...

    if tcpport != 0:  # modbusTCP
        msg='waiting for modbusproxy connection'
        print(msg)
        syslog(msg)
        while socket_restart == 0: # endless retry
            tcperr = tcperr + 1
            if tcperr%10 == 0:
                msg='no tcp connection to modbusproxy'
                print(msg)
                syslog(msg)
                #droid.ttsSpeak(msg) # does not work with every language settings!
            time.sleep(1)

    # try to read the wlan mac and sim card serial from the modbusproxy. then the setup can be sent to the server without reading the.
    if OSTYPE == 'android':
        ProxyState=read_proxy('all') # wlan mac and a few other things to find out / getting here only if tcp conn ok
        if ProxyState == 0: # ok
            msg='proxy connected and readable'
            sendstring=sendstring+'S310:'+mac+'\nS300:'+UUID+'\nS0:'+ProxyVersion+'\nS302:'+SIMserial+'\n'
            udpsend(0,int(ts)) # no need for ack, thus inumm=0
            
            #
        
        else:
            msg='proxy CANNOT be connected and read!'

        print(msg)
        syslog(msg)
        #report_setup() # get the mac from setup - not from setup!
        tcperr = 0 # ??
    else: # linux eth? mac needed   //  assuming archlinux
        mac=get_network('ether')[0] # 
        print('mac from network configuration',mac)

    
    SUPPORTHOST='www.itvilla.ee/support/pyapp/'+mac # could be in setup.sql, but safer this way

    # start modbus coomunication and chk/chg slave configuration ###
    try:
        client.read_holding_registers(address=regadd, count=2, unit=mba) # likely to fail, if first in 30s
    except:
        pass
        
    while channelconfig() > 0 and cfgnum<5: # do the setup but not for more than 5 times
        msg='attempt no '+str(cfgnum+1)+' of 5 to configure modbus slave devices'
        print(msg)
        syslog(msg)
        cfgnum=cfgnum+1
        time.sleep(2)

    if cfgnum == 5: # failed setup...
        msg='channelconfig() failure! giving up on try '+str(cfgnum)
    else:
        msg='channelconfig() success on try '+str(cfgnum)
        MBsta=[0,0,0,0]
    print(msg)
    syslog(msg)
    sys.stdout.flush()
    time.sleep(1)
            
            
    sendstring=array2regvalue(MBsta,'EXW',2) # adding EXW, EXS to sendstring based on MBsta[]
    sendstring=sendstring+"UPV:0\nUPS:1\nTCW:?\n" # restoring traffic volume from server in case of restart. need to reset it in the beginning of the month.
    udpsend(0,int(ts)) # version data  / no need for ack and deletion from buff2server

    sys.stdout.flush()
    time.sleep(1)

    print('reporting setup') # must be done twice, the second can be more successful with connection and mac known (tmp hack)
    report_setup() # sending some data from asetup/setup to server on startup
    report_channelconfig() # sending some data from modbuschannels/*channels to server on startup
    msg='starting the main loop' #  at '+str(int(ts))+'. mac '+mac+', saddr '+str(repr(saddr))+', modbusproxy '+tcpaddr+':'+str(tcpport)
    print(msg)
    syslog(msg) # log message to file
    if OSTYPE == 'android':
        droid.ttsSpeak(msg)


ts=time.mktime(datetime.datetime.now().timetuple()) #seconds now, once again
#setbit_dochannels(15,1) # to be sure that gsm power (do8) is up - should be based on register 272, but may be down if program crashed during power break
ts_udpsent=ts # last successful udp send timeput counting starts now

      
while stop == 0: # ################  MAIN LOOP BEGIN  ############################################################
    ts=time.mktime(datetime.datetime.now().timetuple()) #seconds now, with comma
    MONTS=str(int(ts)) # as integer, without comma
    data='' # avoid old data to be processed again

    try: # if anything comes into udp buffer in 0.1s
        rdata,raddr = UDPSock.recvfrom(buf)
        data=rdata.decode("utf-8") # python3 related need due to mac in hex
        
        #print('got from monitoring server',repr(raddr),repr(data)) # debug
        
        TCW[0]=TCW[0]+len(data) # adding top the incoming UDP byte counter

        #print("got message from addr ",raddr," at ",ts,":",data.replace('\n', ' ')) # showing datagram members received on one line, debug
        #syslog.syslog('<= '+data.replace('\n', ' ')) # also to syslog (communication with server only)

        if (int(raddr[1]) < 1 or int(raddr[1]) > 65536):
            msg='illegal source port '+str(raddr[1])+' in the message received from '+raddr[0]
            print(msg)
            syslog(msg)

        if raddr[0] != shost:
            msg='illegal sender '+str(raddr[0])+' of message: '+data+' at '+str(int(ts))  # ignore the data received!
            print(msg)
            syslog(msg)
            data='' # data destroy

        if "id:" in data: # mac aadress
            id=data[data.find("id:")+3:].splitlines()[0]
            if id != mac:
                print("invalid id in server message from ", addr[0]) # this is not for us
                data='' # destroy the datagram, could be for another controller behind the same connection
            else:
                ts_udpgot=ts # timestamp of last udp received

            Cmd1=""
            Cmd2=""

            if "in:" in data:
                #print 'found in: in the incoming message' # #lines=data[data.find("in:")+3:].splitlines()   # vaikesed tahed
                inum=eval(data[data.find("in:")+3:].splitlines()[0].split(',')[0]) # loodaks integerit
                if inum >= 0 and inum<65536:  # valid inum, response to message sent if 1...65535. datagram including "in:0" is a server initiated "fast communication" message
                    #print "found valid inum",inum,"in the incoming message " # temporary
                    msg='got ack '+str(inum)+' in message: '+data.replace('\n',' ')
                    print(msg)
                    syslog(msg)

                    #try: # commLED off due to valid ack
                        #client.write_register(address=0, value=0, unit=1) # so far there are no other than do7 and do8 in use
                        #setbit_dochannels(14,0) # commLED OFF
                    #except:
                        #pass
                        
                    Cmd="BEGIN IMMEDIATE TRANSACTION" # buff2server, to delete acknowledged rows from the buffer
                    conn1.execute(Cmd) # buff2server ack transactioni algus, loeme ja kustutame saadetud read

                    Cmd1="SELECT * from buff2server WHERE mac='"+id+"' and inum='"+str(inum)+"'" # matching lines to be moved into sent2server
                    #print "mark as sent: sent Cmd1=",Cmd1
                    Cmd3="DELETE from buff2server WHERE mac='"+id+"' and inum='"+str(inum)+"'"  # deleting all rows where inum matches server ack
                    # siia voiks  lisada ka liiga vanade kirjete automaatne kustutamine. kui ei saa, siis ei saa!
                    #print "delete: Cmd3=",Cmd3
                    try:
                        cursor1.execute(Cmd1) # selected
                        conn1.execute(Cmd3) # deleted
                    except:
                        msg='problem with '+Cmd3+' '+str(sys.exc_info()[1])
                        print(msg)
                        syslog(msg)
                        time.sleep(1)
                        #

                    conn1.commit() # buff2server transaction end
                    #print "table buff2server cleaning off the members of the message sent with inum",inum,"done" # debug



                    #Cmd="BEGIN IMMEDIATE TRANSACTION" # sent2server transaction / switched off 16.03.2013
                    #conn2.execute(Cmd) #

                    #for row in cursor1: # this is from buff2server
                    #    print "row from buff2server:",repr(row) # for every row in buff2server with given inum add a row into sent2server
                    #    Cmd2="INSERT into sent2server values ('"+row[0]+"','"+row[1]+"','"+row[2]+"','"+row[3]+"','"+row[4]+"','"+row[5]+"','"+row[6]+"','"+row[7]+"','"+row[8]+"','"+row[9]+"','"+row[10]+"','"+MONTS+"')" # ts_ack added
                    #    print "Cmd2=",Cmd2
                     #   try:
                      #      conn2.execute(Cmd2) # add into table sent2server

                       # except:
                        #    print "trouble with",Cmd2
                         #   traceback.print_exc()

                    #conn2.commit() # sent2buffer transaction end - successful communication log, needs to truncated some time!
                    #print "added the members of the message sent with inum",inum,"into sent2server table"



                    #print 'wait a little...' # give some time for sqlite?
                    #time.sleep(1) # temporary test

                    #temporary check = are the rows really deleted from buff2server and moved into sent2server?
                    Cmd1="SELECT count(inum) from buff2server WHERE mac='"+id+"' and inum='"+str(inum)+"'"
                    #print Cmd1  # temporary
                    try:
                        cursor1.execute(Cmd1)
                        conn1.commit()
                        for row in cursor1: # should be one row only
                            rowcount1=row[0] #number of rows still there with given inum
                            if row[0]>0:
                                print("ack ERROR: there are still",row[0],"rows in buff2server with inum",inum)
                            #else:
                                #print ', rows with inum',inum,'deleted from buff2server' # debug

                    except:
                        msg='trouble with '+Cmd1+': '+str(sys.exc_info()[1])
                        print(msg)
                        syslog(msg)
                        traceback.print_exc()
                        #sys.stdout.flush()
                        time.sleep(1)


            # #### possible SETUP information contained in received from server message? ########
            # no insert into setup, only update allowed!
            lines=data.splitlines() # all members as pieces again

            setup_change=0 # flag to detect possible setup changes
            for i in range(len(lines)): # looking into every member of incoming message
                if ":" in lines[i]:
                    #print "   "+lines[i]
                    line = lines[i].split(':')
                    sregister = line[0] # setup reg name
                    svalue = line[1] # setup reg value
                    if sregister != 'in' and sregister != 'id': # others may be setup or command (cmd:)
                        msg='got setup/cmd reg:val '+sregister+':'+svalue  # need to reply in order to avoid retransmits of the command(s)
                        print(msg)
                        syslog(msg)
                        sendstring=sendstring+sregister+":"+svalue+"\n"  # add to the answer
                        udpsend(0,int(ts)) # send the response right away to avoid multiple retransmits
                        time.sleep(0.1)
                        if sregister != 'cmd': # can be variables to be saved into setup table or to be restored. do not accept any setup values that are not in there already!
                            if sregister[0] == 'W' or sregister[0] == 'B' or sregister[0] == 'S': # could be setup variable
                                if change_setup(sregister,svalue) == 0: # successful change in memory, not in file yet!
                                    setup_change = 1 # flag the change
                                    msg='setup changed, '+sregister+svalue
                                    print(msg)
                                    syslog(msg)
                                    
                            else: # sregister did not begin with W B S, some program variable to be restored?
                                if sregister == 'TCW': # traffic volumes to be restored
                                    if len(svalue.split(' ')) == 4: # member count for traffic: udpin, udpout, tcpin, tcpout in bytes
                                        for member in range(len(svalue.split(' '))): # 0 1 2 3
                                            TCW[member]=int(float(svalue.split(' ')[member]))
                                    msg='restored traffic volume array TCW to'+repr(TCW)
                                elif sregister == 'V1W': # vent setpoints, test
                                    if len(svalue.split(' ')) == 2: # 2 members
                                        for member in range(len(svalue.split(' '))): # 0 1 
                                            try:
                                                Cmd3="update aochannels SET value = '"+str(svalue.split(' ')[member])+"' where mba||regadd in \
                                                (select aochannels.mba||aochannels.regadd from aichannels LEFT join aochannels on \
                                                aichannels.mba = aochannels.mba and aichannels.regadd=aochannels.regadd where \
                                                aichannels.member='"+str(member+1)+"' and aichannels.val_reg='"+sregister+"')"
                                                conn3.execute(Cmd3)
                                                msg='vent setpoint '+str(member+1)+' is now '+str(svalue.split(' ')[member])
                                            except:
                                                #traceback.print_exc()
                                                msg='Cmd3 '+Cmd3+' failed! '+str(str(sys.exc_info()[1]))
                                                print(msg)
                                    
                                else: # got no svc variables
                                    msg=''
                                    
                                if len(msg)>0:
                                    print(msg)
                                    syslog(msg)

                                # counters restore
                                Cmd3="select mba,regadd,member,wcount,x2,y2 from counters where val_reg='"+sregister+"'"
                                cursor3.execute(Cmd3)
                                #print(Cmd3) # debug
                                conn3.commit()
                                for row in cursor3:
                                    #print('going to restore '+sregister+' based on '+repr(row)) # debug
                                    if restore_counter(sregister,svalue,row) == 0: # restoring the counter if match exists
                                        msg='successfully restored '+sregister+' to counter'
                                    else:
                                        msg='FAILED to restore '+sregister+' to counter'
                                    
                                    print(msg)
                                    syslog(msg)
                                    
                        else: # must be cmd, not to be saved into setup table
                            msg='remote command '+sregister+':'+svalue+' detected at '+str(int(ts))
                            print(msg)
                            syslog(msg)
                            if TODO == '': # no change if not empty
                                TODO=svalue # command content to be parsed and executed
                                print('TODO set to',TODO)
                            else:
                                print('could not set TODO to',svalue,', TODO still',TODO)

                    # all members that are not in or id were added to sendstring above!
                    if sendstring != '':
                        udpsend(0,int(ts))  # send back the ack for commands. this adds in and id always. no need for server ack, thus 0 instead of inumm

            if setup_change == 1: #there were some changes done  to setup, dump setup.sql!
                setup_change=0 #back to normal
                # dump asetup/setup setup into setup.sql  ####
                msg='going to dump setup into setup.sql'
                try:
                    with open('setup.sql', 'w') as f:
                        for line in conn4.iterdump(): # only one table, setup connected 
                            f.write('%s\n' % line)
                except:
                    msg='FAILURE dumping setup into setup.sql '+str(sys.exc_info()[1])
                    print(msg)
                    syslog(msg)
                    #traceback.print_exc()
                    
                print(msg)
                syslog(msg)
                
                TODO='VARLIST' # let's report the whole setup just in case due to change. not really needed.
                
        else: # illegal udp msg
            msg="got illegal message (no id) from "+str(addr)+" at "+str(int(ts))+": "+data.replace('\n',' ')  # missing mac
            print(msg)
            syslog(msg)
            data='' # destroy received data

    except:  # no new data in 0.1s waiting time
        #print '.',  #currently no udp response data on input, printing dot
        #traceback.print_exc() # debug
        
        unsent()  # delete from buff2server the services that are unsent for too long (3*renotifydelay)

        #something to do? chk udp communication first
        if ts - ts_udpsent > 900: # no udp comm possible for some reason, try to reboot the device
            TODO='FULLREBOOT' # send 255 666 dead or reboot on linux
            msg='trying full reboot to restore monitoring connectivity'
            syslog(msg) # log message to file
            print(msg)
            if OSTYPE == 'android':
                droid.ttsSpeak(msg)
                time.sleep(10)

        if ts - ts_udpgot > 100: # no udp response 
            print('last udp received',int(ts - ts_udpgot),'ago') # debug
            
        if OSTYPE != 'android' and (ts - ts_udpgot > 300):    # no break before 10 min comm loss #  > 600
            msg=''
            if (ts>ts_gsmbreak+300): # no reset immediately after reset , once in 15 min max # 900 normal
                #msg='trying gsmPWR break via 1.115 to restore monitoring connectivity'
                msg='NOT starting gsmbreak to restore monitoring connectivity'
                #setbit_dochannels(15,0) # break start, do8. optionally mba read can be set to something else than 1 0 by default!
                gsmbreak=1
                ts_gsmbreak = ts
                #client.write_register(address=115, value=5000, unit=1)  # pulse to gsmPWR, will be canceled by di/do sync!
                syslog(msg) # log message to file
                print(msg)

        if (ts>ts_gsmbreak+5) and gsmbreak == 1: # return from gsmbreak always whoever started it
            msg='ending gsmPWR break'
            gsmbreak=0
            #setbit_dochannels(15,1) # break end
            #msg='power for communication device restored'
            print(msg)
            #syslog(msg) # log message to file
                    
        if ts - ts_udpgot > 1800: # for 30 min no response from udpserver
            TODO='FULLREBOOT' # try if it helps. if send fails, after 300 s also full reboot
            msg='trying full reboot to restore monitoring connectivity'
            print(msg)
            syslog(msg)
            if OSTYPE == 'android':
                droid.ttsSpeak(msg)
                time.sleep(10)

        if OSTYPE == 'android' and (ts - ts_proxygot > 400): # proxy maha surnud? siis tee fullreboot, MITTE REBOOT! # 300 OLI LIIGA VAHE, PARANES ISE KOHE PEALE SEDA
            msg='going to full reboot due to proxy lost '+str(int(ts - ts_proxygot))+' seconds ago'
            print(msg,ts,ts_proxygot)
            syslog(msg) # ,ts,ts_proxygot)  # esialgu vaid 1 argument!
            droid.ttsSpeak(msg)
            time.sleep(1)
            TODO = 'FULLREBOOT'
            
    
        if TODO != '': # yes, it seems there is something to do
            todocode=todocode+1 # limit the retrycount
            print('going to execute cmd',TODO)
            
            if TODO == 'VARLIST':
                todocode=report_setup() # general setup from asetup/setup
                todocode=todocode+report_channelconfig() # iochannels setup from modbus_channels/dichannels, aichannels, counters* - last ytd
                if todocode == 0:
                    print(TODO,'execution success')
                    #TODO='' # do not do it here! see the if end
                    
            if TODO == 'REBOOT': # stop the application, not the system
                if OSTYPE == 'android' and ProxyState != 0: # EI TOHI!!!! proxy voib maas olla
                    todocode=1 # voimalik, et proxy surnud ja tuleks hoopis seda kaivitada
                else:
                    stop=1 
                    todocode=0
                    msg='stopping for script restart due to command'
                    print(msg)
                    syslog(msg) 
                    sys.stdout.flush()
                    if OSTYPE == 'android':
                        droid.ttsSpeak(msg)
                        time.sleep(10)
                time.sleep(1)

            if TODO == 'WLANON':
                todocode=0
                msg='wireless on due to command'
                print(msg)
                syslog(msg) # log message to file
                if OSTYPE == 'android':
                    try:
                        #print 'wifi state',droid.checkWifiState().result
                        droid.toggleWifiState(True)
                        todocode=0
                        droid.ttsSpeak(msg)
                        time.sleep(10)

                    except:
                        todocode=1

            if TODO == 'WLANOFF':
                todocode=0
                msg='wireless off due to command'
                print(msg)
                syslog(msg) # log message to file
                if OSTYPE == 'android':
                    try:
                        #print 'wifi state',droid.checkWifiState().result
                        droid.toggleWifiState(False)
                        todocode=0
                        droid.ttsSpeak(msg)
                        time.sleep(10)

                    except:
                        todocode=1

            if TODO == 'WLAN?': # finding the state, true or false as dnsize
                todocode=0
                msg='checking wireless state due to command'
                print(msg)
                syslog(msg) # log message to file
                if OSTYPE == 'android':
                    try:
                        dnsize=droid.checkWifiState().result
                        print('wlan state',dnsize)
                        todocode=0

                    except:
                        todocode=1
                        
            if TODO == 'GSMBREAK': # external router power break do8
                msg='power cut for communication device due to command'
                print(msg)
                syslog(msg) # log message to file
                #setbit_dochannels(15,0) # gsm power down, do8
                ts_gsmbreak = ts
                gsmbreak = 1
                todocode = 0
                
                
            if TODO.split(',')[0] == 'free': # finding the free MB and % of current or stated path, return values in ERV
                free=[]
                msg='checking free space due to command'
                print(msg)
                syslog(msg) # log message to file
                try:
                    free=free(TODO.split(',')[1]) # the parameter can be missing
                    todocode=0
                except:        
                    todocode=1


            if TODO == 'FULLREBOOT': # full reboot, NOT just the application. android as well!
                #stop=1 # cmd:FULLREBOOT
                try:
                    msg='started full reboot due to command' # 
                    syslog(msg)
                    print(msg)
                    if OSTYPE == 'android':
                        droid.ttsSpeak(msg)
                        time.sleep(10)
                        returncode=subexec(['su','-c','reboot'],0) # 2 channels for rebooting
                        todocode=0
                    else: # LINUX
                        print('going to reboot now!')
                        returncode=subexec(['reboot'],0) # linux
                        
                except:
                    todocode=1
                    msg='full reboot failed at '+str(int(ts))
                print(msg)
                syslog(msg) # log message to file

            if TODO == 'CONFIG': #
                todocode=channelconfig() # configure modbus registers according to W... data in setup

            if TODO == 'LOGCAT': #
                if OSTYPE == 'android':
                    todocode=logcat_dumpsend() # configure modbus registers according to W... data in setup
                else:
                    TODO="" # esialgu, kuni linuxile midagi aretada
                    todocode=1
                    
            if TODO.split(',')[0] == 'pull':
                print('going to pull') # debug
                if len(TODO.split(',')) == 3: # download a file (with name and size given)
                    filename=TODO.split(',')[1]
                    filesize=int(TODO.split(',')[2])

                    if pulltry == 0: # first try
                        pulltry=1 # partial download is possible, up to 10 pieces!
                        startnum=0
                        todocode=1 # not yet 0

                    if pulltry < 10 and todocode >0: # NOT done yet
                        if pulltry == 1: # there must be no file before the first try
                            try:
                                os.remove(filename+'.part')
                            except:
                                pass
                        else: # second and so on try
                            try:
                                filepart=filename+'.part'
                                startnum=os.stat(filepart)[6]
                                msg='partial download size '+str(dnsize)+' on try '+str(pulltry)
                            except:
                                msg='got no size for file '+os.getcwd()+'/'+filepart+', try '+str(pulltry)
                                startnum=0
                                #traceback.print_exc()
                            print(msg)
                            syslog(msg)

                        if pull(filename,filesize,startnum)>0:
                            pulltry=pulltry+1 # next try will follow
                            todocode=1
                        else: # success
                            pulltry=0
                            todocode=0
                else:
                    todocode=1
                    print('wrong number of parameters for pull')
                    
            if TODO.split(',')[0] == 'push': # upload a file (with name and passcode given)
                try:
                    filename=TODO.split(',')[1]
                    print('starting push with',filename)
                    todocode=push(filename) # no automated retry here
                except:
                    msg='invalid cmd syntax for push'
                    print(msg)
                    syslog(msg)
                    todocode=99

            if TODO.split(',')[0] == 'sqlread':
                if len(TODO.split(',')) == 2: # cmd:sqlread,aichannels (no extension for sql file!)
                    tablename=TODO.split(',')[1]
                    if '.sql' in tablename:
                        msg='invalid parameters for cmd '+TODO
                        print(msg)
                        syslog(msg)
                        pulltry=88 # need to skip all tries below
                    else:
                        todocode=sqlread(tablename) # hopefully correct parameter (existing table, not sql filename)
                        if tablename == 'setup' and todocode == 0: # table refreshed, let's use the new setup
                            channelconfig() # possibly changed setup data to modbus registers
                            report_setup() # let the server know about new setup
                else: # wrong number of parameters
                    todocode=1
            
            if TODO.split(',')[0] == 'RMLOG': # delete log files in working directory (d4c)
                files=glob.glob('*.log')
                try:
                    for filee in files:
                        os.remove(filee)
                        todocode=0
                except:
                    todocode=1 # failure to delete *.log
                    
            # start scripts in parallel (with 10s pause in this channelmonitor). cmd:run,nimi,0 # 0 or 1 means bg or fore
            # use background normally, the foreground process will open a window and keep it open until closed manually
            if TODO.split(',')[0] == 'run':
                if len(TODO.split(',')) == 3: # run any script in the d4c directory as foreground or background subprocess
                    script=TODO.split(',')[1]
                    if script in os.listdir('/sdcard/sl4a/scripts/d4c'): # file exists
                        fore=TODO.split(',')[2] # 0 background, 1 foreground
                        extras = {"com.googlecode.android_scripting.extra.SCRIPT_PATH":"/sdcard/sl4a/scripts/d4c/%s" % script}
                        joru1="com.googlecode.android_scripting"
                        joru2="com.googlecode.android_scripting.activity.ScriptingLayerServiceLauncher"
                        if fore == '1': # see jatab akna lahti, pohiprotsess kaib aga edasi
                            myintent = droid.makeIntent("com.googlecode.android_scripting.action.LAUNCH_FOREGROUND_SCRIPT", None, None, extras, None, joru1, joru2).result
                        else: # see ei too mingit muud jura ette, toast kaib ainult labi
                            myintent = droid.makeIntent("com.googlecode.android_scripting.action.LAUNCH_BACKGROUND_SCRIPT", None, None, extras, None, joru1, joru2).result
                        try:
                            droid.startActivityIntent(myintent)
                            msg='tried to start'+script
                            if fore == 1:
                                msg=msg+' in foreground'
                            else:
                                msg=msg+' in background'
                            print(msg)
                            syslog(msg)
                            todocode=0
                        except:
                            msg='FAILED to execute '+script+' '+str(sys.exc_info()[1])
                            print(msg)
                            syslog(msg)
                            #traceback.print_exc()
                            todocode=1
                        time.sleep(10) # take a break while subprocess is active just in case...
                    else:
                        msg='file not found: '+script
                        print(msg)
                        todocode=1
                        time.sleep(2)
                    
                else:
                    todocode=1 # wrong number of parameters

            if TODO.split(',')[0] == 'size': # get the size of filename (cmd:size,setup.sql)
                script=TODO.split(',')[1]
                try:
                    dnsize=os.stat(script)[6]
                    todocode=0
                except:
                    todocode=1


            # common part for all commands below
            if todocode == 0: # success with TODO execution
                msg='remote command '+TODO+' successfully executed'
                if TODO.split(',')[0] == 'size' :
                    msg=msg+', size '+str(dnsize)
                if TODO.split(',')[0] == 'free' :
                    msg=msg+', free MB,% '+repr(free)
                if TODO == 'WLAN?':  # just reporting via ERV here 
                    msg=msg+', state '+str(dnsize) # dnsize used as True or False variable
                sendstring=sendstring+'ERS:0\n'
                TODO='' # no more execution
            else: # no success
                msg='remote command '+TODO+' execution failed or incomplete on try '+str(pulltry)
                sendstring=sendstring+'ERS:2\n'
                if TODO.split(',')[0] == 'size':
                    msg=msg+', file not found'
                if 'pull,' in TODO and pulltry<5: # pull must continue
                    msg=msg+', shall try again TODO='+TODO+', todocode='+str(todocode)
                else: # no pull or enough pulling
                    msg=msg+', giving up TODO='+TODO+', todocode='+str(todocode)
                    TODO=''
            print(msg)
            syslog(msg)
            sendstring=sendstring+'ERV:'+msg+'\n' # msh cannot contain colon or newline
            udpsend(0,int(ts)) # SEND AWAY. no need for server ack so using 0 instead of inumm

            #TODO='' # must be emptied not to stay in loop
            #print 'remote command processing done'
            sys.stdout.flush()
            #time.sleep(1)
        else:
            pulltry=0 # next time like first time
        # ending processing the things to be done



    # ####### now other things like making services messages to send to the monitoring server and launching REGULAR MESSANING ########
    ts=time.mktime(datetime.datetime.now().timetuple()) #time in seconds now

    # ###### FIRST THE THINGS TO DO MORE OFTEN, TO BE REPORTED ON CHANGE OR renotifydelay TIMEUT (INDIVIDUAL PER SERVICE!) ##########
    time.sleep(0.1) # time.sleep(0.05) # try to avoid first false di reading after ai readings
    #mbcommresult=read_dichannel_bits() # should be done by addresses, not all of the addresses are up perhaps...
    if OSTYPE == 'android':
        ProxyState=read_dichannel_bits(255) # 0 if reading was possible, proxy sw running and responsive # ei rpuugi ju android olla!
    
    if OSTYPE == 'android' and USBstate != 1: # android but usb down
        pass
    else: # in all other cases go ahead reading di channels
        mbcommresult=read_dichannel_bits(1) # read di into sql # tegelikult vaja intelligentsemalt teha, et ei peaks siin aaadressi fikseerima !!!! 
        if mbcommresult == 0: # ok, else incr err_dichannels
            msg='dichannels read success'
            err_dichannels=0
            make_dichannels() # di related service messages creation, insert message data into buff2server to be sent to the server # tmp OFF!
            write_dochannels() # compare the current and needed channel values and write the channels to be changed with
            write_aochannels() # compare the current and needed channel values and write the channels to be changed with
        else:
            err_dichannels=err_dichannels+1 # read data into sqlite tables
            msg='dichannels read failure, err_dichannels '+str(err_dichannels)
            print(msg)


    #if USBstate == 1: # USB running (but errors on channels)
        if err_dichannels == 50: #reread dichannels.sql due to consecutive read errors'
            msg='going to reread dichannels.sql due to consecutive read errors'
            print(msg)
            syslog(msg)
            sqlread('dichannels')  # try to restore the table
        if err_dichannels == 250 and ProxyState == 0: # stop, but only if proxy active to restart again!
            #TODO='run,dbREcreate.py,0' # recreate databases before stopping - not needed any more, tables in  memory!
            stop=1  # restart via main.py due to dichannels problem
            msg='script will be stopped due to errors on binary inputs_dichannels'
            syslog(msg) # log message to file
            print(msg)
            if OSTYPE == 'android':
                droid.ttsSpeak(msg)
                time.sleep(10)

    if MBsta != MBoldsta: # change to be reported
        print('change in MBsta, from  to',MBoldsta,MBsta,'at',ts)
        sendstring=sendstring+array2regvalue(MBsta,'EXW',2) # EXW, EXS reporting if changed
        MBoldsta=MBsta

    #check tcp socket health, restart also if tcperr too high (consecutive errors), once in 5 seconds or so
    if ts>ts_interval1+interval1delay: # not to try too often, deal with other things too
        ts_interval1=ts
        #print 'MBoldsta, MBsta',MBoldsta,MBsta,'at',ts # report once in 5 seconds or so
        if OSTYPE == 'android':
            if mac[0:3] == 'D05' or mac[0:3] == 'BCF': # sony & LG wlan mac
                ProxyState=read_proxy('') # recheck the basic parameters accessible via modbusproxy
            else:
                ProxyState=read_proxy('all') # try to get the correct wlan mac mac

            if ProxyState == 0:
                tcperr=0
                read_batt() # check the battery values and write them into sqlite tables aichannels, dichannels
                #msg='outside read_proxy: phoneuptime '+str(PhoneUptime)+', proxyuptime '+str(ProxyUptime)+', gsmlevel '+str(GSMlevel)+', wlanlevel '+str(WLANlevel)
                #syslog(msg) # debug
            else:
                tcperr=tcperr+1
        else:
            tcperr=0 
            

        if MBerr[0]+MBerr[1]+MBerr[2]+MBerr[3] > 0: # regular notif about modbus problems
            msg='MBerr '+str(repr(MBerr))+', tcperr '+str(tcperr)+', USBstate '+str(USBstate)
            syslog(msg)
            print(msg)


        if err_dichannels+err_aichannels+err_counters>0: # print channel comm errors
            print('modbus errors di ai count',err_dichannels,err_aichannels,err_counters)
        print
        if tcperr>4: # restart tcp socket
            #msg='trying to recreate the databases and restart due to consecutive tcperr at '+str(ts)
            msg='trying to reconnect to modbusproxy due to consecutive tcperr at '+str(ts)
            print(msg)
            syslog(msg)
            if socket_restart()>0: # failed to connect modbusproxy
                tcperr=0 # restart error counter
            sys.stdout.flush()
            time.sleep(0.5)

        mbcommresult=read_aichannels()
        if mbcommresult == 0: # ok, else incr err_aichannels
            err_aichannels=0
        else:
            err_aichannels=err_aichannels+1 # read data into sqlite tables

        #if USBstate == 1: # but errors in register reading
        if OSTYPE == 'android' and USBstate != 1: # android but usb down
            pass
        else:
            if err_aichannels == 5: # reread aichannels
                msg='going to reread aichannels.sql due to consecutive errors'
                print(msg)
                syslog(msg)
                sqlread('aichannels')  # try to (drop and) restore the table
            
    # ### NOW the ai and counter values, to be reported once in 30 s or so
    if ts>appdelay+ts_lastappmain:  # time to read analogue registers and counters, not too often
        # this is the appmain part below
        ts_lastappmain=ts # remember the execution time

        # signal levels to send. measured once in 5s if android
        #if GSMlevel == -115:  # flight mode, asu -1 . or 99? 0\n' # 0..31
        #sendstring=sendstring+'1\n'
        if OSTYPE == 'android':
            msg='GSMlevel, WLANlevel are '+str(GSMlevel)+', '+str(WLANlevel)
            print(msg)
            syslog(msg)
            sendstring=sendstring+'SLW:'+str(GSMlevel)+' '+str(WLANlevel)+'\nSLS:0\n' # status to be added!


        make_aichannels() # put ai data into buff2server table to be sent to the server - only if successful reading!

        mbcommresult=read_counters() # read counters (2 registers usually, 32 bit) and put data into buff2server table to be sent to the server - only if successful reading!
        if mbcommresult == 0: # ok, else incr err_counters
            err_counters=0
        else:
            err_counters=err_counters+1 # read data into sqlite tables

        #if USBstate == 1: #
        if OSTYPE == 'android' and USBstate != 1: # android but usb down
            pass
        else:
            if err_counters == 5: # reread counters.sql
                msg='going to reread counters.sql due to consecutive read errors'
                print(msg)
                syslog(msg)
                sqlread('counters')  # try to restore the table
            if err_counters == 6 and ProxyState == 0: # stop but only if proxy is up
                #TODO='run,dbREcreate.py,0' # recreate databases before stopping
                stop=1  # restart via main.py due to counters problem
                msg='script will be stopped (and databases recreated) due to errors with counters'
                syslog(msg) # log message to file
                print(msg)
                if OSTYPE == 'android':
                    droid.ttsSpeak(msg)

        #if OSTYPE == 'archlinux':
            #getset_network('ether') # chk and chg network parameters / creates netlink l eftover??
        
        # ############################################################ temporary check to debug di part here, not as often as normally
        #read_dichannel_bits() # di read as bitmaps from registers. use together with the make_dichannel_svc()!
        #make_dichannel_svc() # di related service messages creation, insert message data into buff2server to be sent to the server
        #write_dochannels() # compare the current and new channels values and use write_register() to control the channels to be changed with
        # end di part. put into fastest loop for fast reaction!
        # ###########################################################

    # ### resending the unchanged di values just to avoid unknown state for them oin nagios, once in 4 minutes or so
    if ts>renotifydelay+ts_lastnotify:  # regular messaging not related to registers but rather to program variables
        msg="renotify application variables due to ts "+str(ts)+">"+str(renotifydelay+ts_lastnotify)+", renotifydelay "+str(renotifydelay)
        print(msg)
        syslog(msg)
        ts_lastnotify=ts # remember timestamp

        make_dichannels() # test to fix renotify

        sendstring=sendstring+array2regvalue(MBsta,'EXW',2) # EXW, EXS reporting periodical based on MBsta[] for up to 4 modbus addresses
        sendstring=sendstring+array2regvalue(TCW,'TCW',0) # traffic TCW[] reporting periodical, no status above 0

        #testdata() # test services / can be used instead of read_*()
        #unsent()  # unsent by now. chk using renotifydelay to send again or delete of too old. vigane! kustutab ka selle, mis on vaja saata!

        #if ts>ts_boot + 20: # to avoid double messsaging on startup
        sendstring=sendstring+array2regvalue(MBsta,'EXW',2) # EXW, EXS reporting even if not changed

        AppUptime=int(ts-ts_boot)
        sendstring=sendstring+"UPV:"+str(AppUptime)+"\nUPS:" # uptime value in seconds
        if AppUptime>1800: # status during first 30 min of uptime is warning, then ok
            sendstring=sendstring+"0\n" # ok
        else:
            sendstring=sendstring+"1\n" # warning


        sendstring=sendstring+'UDW:'+str(PhoneUptime)+' '+str(ProxyUptime)+' '+str(USBuptime)+' '+str(AppUptime)+'\nUDS:' # diagnostic uptimes, add status!
        if USBuptime>900 and AppUptime>1800:
            sendstring=sendstring+'0\n' # ok
        else:
            sendstring=sendstring+'1\n' # warning about recent restart




    #send it all away, some go via buff2server, some directly from here below


    if sendstring != '': # there is something to send, use udpsend()
        udpsend(0,int(ts)) # SEND AWAY. no need for server ack so using 0 instead of inumm

    # REGULAR MESSAGING RELATED PART END (AI, COUNTERS)




    # control logic FOR OUTPUTS goes to a separate script, manipulating dochannels only. ##################



    udpmessage() # chk buff2server for messages to send or resend. perhaps not on the fastest possible rate?



    #but immediately if there as a change in dichannels data. no problems executong every time if select chg is fast enough...

    #print '.', # dots are signalling the fastest loop executions here - blue led is better...
    sys.stdout.flush() # to update the log for every dot - this alone is really needed to see the real time log


UDPlockSock.close()
msg='script ending due to stop signal'
print(msg)
syslog(msg)
sys.stdout.flush()
if OSTYPE == 'android':
    droid.ttsSpeak(msg)
    time.sleep(10)

#main end. main frequency is defined by udp socket timeout!
######## END  ######################
