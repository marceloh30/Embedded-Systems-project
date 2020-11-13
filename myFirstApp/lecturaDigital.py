import os
import glob
import time
from app import configuraciones, db, valoresTD

ts = 0

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
 
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

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

while True:
    temperatura = Valortemp()
    print("El valor de la temperatura es: " + str(temperatura))

    ingreso = valoresTD(temp = temperatura)

    db.session.add(ingreso)
    db.session.commit()

    tiempo = db.session.query(configuraciones).get(1).ts
    time.sleep(tiempo)

    

