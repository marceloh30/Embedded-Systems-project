import time
from datetime import date
from datetime import datetime

global temperatura
temperatura = 0
#TL,TH, ts, destino,tA, Rt, Ct, Rl, Cl
valoresPredeterminados = [0, 200, 5, "nadie", 10, 10000, 550*10**-9, 10000, 200*10**-9]
#Comienzo con valores predeterminados
valoresIngresados = valoresPredeterminados 

estadoAlarma = False
tiempoEntreAlarmas = 0
global posicionLectura 
posicionLectura = 0
archConf="configuracion.txt"

##Pruebo abrir archConf, si no existe lo creo.
try:    
    with open(archConf,"r") as arch:
        print("Archivo",archConf,"existente.")
        #Leo los valores del archivo:


except Exception as e:
    #No existe archivo. Lo creo:
    with open(archConf, 'x') as f:
        print(e,"\nArchivo no existe. Creo el archivo:\n",str(f))



def verificacionVariable(variable, type): #Verifico si la variable es del tipo que espero 
    if not isinstance(variable, type):
        return False #Si es falso tomo prederterminado o el anterior dependiendo del caso
    else:
        return True

def guardadoVariables():
    #guardo variables en archivo de configuracion
    with open(archConf, "w") as pc: 
        pc.write("TL = "+str(valoresIngresados[0])+'\n')
        pc.write("TH = "+str(valoresIngresados[1])+'\n')
        pc.write("ts = "+str(valoresIngresados[2])+'\n')
        pc.write("destino = "+str(valoresIngresados[3])+'\n')
        pc.write("tA = "+str(valoresIngresados[4])+'\n')
        pc.write("Rt = "+str(valoresIngresados[5])+'\n')
        pc.write("Ct = "+str(valoresIngresados[6])+'\n')
        pc.write("Rl = "+str(valoresIngresados[7])+'\n')
        pc.write("Cl = "+str(valoresIngresados[8])+'\n')


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

    #Guardo variables:
    guardadoVariables()

    return aux

def envioAlarma():
    with open("EstadoDeAlarma.txt", "w") as eA:

        if estadoAlarma == 1:
            eA.write("1")
        else:
            eA.write("0")


#Funcion para leer valores num(Temp o Lux) de sus respectivos txt
def leerValor(tipo, pos): #Devuelve largo de linea y valNum
    rets=[0,0]
    if (tipo == "T"):
        strArch = "valoresT.txt"
    else:
        strArch = "valoresL.txt"
    try:
        with open(strArch, "r") as f:
            #Lo llevo a la posicion del ultimo ingreso
            f.seek(pos)
            #Leo el ultimo valor
            linea = f.readline()
            rets[1] = len(linea)
            if rets[1] != 0:
                rets[0]=linea.split(",")[1]	#Guardo valNum
            
    except Exception as e:
        with open(strArch, "x") as f:
            print(e, "\nArchivo no existe. Creo el archivo", strArch, ".")
    
    return rets



##Funcion de busqueda de fechas: Retorna Fechas,valorNum(temp o lux)
def buscarVals(tipo,f_desde,f_hasta):

    if (tipo=="T"):
        strArch = "valoresT.txt"
    else:
        strArch = "valoresL.txt"

    with open(strArch, "r") as arch:
        #Defino listas a devolver
        rets=[[],[]] #rets[0]=fechas[],[1]=vals[]

        for linea in arch.readlines():
            #separo fecha y valor num. de linea:
            arr=linea.split(",")
            #Separo dia y horario de la fecha de arr
            fh_array=arr[0].split(" ")
            #Separo dia,mes,anio de la fecha
            dte=fh_array[0].split("-")
            #Separo hora, min y seg del horario
            hora=fh_array[1].split(":")

            #Creo datetime con los valores de linea
            fecha_l=datetime(int(dte[0]),int(dte[1]),int(dte[2]),int(hora[0]),int(hora[1]),int(hora[2]),0)
            valNum=float(arr[1])
            #Verifico si estoy dentro de valores de tiemop
            if (f_desde <= fecha_l and f_hasta >= fecha_l):
                rets[0].append(fecha_l)
                rets[1].append(valNum)
    return rets