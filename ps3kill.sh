#!/bin/sh
#for techbase npe may 2014 neeme
#silent execution, use with caution

if [ "$3" = "" ]
then
   echo "params: if no $1 then kill $2 if $3 exists"; sleep 1
fi

#echo par1 $1 par2 $2 par3 $3 # debug

if [ `./ps1 $3 | grep -v ps3kill | wc -l` -gt 0 ]; then # restarting parent exist
  if [ `./ps1 $1 | grep -v ps3kill | wc -l` -eq 0 ]; then # no processes matching
    echo going to kill $2 processes due to missing alive ps but existing parent $3 \
       | tee -a appd.log  # debug
    logger -t d4c going to kill $2 processes due to missing $1 but existing parent $2
    pslist=`/mnt/nand-user/d4c/ps1 $2 | grep -v ps3kill | grep -v $3 | cut -c1-5 \
       | tr '\n' ' '` # tr works here but not sed
    echo "$pslist" # debug
    exec="kill $pslist"
    echo "process $1 missing, going to $exec" # debug
    $exec
  else
    echo process matching $1 exists
  fi
else
  echo could not kill $2 due to no parent $3 found in ps list
fi

exit 0