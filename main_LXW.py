#!/usr/bin/python

APVER='main_LXW 4.2.2015' # for olinuxino
# valgustuse signaali saatmine eliko serverisse


#################### functions ######################################################

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

    if udp.sk.get_state()[3] == 1: # restore now the variables from the server
        sendstring="AVV:"+APVER+"\nAVS:0\nTCW:?\n"  # counters are restored automatically by
        ac.ask_counters()
        print('******* uniscada connectivity up, sent AVV and tried to restore counters ********')
        udp.udpsend(sendstring)


    udp.unsent() # vana jama maha puhvrist
    ##d.doall()  #  di koik mis vaja, loeb tihti, raporteerib muutuste korral ja aeg-ajalt asynkroonselt
    ac.doall() # ai koik mis vaja, loeb ja vahel raporteerib
    for mbi in range(len(mb)): # check modbus connectivity
        mberr=mb[mbi].get_errorcount()
        if mberr > 0: # errors
            print('### mb['+str(mbi)+'] problem, errorcount '+str(mberr)+' ####')
            time.sleep(2) # not to reach the errorcount 30 too fast!
            if mberr > 30: # too many errors
                print('### going to reboot due to too many errors for mb['+str(mbi)+'] ###')
                p.subexec('reboot',0)   #################################

    #if OSTYPE == 'archlinux': # uniscada.py tegeleb commlediga
    #    led.commLED(0) # comm LED off
    r.regular_svc(svclist = ['UPW','TCW','ip']) # uptimes, traffic. UTW,ULW are default. also forks alive processes!
    got = udp.comm() # loeb ja saadab udp, siin 0.1 s viide sees. tagastab {} saadud key:value vaartustega
    if OSTYPE == 'archlinux':
        if udp.read_buffer(mode=1)[0] > 30: # too many waiting svc lines in buffer
            udp.led.alarmLED(1) # warning
        elif udp.read_buffer(mode=1)[0] == 0: # stats ok
            udp.led.alarmLED(0) # ok

    if got != '' and got != None: # got something from monitoring server
        #if OSTYPE == 'archlinux':
        #    led.commLED(1)
        if got != {}:
            ac.parse_udp(got) # chk if setup or counters need to be changed
            d.parse_udp(got) # chk if setup ot toggle for di
            todo=p.parse_udp(got) # any commands or setup variables from server?

            # a few command to make sure they are executed even in case of udp_commands failure
            if todo == 'REBOOT':
                stop = 1 # kui sys.exit p sees ei moju millegiparast
                print('emergency stopping by main loop, stop=',stop)
            elif todo == 'FULLREBOOT':
                print('emergency rebooting by main loop')
                p.subexec('reboot',0) # no []
            elif todo.split(',')[0] == 'mbread' and len(todo.split(',')) == 5: # read any modbus register , params mbi,mba,regadd,count. return value via ERV
                print('comm_doall cmd:',todo)
                res=mb[todo.split(',')[1]].read(todo.split(',')[2],todo.split(',')[3],todo.split(',')[4]) # read value, can be tuple
                print('mbread result',res)
                sendstring += 'ERV:'+msg+'\n' # msh cannot contain colon or newline
                udp.udpsend(sendstring) # SEN
            elif todo.split(',')[0] == 'mbwrite': # write any odbus register , params mbi,mba,regadd,value. return ok via ERV
                print('comm_doall cmd:',todo)

            # end making sure
            # vpn start stop handled by udp_commands
            #print('main: todo',todo) # debug
            p.todo_proc(todo) # execute other possible commands


def app_doall():
    ''' Application part for energy metering and consumption limiting, via services if possible  '''
    # lisada andurite erinevuste vordlemine ja korras anduri valik liiga suure erinevuse korral
    global ts, ts_app, ts_lux, LXW # LXW 2 anduri keskmise alusel elikosse saatmine
    if ts > ts_app + 20: # read luxmeter every 20 s
        ts_app = ts
        
        LXW = s.get_value('LXW','aicochannels') # unit clx (sentilux). liikmed 0 ja 1 keskmista. esialgu vaid 0 olemas
        for i in range(2):
            if LXW[i] < 0:
                LXW[i] = 0 # lahtine sisend annab negatiivse lugemi

        #if LXW[1] > 100: # 2 andurit olemas
        #    LXeliko = round((LXW[0] +LXW[1])/200.0, 2)  # lx
        #else:
        LXeliko = round(LXW[0]/100.0, 2) # lx
        

    if ts > ts_lux + 60: # send lux once per minute
        ts_lux = ts
        log.info('lighting level to eliko '+str(LXeliko)+' lx')
        lux = 'lux='+str(LXeliko)
        res = rs.dorequest(lux) # expected default response is 'ok' 
        if res != 0:
            log.warning('FAILED to send lux data!')
    
    

    
 ################  MAIN #################

import os, sys, time
import logging
logging.basicConfig(stream=sys.stderr, level=logging.INFO)
#logging.getLogger('acchannels').setLevel(logging.DEBUG) # acchannels esile
#logging.getLogger('pic_update').setLevel(logging.DEBUG) # acchannels esile
log = logging.getLogger(__name__)

mac_ip = ['','']

# env variable HOSTNAME should be used to resolve cases with no OSTYPE information
try:
    HOSTNAME = os.environ['HOSTNAME']
    print('env var HOSTNAME is',os.environ['HOSTNAME'])
except:
    HOSTNAME='olinuxino' # 'unknown'
    print('got no env var HOSTNAME, set local var to',HOSTNAME)
    os.environ['HOSTNAME'] = HOSTNAME

try:
    OSTYPE = os.environ['OSTYPE']
    print('env var OSTYPE is',OSTYPE)
except:
    OSTYPE='archlinux'
    print('got no env var OSTYPE, set local var OSTYPE to',OSTYPE)
    os.environ['OSTYPE'] = OSTYPE

print('OSTYPE',OSTYPE, 'HOSTNAME', HOSTNAME)  # debug

from droidcontroller.udp_commands import * # sellega alusta, kaivitab ka SQlgeneral
p=Commands(OSTYPE) # setup and commands from server
r=RegularComm(interval=120) # variables like uptime and traffic, not io channels

from droidcontroller.request import *
rs = Request(part1='http://streetlight.tartu.ee/cgi-bin/lightctrl?')

from droidcontroller.pic_update import *
up=PicUpdate() # io-board updater

#if os.environ['HOSTNAME'] == 'server': # test linux
if OSTYPE == 'linux': # test linux
    #mac_ip=p.subexec('./getnetwork.sh',1).decode("utf-8").split(' ')
    mac_ip[0]='000101100000' # replace! CHANGE THIS!
    mac_ip[1] = '10.0.0.253'
    print('replaced mac_ip to',mac_ip)
#elif os.environ['HOSTNAME'] == 'olinuxino':
elif OSTYPE == 'archlinux': # olinuxino
    mac_ip=p.subexec('/root/d4c/getnetwork.sh',1).decode("utf-8").split(' ')
else: # techbase?
    mac_ip=p.subexec('/mnt/nand-user/d4c/getnetwork.sh',1).decode("utf-8").split(' ')
    print('unknown OSTYPE',OSTYPE,', assuming techbase!') # FIXME

from droidcontroller.acchannels import * # ai and counters
#from droidcontroller.dchannels import * # di, do
#from droidcontroller.heatflow import * # heat flow and energy
#from droidcontroller.pid import * # pid and 3step control

print('mac ip',mac_ip)
mac = get_hostID('network.conf') # mac algusega reast
ip = mac_ip[1]

if mac is None:
    mac = ''
    log.error('wrong mac!!! '+mac)

r.set_host_ip(ip) # ip=mac_ip[1]
udp.setID(mac) # env muutuja kaudu ehk parem?
tcp.setID(mac) #
udp.setIP('195.222.15.51') # ('46.183.73.35') # mon server ip. only 195.222.15.51 has access to starman
udp.setPort(44445)


ac=ACchannels(in_sql = 'aicochannels.sql', readperiod = 5, sendperiod = 30) # counters, power. also 32 bit ai! trigger in aichannels
s.check_setup('aicochannels')


s.set_apver(APVER) # set version

ts=time.time() # needed for manual function testing
ts_app = ts # time.time used for timestamping here
ts_lux = ts # do not send too early

LXW=[]
LXeliko = 0



if __name__ == '__main__':  ############################################################################
    msg=''
    stop=0
    if OSTYPE == 'archlinux':
        udp.led.commLED(0)
        udp.led.alarmLED(1) # because we are starting


    while stop == 0: # endless loop
        ts=time.time() # global for functions
        comm_doall()  # communication with io and server
        app_doall() # application rules and logic, via services if possible
        time.sleep(0.1)  # main loop takt 0.1
        sys.stdout.write('.') # dot without newline for main loop
        sys.stdout.flush()
    # main loop end, exit from application
