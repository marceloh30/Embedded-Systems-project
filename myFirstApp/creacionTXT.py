
def creacionArchivos(archivo):
    try:
        with open(archivo, "r") as f:  
            print(archivo," creado")

    except:
        if archivo == "configuracion.txt":
            with open(archivo, 'w') as pc:
                print("Archivo no existe. Creo y escribo el archivo ", archivo)
                pc.write("TL = "+str(0)+'\n')
                pc.write("TH = "+str(0)+'\n')
                pc.write("ts = "+str(0)+'\n')
                pc.write("destino = "+str(0)+'\n')
                pc.write("tA = "+str(0)+'\n') ##
                pc.write("Rt = "+str(0)+'\n') ##En ohm
                pc.write("Ct = "+str(0)+'\n') ##En nF
                pc.write("Rl = "+str(0)+'\n') ##En ohm
                pc.write("Cl = "+str(0)+'\n') ##En nF
        else:
            with open(archivo, 'x') as pc:
                print("Archivo no existe. Creo el archivo ", archivo)
                

creacionArchivos("EstadoDeAlarma.txt")
creacionArchivos("configuracion.txt")
creacionArchivos("valoresL.txt")
creacionArchivos("valoresT.txt")




