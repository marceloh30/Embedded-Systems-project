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
        estadoAlarma = open("EstadoDeAlarma.txt", "r")
        estado = estadoAlarma.read()
        estadoAlarma.close()
        configuracion = open("configuracion.txt", "r")
        confi = configuracion.readlines()
        tA = confi[4].split("= ")[1]
        destino = confi[3].split("= ")[1]
        configuracion.close()
        

        if estado == "1 - 1":
            if tiempoAlarmas == 0:
                tiempoAlarmas = time.time()
                print("Enviando aviso...")
                envioMail(destino)
            elif (time.time() - tiempoAlarmas) >= float(tA)*60:
                tiempoAlarmas = time.time()
                print("Enviando aviso...")
                envioMail(destino)
        elif estado == "1 - 0":
            print("Se encendio alarma.")
        else:
            pass
            
            
    except:
        print("Error en el envio de mail")