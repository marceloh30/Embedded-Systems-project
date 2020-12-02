import time
import asyncio
import websockets
from app import db, configuraciones, valoresT, valoresL, valoresTD
from datetime import datetime

#Primero obtengo zona de lectura
zona_lect = db.session.query(configuraciones).get(1).zona


#Funcion para agregar datos recibidos a db del tipo de variable
def agregarDB(strDatos):
    #strDatos=[(T, TD o L);valor numerico;fecha;zona]
    datos=strDatos.split(";")
    #Obtengo datos de fecha para crear datetime
    dia,hora=datos[2].split(" ")
    dma=dia.split('-')
    hm=hora.split(':')
    #Para evitar errores leo segundos por separado
    seg=int(hm[2].split('.')[0])
    #Genero datetime con valores recibidos
    fechaRec=datetime(int(dma[0]),int(dma[1]),int(dma[2]),int(hm[0]),int(hm[1]),seg,0)

    #Segun el tipo de variable y datos recibidos, creo objeto y lo ingreso a la db
    if (datos[0]=="T"):                
        ingreso = valoresT(temp = float(datos[1]),fecha = fechaRec,zona=datos[3])
    elif (datos[0]=="TD"):
        ingreso = valoresTD(temp = float(datos[1]),fecha = fechaRec,zona=datos[3])
    elif (datos[0]=="L"):
        ingreso = valoresL(lux = float(datos[1]),fecha = fechaRec,zona=datos[3])
  
    db.session.add(ingreso)
    valoresT.query.order_by(valoresT.fecha.desc()) #Ordeno para cuando agrego los balores a DB y asi siempre mostrar los mas actuales
    valoresTD.query.order_by(valoresTD.fecha.desc())
    valoresL.query.order_by(valoresL.fecha.desc())
    db.session.commit()
            
#Defino funcion asincrona de recepcion
async def recepcion(websocket, path):
    #Recibo asincronamente datos
    datos = await websocket.recv()
    print("Datos recibidos:", datos)
    agregarDB(datos)
    #Envio asicronamente el msj aclarando recepcion:
    msj = "Recibi datos: "+datos
    await websocket.send(msj)
    time.sleep(1) #Lo duermo 1 seg para evitar bloqueos

#Obtengo puerto segun configuracion de la zona:
if (zona_lect == "Montevideo"):
    puerto = 5555 
else:   #Asumo solo dos zonas: Montevideo y Salinas
    puerto = 8081

#Inicializo websocket en la ip del Raspberry y el puerto recien obtenido
start_server = websockets.serve(recepcion, "192.168.0.200", puerto)

#Dejo en loop infinito esperando recibir datos a traves del websocket
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
     