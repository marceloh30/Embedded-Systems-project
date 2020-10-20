import time
import smtplib

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

        with open("EstadoDeAlarma.txt", "r") as estadoAlarma:  
            estado = estadoAlarma.read()

        with open("configuracion.txt", "r") as configuracion: 
            confi = configuracion.readlines()
            tA = confi[4].split("= ")[1]
            destino = confi[3].split("= ")[1]
        
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
        print("Error en el envio de mail:",e)
        if e==smtplib.SMTPException:
            print("Error de correo")            
        #Si es una excepcion debido a que archivo no existe lo creo:
        if (e.args[0]==2):
            with open("EstadoDeAlarma.txt", 'x') as f:
                print("Archivo no existe. Creo el archivo EstadoDeAlarma.txt.")



            
