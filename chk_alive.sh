#!/bin/sh
# watch for $1 process(es), if none, kill $2 if $3 is present 
# usage ./chk_alive.sh sleep tartu
# if $1 is not in ps list and $3 is, then kill $2

LOG=chk_alive.log

let $# || { echo No arguments supplied; exit 1; }  # Exit if no arguments!

proc=$1  # python_alive (sisaldab vaid sleepi, kuid sleep voib esineda ka muidu!)
killproc=$2 # tartu
appd=$3 # appd

cd /mnt/nand-user/d4c

count=`./ps1 $proc | grep -v chk_alive.sh | wc -l`
if [ $count -gt 0 ]; then # ok
    echo $count $proc exist in ps list
    ./ps1 $proc # debug
    exit 0
else
    count=`./ps1 $ikillproc | grep -v chk_alive.sh | wc -l`
    if [ $count -eq 0 ]; then #  no processes to kill
        echo no $killproc exist in ps list
        exit 0
    fi
fi

echo going to kill $killproc if $appd present # debug

# no $proc processes found, kill all matching $killproc if appd.sh is present
if [ `./ps1 $appd | grep -v chk_alive.sh | wc -l` -gt 0 ]; then # appd.sh exists to restart
    echo kill $killproc permitted as $appd is present # debug
    ./pskill.sh $killproc chk_alive.sh # exclude the process defined by second parameter
    (echo -n "killed $killproc due to no $proc in ps list "; date) >> $LOG
else
    (echo -n "$killproc frozen but NOT killed due to no $appd in ps list "; date) >> $LOG
fi 
exit 0

        