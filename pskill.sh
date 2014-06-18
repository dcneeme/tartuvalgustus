#!/bin/sh
#for techbase npe may 2014 neeme
#silent execution, use with caution

logger -t d4c going to kill $1 processes
pslist=`/mnt/nand-user/d4c/ps1 $1 | grep -v pskill | cut -c1-5 | tr '\n' ' '` # tr works here but not sed

if [ `echo $pslist | wc -c` -gt 0 ]; then
    exec="kill $pslist"
    #echo $exec
    $exec
else
  echo no match for $1
fi

exit 0