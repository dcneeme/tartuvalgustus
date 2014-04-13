#!/usr/bin/python
# test_tartu.py


#from uniscada import * # achannel ja dchannel impordivad sqlgenerali ja see jalle uniscada. 
from droidcontroller.achannels import *
from droidcontroller.dchannels import *
from droidcontroller.cchannels import *

a=Achannels() # both ai and ao
d=Dchannels()
c=Cchannels() 
udp.setID('000101100001') # tartu nr 1

# c.set_counter(1000,mba=1,regadd=400) # voi siis sta_reg ja member alusel
#stp=Setup()
#gc=GoogleCalendar()


################  MAIN #################

if __name__ == '__main__':
    stop=0
    got=None
    while stop == 0:
        stop = udp.unsent() # vana jama maha puhvrist
        stop = d.doall()  #  di koik mis vaja, loeb tihti, raporteerib muutuste korral ja aeg-ajalt asynkroonselt
        stop = c.doall() # loeb ja vahel ka raporteerib
        stop = a.doall() # ai koik mis vaja, loeb ja vahel raporteerib
        got = udp.comm() # loeb ja saadab udp, siin 0.1 s viide sees
        if got != None:
            print(got)
        time.sleep(0.5)  # main loop takt, debug jaoks suurem
        
        # miks vaid esimese ringiga onnestus?? sest et renotifydelay oli 240 s...
    