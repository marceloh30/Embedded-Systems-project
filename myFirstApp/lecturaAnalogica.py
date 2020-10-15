import RPi.GPIO as GPIO
import time
from datetime import datetime
import math
import sys #importo sys para obtener parametros de la ejecucion.
import variablesWeb

##Suponemos que tanto LDR como termistor son siempre el mismo (o el mismo tipo),
##por lo tanto, los siguientes valores caracteristicos de los mismos seran fijos.

#Parametros de LDR y NTC:
Lo=390          # Lux
Ro_LDR=2.57**3  # Ro(Lo)- en Ohms
gama_LDR=0.8    # parametro caracteristico de LDR (Adimensionado)
To_NTC=25+273       # Kelvin
Ro_NTC=10**3    # Ro(To)- en Ohms
B = 3977        # B de NTC (Kelvin)

GPIO.setmode(GPIO.BCM)

#Pines por defecto de entrada y salida
a_pin = 18
b_pin = 23

##Este codigo se ejecuta con "Python lecturaAnalogica.py <"T" o "L">"
#Por lo tanto, obtendre tipo de lectura (Temp. o Lux)
if(str(sys.argv[1])=="T"):
    strArch = "valoresT.txt"
    #Mantengo pines
elif(str(sys.argv[1])=="L"):
    strArch = "valoresL.txt"
    #Redefino pines de entrada y salida para Lux
    a_pin = 17
    b_pin = 27
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

#Funcion para convertir la resistencia leida en Temp o Lux
def convertVar(res,tipo):
    valRet = 0.0
    if (tipo == "T"):
        valRet = 1 / ( math.abs(math.log(res/Ro_NTC))/B + 1/To_NTC )
    elif (tipo == "L"):
        valRet = Lo * math.pow(res/Ro_LDR,gama_LDR)
    else:
        valRet = -1 #Error inesperado
    return valRet

while True:

    #Obtengo de .txt de parametros configurables
    coso = 1.29/3.3
    R = analog_read()/(-math.log(1-coso)*550*10**-9)    
    valNum = convertVar(R,str(sys.argv[1]))
    valNum = math.trunc(valNum*10)/1 #Lo trunco a formato "T=x.x"
    #Creo string y escribo valor en strArch
    with open(strArch, "a") as f:
        strn=str(datetime.now())+","+str(valNum)+"\n"
        f.write(strn)
    time.sleep(variablesWeb.valoresIngresados[2]) #Espero ts entre medidas
    