import os
import glob
import time
from app import configuraciones, db, valoresTD, datosSinEnviar
#imports para envio de datos por socket!
import asyncio
import websockets
from datetime import datetime

#Primero obtengo zona de lectura
zona_lect = db.session.query(configuraciones).get(1).zona

#Obtengo uri segun zona:
if (zona_lect == "Montevideo"):
    ws_uri="ws://obligatorio.ddns.net:8081"
else:   #Asumo solo dos zonas: Montevideo y Salinas
    ws_uri="ws://oblmhjf.ddns.net:5555"

ts = 0

os.system('sudo modprobe w1-gpio')
os.system('sudo modprobe w1-therm')
try: 
    base_dir = '/sys/bus/w1/devices/'
    device_folder = glob.glob(base_dir+ '28*')
    device_file = device_folder[0] + '/w1_slave'
except Exception as e:
    print("Ocurrio un error al buscar directorio, posible sensor roto.",e)
    #Aqui reinicio el programa para intentar obtener bien el directorio
    # y asi puedo leer correctamente temperatura digital
    os.system("python3 lecturaDigital.py Montevideo")
    exit()
    
    

def leerTemperatura():
    #creo lines vacio por si no puedo abrir archivo
    lines = None
    try:
        f = open(device_file, 'r')
        lines = f.readlines()
        f.close()
    except Exception as e:
        print("Ocurrio un error al abrir archivo: ",e)
        
    return lines
 
def Valortemp():
    #Si no puedo abrir arch, es decir no puedo leer temp,
    # le mando un none y asi puedo activar alarma:
    lines = leerTemperatura()
    if (lines is None):
        temp = None
    else:            
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = leerTemperatura()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp = float(temp_string) / 1000.0
    return temp
        
#Funcion asincrona de envio de datos por websocket a otro servidor
async def envioWs(valNum):
    timeout = 1 #Timeout pequeno para no afectar mediciones
    try:
        #Realizo intento de conexion
        websocket = await asyncio.wait_for(websockets.connect(ws_uri), timeout)
        datos = str("TD")+";"+str(valNum)+";"+str(datetime.utcnow())+";"+zona_lect
        #Envio: "Tipo;valorNum;fecha actual;zona"
        await websocket.send(datos)
        print("Datos enviados: ",datos)

        resp = await websocket.recv()
        print(resp)
    except Exception as e:
        print('Error al intentar enviar datos: posiblemente falla de conexion.', e)
        #Agregar a base de datosSinEnviar
        datoSinEnviar=datosSinEnviar(tipoVar="TD",valor=valNum)
        db.session.add(datoSinEnviar)
        db.session.commit()   

while True:
    temperatura = Valortemp()
    print("El valor de la temperatura es: " + str(temperatura))
    
    #Intento enviar datos a la base de datos de la otra zona
    try:
        asyncio.get_event_loop().run_until_complete(envioWs(temperatura))
    except Exception as e:
        print("No se pudo enviar datos: ", e)
        
    ingreso = valoresTD(temp = temperatura)

    db.session.add(ingreso)
    db.session.commit()

    tiempo = db.session.query(configuraciones).get(1).ts
    time.sleep(tiempo)

    

