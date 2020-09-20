import RPi.GPIO as GPIO
import time
import math

GPIO.setmode(GPIO.BCM)

a_pin = 18
b_pin = 23

C = 120*10**-9


def descarga():
    GPIO.setup(a_pin,GPIO.IN)
    GPIO.setup(b_pin,GPIO.OUT)
    GPIO.output(b_pin, False)
    time.sleep(1)
    
def carga():
    GPIO.setup(b_pin, GPIO.IN)
    GPIO.setup(a_pin, GPIO.OUT)
    GPIO.output(a_pin, True)
    t1 = time.time()
    while not GPIO.input(b_pin):
        pass
    t2 = time.time()
    print("t: "+str(t2-t1))
    return (t2 - t1)

def analog_read():
    descarga()
    return carga()
   
   
R0 = 10000
R = 0
k =  0.5 # k = 1 / (1 - V(t)/Vcc) donde V(t)=cte*Vcc con 0<cte<1 

while True:    

    while (abs(R-R0) > 100):        
        R = analog_read()/(-math.log(k)*C)
        print(R)
        if( R-R0 > 100):
            k = k - 0.01   
            R = analog_read()/(-math.log(k)*C)
            print("k-=0.01: " +str(R))            
        elif(R-R0 < -100):           
            k = k + 0.01
            R = analog_read()/(-math.log(k)*C)
            print("k+=0.01: " +str(R))                    
    print("Finalmente obtuve: " +str(R)+", k="+str(k))
    
    while True:
        print("Calibrado... ahora a probarle")
        Rnuevo = analog_read()/(-math.log(k)*C)
        print(Rnuevo)
    
    time.sleep(1)