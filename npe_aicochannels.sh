#/bin/sh
# scp root@10.0.0.253:/srv/scada/droidsimu/tartuvalgustus/npe_aicochannels.sh .
# asendame aicochannels konfis loendimoodulite aadressid oigetega, aluseks 14 15 17

cd /mnt/nand-user/d4c
pwd
sleep 1
scp root@10.0.0.253:/srv/scada/droidsimu/tartuvalgustus/*14_15*.sql .

echo -n " anna esimese loendimooduli mba: ";read n1
if [ "$n1" = "" ]; then
   echo katkestan
   exit 0
fi

echo -n " anna teise loendimooduli mba voi XX kui rohkem pole: ";read n2
if [ "$n2" = "" ]; then
   echo katkestan
   exit 0
fi

echo -n " anna kolmanda loendimooduli mba voi XX kui rohkem pole: ";read n3
if [ "$n3" = "" ]; then
   echo katkestan
   exit 0
fi


echo aadresside muutmine... kui kanaleid on rohkem lisa hiljem kasitsi vastav plokk /mnt/nand-user/d4c/aicochannels.sql

if [ ! -f aico14_15_17channels.sql ]; then
    if [ `cat aicochannels.sql | grep 14  | grep 15 | grep 17 | wc -l` -gt 0 ]; then # algandmed olemas
        cp aicochannels.sql aico14_15_17channels.sql
        echo algfail aico14_15_17channels.sql puudub... aicochannels.sql sobib... kopeeritud
    else
        echo puudub sobiv algfail kus oleks loendiaadressid 24 15 17... katkestan...
        exit 1
    fi
else
    echo aico14_15_17channels.sql oli olemas...
fi

if [ ! -f aico14_15_17channels.sql ]; then  # igaks juhuks, tegelikult pole vaja
    echo aico14_15_17channels.sql puudub... katkestan...
    exit 1
fi

if [ ! -f devices14_15_17.sql ]; then
    echo devices14_15_17channels.sql puudub...
    scp root@10.0.0.253:/srv/scada/droidsimu/tartuvalgustus/devices14_15_17.sql .
    #exit 1
fi

cat aico14_15_17channels.sql | sed 's/\"//g' >  aico14_15_17channels.tmp
mv aico14_15_17channels.tmp aico14_15_17channels.sql
cat aico14_15_17channels.sql

cat aico14_15_17channels.sql | sed "s/VALUES('14',/VALUES('$n1',/g" \
    | sed "s/VALUES('15',/VALUES('$n2',/g" \
    | sed "s/VALUES('17',/VALUES('$n3',/g" > aicochannels.sql

# | sed "s/INSERT INTO 'aicochannels' VALUES('1','40/-- INSERT INTO 'aicochannels' VALUES('1','40/g"
    
echo valmis... testime ja vaata yle
sleep 1

if echo -e ".read aicochannels.sql\n.quit\n" | sqlite3
then
   echo tundub korras...
else
   echo midagi oli vist valesti...
   sleep 2
fi

if [ `cat aicochannels.sql | grep XX | wc -l` -gt 0 ]; then
    echo kustuta need plokid kus X esineb. valjumiseks 2x ESC
    mcedit aicochannels.sql
else
    echo aicochannels peaks olema korras... vaata yle
    more aicochannels.sql
fi


echo nyyd devices...
sleep 2

cat devices14_15_17.sql | sed "s/VALUES(2,14,/VALUES(2,$n1,/g" \
    | sed "s/VALUES(3,15,/VALUES(3,$n2,/g" \
    | sed "s/VALUES(4,17,/VALUES(4,$n3,/g" \
    | sed "s/10.0.0.122:/127.0.0.1:/g"  \
    | sed "s/10.0.0.121:/127.0.0.1:/g" > devices.sql


if echo -e ".read devices.sql\n.quit\n" | sqlite3
then
   echo tundub korras...
else
   echo midagi oli vist valesti...
   sleep 2
fi

if [ `cat devices.sql | grep XX | wc -l` -gt 0 ]; then
    echo kustuta need read kus X esineb. valjumiseks 2x ESC
    mcedit devices.sql
else
    echo devices peaks olema korras... vaata yle
    more devices.sql
fi
