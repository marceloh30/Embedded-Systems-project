import time

global temperatura
temperatura = 0
valoresPredeterminados = [0, 200, 5, "nadie", 10, 10000, 550*10**-9]
valoresIngresados = [0, 0, 5, " ", 0, 10000, 550*10**-9, 10000, 0] #TL,TH, ts, destino,tA, Rt, Ct, Rl, Cl
estadoAlarma = False
tiempoEntreAlarmas = 0
posicionLectura = 0


def verificacionVariable(variable, type): #Verifico si la variable es del tipo que espero 
    if not isinstance(variable, type):
        return False #Si es falso tomo prederterminado o el anterior dependiendo del caso
    else:
        return True

def guardadoVariables(TL,TH, ts, destino,tA, Rt, Ct, Rl, Cl):
    pc = open("configuracion.txt", "w")
    pc.write("TL = "+str(TL)+'\n')
    pc.write("TH = "+str(TH)+'\n')
    pc.write("ts = "+str(ts)+'\n')
    pc.write("destino = "+str(destino)+'\n')
    pc.write("tA = "+str(tA)+'\n')
    pc.write("Rt = "+str(Rt)+'\n')
    pc.write("Ct = "+str(Ct)+'\n')
    pc.write("Rl = "+str(Rl)+'\n')
    pc.write("Cl = "+str(Cl)+'\n')
    pc.close()

def cambioValores(TL,TH, ts, destino,tA, Rt, Ct, Rl, Cl):
    aux = "" #Variable para devolver los parametros erroneos y mostrarlos en pagina web
    if (verificacionVariable(TL, float) and TL < TH) or TL is None:
        if TL is not None:
            valoresIngresados[0] = TL
        #Si es None, osea no se ingreso nada no lo tomo como error y me quedo con el estado anterior
    else:
        aux = "TL "
    if (verificacionVariable(TH, float) and TH > TL) or TH is None:
        if TH is not None:
            valoresIngresados[1] = TH
    else:
        aux = aux + "TH "
    if (verificacionVariable(ts, float) and ts >= 5) or ts is None:
        if ts is not None:
            valoresIngresados[2] = ts
    else:
        aux = aux + "ts "
    if verificacionVariable(destino, str) or len(destino) == 0:
        if len(destino) != 0:
            valoresIngresados[3] = destino
    else:
        aux = aux + "destino "
    if (verificacionVariable(tA, float) and tA > 0) or tA is None:
        if tA is not None:
            valoresIngresados[4] = tA
    else:
        aux = aux + "tA"
    if (verificacionVariable(Rt, float) and Rt > 0) or Rt is None:
        if Rt is not None:
            valoresIngresados[5] = Rt
    else:
        aux = aux + "Rt"
    if (verificacionVariable(Ct, float) and Ct > 0) or Ct is None:
        if Ct is not None:
            valoresIngresados[6] = Ct
    else:
        aux = aux + "Ct"
    if (verificacionVariable(Rl, float) and Rl > 0) or Rl is None:
        if Rl is not None:
            valoresIngresados[7] = Rl
    else:
        aux = aux + "Rl"        
    if (verificacionVariable(Cl, float) and Cl > 0) or Cl is None:
        if Cl is not None:
            valoresIngresados[8] = Cl
    else:
        aux = aux + "Cl"        

    return aux

def envioAlarma(tA):
    if estadoAlarma == 1:
        if valoresIngresados[1] > temperatura or valoresIngresados[2] < temperatura:
            if tiempoEntreAlarmas == 0:
               tiempoEntreAlarmas =  time.time()
               exec("alarma.py")
            elif (tiempoEntreAlarmas - time.time()) == (valoresIngresados[5]*60):
               exec("alarma.py")
            
        
