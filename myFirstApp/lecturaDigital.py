import os
import glob
import time
from app import configuraciones, db, valoresTD
#imports para envio de datos por socket!
import asyncio
import websockets

#uri:
ws_uri="ws://obligatorio.ddns.net:8080"
zona = "Montevideo"
ts = 0

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
 
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir+ '28*')
print(device_folder)
device_file = device_folder[0] + '/w1_slave'

def leerTemperatura():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines
 
def Valortemp():
    lines = leerTemperatura()
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

    async with websockets.connect(ws_uri) as websocket:
        datos = str("TD")+";"+str(valNum)+";"+str(datetime.utcnow())+";"+zona
        #Envio: "Tipo;valorNum;fecha actual;zona"
        await websocket.send(datos)
        print("Datos enviados: ",datos)

        resp = await websocket.recv()
        print(resp)


while True:
    temperatura = Valortemp()
    print("El valor de la temperatura es: " + str(temperatura))
    
    #Intento enviar datos a la base de datos de la otra zona
    try:
        asyncio.get_event_loop().run_until_complete(envioWs(valNum))
    except Exception as e:
        print("No se pudo enviar datos: ", e)
        
    ingreso = valoresTD(temp = temperatura)

    db.session.add(ingreso)
    db.session.commit()

    tiempo = db.session.query(configuraciones).get(1).ts
    time.sleep(tiempo)

    

