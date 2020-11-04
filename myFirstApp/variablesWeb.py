import time
from datetime import date
from datetime import datetime
from validate_email import validate_email
#from modelosDB import configuraciones, db
import math
from app import configuraciones, db, valoresT, valoresL

temperatura = 0
#TL,TH, ts, destino,tA, Rt, Ct, Rl, Cl
valoresPredeterminados = [0.0, 200.0, 5.0, "nadie", 10.0, 10000.0, 550.0, 10000.0, 550.0]
#Comienzo con valores predeterminados
valoresIngresados = valoresPredeterminados 

estadoAlarma = False
tiempoEntreAlarmas = 0
posicionLectura = 0
archConf="configuracion.txt"
'''
##Pruebo abrir archConf, si no existe lo creo.
def ver_archConf():
    try:    
        with open(archConf,"r") as arch:
            print("Archivo",archConf,"existente.")
            #Leo los valores del archivo:
            print("Valores actuales:")
            for linea in arch.readlines():
                print(linea)

    except Exception as e:
        print(e.args,": Excepcion capturada")
        #Si es una excepcion debido a que archivo no existe lo creo:
        if(e.args[0]==2):
            with open(archConf, 'x') as f:
                print(e,"\nArchivo no existe. Creo el archivo:\n",str(f))
                #Hago el primer guardado de valores predeterminados
                guardadoVariables()
'''
def guardadoVariables():
    #guardo variables en base de datos
    confi = configuraciones(TL = valoresIngresados[0], TH= valoresIngresados[1], ts = valoresIngresados[2], destino = valoresIngresados[3], tA = valoresIngresados[4], Rt = valoresIngresados[5], Ct = valoresIngresados[6], Rl = valoresIngresados[7], Cl = valoresIngresados[8])
    try:
        if len(configuraciones.query.all()) < 1:
            db.session.add(confi)
            db.session.commit()
        else:
            confiVieja = configuraciones.query.get(1)
            confiVieja.TL = confi.TL
            confiVieja.TH = confi.TH
            confiVieja.ts = confi.ts
            confiVieja.destino = confi.destino
            confiVieja.tA = confi.tA
            confiVieja.Rt = confi.Rt
            confiVieja.Ct = confi.Ct
            confiVieja.Rl = confi.Rl
            confiVieja.Cl = confi.Cl
            db.session.commit()
        print("TL = ", configuraciones.query.get(1).TL)
        print("TH = ", configuraciones.query.get(1).TH)
        print("ts = ", configuraciones.query.get(1).ts)
        print("destino = ", configuraciones.query.get(1).destino)
        print("tA = ", configuraciones.query.get(1).tA)
        print("Rt = ", configuraciones.query.get(1).Rt)
        print("Ct = ", configuraciones.query.get(1).Ct)
        print("Rl = ", configuraciones.query.get(1).Rl)
        print("Cl = ", configuraciones.query.get(1).Cl)
    except Exception as e:
        print("Hubo un error: ", e)

def verificacionVariable(variable, type): #Verifico si la variable es del tipo que espero 
    if not isinstance(variable, type):
        return False #Si es falso tomo prederterminado o el anterior dependiendo del caso
    else:
        return True

def cambioValores(TL,TH, ts, destino,tA, Rt, Ct, Rl, Cl):
    aux = "" #Variable para devolver los parametros erroneos y mostrarlos en pagina web
    if (verificacionVariable(TL, float)):
        if TL is not None:
            if TH is None:
                val = valoresIngresados[1]
            else:
                val = TH
            if TL < val:
                valoresIngresados[0] = TL
                aux = "TL "
            
        #Si es None, osea no se ingreso nada no lo tomo como error y me quedo con el estado anterior
        
    if (verificacionVariable(TH, float)):
        if TH is not None:
            if TL is None:
                val = valoresIngresados[0]
            else:
                val = TL
            if TH > val:
                valoresIngresados[1] = TH
                aux = aux + "TH "
        
    if (verificacionVariable(ts, float) and ts >= 5) or ts is None:
        if ts is not None:
            valoresIngresados[2] = ts
            aux = aux + "ts "
        
    if (validate_email(email_address=destino, check_regex=True, check_mx=True) or len(destino) == 0):
        if len(destino) != 0:
            valoresIngresados[3] = destino
            aux = aux + "destino "

    if (verificacionVariable(tA, float) and tA > 0) or tA is None:
        if tA is not None:
            valoresIngresados[4] = tA
            aux = aux + "tA "
        
    if (verificacionVariable(Rt, float) and Rt > 0) or Rt is None:
        if Rt is not None:
            valoresIngresados[5] = Rt
            aux = aux + "Rt "

    if (verificacionVariable(Ct, float) and Ct > 0) or Ct is None:
        if Ct is not None:
            valoresIngresados[6] = Ct
            aux = aux + "Ct "

    if (verificacionVariable(Rl, float) and Rl > 0) or Rl is None:
        if Rl is not None:
            valoresIngresados[7] = Rl
            aux = aux + "Rl "
                
    if (verificacionVariable(Cl, float) and Cl > 0) or Cl is None:
        if Cl is not None:
            valoresIngresados[8] = Cl
            aux = aux + "Cl "
            

    #Guardo variables:
    guardadoVariables()

    return aux

def envioAlarma():

    with open("EstadoDeAlarma.txt", "w") as eA:

        if estadoAlarma == True:
            if temperatura is None or float(temperatura) < float(valoresIngresados[0]) or float(temperatura) > float(valoresIngresados[1]):
                eA.write("1 - 1")
            else:
                eA.write("1 - 0")
        else:
            eA.write("0 - 0")


#Funcion para leer valores num(Temp o Lux) de sus respectivos txt
def leerValor(tipo): #Devuelve largo de linea y valNum
    ret=None
    if (tipo == "T"):
        strArch = "valoresT.txt"
    elif (tipo == "L"):
        strArch = "valoresL.txt"
    else:
        strArch = None
    if strArch is not None:
        try:
            with open(strArch, "r") as f:
                ult_linea=[]
                #Leo lineas y tomo la ultima
                for linea in f.readlines():
                    ult_linea=linea
                    pass
                
                if len(ult_linea) != 0:
                    ret=ult_linea.split(",")[1]	#Guardo valNum
                    if(ret=="None\n"):
                        ret=None
                
        except Exception as e:
            print(e.args,": excepcion capturada.")
            #Verifico si excepcion es por archivo no creado y en ese caso lo creo.
            if(e.args[0]==2):
                with open(strArch, "x") as f:
                    print(e, "\nArchivo no existe. Creo el archivo", strArch, ".")
        
    return ret



##Funcion de busqueda de fechas: Retorna Fechas,valorNum(temp o lux)
def buscarVals(tipo,f_desde,f_hasta):

    if (tipo == "T"):
        ##strArch = "valoresT.txt"
        fechasDeseadas = valoresT.query.filter(valoresT.fecha.between(f_desde,f_hasta))
    elif (tipo == "L"):
        fechasDeseadas = valoresL.query.filter(valoresL.fecha.between(f_desde,f_hasta))
    
    
    #Defino listas a devolver
    rets=[[],[]] #rets[0]=fechas[],[1]=vals[]
    if fechasDeseadas.count() > 0:
    #supongo archivos ya creados:
        
        for i in fechasDeseadas:
            '''
            #separo fecha y valor num. de linea:
            arr=linea.split(",")
            #Separo dia y horario de la fecha de arr
            fh_array=arr[0].split(" ")
            #Separo dia,mes,anio de la fecha
            dte=fh_array[0].split("-")
            #Separo hora, min y seg del horario
            hora=fh_array[1].split(":")
            '''
            #Creo datetime con los valores de linea
            fecha_l=i.fecha#datetime(int(dte[0]),int(dte[1]),int(dte[2]),int(hora[0]),int(hora[1]),int(hora[2]),0)
            if tipo == 'T':
                val = i.temp
            else:
                val = i.lux
            if(val is None):
                valNum=None
            else:  
                valNum=val
            #Verifico si estoy dentro de valores de tiempo
            if (f_desde <= fecha_l and f_hasta >= fecha_l):
                
                rets[0].append(fecha_l)
                rets[1].append(valNum)

    return rets

def arch_Historial(tipo,vals,fechas):
    dirArch="/tmp/archivoHistorial.txt"
    try:
        with open(dirArch,"x") as cf:
            print(str(cf),"Archivo de historial creado")
    except Exception as e:
        #Como es la unica excepcion posible, realizo lo siguiente:
        print(e,": Archivo ya creado.. se procede a limpiarlo")
        with open(dirArch,"w+") as wf:
            #Vacio archivo ya existente
            wf.truncate()
            
    #Una vez con archivo creado/limpiado, escribo datos:
    with open(dirArch,"w+") as arch:
        #Itero y voy escribiendo las lineas:
        for val, fecha in zip(vals, fechas):
            if tipo=="T":
                strTipo = ["Temperatura: "," grados Celcius"]
            else:
                strTipo = ["Valor de luz: "," Lux"]
            #Escribo: "Fecha: xx/xx/xxxx xx:xx:xx - Valor: xxx Lux/grados Celcius"
            arch.write("Fecha: "+str(fecha)+" - "+strTipo[0]+str(val)+strTipo[1]+"\n")
    #Una vez grabado el archivo, devuelvo la direccion donde se creo el archivo    
    return dirArch
