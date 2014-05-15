#!/usr/bin/python

APVER='tartuvalgustus 07mai2014' # for npe only, test on other platforms before using!

import os
# env variable HOSTNAME should be set before starting python
try:
    print('HOSTNAME is',os.environ['HOSTNAME'])
except:
    os.environ['HOSTNAME']='olinuxino' # techbase # to make sure it exists on background of npe too
    print('set HOSTNAME to techbase')
    
from droidcontroller.udp_commands import * # sellega alusta, kakaivitab ka SQlgeneral
p=Commands() # setup and commands from server
r=RegularComm() # variables like uptime and traffic, not io channels

if os.environ['HOSTNAME'] == 'server': # test linux  
    mac_ip=p.subexec('./getnetwork.sh',1).decode("utf-8").split(' ')
    mac='000101100002' # replace! CHANGE THIS!
    print('replaced mac to',mac_ip)
elif os.environ['HOSTNAME'] == 'olinuxino':
    mac_ip=p.subexec('/root/d4c/getnetwork.sh',1).decode("utf-8").split(' ')
elif os.environ['HOSTNAME'] == 'techbase':
    mac_ip=p.subexec('/mnt/nand-user/d4c/getnetwork.sh',1).decode("utf-8").split(' ')

print('mac ip',mac_ip)
mac=mac_ip[0]
ip=mac_ip[1]
r.set_host_ip(ip)

udp.setID(mac) # env muutuja kaudu ehk parem?
tcp.setID(mac) # 
udp.setIP('46.183.73.35')
udp.setPort(44445)

from droidcontroller.achannels import *
from droidcontroller.cchannels import *
from droidcontroller.dchannels import *

# the following instances are subclasses of SQLgeneral. why?
a=Achannels() # both ai and ao
d=Dchannels() # di and do 
c=Cchannels() # counters, power

s.check_setup('aichannels')
s.check_setup('dichannels')
s.check_setup('counters')

s.set_apver(APVER) # set version

#print('achannels a',a) # debug
#print('dchannels d',d)
#print('counters c',c)
#print('sqlgeneral s',s)
#print('regular r',r)
#print('commands p',p)
#print('udp conn udp',udp)
#print('tcp conn tcp',tcp) # debug

#stp=Setup()
#gc=GoogleCalendar()


# TAASTA loendite seisud - sellega tegeleb cchannels.py ise
# LASE MUUTA loendite ja voimsuse alarmipiire
# arvesta DI seisu valjundi lylitusel

# functions

def comm_doall():
    ''' Handle the communication with io channels via modbus and the monitoring server  '''
    udp.unsent() # vana jama maha puhvrist
    d.doall()  #  di koik mis vaja, loeb tihti, raporteerib muutuste korral ja aeg-ajalt asynkroonselt
    c.doall() # loeb ja vahel ka raporteerib
    a.doall() # ai koik mis vaja, loeb ja vahel raporteerib
    r.regular_svc(svclist = ['ULW','UTW','ip']) # UTW,ULW are default
    got = udp.comm() # loeb ja saadab udp, siin 0.1 s viide sees. tagastab {} saadud key:value vaartustega
    if got != None:
        print(got) # debug
        todo=p.parse_udp(got) # any commands or setup varioables from server?
        
        # a few command to make sure they are executed even in case of udp_commands failure
        if todo == 'REBOOT':
            stop = 1 # kui sys.exit p sees ei moju millegiparast
            print('emergency stopping by main loop, stop=',stop)
        if todo == 'FULLREBOOT':
            print('emergency rebooting by main loop')
            p.subexec(['reboot'],0)
        # end making sure 
        
        #print('main: todo',todo) # debug
        p.todo_proc(todo) # execute other possible commands
    
        
        
def app_doall():
    ''' Application rules and logic, via services if possible  '''
    global ts, LRW_ts
    try:
        LAWchange=0
        LSW=s.get_value('LSW','dichannels') # bin ana selector / lighting sensors
        SensorMode=LSW[2] # member 3 is sensor selector, 0=D, 1=A
        LAW=s.get_value('LAW','aichannels') # analogue light sensor and thresholds on off
        LRW=s.get_value('LRW','dichannels') # lighting control, out sens cal remote
        
        #print('app_doall 0: LAW LSW LRW',LAW,LSW,LRW) # debug

        if LAW[0] > LAW[2]: #switch off threshold crossed
            s.set_membervalue('LSW',2,0,'dichannels') # sensor svs modified, analogue to binary, member 2!
            LAWchange=1
        elif LAW[0] < LAW[1]: # switch on threshold crossed
            s.set_membervalue('LSW',2,1,'dichannels') # 
            LAWchange=1
        if LAWchange > 0 and SensorMode >0: # reread LSW
            LSW=s.get_value('LSW','dichannels') # LSW REREAD
        
        #print('app_doall 1: LAW LSW LRW',LAW,LSW,LRW) # debug
        
        #LRW member update, from bi or ana sensor
        if SensorMode == 0: # binary sensor enabled
            s.set_membervalue('LRW',2,LSW[0],'dichannels') # binary sensor state to LRW member2
        else: # analogue sensor
            s.set_membervalue('LRW',2,LSW[1],'dichannels') # binary sensor state to LRW member2
        
        LRW=s.get_value('LRW','dichannels') # LRW REREAD
        #print('app_doall 2: LAW LSW LRW',LAW,LSW,LRW) # debug
        
        # actual control based on input variables (sensor, calendar, remote)
        
        #print('LRW',LRW) # debug
        if round(LRW[0]) != round((LRW[1]|LRW[2]|LRW[3])): # relay toggle needed if any of the input parameters is not 0
            s.setby_dimember_do('LRW',1,(LRW[1]|LRW[2]|LRW[3])) # svc, member, value. writing dochannel that corresponds to the given member of LRW        
            msg='changed lighting state to '+str(LRW[1]|LRW[2]|LRW[3])
            LRW=s.get_value('LRW','dichannels') # LRW REREAD
            LRW_ts=ts
        #print('app_doall 3: LAW LSW LRW',LAW,LSW,LRW) # debug
    
    except:
        msg='main: app logic error!'
        print(msg)
        udp.syslog(msg)
        traceback.print_exc()
        time.sleep(5)
        

def crosscheck(): # FIXME: should be autoadjustable to the number of counter state channels RxyV
    ''' Report failure states (via dichannels) depending on other states (from counters for example) '''
    global ts, LRW_ts
    LRW=s.get_value('LRW','dichannels') # LRW REREAD
    
    services=s.get_column('counters','val_reg','R__V') # table,column,like = ''
    for svc in services:
        feeder=svc[1]
        phase=svc[2]
        try:
            phasestate=s.get_value('R'+feeder+phase+'V','counters')[0]  # must not be empty!! should be ok in the end when values appear
            if ts > LRW_ts + 20: # time to check if state based on power is the same as LRW[0]. off_tout = 10
                s.set_membervalue('F'+feeder+'W', eval(phase),(LRW[0]^phasestate),'dichannels') # for 3in1 service, members are phases
                #s.set_membervalue('F'+feeder+phase'S', 1,(LRW[0]^phasestate),'dichannels') # for 1by1 service, always member 1
 
        except:
            print('feeder,phase',feeder+1,phase+1) # debug
            traceback.print_exc()
            time.sleep(5)
    
 ################  MAIN #################
ts=time.time() # needed for manual function testing
LRW_ts=ts

if __name__ == '__main__':
    #kontrollime energiamootjate seisusid. koik loendid automaatselt?
    msg=''
    stop=0
    
    # saada apver jaj taasta valgustuse olek reboodi korral
    sendstring="AVV:"+APVER+"\nAVS:0\nLRW:?0\nLSW:?"  # taastame moned seisud serverist
    udp.udpsend(sendstring)


    while stop == 0: # endless loop 
        ts=time.time() # global for functions
        comm_doall()  # communication with io and server
        #app_doall() # application rules and logic, via services if possible 
        #crosscheck() # check for phase consumption failures 
        # #########################################
        
        if len(msg)>0:
            print(msg)
            udp.syslog(msg)
            msg=''
        #time.sleep(1)  # main loop takt 0.1, debug jaoks suurem / jookseb kinni kui viidet pole? subprocess?
        sys.stdout.write('.') # dot without newline for main loop
        sys.stdout.flush()        
    # main loop end, exit from application