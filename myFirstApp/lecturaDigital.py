import os
import glob
import time
from app import configuraciones, db, valoresTD, datosSinEnviar
#imports para envio de datos por socket!
import asyncio
import websockets
from datetime import datetime
from w1thermsensor import W1ThermSensor

#Primero obtengo zona de lectura
zona_lect = db.session.query(configuraciones).get(1).zona

#Obtengo uri segun zona:
if (zona_lect == "Montevideo"):
    ws_uri="ws://obligatorio.ddns.net:8081"
else:   #Asumo solo dos zonas: Montevideo y Salinas
    ws_uri="ws://oblmhjf.ddns.net:5555"

ts = 0
sensor = W1ThermSensor()
        
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
    #Intento enviar datos a la base de datos de la otra zona
    try:
        temperatura = sensor.get_temperature()#Obtengo el valor de la temperatura
        print("El valor de la temperatura es: " + str(temperatura))
        asyncio.get_event_loop().run_until_complete(envioWs(temperatura))
    except IndexError:
        print("Error en el sensor digital")
        temperatura = None
        asyncio.get_event_loop().run_until_complete(envioWs(temperatura))
    except Exception as e:
        print("No se pudo enviar datos: ", e)
        
    ingreso = valoresTD(temp = temperatura)

    db.session.add(ingreso)
    db.session.commit()

    tiempo = db.session.query(configuraciones).get(1).ts
    time.sleep(tiempo)