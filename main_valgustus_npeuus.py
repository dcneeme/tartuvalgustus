#!/usr/bin/python

APVER='tartuvalgustus 27.1.2015' # for npe only, test on other platforms before using!
# 24.5.2014 added imod (re)start in case of mb[0 problems
# 30.05.2014 acchannels kasutusele
#15.06.2014 pull, push ok
# lisatud OSTYPE, vigane UTS ULS parandatud

#chk: mb[1].errorcount ei kasva yle 1, mb[0] aga kasvab palju tahab??? 300 juures app restart
#todo: mb kanalite vigade naitamine montooringusse, stack

# 3.1.2015 uuenda npe_io.sh, main_valgustus_tartu.py, acchannels.py. kasutab watchdog -t 900! start watchdog in syscfg!
#sama asi olinuxino peal kaima vordluseks


#####################################################



# functions

def get_hostID(filename):
    ''' ID as mac is not reliable on olinuxino. use the mac from file to become id ! '''
    mac = None
    try:
        with open(filename) as f:
            lines = f.read().splitlines()
            mac = None
            for line in lines:
                if 'mac ' in line[0:5]:
                    mac=line[4:].replace(':','')
                    if len(mac) == 12:
                        log.info('found host id (variable mac) to become '+mac)
                    else:
                        log.error('found host id (variable mac) with WRONG length! '+mac)
    except:
        log.error('no readable file '+filename+' for host_id!')
    return mac

    
def comm_doall():
    ''' Handle the communication with io channels via modbus and the monitoring server  '''
    global OSTYPE, ip, mac, ts_alive, stop
    todocode=0
    udp.unsent() # vana jama maha puhvrist
    d.doall()  #  di koik mis vaja, loeb tihti, raporteerib muutuste korral ja aeg-ajalt asynkroonselt
    ac.doall() # loeb ja vahel ka raporteerib
    #a.doall() # ai koik mis vaja, loeb ja vahel raporteerib
    for mbi in range(len(mb)): # check modbus connectivity # korras kanal argu nullistagu rikkis summat
        mberr=mb[mbi].get_errorcount()
        if mberr > 0: # errors
            print('### mb['+str(mbi)+'] problem, errorcount '+str(mberr)+' ####')
            time.sleep(2) # not to reach the errorcount 30 too fast!
            if mberr > 300: # too many errors, restart app (appd.sh must exist for that to happen)
                print('### STOPPING THE APP DUE TO mb['+str(mbi)+'] problem, errorcount '+str(mberr)+' ####')
                stop=1

    r.regular_svc(svclist = ['ULW','UTW','ip']) # UTW,ULW are default. also forks alive processes!
    got = udp.comm() # loeb ja saadab udp, siin 0.1 s viide sees. tagastab {} saadud key:value vaartustega
    if got != None and len(got)>0: # got something from monitoring server
        print('main: got: ',got) # debug - {key:value,...}]
        ac.parse_udp(got) # chk if setup or counters need to be changed
        d.parse_udp(got) # chk if setup ot toggle for di
        todo=p.parse_udp(got) # any commands or special setup variables from server?

        # a few commands double checked to make sure they are executed even in case of udp_commands failure
        if todo == 'REBOOT':
            stop = 1 # kui sys.exit p sees ei moju millegiparast
            print('emergency stopping by main loop, stop=',stop)
        if todo == 'FULLREBOOT':
            print('emergency rebooting by main loop')
            p.subexec('reboot',0) # no []
        # end making sure

        #print('main: todo',todo) # debug
        p.todo_proc(todo) # execute other possible commands

    if OSTYPE == 'techbaselinux': # special checks on npe
        if time.time() > ts_alive + 150: # time to fork another py_alive process
            print('******* marker time ********, ts_alive, time',ts_alive,time.time()) # debug
            mb[0].udpcomm(2,300,type='p')  # create marker process over socat containing sleep 300
            mb[0].udpcomm(4,900,type='p')  # watchdog -t 900  - last resort, restarting every 15 min if no udp comm
            # reg 2 py_alive, reg 3 udp_alive, reg 4 watchdog -t 600
            # if no alive processes then kill py app or even reboot...

            mac_ip=mb[0].udpcomm(10,2,type='bs') # getnetwork.sh over socat. count = 2: mac ip
            if mac_ip != None:
                print('got from socat mac, ip',mac_ip)
                ip=mac_ip[1]
                r.set_host_ip(ip)
                #if mac == '000000000000': # can happen sometimes, tartu 00010 for example
                #    mac = mac_ip[0]
                #    udp.setID(mac)
                #    tcp.setID(mac)
                #    sendstring = "AVV:"+APVER+"\nAVS:0\nLRW:?\nLSW:?\nEC6W:?\nEC9W:?\n"  # counters asked on sqlgeneral init but must be asked again if wrong mac
                #    udp.udpsend(sendstring) # ei joudnud enne kohale, kui mac vale oli sel ajal

            VPW=s.get_value('VPW','dichannels') # VPN control, actual local remote
            vpn_status=mb[0].udpcomm(11,1,type='b') # slow, use socat timeout 5s
            if vpn_status != None and len(vpn_status) >0:
                vpn_status=vpn_status[0] # vpn status, socat returns tuple
                if vpn_status != '':
                    print('got vpn_status',vpn_status) # debug
                    if 'OFF' in vpn_status:
                        d.set_divalue('VPW',1,0) # to show actual value
                        if (VPW[1]|VPW[2]) > 0: # vpn should be on
                            print('going to start vpn') # debug
                            todocode+=p.subexec('./vpnon',2) # start vpn
                            if todocode == 0:
                                print('vpn should be starting')
                            else:
                                print('vpn start FAILED')
                    elif 'ACTIVE' in vpn_status:
                        d.set_divalue('VPW',1,1) # to show actual value via member 1
                        if (VPW[1]|VPW[2]) == 0: # vpn should be off
                            print('going to stop vpn') # debug
                            todocode=p.subexec('vpn stop',2) # stop vpn
                            if todocode == 0:
                                print('vpn should be stopped')
                                d.set_divalue('VPW',1,0) # to show actual value sooner
                            else:
                                print('vpn stop FAILED')
                    elif 'UNREACHABLE' in vpn_status:
                        d.set_divalue('VPW',1,0) # to show actual value
                        todocode=p.subexec('vpn stop',2) # stop vpn first
                        print('invalid vpn state! stopping and possibly starting') # debug
                        if (VPW[1]|VPW[2]) >0: # restart vpn
                            time.sleep(5)
                            todocode+=p.subexec('./vpnon',2) # start vpn
                            if todocode == 0:
                                print('vpn should be starting')
                            else:
                                print('vpn start FAILED')
                    else: # must be CONNECTING, do nothing
                        print('vpn probably connecting') # debug
                else:
                    print('got NO vpn_status from socat') # debug
            ts_alive=time.time()


def app_doall():
    ''' Application rules and logic, via services if possible  
        Kontaktor LRW[0] rakendub siis, kui kehtib kas valgusanduri signaal LRW[1], kalender LRW[2] voi kaugjuhtimine LRW[3].
        Valgusandureid on 2, vana kohalik LRW[0] ja uus ai1 baasil di LSW[1]. Nende vahel valib LSW[2]. 1 = [1]
    '''
    global ts, LRW_ts
    try:
        LAWchange=0
        LSW=s.get_value('LSW','dichannels') # bin ana selector / lighting sensors
        SensorMode=LSW[2] # member 3 is sensor selector, 0=D, 1=A
        LAW=s.get_value('LAW','aicochannels') # analogue light sensor and thresholds on off
        LRW=s.get_value('LRW','dichannels') # lighting control, out sens cal remote


        print('app_doall 0: LAW LSW LRW',LAW,LSW,LRW) # debug

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

        log.debug('LRW'+str(LRW))
        
        if round(LRW[0]) != round((LRW[1]|LRW[2]|LRW[3])): # relay toggle needed if any of the input parameters is not 0
            ''' Lighting switching via do0 '''
            s.setby_dimember_do('LRW',1,(LRW[1]|LRW[2]|LRW[3])) # svc, member, value. writing dochannel that corresponds to the given member of LRW
            msg='changed lighting state to '+str(LRW[1]|LRW[2]|LRW[3])
            log.info(msg)
            LRW=s.get_value('LRW','dichannels') # LRW REREAD
            LRW_ts=ts
        
        print('app_doall 3: LAW LSW LRW',LAW,LSW,LRW) # debug

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

    services=s.get_column('aicochannels','val_reg','R__V') # table,column,like = ''
    for svc in services:
        feeder=svc[1]
        phase=svc[2]
        try:
            phasestate=s.get_value('R'+feeder+phase+'V','aicochannels')[0]  # must not be empty!! should be ok in the end when values appear
            if ts > LRW_ts + 20: # time to check if state based on power is the same as LRW[0]. off_tout = 10
                s.set_membervalue('F'+feeder+'W', eval(phase),(LRW[0]^phasestate),'dichannels') # for 3in1 service, members are phases
                #s.set_membervalue('F'+feeder+phase'S', 1,(LRW[0]^phasestate),'dichannels') # for 1by1 service, always member 1

        except:
            print('feeder,phase',feeder+1,phase+1) # debug
            traceback.print_exc()
            time.sleep(5)



def io2test():

    start=time.time()
    d.read_di_grp(1,100,3,mbi=0)  # d.sync_di()
    stop=time.time()
    print('npe di',round(stop-start,2),'s')
    time.sleep(1)

    start=time.time()
    ac.read_grp(1,500,3,1,mbi=0)
    stop=time.time()
    print('npe ai',round(stop-start,2),'s')
    time.sleep(1)

    start=time.time()
    ac.read_grp(1,400,12,2,mbi=1)
    stop=time.time()
    print('counters',round(stop-start,2),'s')



################  MAIN ##################################################################

import sys, os, time
import logging
logging.basicConfig(stream=sys.stderr, level=logging.INFO) # INFO
logging.getLogger('acchannels').setLevel(logging.DEBUG) # ei moju?
logging.getLogger('sqlgeneral').setLevel(logging.DEBUG) # yks esile kui kommenteerimata
#logging.getLogger('counter2power').setLevel(logging.DEBUG) # yks esile kui kommenteerimata
log = logging.getLogger(__name__)

HOSTNAME = 'unknown'
OSTYPE = 'unknown'

try:
    HOSTNAME=os.environ['HOSTNAME']
    if HOSTNAME == 'd4c_controller':
        OSTYPE='archlinux' # npe
    elif HOSTNAME == 'techbase':
        OSTYPE='techbaselinux'
    elif HOSTNAME == 'server':
        OSTYPE='linux'
    else:
        log.warning('unknown HOSTNAME: '+HOSTNAME)
        
except:
    log.warning('undefined env variable HOSTNAME!')
    time.sleep(5)

log.info('running on OSTYPE '+OSTYPE+', HOSTNAME '+HOSTNAME)

from droidcontroller.udp_commands import * # sellega alusta, kaivitab ka SQlgeneral
p=Commands(OSTYPE) # setup and commands from server
r=RegularComm(interval=120) # variables like uptime and traffic, not io channels

mac_ip=['000000000000','127.0.0.1'] # dummy initial
if HOSTNAME == 'server': # test linux
    mac_ip=p.subexec('./getnetwork.sh',1).decode("utf-8").split(' ')
elif HOSTNAME == 'olinuxino':
    mac_ip=p.subexec('/root/d4c/getnetwork.sh',1).decode("utf-8").split(' ')
elif HOSTNAME == 'techbase':
    #mac_ip=p.subexec('/mnt/nand-user/d4c/getnetwork.sh',1).decode("utf-8").split(' ')
    try:
        mac_ip=mb[0].udpcomm(10,2,type='bs') # getnetwork.sh over socat. count = 2: mac ip
        if mac_ip != None:
            print('got from socat mac, ip',mac_ip)
        else:
            mac_ip=['000000000000','127.0.0.1']
    except:
        print('could not get mac_ip from getnetwork.sh over socat, using default')
        mac_ip=['000000000000','127.0.0.1']
        time.sleep(2)

print('mac ip',mac_ip)
mac = mac_ip[0]
ip = mac_ip[1]
r.set_host_ip(ip)
mac = get_hostID('network.conf') # mac algusega reast


udp.setID(mac) # env muutuja kaudu ehk parem?
tcp.setID(mac) #
udp.setIP('46.183.73.35')
udp.setPort(44445)

from droidcontroller.acchannels import * # ai and counters together
#from droidcontroller.achannels import *
#from droidcontroller.cchannels import *
from droidcontroller.dchannels import *

# the following instances are subclasses of SQLgeneral. why?
ac = ACchannels(readperiod = 3, sendperiod = 30) # counters, ai and ao, incl pwr # use 60?
d = Dchannels(readperiod = 0, sendperiod = 180) # di and do. immediate notification, read as often as possible.

s.check_setup('aicochannels')
s.check_setup('dichannels')
#s.check_setup('counters')

s.set_apver(APVER) # set version


print('mac ip',mac_ip)
# mac = get_hostID('network.conf') # mac algusega reast /  ettepoole
ip = mac_ip[1]
mac = mac_ip[0]

if mac is None:
    mac = ''
    log.error('wrong mac!!! '+mac)

#r.set_host_ip(ip) # ip=mac_ip[1]
#udp.setID(mac) # env muutuja kaudu ehk parem?
#tcp.setID(mac) #
#udp.setIP('195.222.15.51') # ('46.183.73.35') # mon server ip. only 195.222.15.51 has access to starman
#udp.setPort(44445)


ts=time.time() # needed for manual function testing
LRW_ts=ts
ts_alive=0 # marker processes and ip refresh with 150 s interval

if __name__ == '__main__':
    #kontrollime energiamootjate seisusid. koik loendid automaatselt?
    msg=''
    stop=0

    # saada apver jaj taasta valgustuse olek reboodi korral
    sendstring="AVV:"+APVER+"\nAVS:0\nLRW:?\nLSW:?"  # \nE6CW:?\n"  # counters will be asked on sqlgeneral init
    udp.udpsend(sendstring) # ei joua kohale, kui side sel ajal puudu veel


    while stop == 0: # endless loop
        ts=time.time() # global for functions
        comm_doall()  # communication with io and server
        app_doall() # application rules and logic, via services if possible
        crosscheck() # check for phase consumption failures
        # #########################################

        if len(msg)>0:
            print(msg)
            udp.syslog(msg)
            msg=''
        time.sleep(0.5)  # main loop takt 0.1, debug jaoks suurem / jookseb kinni kui viidet pole? subprocess?
        #sys.stdout.write('.') # dot without newline for main loop
        #sys.stdout.flush()
    # main loop end, exit from application