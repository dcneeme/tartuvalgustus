#!/usr/bin/python
# test_tartu.py

host_id = '000101100001' # from sql? system?
APVER='test_tartu 03mai2014'

import os
try:
    print(os.environ['HOSTNAME'])
except:
    os.environ['HOSTNAME']='techbase' # to make sure it exists on background of npe too

#from uniscada import * # achannel ja dchannel impordivad sqlgenerali ja see jalle uniscada. 
from droidcontroller.achannels import * # see loob modbus, sqlite ja uniscada kanalid
udp.setIP('46.183.73.35')
udp.setPort(44445)
udp.setID(host_id) # muidu kysib vana loendiseisu juba enne selle id saamist!
tcp.setID(host_id) # ei toii siin?
from droidcontroller.cchannels import *
from droidcontroller.dchannels import *
from droidcontroller.udp_commands import *

# the following instances are subclasses of SQLgeneral. why?
a=Achannels() # both ai and ao
d=Dchannels() # di and do 
c=Cchannels() # counters, power
p=Commands() # setup and commands from server
r=RegularComm() # variables like uptime and traffic, not io channels
s.set_apver(APVER) # set version

print('a',a) # debug
print('d',d)
print('c',c)
print('s',s)
print('r',r)
print('p',p)
print('udp',udp)
print('tcp',tcp) # debug

# c.set_counter(1000,mba=1,regadd=400) # voi siis sta_reg ja member alusel
#stp=Setup()
#gc=GoogleCalendar()

# taasta valgustuse olek reboodi korral
sendstring='LRW:?'
udp.udpsend(sendstring)

# TAASTA loendite seisud - selega tegeleb cchannels.py ise
# LASE MUUTA loendite ja voimsuse alarmipiire
# arvesta DI seisu valjundi lylitusel

################  MAIN #################

if __name__ == '__main__':
    #kontrollime energiamootjate seisusid. koik loendid automaatselt?
    msg=''
    stop=0
    got=None
    SensorMode=1 # pane see instance?
    while stop == 0:
        stop = udp.unsent() # vana jama maha puhvrist
        stop = d.doall()  #  di koik mis vaja, loeb tihti, raporteerib muutuste korral ja aeg-ajalt asynkroonselt
        stop = c.doall() # loeb ja vahel ka raporteerib
        stop = a.doall() # ai koik mis vaja, loeb ja vahel raporteerib
        r.regular_svc() # UTW,ULW are default
        r.set_uptime()  #  sys uptime, app uptime
        r.regular_svc() # a few regular services if it is their time
        got = udp.comm() # loeb ja saadab udp, siin 0.1 s viide sees. tagastab {} saadud key:value vaartustega
        if got != None:
            print(got) # debug
            todo=p.parse_udp(got) # any commands or setup varioables from server?
            
            # a few command to make sure they are executed even in case of udp_commands failure
            if todo == 'REBOOT':
                stop = 1 # kui sys.exit p sees ei moju milllegiparast
                print('emergency stopping by main loop, stop=',stop)
            if todo == 'FULLREBOOT':
                print('emergency rebooting by main loop')
                p.subexec(['reboot'],0)
            # end making sure 
            
            print('main: todo',todo) # debug
            p.todo_proc(todo) # execute other possible commands
            
        #print '.', # debug
        
        # application logic
        if SensorMode == 1: # binary sensor enabled
            LSW=s.get_value('LSW','dichannels') # tuple bin ana
            #print('sensor states',LSW) # debug
            res=s.set_membervalue('LRW',2,LSW[0],'dichannels') # binary sensor state to LRW member2
            if res > 0:
                print('sensor value update FAILED for LRW member 2 to ',LSW[0]) # debug
        
        LRW=s.get_value('LRW','dichannels') # lighting control, output=member1
        print('LRW',LRW) # debug
        if round(LRW[0]) <> round((LRW[1]|LRW[2]|LRW[3])): # relay toggle needed if any of the input parameters is not 0
            s.setby_dimember_do('LRW',1,(LRW[1]|LRW[2]|LRW[3])) # svc, member, value. writing dochannel that corresponds to the given member of LRW        
            msg='changed lighting state to '+str(LRW[1]|LRW[2]|LRW[3])
            
        
        
        #elif:
        #    pass # more rules
        
        ##########################################
        
        if len(msg)>0:
            print(msg)
            udp.syslog(msg)
            msg=''
        # app logic end
        #time.sleep(0.1)  # main loop takt 0.1, debug jaoks suurem
        
    # main loop end, exit from application