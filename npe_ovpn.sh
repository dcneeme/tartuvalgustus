#/bin/sh
#vpn stop
#sleep 3
#vpn start /mnt/mtd/openVPN/config/itvilla.conf

if [ `ip addr | grep tun | grep UP | wc -l` -eq 0 ]; then # no double etc starting
  vpn start /mnt/mtd/openVPN/config/itvilla.conf
else
  echo vpn already active...
fi
