import time
import smtplib

def envioMail(destino):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login("obligatorioferreirahenandez@gmail.com", "Embebidos2020")
    msg="Puto esta sonando la alarma"
    to = destino + "@gmail.com"
    server.sendmail("obligatorioferreirahernandez@gmail.com", to, msg)
    server.quit()
try:
    tiempoAlarmas = 0.0
    while True:
        estadoAlarma = open("EstadoDeAlarma.txt", "r")
        estado = estadoAlarma.read()
        estadoAlarma.close()
        configuracion = open("configuracion.txt", "r")
        confi = configuracion.readlines()
        tA = confi[4].split("= ")[1]#Hacer magia
        print(tA)
        destino = confi[3].split("= ")[1]#Leer el valor querido nose como chelo creo que si
        print(destino)
        configuracion.close()
        

        if estado == '1':
            if tiempoAlarmas == 0:
                tiempoAlarmas = time.time()
                print("Enviando aviso...")
                envioMail(destino)
            elif (time.time() - tiempoAlarmas) >= float(tA)*60:
                tiempoAlarmas = time.time()
                print("Enviando aviso...")
                envioMail(destino)
        else:
            estado = '0'
except:
    print("Error en el envio de mail")