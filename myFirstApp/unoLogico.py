import RPi.GPIO as GPIO
import time
import math
import sys #importo sys para obtener parametros de la ejecucion.


a_pin = 18
b_pin = 23

GPIO.setmode(GPIO.BCM)


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
    while not GPIO.input(b_pin):
        count = count + 1
        pass
    t2 = time.time()
    print(count)
    descarga()
    return (t2 - t1)

def analog_read():
    descarga()
    return carga()
    
def convertVar(lectura):

    cocienteVcc=0 #hicimos medidas ;) -anterior: 1.20/3.3 
    valRet = -1.0 #Si se mantiene es un error inesperado

    #Realizo conversion segun Ct,Rt:
    Vc = 3.3*(1-math.exp(-lectura/(10000*550*10**-9)))
    print("Vc: ",Vc)

    return valRet
    
while True:
    
    #Realizo 10 lecturas y obtengo promedio
    lectura = 0
    for i in range(10):
        lectura = lectura + analog_read()
    lectura = lectura/10
    print(lectura)
    valNum = convertVar(lectura)
    valNum = round(valNum*10)/10 #Lo trunco a formato "T=x.x"