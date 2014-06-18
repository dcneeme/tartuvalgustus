#!/bin/sh
# Techbase NPE pythons app & ovpn install

# d4c, droidcontroller, requests, pymodbus
# /mnt/mtd/rcs, sysconfig, add_cron
# ovpn
# *.sql

#scp root@10.0.0.253:/srv/scada/droidsimu/tartuvalgustus/npe_install.sh .

echo going to install techbase npe for tartuvalgustus...
pwd

#cd /mnt/nand-user
scp root@10.0.0.253:/srv/scada/droidsimu/tartuvalgustus/d4c.tar .

tar xvf d4c.tar
cd d4c
cd config
cp /mnt/nand-user/d4c/MainConfig.xml .
ln -s /mnt/nand-user/d4c d4c
cd d4c

softmgr update python
echo; sleep 2
softmgr -b Artur update libnpe
echo; sleep 2
softmgr -b Artur update imod

#In this packages (both - 1404301517) there is a new npe_service application that allow you to read changes of DI with frequency about 50Hz. In iMod we upgrade the DIO reading time - right now iMod is reading over 12 impulses per second. 
#Please use the element:
#parameter_db="false" in iMod configuration 

echo modifying 14 to 12 where STAMP; sleep 2
#vi /mnt/nand-user/iMod/scripts/respawn
cat /mnt/nand-user/iMod/scripts/respawn | sed 's/print $14/print $12/' > /mnt/nand-user/iMod/scripts/respawn.tmp
mv /mnt/nand-user/iMod/scripts/respawn.tmp /mnt/nand-user/iMod/scripts/respawn

#change the line:
#STAMP=`stat -t /tmp/status | awk '{print $14}'`
#to
#STAMP=`stat -t /tmp/status | awk '{print $12}'`
 
echo changing failedtrigger 3 to 6; sleep 2
#vi /mnt/mtd/gprs/bin/gprs_reconnect and element:
cat /mnt/mtd/gprs/bin/gprs_reconnect | sed 's/failedtrigger=3/failedtrigger=6/' > /mnt/mtd/gprs/bin/gprs_reconnect.tmp
mv /mnt/mtd/gprs/bin/gprs_reconnect.tmp /mnt/mtd/gprs/bin/gprs_reconnect
#failedtrigger=3 # selle asemel 6

#Also please in script 
echo removing -s 8 everywhere; sleep 2
#vi /mnt/mtd/gprs/modem_plugins/MU609_new
cat /mnt/mtd/gprs/modem_plugins/MU609_new | sed 's/-s 8 //g' > /mnt/mtd/gprs/modem_plugins/MU609_new.tmp
mv /mnt/mtd/gprs/modem_plugins/MU609_new.tmp /mnt/mtd/gprs/modem_plugins/MU609_new

#please modify the ping_status() and check() function - you need to remove the -s 8 element in ping action 
#we discovered that there can be a packages lost when in ping application we are using the -s parameter 
#this allow to send data in packets with defined amounts of bytes (default it`s 56 - we changed it to 8).

echo changing syscfg... edit mac then; sleep 2

#  neid kahte rida muudab urmase script
#| sed 's/VPN_SERVER_IP1=demo.imodcloud.com/VPN_SERVER_IP1=195.222.15.51/' \
#| sed 's/VPN_SERVER_IP2=imodcloud.com/VPN_SERVER_IP2=195.222.15.51/' \

cat /mnt/mtd/syscfg | sed 's/HOST_IP=/HOST_IP=10.0.0.121 # /' | sed 's/GW_IP=/GW_IP=10.0.0.253 # /' \
    | sed 's/START_DHCP=Y/START_DHCP=N/' | sed 's/CET-1CEST/CET-2CEST/' | sed 's/pl.pool.ntp.org/ee.pool.ntp.org/' \
    | sed 's/START_APACHE=Y/START_APACHE=N/' | sed 's/GPRS_APN_NAME=/GPRS_APN_NAME=internet.emt.ee/' \
    | sed 's/GPRS_PING_IP_1=208.67.222.222/GPRS_PING_IP_1=195.222.15.51/' | sed 's/AUTOSYNC_TIME=OFF/AUTOSYNC_TIME=ON/' \
    | sed 's/VPN_AUTOSTART=Y/VPN_AUTOSTART=N/' \
    | sed 's/HOST_MAC=/HOST_MAC=00:01:01:10:00:05 # /' \
    | sed 's/START_FTP=Y/START_FTP=N/' | sed 's/START_TELNET=Y/START_TELNET=N/' | sed 's/GPRS_RECONNECT=N/GPRS_RECONNECT=Y/'  > /mnt/mtd/syscfg.tmp
    
mv /mnt/mtd/syscfg.tmp /mnt/mtd/syscfg
vi /mnt/mtd/syscfg # kontrolliks

addcron=`cat << EOF
   
#use the following instead of crontab -e, updates by name if already exist
cron_add d4c1 "*/2 * * * *      /mnt/nand-user/d4c/chk_alive.sh python_alive tartu appd > /dev/null # python alive chk"
cron_add d4c2 "*/3 * * * *      /mnt/nand-user/d4c/chk_modbus.sh > /dev/null #  test and restart imod and modbusd" 
cron_add d4c3 "*/2 * * * *      /mnt/nand-user/d4c/chk_conn.sh > /dev/null # connectivity chk resulting gprs restart if needed"

/mnt/nand-user/d4c/mbd & # keep modbusd running
/mnt/nand-user/d4c/appd.sh & # keep python apps running

gprs connect # igaks juhuks, peaks ka syscfg alusel startima...
#vpn start /mnt/mtd/openVPN/config/itvilla.conf # sed laheb hiljem vaja vaid app katkemisel

EOF`

echo -e "${addcron}" >> /mnt/mtd/rcs

sleep 2

echo openvpn now...

softmgr update openvpn
softmgr update openssl

cat > /mnt/mtd/openVPN/keys/ca-itvilla.crt <<EOF
-----BEGIN CERTIFICATE-----
MIIDYzCCAsygAwIBAgIJAKZ4DDq9LEQJMA0GCSqGSIb3DQEBBQUAMH8xCzAJBgNV
BAYTAkVFMREwDwYDVQQIEwhIYXJqdW1hYTEQMA4GA1UEBxMHVGFsbGlubjERMA8G
A1UEChMISVQgVmlsbGExFzAVBgNVBAMTDmFzdXN2cG4tc2VydmVyMR8wHQYJKoZI
hvcNAQkBFhBjb3VnYXJAcmFuZG9tLmVlMB4XDTA3MDcyNDA4NDUxOFoXDTE3MDcy
MTA4NDUxOVowfzELMAkGA1UEBhMCRUUxETAPBgNVBAgTCEhhcmp1bWFhMRAwDgYD
VQQHEwdUYWxsaW5uMREwDwYDVQQKEwhJVCBWaWxsYTEXMBUGA1UEAxMOYXN1c3Zw
bi1zZXJ2ZXIxHzAdBgkqhkiG9w0BCQEWEGNvdWdhckByYW5kb20uZWUwgZ8wDQYJ
KoZIhvcNAQEBBQADgY0AMIGJAoGBALguMat+mULiFIhPPlm8XEN1Un/Ino9TNMDR
fCeMd8rh/yPA5ZmMPdvzS5IP8BA1rB5Mm6A39fWlka3xGrG8LxvLfJE0M9hQ7D+Q
jURyDVZ4T0YdZUba0yDC8wPNQDWJRAG6kMZozzoNyW0TYARYsrveKvUAfu8Od0Ky
WaJo/zYDAgMBAAGjgeYwgeMwHQYDVR0OBBYEFNbD1DjewTTm/srEJd0amRepe/Bn
MIGzBgNVHSMEgaswgaiAFNbD1DjewTTm/srEJd0amRepe/BnoYGEpIGBMH8xCzAJ
BgNVBAYTAkVFMREwDwYDVQQIEwhIYXJqdW1hYTEQMA4GA1UEBxMHVGFsbGlubjER
MA8GA1UEChMISVQgVmlsbGExFzAVBgNVBAMTDmFzdXN2cG4tc2VydmVyMR8wHQYJ
KoZIhvcNAQkBFhBjb3VnYXJAcmFuZG9tLmVlggkApngMOr0sRAkwDAYDVR0TBAUw
AwEB/zANBgkqhkiG9w0BAQUFAAOBgQC0LGcNb42XdZKM4n5eGsrKQqAV89nKz0On
VC60Ped4e/DwP1DF6MvhzQdU9tHHVSRYVMB0JWzN4J4AGyMbVqhBblOxEj6YL2cI
a+Mfpd77SBhu+j1mwKZoqjalbJIjV7BFOe1qwowq7kBlwCkUdOPcmiHbIWR3qfLV
ynHaHHqgog==
-----END CERTIFICATE-----
EOF

cat > /mnt/mtd/openVPN/keys/techbase-npe.crt <<EOF
-----BEGIN CERTIFICATE-----
MIIDNjCCAp+gAwIBAgIBEDANBgkqhkiG9w0BAQQFADBiMQswCQYDVQQGEwJFRTER
MA8GA1UECBMISGFyanVtYWExEDAOBgNVBAcTB1RhbGxpbm4xETAPBgNVBAoTCElU
IFZpbGxhMRswGQYJKoZIhvcNAQkBFgx1cm1hc0BhdXYuZWUwHhcNMTQwNTA3MDcw
MjA1WhcNMjQwNTA0MDcwMjA1WjBrMQswCQYDVQQGEwJFRTERMA8GA1UECBMISGFy
anVtYWExETAPBgNVBAoTCElUIFZpbGxhMRUwEwYDVQQDEwx0ZWNoYmFzZS1ucGUx
HzAdBgkqhkiG9w0BCQEWEG5lZW1lQGl0dmlsbGEuZWUwgZ8wDQYJKoZIhvcNAQEB
BQADgY0AMIGJAoGBANo/U4RLlX5vbVGjK3Tbh77yS6cS4OeA/q5KzsRBDY7vxnC6
DEAlDr2FgEEFgSC+Cj473ZgqsHk0cPXGP5G/E9bbsMfAaQLQFc6dKNOmlCbzW9mZ
rIH+uK5fE1B3bXofLiVoCUzWK/D2Z3qEQq++/DPY0DzPdLHerSuG5rBVqaFtAgMB
AAGjgfIwge8wCQYDVR0TBAIwADAsBglghkgBhvhCAQ0EHxYdT3BlblNTTCBHZW5l
cmF0ZWQgQ2VydGlmaWNhdGUwHQYDVR0OBBYEFKJlGUrx1sIqCxX+Q8x7ZaqzvlBf
MIGUBgNVHSMEgYwwgYmAFIyk/0Q9Rj7kBT+vZQShq9Hj+lcRoWakZDBiMQswCQYD
VQQGEwJFRTERMA8GA1UECBMISGFyanVtYWExEDAOBgNVBAcTB1RhbGxpbm4xETAP
BgNVBAoTCElUIFZpbGxhMRswGQYJKoZIhvcNAQkBFgx1cm1hc0BhdXYuZWWCCQCu
8eHiUE/Y6TANBgkqhkiG9w0BAQQFAAOBgQBIrrpo1AmSOKX1BNsa5eKuQvYORaf3
7gFkJqs7RhnRQtRYbni/aCJmSrCwn5NWCCYM0tgyYvEUvafujCcLY+LHQSqcnzxQ
WZIvciyzqfeGisT418W1cNCsISECWG3mIoRi9KMVjwEk5TtrnXaLLc8Wft1A/KrQ
WyUyficnhD5nfw==
-----END CERTIFICATE-----
EOF

cat > /mnt/mtd/openVPN/keys/techbase-npe.key <<EOF
-----BEGIN PRIVATE KEY-----
MIICeAIBADANBgkqhkiG9w0BAQEFAASCAmIwggJeAgEAAoGBANo/U4RLlX5vbVGj
K3Tbh77yS6cS4OeA/q5KzsRBDY7vxnC6DEAlDr2FgEEFgSC+Cj473ZgqsHk0cPXG
P5G/E9bbsMfAaQLQFc6dKNOmlCbzW9mZrIH+uK5fE1B3bXofLiVoCUzWK/D2Z3qE
Qq++/DPY0DzPdLHerSuG5rBVqaFtAgMBAAECgYB8tCh9dE7EQtj9B7YB/JpQ8dNm
cLQPs7ZSUq5Yly8vGDSUHsp3MHV+tzR0cre4xL3Hl59jnijd6KgO1ytllP+4+92s
hWb+S2fy1hu49x3ZRw9Y0CCYEk3oaVL2u84zC2Op8H18KaSUkGnhFxPhOjZV7jfA
+lyLhJHmoxgKi5zGhQJBAPTqTbSqFRhjZdufLG4NtnlsMZEbcmTBYTm4fAX7ARSM
trHonVoKOaIhY2Bk30J24fzkTK0154DdHGmvaqKpI18CQQDkIAluNnh/x+ollWQD
kn02iFN9/5GfTGpj4JbNMq8epHxuTyQF3W73eXSCz0H9RbhtdJ9LG/lRTKSTqhID
GdqzAkEAkoLby1j316gWleRJquhvIYIUwM6fhyCb7fCr2NQIGGf5HsKd5vA4/AFn
NpIBcPw3Qpa8O94ESHV9eseiTf5KlwJBAOQRx3vhh20xAD3c8mXD4d1QRDDW/s7F
RiRemEXEY2H+Tsy14Kzgah2O1tYkwbOmLbF4g/1ClWsbdfqPcHybL5MCQQDoiWe2
wd7F56LW9RHeh0/wvXLiMeeTMb4gA5bbUtD0Kwfl/d2WLDIuiXMKaHs7kx9UqNVc
2FLn6RZYJ2in/3Sd
-----END PRIVATE KEY-----
EOF

cat > /mnt/mtd/openVPN/config/itvilla.conf <<EOF
client
dev tun
remote 195.222.15.51 41194
nobind
proto tcp-client
tls-client
ca /mnt/mtd/openVPN/keys/ca-itvilla.crt
cert /mnt/mtd/openVPN/keys/techbase-npe.crt
key /mnt/mtd/openVPN/keys/techbase-npe.key
persist-key
persist-tun
comp-lzo
EOF

sed -i "s/\(VPN_PING_IP=\).*/\\110.200.0.1/" /mnt/mtd/syscfg
sed -i "s/\(VPN_SERVER_IP.=\).*/\\1195.222.15.51 41194/" /mnt/mtd/syscfg

# --- start, status, stop
# ara jatta sisse vpn start Y /mnt/mtd/syscfg, see stardib (edutult) techbase vpn kui yhendus korraks katkeb!
vpn start /mnt/mtd/openVPN/config/itvilla.conf
vpn status
# vpn stop


echo vist on valmis... reboodi

#reboot






