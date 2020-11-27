import time
import asyncio
import websockets
from app import db, configuraciones, valoresT, valoresL, valoresTD
from datetime import datetime

#Primero obtengo zona de lectura
zona_lect = db.session.query(configuraciones).get(1).zona

#uri:
if (zona_lect == "Montevideo"):
    puerto = 5555
else:   #Asumo solo dos zonas: Montevideo y Salinas
    puerto = 8081

#Funcion para agregar datos recibidos a db del tipo de variable
def agregarDB(strDatos):
    #strDatos=[(T, TD o L);valor numerico;fecha;zona]
    datos=strDatos.split(";")
    #Obtengo datos de fecha para crear datetime
    dia,hora=datos[2].split(" ")
    dma=dia.split('-')
    hm=hora.split(':')
    
    seg=int(hm[2].split('.')[0])
    fechaRec=datetime(int(dma[0]),int(dma[1]),int(dma[2]),int(hm[0]),int(hm[1]),seg,0)

    if (datos[0]=="T"):                
        ingreso = valoresT(temp = float(datos[1]),fecha = fechaRec,zona=datos[3])
    elif (datos[0]=="TD"):
        ingreso = valoresTD(temp = float(datos[1]),fecha = fechaRec,zona=datos[3])
    elif (datos[0]=="L"):
        ingreso = valoresL(lux = datos[1],fecha = fechaRec,zona=datos[3])
  
    db.session.add(ingreso)
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


start_server = websockets.serve(recepcion, "192.168.0.200", puerto)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
     