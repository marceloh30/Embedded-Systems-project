import time
import smtplib
from app import configuraciones, db

#Funcion para envio de mail
def envioMail(destino, zona):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login("obligatorioferreirahenandez@gmail.com", "Embebidos2020")
    msg="""From: Pi <obligatorioferreirahenandez@gmail.com>
To: To Destino <%s>
Subject: Alerta de alarma

La alarma se ha activado en la zona:
%s
""" % (destino,zona)
    print(msg)
    to = destino
    server.sendmail("obligatorioferreirahernandez@gmail.com", to, msg)
    server.quit()
####

#
tiempoAlarmas = 0.0

while True:
    try:
        #Tengo try para evitar que se caiga el programa a la hora de llamar a envioMail o algun otro error

        destino = configuraciones.query.get(1).destino
        tA = configuraciones.query.get(1).tA
        estado = configuraciones.query.get(1).alarma

        print("Estado: ",estado)
        if estado == "1 - 1 - 0" or estado == "1 - 1 - 1" or estado == "1 - 0 - 1":
            if estado == "1 - 1 - 0":
                zona = " Sensor analogico"
            elif estado == "1 - 1 - 1":
                zona = " Ambos sensores"
            else:
                zona = " Sensor digital"
            tiempoAlarmas = time.time()
            print("Enviando aviso...")
            envioMail(destino, zona)
            time.sleep(float(tA)*60)#Duermo el programa hasta que tenga que sonar nuevamente la alarma
        elif estado == "1 - 0":
            print("Se encendio alarma.")
            time.sleep(30)#Duermo el programa 
        else:
            tiempoAlarmas = 0
            time.sleep(30)#Duermo el programa
            pass
               
         
    except Exception as e:
        print("Ocurrio un error:",e)
        time.sleep(30)
        if e==smtplib.SMTPException:
            print("Error de correo")            




            
