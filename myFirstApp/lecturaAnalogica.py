import RPi.GPIO as GPIO
import time
from datetime import datetime
import math
import sys #importo sys para obtener parametros de la ejecucion.

##Suponemos que tanto LDR como termistor son siempre el mismo (o el mismo tipo),
##por lo tanto, los siguientes valores caracteristicos de los mismos seran fijos.

#Parametros de LDR y NTC:
Lo=390          # Lux
Ro_LDR=2.57**3  # Ro(Lo)- en Ohms
gama_LDR=0.8    # parametro caracteristico de LDR (Adimensionado)
To=25+273       # Kelvin
Ro_NTC=10**3    # Ro(To)- en Ohms

GPIO.setmode(GPIO.BCM)

a_pin = 18
b_pin = 23

##Este codigo se ejecuta con "Python lecturaAnalogica.py <"T" o "L">"
#Por lo tanto, obtendre tipo de lectura (Temp. o Lux)
if(str(sys.argv[1])=="T"):
    strArch = "valoresT.txt"
elif(str(sys.argv[1])=="L"):
    strArch = "valoresL.txt"
else:
    print("Ocurrio un error interpretando argumento (tipo de archivo)")


def descarga():
    GPIO.setup(a_pin,GPIO.IN)
    GPIO.setup(b_pin,GPIO.OUT)
    GPIO.output(b_pin, False)
    time.sleep(0.1)
    
def carga():
    GPIO.setup(b_pin, GPIO.IN)
    GPIO.setup(a_pin, GPIO.OUT)
    GPIO.output(a_pin, True)
    t1 = time.time()
    count = 0 
    while not GPIO.input(b_pin):
        count = count + 1
        pass
    t2 = time.time()
    print(count)
    return (t2 - t1)

def analog_read():
    descarga()
    return carga()

##Main

##Pruebo abrir strArch, si no existe lo creo.
try:    
    with open(strArch,"r") as arch:
        print("Archivo",strArch,"existente.")

except Exception as e:
    #No existe archivo. Lo creo:
    with open(strArch, 'x') as f:
        print(e,"\nArchivo no existe. Creo el archivo:\n",str(f))

while True:

    #Obtengo de .txt de parametros configurables
    coso = 1.29/3.3
    R = analog_read()/(-math.log(1-coso)*550*10**-9)    
    

    #Creo string y escribo valor
    strn=str(datetime.now())+","+str(valNum)+"\n"
    f = open(strArch, "a")
    archT.write(strn)
    f.write(+"- R = "+str(R)+'\n')
    f.close()
    print(analog_read(), str(R))
    time.sleep(5)
    