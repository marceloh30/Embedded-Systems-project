#!/bin/bash
##Recibo parametro ($1): zona elegida ("Salinas" o "Montevideo")
echo Zona elegida: $1
python3 /home/pi/Desktop/obl/myFirstApp/app.py $1 &
python3 /home/pi/Desktop/obl/myFirstApp/lecturaDigital.py $1 &
python3 /home/pi/Desktop/obl/myFirstApp/lecturasExternas.py $1 &
python3 /home/pi/Desktop/obl/myFirstApp/enviosAtrasados.py $1 &
python3 /home/pi/Desktop/obl/myFirstApp/alarma.py $1 &
python3 /home/pi/Desktop/obl/myFirstApp/lecturaAnalogica.py $1 T &
python3 /home/pi/Desktop/obl/myFirstApp/lecturaAnalogica.py $1 L &

