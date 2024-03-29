import RPi.GPIO as GPIO
import time
time.sleep(120)
from datetime import datetime
import math
import sys #importo sys para obtener parametros de la ejecucion.
from app import configuraciones, db, valoresT, valoresL, datosSinEnviar
#imports para envio de datos por socket!
import asyncio
import websockets

#Primero obtengo zona de lectura
zona_lect = db.session.query(configuraciones).get(1).zona

#Obtengo uri segun zona:
if (zona_lect == "Montevideo"):
    ws_uri="ws://obligatorio.ddns.net:8081"
else:   #Asumo solo dos zonas: Montevideo y Salinas
    ws_uri="ws://oblmhjf.ddns.net:5555"

##Suponemos que tanto LDR como termistor son siempre el mismo (o el mismo tipo),
##por lo tanto, los siguientes valores caracteristicos de los mismos seran fijos.

#Parametros de LDR y NTC:
Lo=110.0            # Lux
Ro_LDR=12300        # Ro(Lo)- en Ohms
gama_LDR=0.7        # parametro caracteristico de LDR (Adimensionado)
To_NTC=25.0+273.0   # Kelvin
Ro_NTC=10000        # Ro(To)- en Ohms
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
if(str(sys.argv[2])=="T"):

    C = db.session.query(configuraciones).get(1).Ct*10**-9 #Ct
    R0 = (db.session.query(configuraciones).get(1).Rt)     #Rt
    #Mantengo pines
elif(str(sys.argv[2])=="L"):

    C = (db.session.query(configuraciones).get(1).Cl)*10**-9 #Cl
    R0 = (db.session.query(configuraciones).get(1).Rl)      #Rl
    #Redefino pines de entrada y salida para Lux
    a_pin = 24
    b_pin = 25
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
    while not GPIO.input(b_pin) and count < 500000:
        count = count + 1
        pass
    t2 = time.time()
    descarga()
    if count >= 500000:
        ret = None
    else:
        ret = t2 - t1
    return ret

def analog_read():
    descarga()
    return carga()

#Funcion asincrona de envio de datos por websocket a otro servidor
async def envioWs(valNum):
    timeout = 1 #Timeout pequeno para no afectar mediciones
    try:
        #Realizo intento de conexion
        websocket = await asyncio.wait_for(websockets.connect(ws_uri), timeout)
        datos = str(sys.argv[2])+";"+str(valNum)+";"+str(datetime.utcnow())+";"+zona_lect
        #Envio: "Tipo;valorNum;fecha actual;zona"
        await websocket.send(datos)
        print("Datos enviados: ",datos)

        resp = await websocket.recv()
        print(resp)

    except Exception as e:
        print('Error al intentar enviar datos: posiblemente falla de conexion.', e)
        #Agregar a base de datosSinEnviar
        datoSinEnviar=datosSinEnviar(tipoVar=str(sys.argv[2]),valor=valNum)
        db.session.add(datoSinEnviar)
        db.session.commit()        

    


##Main


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
                ParteA =  math.log(R/Ro_NTC)/B
                print("ParteA: ", ParteA)
                ParteB =  1/To_NTC         
                print("ParteB: ", ParteB)
                valRet = 1 / (ParteA + ParteB )
                valRet -= 273
                print("T: ",valRet)
                
            elif (tipo == "L"):
                #Realizo conversion segun Cl,Rl: (VERSION EXPERIMENTAL)
                valRet =(1.25*10**7)*R**-1.4059  #Lo * math.pow(R/Ro_LDR,-1/gama_LDR)
                print("Lux:",valRet)
                
        else:
            print("Resistencia Negativa o 0.")
    except Exception as e:
        print("Al convertir lectura en valor de temp/lux, ocurrio excepcion:",e)

    return valRet
ts = 5 # ts
while True:
    #Refresco valores de C y R de bd de configuraciones
    if(str(sys.argv[2])=="T"):
        
        C = db.session.query(configuraciones).get(1).Ct*10**-9 #Ct
        R0 = (db.session.query(configuraciones).get(1).Rt)     #Rt
    elif(str(sys.argv[2])=="L"):

        C = (db.session.query(configuraciones).get(1).Cl)*10**-9 #Cl
        R0 = (db.session.query(configuraciones).get(1).Rl)      #Rl
    else:
        print("Ocurrio un error interpretando argumento (tipo de archivo)")
    ts = db.session.query(configuraciones).get(1).ts   
    
        
    #Realizo 10 lecturas y obtengo promedio
    lectura = 0
    ult_lectura = 0
    i = 0
    #Verifico ademas que no haya ocurrido algun error en lectura (Configuracion del circuito erronea, etc)
    while i<10 and ult_lectura is not None:
        ult_lectura = analog_read()
        if (ult_lectura is not None):
            lectura = lectura + ult_lectura
        i+=1
    if ult_lectura is None:
        lectura = None
    else:
        lectura = lectura/10

    print("Lectura: ", lectura)
    if lectura is not None:
        valNum = convertVar(lectura,str(sys.argv[2]))
        if valNum is not None:    
            valNum = round(valNum*10)/10 #Lo trunco a formato "T=x.x"
    else:
        valNum = None
    #Envio valNum aunque siendo algun valor o None para indicar error
    # y que pueda saltar alarma:
    
    #Intento enviar datos a la base de datos de la otra zona
    try:
        asyncio.get_event_loop().run_until_complete(envioWs(valNum))
    except Exception as e:
        print("No se pudo enviar datos: ", e)
    #Dependiendo de si es temp o lux creo el objeto necesario para db
    if(str(sys.argv[2])=="T"):                
        ingreso = valoresT(temp = valNum, zona=zona_lect)
    else:
        ingreso = valoresL(lux = valNum, zona=zona_lect)
      
    db.session.add(ingreso)
    db.session.commit()

    time.sleep(ts) #Espero ts entre medidas
    
