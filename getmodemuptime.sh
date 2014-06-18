#!/bin/sh
# find out if connectivity is ok. start by crontab

testserver="195.222.15.51"
LOG=/mnt/nand-user/d4c/chk_conn.log
vpnconf=/mnt/mtd/openVPN/config/itvilla.conf

cd /mnt/nand-user/d4c/

if [ `ping -c3 $testserver | grep "0 packets received" | wc -l` -gt 0 ]; then # conn lost
    (echo -n "no ping response from ${testserver}, eaiting for retry "; date) | tee -a $LOG
    logger -t d4c no response to ping $testserver
    sleep 20 # wait before retry
    
    if [ `ping -c3 $testserver | grep "0 packets received" | wc -l` -gt 0 ]; then # conn lost
        (echo -n "no ping response again from ${testserver}, trying to restart gprs "; date) | tee -a $LOG
        logger -t d4c no response to ping again... going to restart gprs
        ./conn_restart.sh &
    else
        echo connectivity ok
        logger -t d4c connectivity ok on second try based on ping $testserver
    fi
        
else
    echo connectivity ok
    logger -t d4c connectivity ok on first try based on ping $testserver
    
    # chk if not alive in ps then vpn should be started
    count=`./ps1 alive | grep -v chk_conn.sh | wc -l`
    if [ $count -eq 0 ]; then # no need for auto vpn
        echo missing alive processes... starting vpn
        logger -t missing alive processes... starting vpn
        vpn stop
        vpn start $vpnconf
        #./ps1 $proc # debug
        exit 0
    fi

fi
exit 0
