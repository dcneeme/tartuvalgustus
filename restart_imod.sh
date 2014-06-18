#!/bin/sh
# restart imod

logger -t d4c restarting failing imod
/bin/imod start | grep started >> /mnt/nand-user/d4c/appd.log
