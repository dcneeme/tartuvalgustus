#!/bin/sh
# for techbase only!

# start by watchdog script / crontab or from python
# param $1 simply gets logged, usable for reason.

LOG=/mnt/nand-user/d4c/conn_restart.log
proc=gprs_restarting.sh

count=`./ps1 $proc | grep -v conn_restart.sh | wc -l`
if [ $count -gt 0 ]; then # already restarting
    echo $proc exists in ps list... gprs already restarting
    #./ps1 $proc # debug
    exit 0
fi

# no connectivity
logger -t d4c $0 going to restart gprs and start vpn

echo trying to restore connectivity
./$proc 200 & # in 200 s restart can be avoided, if ps checked

vpn stop
gprs disconnect #
sleep 4
gprs connect # 
sleep 4
vpn start /mnt/mtd/openVPN/config/itvilla.conf # comment later if not needed any more

(echo -n "gprs (and possibly vpn) restarted for/by $1 at "; date) >> $LOG

