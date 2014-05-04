#!/bin/sh
#techbase variant, bin/sh nmitte /usr/bin/bash
# parameter ether or smthg

# mac vahetus tehtav /mnt/mtd/syscfg

#tagastab jargmise:

#[root@techbase /mnt/nand-user/d4c]# ./getnetwork.sh
#1883C404336C 10.0.0.121/24

#neeme 2013

if [ "$1" = "" ]; then
    iface="ether"
else
    iface=$1
fi
ip addr | cut -c5- | grep -A1 $iface | tr -d "\n" | tr -d ":" | tr '[a-f]' '[A-F]' | cut -d" " -f2,5
