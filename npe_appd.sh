#!/bin/sh
cd /mnt/nand-user/d4c
HOSTNAME='techbase'; export HOSTNAME

logger  -t d4c /mnt/nand-user/d4c/appd.sh start # to /mnt/mtd/messages

LOG=appd.log

date > /dev/ttyAPP0  # to end long blue signal
(echo -n "##### appd.sh start ####  "; date) >> $LOG

#exit

######## endless loop  to keep app running #################
app=tartuvalgustus.py # controller application
rescue=tartuvalgustus_rescue.py #  this will be started if the latest

while true
do
   (echo -n "${app} restart "; date) >> $LOG
   ### python $app 1>>$LOG 2>> $LOG  # debug mode
   ./python_alive.sh 111 & # first process to avoid killing too early
   ./udpconn_alive.sh 111 & # first process to avoid restart gprs too early
   
   logger  -t d4c /mnt/nand-user/d4c/python tartuvalgustus start # to /mnt/mtd/messages
   python $app 1>>/dev/null 2>> $LOG
   
   sleep 5

   count=`./ps1 tartu | grep -v appd.sh | wc -l`
   if [ $count -gt 0 ]; then # hanging processes to be killed!
       logger -t d4c /mnt/nand-user/d4c/appd.sh going to kill processes with tartu
       ./pskill tartu
   fi

   sleep 10 # limit the numb
done
