#!/bin/sh
# query or set digital inputs and outputs from NPE_io of Techbase PL
# neeme june 2014
# type w writes to npe_io, r reads, p forks subprocess over socat , b reads from subprocess over socat
# 10.06.2014 neeme
# register must be unique over types! types: r read, w write, p process form, b send data back
#registers in use: 1, 2, 3, 10,     100-104, 200-206, (400-411), 500-503
#           led, pyalive, udpalive, do,      di,      (count),   ai 

#use from cli on npe: ./npe_io.sh 100 1 r
# or via socat using netcat: echo "100 2 r" | netcat -w1 -u 10.0.0.121 44441
# 2541 root     /bin/sh /mnt/nand-user/d4c/socatd
# 2544 root     ./socat -t5 UDP4-RECVFROM:44441,reuseaddr,fork SYSTEM:/mnt/nand-user/d4c/npe_io.sh

stdin=0
LOG=/tmp/appd.log

let $# || { read register count type; stdin=1; }  

if [ $stdin -eq 0 ]; then # no std input
  register=$1
  
    # do, po 100..106
    # di 100..107
    # ai 500..503 as di read from 300..303

    if [ ! "$3" = "" ]; then
        type=$3
        count=$2
    else
        echo invalid parameter count
        exit 1
    fi
fi


#echo params register $register count $count type $type >> $LOG # debug

if [ "$type" = "p" ]; then # fork a predefined (for security) process based on $register and $count
  if [ $register -eq 2 ]; then
    /mnt/nand-user/d4c/python_alive.sh $count & # python_alive
    exit 0
  elif [ $register -eq 3 ]; then # udp_alive
    /mnt/nand-user/d4c/udp_alive.sh $count &
    exit 0
  elif [ $register -eq 4 ]; then # watchdog restart, to be done if everything is ok
    watchdog -t $count /dev/watchdog & # npe will reboot if no rewrite in $count s. start watchdog in syscfg!
    exit 0
  else
    echo "illegal_register_${register}_and_type_${type}_combination"
    exit 1
  fi
fi

if [ "$type" = "b" ]; then # read some shell script
  if [ $register -eq 10 ]; then # getnetwork.sh, count must be 2 (equals to the number of var mebers in string to return)
    output=`/mnt/nand-user/d4c/getnetwork.sh | cut -d"/" -f1` # returns space separated mac and ip, avoid slash in response
    echo $register $output
    #echo npe_io.sh returned $register $output >> $LOG #debug
    exit 0
  
  elif [ $register -eq 11 ]; then # vpn status. count must be 1 (equals to the number of var mebers in string to return)
    output=`vpn status | grep STATUS | cut -d":" -f2` # slow, use type b not bs
    if [ "$output" = "" ]; then
        output="OFF"
    fi
    echo $register $output
    #echo npe_io.sh returned $register $output >> $LOG #debug
    exit 0
  else
    echo "illegal_register_${register}_and_type_${type}_combination" 
    exit 1
  fi
fi

if [ "$type" = "w" ]; then # write
    value=$count
    if [ $register -gt 99 -a $register -lt 102 ]; then # DO1,DO2
        addr=`expr $register - 99`
        d="DO${addr}"
    elif [ $register -gt 101 -a $register -lt 106 ]; then # PO1..PO4   
        addr=`expr $register - 101`
        d="PO${addr}"
    elif [ $register -eq 1 ]; then # USER_LED, comm ok with server if on
        d="USER_LED" 
    else
        echo 'invalid register' $register and type $type combination 
        exit 1
    fi

    if [ $value -gt 0 ]; then
        s="+"
    else
        s="-"
    fi

    npe "${s}${d}" 
    #echo "npe ${s}${d}" # debug
    exit 0  # write done
elif [ "$type" = "r" ]; then # read, type r or rs
    output=$register
    c=0
    #for (( 0; c < $count; c++ )) # does not work on npe
    while [ $c -lt $count ]
    do
        ana=0
        c=`expr $c + 1`
        #register=`expr $register + 1`
        #echo "register $register reading, count $count type $type"

        if [ $register -gt 99 -a $register -lt 102 ]; then # DO1,DO2
            addr=`expr $register - 99`
            d="DO${addr}"
        elif [ $register -gt 101 -a $register -lt 106 ]; then # PO1..PO4   
            addr=`expr $register - 101`
            d="PO${addr}"
        elif [ $register -gt 199 -a $register -lt 207 ]; then # DI1..DI7   
            addr=`expr $register - 199`
            d="DI${addr}"
        elif [ $register -eq 207 ]; then # DIW   
            d='DIW'
        elif [ $register -gt 199 -a $register -lt 207 ]; then # DI1..DI7   
            addr=`expr $register - 201`
            d="DI${addr}"
        elif [ $register -gt 299 -a $register -lt 303 ]; then # AI1..AI3 as  DI   
            addr=`expr $register - 299`
            ana=2 # special flag
            d="AI${addr}"
        elif [ $register -eq 1 ]; then # USER_LED   
            d="USER_LED"
        elif [ $register -eq 303 ]; then # AIV as di   
            d="AIV"
            ana=2 # special
        elif [ $register -gt 499 -a $register -lt 503 ]; then # AI1..AI3 as 
            addr=`expr $register - 499`
            d="AI${addr}"
            ana=1
        elif [ $register -eq 503 ]; then # AIV   
            d="AIV"
            ana=1
        else
            echo "invalid_register_${register} and type ${type} combination"
            exit 1
        fi

        
        if [ $ana -eq 0 ]; then # npe DI/DO
            #echo "npe ?${d}"; out=1 # debug
            out=`npe "?${d}"; echo $?`  # on npe
        elif [ $ana -eq 2 ]; then # npe AI as DI
            out=`npe "?${d}" > /dev/null; echo $?`
        else
            out=`npe "?${d}"`  # npe AI  - hex!
            #echo "npe ?${d}"; out=100 # debug
        fi
        output="${output} ${out}"
        register=`expr $register + 1`
    done
#echo npe_io.sh returning $output >> $LOG #debug
echo $output
exit 0 # read done
fi


        