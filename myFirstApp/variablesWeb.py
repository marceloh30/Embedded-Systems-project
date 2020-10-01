import time

global resistencia
resistencia = 0
valoresPredeterminados = [0, 200, 5, "nadie", 10, 10000, 550*10**-9]
valoresIngresados = [0, 0, 0, " ", 0, 0, 0]#TL,TH, ts, destino,tA, Rt, Ct
estadoAlarma = False
tiempoEntreAlarmas = 0
posicionLectura = 0

def verificacionVariables(TL,TH, ts, destino,tA, Rt, Ct):#Nose si hay que verificar algun otro 
    if ts < 5:
        return False
    else:
        return True

def guardadoVariables(TL,TH, ts, destino,tA, Rt, Ct):#Para que quede mas prolijo ponele 
    pc = open("configuracion.txt", "w")
    pc.write("TL = "+str(TL)+'\n')
    pc.write("TH = "+str(TH)+'\n')
    pc.write("ts = "+str(ts)+'\n')
    pc.write("destino = "+str(destino)+'\n')
    pc.write("tA = "+str(tA)+'\n')
    pc.write("Rt = "+str(Rt)+'\n')
    pc.write("Ct = "+str(Ct)+'\n')
    #pc.write("Rl = "+str(Rl)+'\n')
    #pc.write("Cl = "+str(Cl)+'\n')
    pc.close()

def cambioValores(TL,TH, ts, destino,tA, Rt, Ct):
    valoresIngresados[1] = TL
    valoresIngresados[2] = TH
    valoresIngresados[3] = ts
    valoresIngresados[4] = destino
    valoresIngresados[5] = tA
    valoresIngresados[6] = Rt
    valoresIngresados[7] = Ct

def envioAlarma(tA):
    if estadoAlarma == 1:
        if valoresIngresados[1] > resistencia or valoresIngresados[2] < resistencia:
            if tiempoEntreAlarmas == 0:
               tiempoEntreAlarmas =  time.time()
               exec("alarma.py")
            elif (tiempoEntreAlarmas - time.time()) == (valoresIngresados[5]*60):
               exec("alarma.py")
            
        
