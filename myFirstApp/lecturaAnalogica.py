import RPi.GPIO as GPIO
import time
from datetime import datetime
import math

GPIO.setmode(GPIO.BCM)

a_pin = 18
b_pin = 23


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
    return (t2 - t1)

def analog_read():
    descarga()
    return carga()

while True:
    coso = 1.29/3.3
    R = analog_read()/(-math.log(1-coso)*550*10**-9)
    f = open("valorR.txt", "a")
    f.write(str(datetime.now())+"- R = "+str(R)+'\n')
    f.close()
    print(analog_read(), str(R))
    time.sleep(5)
    
