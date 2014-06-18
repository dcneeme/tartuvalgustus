#!/bin/sh
# restart imod or modbusd if no modbus response $retry times
# params: comm port, 502, 1502 or 44441


check(){
### checking the modbus (or socat) channel by port
    retry=6
    #echo "checking the modbus (or socat) channel by port $1 for mba $mba" # debug
    i=0
    while [ $i -ne $retry ];do
        if [ $1 -eq 502 ]; then
            ok=`modmas -p $1 -s $mba read:hold:100-102 | grep SUCCESS | wc -l` # imod
            exe="/bin/imod start | grep started >> $LOG"
            tolog=""
        elif [ $1 -eq 1502 ]; then
            ok=`modmas -p $1 -s $mba read:hold:1-2 | grep SUCCESS | wc -l` # modbusd
            exe="./pskill.sh modbusd"
            tolog="modbusd killed by chk_modbus.sh due to no response"
        elif [ $1 -eq 44441 ]; then # no $mba needed here
            ok=`./npe_io.sh 200 1 r | grep 200 | wc -l` # socat kaudu
            exe="./pskill.sh UDP4-RECVFROM"
            tolog="socat killed by chk_modbus.sh due to no response"
        else
            echo illegal parameter $1
            exit 1
        fi
        
        # $ok should be 1 if ok
        if [ $ok -eq 1 ]; then
            break
        fi
        i=$((i+1));
        sleep 1
    done

    if [ $i -eq $retry ];then
        logger -t d4c chk_modbus.sh $exe
        echo $exe
        $exe
        if [ "$tolog" = "" ]; then
            echo $tolog >> $LOG
        fi
    else
       echo check $1 result ok
    fi
}


#####  MAIN #######################
# check modbus channels on npe

if [ "$1" = "" ]; then
    echo parameter for port needed
    exit 1
else
    if [ ! $1 -gt 0 ]; then
        echo num parameter for port needed
        exit 1
    fi
fi

cd /mnt/nand-user/d4c

mba=`cat devices.sql | grep 1502 | grep -v "^\-\- " | head -1 | cut -d"," -f2`
LOG=/mnt/nand-user/d4c/appd.log

check $1 $mba
exit 0
