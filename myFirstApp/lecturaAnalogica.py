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
To_NTC=25+273       # Kelvin
Ro_NTC=10**3    # Ro(To)- en Ohms
B = 3977        # B de NTC (Kelvin)

GPIO.setmode(GPIO.BCM)

#Pines por defecto de entrada y salida
a_pin = 18
b_pin = 23
#Capacitancia por defecto (para evitar errores)
C = 0
R0 = 0
##Este codigo se ejecuta con "Python lecturaAnalogica.py <"T" o "L">"
#Por lo tanto, obtendre tipo de lectura (Temp. o Lux)
#Cambio tambien C y pines si es necesario
if(str(sys.argv[1])=="T"):
    strArch = "valoresT.txt"
    with open("configuracion.txt","r") as confi:
        linea = confi.readlines()
        C = float(linea[6].split("= ")[1])*10**-9 #Ct
        R0 = float(linea[5].split("= ")[1])       #Rt
    #Mantengo pines
elif(str(sys.argv[1])=="L"):
    strArch = "valoresL.txt"
    #Redefino pines de entrada y salida para Lux
    with open("configuracion.txt","r") as confi:
        linea = confi.readlines()
        C = float(linea[8].split("= ")[1])*10**-9 #Cl
        R0 = float(linea[7].split("= ")[1])       #Rl
    a_pin = 18
    b_pin = 23
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
def convertVar(lectura,tipo):

    cocienteVcc=1.20/3.3
    valRet = -1.0 #Si se mantiene es un error inesperado

    if (tipo == "T"):
        #Realizo conversion segun Ct,Rt:
        R = lectura/(abs(math.log(1-cocienteVcc)*C))
        print("Valores- C:",str(C),"- R:",str(R))
        valRet = 1 / (abs(math.log(R/Ro_NTC))/B + 1/To_NTC )
    elif (tipo == "L"):
        #Realizo conversion segun Cl,Rl:
        R = lectura/(abs(math.log(1-cocienteVcc)*C)) - R0
        valRet = Lo * math.pow(R/Ro_LDR,gama_LDR)

    return valRet

while True:
    
    #Obtengo de .txt de parametros configurables
    lectura = 0
    for i in range(10):
        lectura = lectura + analog_read()
    valNum = convertVar(lectura/10,str(sys.argv[1]))
    valNum = math.trunc(valNum*10)/10 #Lo trunco a formato "T=x.x"
    #Creo string y escribo valor en strArch
    with open(strArch, "a") as f:
        fecha = datetime.now()
        
        #fecha.second() = math.trunc(fecha.second())
        strn=str(datetime.now())+","+str(valNum)+"\n"
        f.write(strn)
    with open("configuracion.txt","r") as confi:
        linea = confi.readlines()
        C = float(linea[6].split("= ")[1])*10**-9 #Ct
        R0 = float(linea[5].split("= ")[1])       #Rt
        time.sleep(float(linea[2].split("= ")[1])) #Espero ts entre medidas
    