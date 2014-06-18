#!/bin/sh
# if no such processes are found, they have been not started during last $1 seconds.
# that condition must be checked via cron in every x minutes to take actions (kill)

sleep $1
