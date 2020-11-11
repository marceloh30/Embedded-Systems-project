import time
import smtplib
from app import configuraciones, db

def envioMail(destino):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login("obligatorioferreirahenandez@gmail.com", "Embebidos2020")
    msg="La alarma esta sonando"
    to = destino
    server.sendmail("obligatorioferreirahernandez@gmail.com", to, msg)
    server.quit()

    
tiempoAlarmas = 0.0
while True:
    try:
        destino = configuraciones.query.get(1).destino
        tA = configuraciones.query.get(1).tA
        estado = configuraciones.query.get(1).alarma
        print(estado)
        if estado == "1 - 1":
            tiempoAlarmas = time.time()
            print("Enviando aviso...")
            envioMail(destino)
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




            
