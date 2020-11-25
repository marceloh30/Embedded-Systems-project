from app import configuraciones, db, datosSinEnviar
import time
import asyncio
import websockets
from datetime import datetime
##Podria ver parametros: N envios y tiempo de sleep en confi... cambiar luego
N=20
t_sleep=1*60 ##1 minuto

#uri para el envio:
ws_uri="ws://obligatorio.ddns.net:8081"

#Funcion asincrona de envio de datos por websocket a otro servidor
async def envioWs_datosSinEnviar(datoSinEnviar): #Funcion recibe objeto de clase datosSinEnviar
    timeout = 1 #Timeout pequeno para no afectar mediciones
    try:
        # make connection attempt
        websocket = await asyncio.wait_for(websockets.connect(ws_uri), timeout)
        datos = str(datoSinEnviar.tipoVar)+";"+str(datoSinEnviar.valor)+";"+str(datoSinEnviar.fecha)+";"+str(datoSinEnviar.zona)
        #Envio: "Tipo;valorNum;fecha;zona"
        await websocket.send(datos)
        print("Datos enviados: ",datos)

        resp = await websocket.recv()
        print(resp)
        #Si todo sale correctamente, elimino objeto enviado de datosSinEnviar
        db.session.delete(datoSinEnviar)
        db.session.commit()
    except Exception as e:
        print('Error al intentar enviar datos: posiblemente falla de conexion.', e)
 

##Loop principal
while True:
    time.sleep(t_sleep) #Duermo en cada iteracion para no saturar a Raspberry

    #Ordeno datos por id y luego obtengo cantidad, printeo y despues intento enviar el minimo entre 20 y la cantidad que haya.
    datos = datosSinEnviar.query.order_by(datosSinEnviar.id) 
    cant_datos = int(len(datosSinEnviar.query.all()))
    print("Datos sin enviar aun: ",cant_datos)
    for dato in datos[0:min(20,cant_datos)]:
        print("Intento enviar: ",dato)
        #Intento enviar datos a la base de datos de la otra zona
        try:
            asyncio.get_event_loop().run_until_complete(envioWs_datosSinEnviar(dato))
        except Exception as e:
            print("No se pudo enviar datos: ", e)
    

