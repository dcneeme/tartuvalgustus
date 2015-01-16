#!/bin/sh
# find out if connectivity is ok. start by crontab
# pings testserver, it no success, restarts gprs
# if ping ok but no udpconn_alive in ps, start vpn
# should work with ethernet connectivity too.
# last change 19.06.2014

testserver="195.222.15.51"
langw1="10.0.0.253"
langw2="10.0.0.254"
LOG=/mnt/mtd/chk_conn.log # will not be erased on reboot
vpnconf=/mnt/mtd/openVPN/config/itvilla.conf

pingtest() {  # single ping test to $1
if ping -qc1 $1; then echo ping $1 ok; return 0; else echo ping $1 NOT ok; return 1; fi
}

upif() { # bitmap of interfaces that are up (1:eth0, 2:ppp; 3:tun)
out=0
iflist=`ip addr | grep "state UP"`
if [ `echo "$iflist" | grep eth0 | wc -l` -gt 0 ]; then
    out=`expr $out + 1`
fi
if [ `echo "$iflist" | grep ppp | wc -l` -gt 0 ]; then
    out=`expr $out + 2`
fi
if [ `echo "$iflist" | grep tun | wc -l` -gt 0 ]; then
    out=`expr $out + 4`
fi

if [ $out -gt 0 ]; then 
  echo $out
  exit 0
else
  echo 0
  exit 1
fi
}

defroute() {
#add default route $1 via eth0
route delete default
route add default gw $1 eth0
}

oklog() { # add CONN_OK if not there already
if [ `tail -1 $1 | grep OK | wc -l` -eq 0 ]; then
    (echo -n "CONN_OK "; date +%s) >> $1
else
    oksince=`tail -1 $1 | cut -d" " -f2`
    now=`date +%s`
    okfor=`expr $now - $oksince`
    echo conn ok for $okfor s
fi
}

losslog() { # add CONN_OK if not there already
if [ `tail -1 $1 | grep LOSS | wc -l` -eq 0 ]; then
    (echo -n "CONN_LOSS "; date +%s) >> $1
else
    lostsince=`tail -1 $1 | cut -d" " -f2`
    now=`date +%s`
    lostfor=`expr $now - $lostsince`
    echo conn lost for $lostfor s
fi
}

######################   MAIN  #########################

cd /mnt/nand-user/d4c/

if ! pingtest $testserver; then # conn probably lost
    sleep 10 # wait before retry
else
    #echo conn ok  # debug
    oklog $LOG
    exit 0
fi
    
if ! pingtest $testserver; then # conn surely lost
    echo "no ping response from ${testserver}"
    /bin/npe -USER_LED # yellow LED off 
    losslog $LOG
else
    echo conn ok on 2nd try
    oklog $LOG
    exit 0
fi
    
# no conn! is eth present?    
ifcode=`upif`
echo ifcode $ifcode # debug

if [ $ifcode -eq 1 ]; then
    echo eth0 up # debug
    if pingtest $langw1; then 
        defroute $langw1; 
    elif pingtest $langw2; then 
        defroute $langw2
    fi
fi
    
if pingtest $testserver; then echo conn ok; ip route; oklog $LOG; /bin/npe +USER_LED; exit 0; else echo conn still NOT ok; fi

#gs=`gprs status | grep STATUS`
#echo $gs

# edasi loodame npe gprs scripti peale kui sidet ikka pole, mis syscfg alusel toimib. lopuks teeme reboodi kui muu ei aita!
#gprs status

lastlog=`tail -1 $LOG`
if [ `echo "$lastlog" | tail -1 | grep "CONN_LOSS" | wc -l` -eq 0 ]; then # loss not detected before
    (echo -n "CONN_LOSS "; date +%s) >> $LOG 
else 
    losstime=`echo "$lastlog" | tail -1 | cut -d" " -f2`
    uptime=`cat /proc/uptime | cut -d"." -f1` # second no is total idle time
    now=`date +%s`
    if [ `expr $now - $losstime` -gt 1800 -a $uptime -gt 1800 ]; then # both uptime and conn loss above 30 min
        echo going to reboot due to conn loss and reboot at least 30 min ago
        reboot
    fi
fi

