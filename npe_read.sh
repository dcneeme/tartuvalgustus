#!/bin/sh
# query digital inputs and outputs from NPE_io
stdin=0

let $# || { read register count type; stdin=1; }  

if [ $stdin -eq 0 ]; then # no std input
  #register=`expr $1 - 1` 
  register=$1
  
# do, po 100..106
# di 100..107
# ai 500..503 as di read from 300..303

  if [ -z "$2" ]; then
  
    count=1
  else
    count=$2
  fi
fi

#echo params register $register count $count # debug
output=""
c=0
#for (( 0; c < $count; c++ )) # does not work on npe
while [ $c -lt $count ]
do
    ana=0
    c=`expr $c + 1`
    #register=`expr $register + 1`
    #echo "register $register reading"

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
        echo "invalid_register_${register}"
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
echo $output
#exit 0

        