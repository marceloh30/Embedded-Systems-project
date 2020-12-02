#!/bin/bash

echo Zona Elegida: $1
python3 /home/pi/Documents/obl/myFirstApp/app.py $1 > /home/pi/Documents/obl/logs/app.log 2>&1 &
python3 /home/pi/Documents/obl/myFirstApp/lecturasExternas.py $1 > /home/pi/Documents/obl/logs/lecturasExternas.log 2>&1 &
python3 /home/pi/Documents/obl/myFirstApp/enviosAtrasados.py $1 > /home/pi/Documents/obl/logs/enviosAtrasados.log 2>&1 &
python3 /home/pi/Documents/obl/myFirstApp/alarma.py $1 > /home/pi/Documents/obl/logs/alarma.log 2>&1 &
python3 /home/pi/Documents/obl/myFirstApp/lecturaDigital.py $1 > /home/pi/Documents/obl/logs/lecturaDigital.log 2>&1 &
python3 /home/pi/Documents/obl/myFirstApp/lecturaAnalogica.py $1 T > /home/pi/Documents/obl/logs/lecturaAnalogicaT.log 2>&1 &
python3 /home/pi/Documents/obl/myFirstApp/lecturaAnalogica.py $1 L > /home/pi/Documents/obl/logs/lecturaAnalogicaL.log 2>&1 &

