#!/bin/sh
#techbase variant, bin/sh nmitte /usr/bin/bash
#neeme takis 2013
if [ "$1" = "" ]; then
    iface="ether"
else
    iface=$1
fi
#ip addr | cut -c5- | grep -A1 $iface | tr -d "\n" | tr -d ":" | tr '[a-f]' '[A-F]' | cut -d" " -f2,5 # kui mac allub syscfg-le
#exit 0

# kui ei allu syscfg poolt maaratule
mac=`cat /mnt/mtd/syscfg | grep HOST_MAC | cut -d"=" -f2 | cut -d" " -f1 | sed 's/://g'`

ipa=`ip addr`
if [ `echo "$ipa" | grep eth0 | grep DOWN | wc -l` -gt 0 ]; then
  # echo eth0 down # debug
  ip=`echo "$ipa" | cut -c5- | grep -A2 tun0 | grep inet | cut -d" " -f2`
  if [ "$ip" = "" ]; then
    ip=`echo "$ipa" | cut -c5- | grep -A2 ppp0 | grep peer | cut -d" " -f2`
  fi
else
  ip=`echo "$ipa" | cut -c5- | grep -A2 eth0 | grep inet | cut -d" " -f2`
fi
echo $mac $ip

# puudus- kui eth kasutusel, siis vpn ip ei anna!
