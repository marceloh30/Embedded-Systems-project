import RPi.GPIO as GPIO
import time
from datetime import datetime
import math
import sys #importo sys para obtener parametros de la ejecucion.

##Suponemos que tanto LDR como termistor son siempre el mismo (o el mismo tipo),
##por lo tanto, los siguientes valores caracteristicos de los mismos seran fijos.

#Parametros de LDR y NTC:
Lo=110.0            # Lux
Ro_LDR=12300        # Ro(Lo)- en Ohms
gama_LDR=0.8        # parametro caracteristico de LDR (Adimensionado)
To_NTC=25.0+273.0   # Kelvin
Ro_NTC=10.0**4      # Ro(To)- en Ohms
B = 3977.0          # B de NTC (Kelvin)

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
    a_pin = 16
    b_pin = 20
else:
    print("Ocurrio un error interpretando argumento (tipo de archivo)")


def descarga():#Descargo el capacitor
    GPIO.setup(a_pin,GPIO.IN)
    GPIO.setup(b_pin,GPIO.OUT)
    GPIO.output(b_pin, False)
    time.sleep(0.1)
    
def carga():#Cargo el capacitor
    GPIO.setup(b_pin, GPIO.IN)
    GPIO.setup(a_pin, GPIO.OUT)
    GPIO.output(a_pin, True)
    t1 = time.time()
    count = 0 
    while not GPIO.input(b_pin) and count < 500000:
        count = count + 1
        pass
    t2 = time.time()
    print(count)
    descarga()
    if count >= 500000:
        ret = None
    else:
        ret = t2 - t1
    return ret

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

    cocienteVcc=1.38/3.3 #hicimos medidas 
    valRet = None #Si se mantiene es un error inesperado
    try:
        R = lectura/(abs(math.log(1-cocienteVcc)*C)) - R0
        print("Resistencia obtenida:",str(R))
        if (R > 0):
            if (tipo == "T"):
                #Realizo conversion segun Ct,Rt:               
                valRet = 1 / (abs(math.log(R/Ro_NTC))/B + 1/To_NTC )
                valRet -= 273
                print("T: ",valRet)
                
            elif (tipo == "L"):
                #Realizo conversion segun Cl,Rl: (VERSION EXPERIMENTAL)
                valRet = Lo * math.pow(R/Ro_LDR,-1/gama_LDR)
                print("Lux:",valRet)
                
        else:
            print("Resistencia Negativa o 0.")
    except Exception as e:
        print("Al convertir lectura en valor de temp/lux, ocurrio excepcion:",e)

    return valRet

while True:
    
    #Realizo 10 lecturas y obtengo promedio
    lectura = 0
    ult_lectura = 0
    i = 0
    #Verifico ademas que no haya ocurrido algun error en lectura (Configuracion del circuito erronea, etc)
    while i<10 and ult_lectura is not None:
        ult_lectura = analog_read()
        lectura = lectura + ult_lectura
        i+=1
    if ult_lectura is None:
        lectura = None
        print("sape")
    else:
        lectura = lectura/10
    #for i in range(10):
    #    lectura = lectura + analog_read()
    print(lectura)
    if lectura is not None:
        valNum = convertVar(lectura,str(sys.argv[1]))
        if valNum is not None:
            valNum = round(valNum*10)/10 #Lo trunco a formato "T=x.x"
    #Creo string y escribo valor en strArch
    with open(strArch, "a") as f:
        fecha = datetime.now()
        #Dejo en 0 los microsegundos
        fecha = fecha.replace(microsecond=0)
        #fecha.second() = math.trunc(fecha.second())
        strn=str(fecha)+","+str(valNum)+"\n"
        f.write(strn)
    #Obtengo de .txt de parametros configurables
    with open("configuracion.txt","r") as confi:
        linea = confi.readlines()

        if(sys.argv[1]=="T"):
            C = float(linea[6].split("= ")[1])*10**-9 #Ct
            R0 = float(linea[5].split("= ")[1])       #Rt
            
        else: ##Solo puede ser T o L
            C = float(linea[8].split("= ")[1])*10**-9 #Cl
            R0 = float(linea[7].split("= ")[1])       #Rl
            
        time.sleep(float(linea[2].split("= ")[1])) #Espero ts entre medidas
    
