#!bin/bash

echo Zona Elegida: $1

python3 /home/pi/Documents/myFirstApp/app.py $1 > /home/pi/Documents/logs/app.log 2>&1 &
python3 /home/pi/Documents/myFirstApp/lecturasExternas.py $1 > /home/pi/Documents/logs/lecturasExternas.log 2>&1 &
python3 /home/pi/Documents/myFirstApp/enviosAtrasados.py $1 > /home/pi/Documents/logs/enviosAtrasados.log 2>&1 &
python3 /home/pi/Documents/myFirstApp/alarma.py $1 > /home/pi/Documents/logs/alarma.log 2>&1 &
python3 /home/pi/Documents/myFirstApp/lecturaDigital.py $1 > /home/pi/Documents/logs/lecturaDigital.log 2>&1 &
python3 /home/pi/Documents/myFirstApp/lecturaAnalogica.py $1 T > /home/pi/Documents/logs/lecturaAnalogicaT.log 2>&1 &
python3 /home/pi/Documents/myFirstApp/lecturaAnalogica.py $1 L > /home/pi/Documents/logs/lecturaAnalogicaL.log 2>&1 &

