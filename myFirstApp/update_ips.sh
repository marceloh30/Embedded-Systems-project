#!/bin/bash

#Recibo como parametro la zona
HOSTNAME=""
PUERTO=0
if [ "$1" = "Montevideo" ]; then
  HOSTNAME=obligatorio.ddns.net
  PUERTO=5555
else #Supongo zona Montevideo o Salinas
  HOSTNAME=oblmhjf.ddns.net
  PUERTO=8081
fi

LOGFILE=/home/pi/Documents/obl/logs/ufw_ddnsip.log

Current_IP=$(host $HOSTNAME | head -n1 | cut -f4 -d' ')
echo anda: $Current_IP, con $HOSTNAME Y $PUERTO, log: $LOGFILE
if [ $LOGFILE="" ] ; then
  sudo ufw insert 6 allow from $Current_IP to any port $PUERTO
  sudo ufw insert 6 allow from $Current_IP to any port 8080
  echo $Current_IP > $LOGFILE
else

  Old_IP=$(cat $LOGFILE)

  if [ "$Current_IP" = "$Old_IP" ] ; then
    echo IP no cambio aun.
  else
    sudo ufw delete allow from $Old_IP to any port $PUERTO
    sudo ufw delete allow from $Old_IP to any port 8080
    sudo ufw insert 6 allow from $Current_IP to any port $PUERTO
    sudo ufw insert 6 allow from $Current_IP to any port 8080
    echo $Current_IP > $LOGFILE
    echo La tabla de permisos de ufw fue actualizada.
  fi
fi
