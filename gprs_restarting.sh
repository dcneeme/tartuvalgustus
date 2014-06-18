#!/bin/sh
# if no such processes are found, they have been not started during last $1 seconds.
# that condition must be checked via cron in every x minutes to take actions (kill)
if [ "$1" = "" ]; then
  echo num parameter required 
  exit 1
fi
sleep $1
