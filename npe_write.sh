#!/bin/sh
# write outputs of NPE_io
# for single write register only !!!

stdin=0
let $# || { read register value type; stdin=1; }

if [ $stdin -eq 0 ]; then # no std input
  #register=`expr $1 - 1`
  register=$1
    
    # do, po 100..106
    # di 100..107
    # ai 500..503 as di read from 300..303
    
  if [ -z "$2" ]; then
      
    value=$1
  else
    value=$2
  fi
fi
                  
                  
#echo params register $register value $value # debug
#echo "register $register writing with value $value"

if [ $register -gt 99 -a $register -lt 102 ]; then # DO1,DO2
    addr=`expr $register - 99`
    d="DO${addr}"
elif [ $register -gt 101 -a $register -lt 106 ]; then # PO1..PO4   
    addr=`expr $register - 101`
    d="PO${addr}"
elif [ $register -eq 1 ]; then # USER_LED, comm ok with server if on
    d="USER_LED" 
else
    echo 'invalid register' $register
    exit 1
fi

if [ $value -gt 0 ]; then
    s="+"
else
    s="-"
fi

npe "${s}${d}" 
#echo "npe ${s}${d}" # debug
exit 0

        