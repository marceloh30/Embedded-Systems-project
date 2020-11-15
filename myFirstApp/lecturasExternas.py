import time
import asyncio
import websockets
from app import db, valoresT, valoresL, valoresTD

#Funcion para agregar datos recibidos a db del tipo de variable
def agregarDB(strDatos):
    #strDatos=[(T, TD o L);valor numerico;fecha;zona]
    datos=strDatos.split(";")
    if (datos[0]=="T"):                
        ingreso = valoresT(temp = float(datos[1]),zona=datos[3])
    elif (datos[0]=="TD"):
        ingreso = valoresTD(temp = datos[1],fecha=datos[2],zona=datos[3])
    elif (datos[0]=="L"):
        ingreso = valoresL(lux = datos[1],fecha=datos[2],zona=datos[3])
        
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


start_server = websockets.serve(recepcion, "192.168.0.200", 5555)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()





#from app import configuraciones, db, valoresT, valoresL, valoresTD
'''
import socket

HOST = '192.168.0.200'  # ip del servidor
PORT = 1234             # Puerto de escucha

##Solo me comunico entre master (este caso) y esclavo: tendre solamente 1 socket
while True:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                conn.sendall(data)
                print(str(data))
'''                