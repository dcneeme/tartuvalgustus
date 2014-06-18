# chk_conn jupid

if     ] iflist then     
        status=`gprs status | grep STATUS` #  ok if ok
        if [ "$status" = "MUX_FAILED" ]; then
            logger -t d4c mux_failed... going to reboot
            reboot
        else
            ./conn_restart.sh & # for all other cases with no connectivity
        fi
    else
        echo connectivity ok
        logger -t d4c connectivity ok on second try based on ping $testserver
    fi
        
else
    echo connectivity ok
    exit 0
    
    logger -t d4c connectivity ok on first try based on ping $testserver
    
    # seda jargnevat jama pole vaja
    
    
    # chk if not alive in ps then vpn should be started / but only if if not active already
    count=`./ps1 alive | grep -v chk_conn.sh | wc -l`
    if [ $count -eq 0 ]; then # need for vpn
        /bin/npe -USER_LED # yellow LED off 
        if [ `vpn status | grep STATUS | grep ACTIVE | wc -l` -eq 0 ]; then # no active vpn
            echo starting vpn due to no alive in ps
            logger -t starting vpn due to no alive in ps
            vpn stop
            vpn start $vpnconf
            exit 0
        fi
    else
        /bin/npe +USER_LED # yellow LED on, udp conn ok, vpn no needed. 
        #vpn auto off? only if appd in ps...
    fi

fi
exit 0

#scp root@195.222.15.52:/srv/scada/droidsimu/tartuvalgustus/chk_conn.sh .
