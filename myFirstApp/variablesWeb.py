import time
from datetime import date
from datetime import datetime
from validate_email import validate_email
#from modelosDB import configuraciones, db
import math
from app import configuraciones, db, valoresT, valoresL, valoresTD, datosSinEnviar

temperatura = None
temperaturaD = None

estadoAlarma = False
tiempoEntreAlarmas = 0
posicionLectura = 0

#valoresIngresados=[0.0, 200.0, 5.0, "nadie", 10.0, 10000.0, 550.0, 10000.0, 550.0, 0.0, 200.0]#Areglar
'''
def guardadoVariables():
    #guardo variables en base de datos
    confi = configuraciones(TL = valoresIngresados[0], TH= valoresIngresados[1], ts = valoresIngresados[2], destino = valoresIngresados[3], tA = valoresIngresados[4], Rt = valoresIngresados[5], Ct = valoresIngresados[6], Rl = valoresIngresados[7], Cl = valoresIngresados[8], TLD = valoresIngresados[9], THD = valoresIngresados[10])
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
            confiVieja.TLD = confi.TLD
            confiVieja.THD = confi.THD            
            
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
        print("alarma = ", configuraciones.query.get(1).alarma) 
        print("TL = ", configuraciones.query.get(1).TLD)
        print("TH = ", configuraciones.query.get(1).THD)       
    except Exception as e:
        print("Hubo un error: ", e)
'''
def verificacionVariable(variable, type): #Verifico si la variable es del tipo que espero 
    if not isinstance(variable, type):
        return False #Si es falso tomo prederterminado o el anterior dependiendo del caso
    else:
        return True

def cambioValores(TL,TH, ts, destino,tA, Rt, Ct, Rl, Cl, TLD, THD):
    aux = "" #Variable para devolver los parametros erroneos y mostrarlos en pagina web
    confi = configuraciones.query.get(1)

    if (verificacionVariable(TL, float)):
        if TL is not None:
            if TH is None:
                val = confi.TH
            else:
                val = TH
            if TL < val:
                confi.TL = TL
                aux = "TL "
            
        #Si es None, osea no se ingreso nada no lo tomo como error y me quedo con el estado anterior
        
    if (verificacionVariable(TH, float)):
        if TH is not None:
            if TL is None:
                val = confi.TL
            else:
                val = TL
            if TH > val:
                confi.TH = TH
                aux = aux + "TH "
        
    if (verificacionVariable(ts, float) and ts >= 5) or ts is None:
        if ts is not None:
            confi.ts = ts
            aux = aux + "ts "
        
    if (validate_email(email_address=destino, check_regex=True, check_mx=True) or len(destino) == 0):
        if len(destino) != 0:
            confi.destino = destino
            aux = aux + "destino "

    if (verificacionVariable(tA, float) and tA > 0) or tA is None:
        if tA is not None:
            confi.tA = tA
            aux = aux + "tA "
        
    if (verificacionVariable(Rt, float) and Rt > 0) or Rt is None:
        if Rt is not None:
            confi.Rt = Rt
            aux = aux + "Rt "

    if (verificacionVariable(Ct, float) and Ct > 0) or Ct is None:
        if Ct is not None:
            confi.Ct = Ct
            aux = aux + "Ct "

    if (verificacionVariable(Rl, float) and Rl > 0) or Rl is None:
        if Rl is not None:
            confi.Rl = Rl
            aux = aux + "Rl "
                
    if (verificacionVariable(Cl, float) and Cl > 0) or Cl is None:
        if Cl is not None:
            confi.Cl = Cl
            aux = aux + "Cl "

    if (verificacionVariable(TLD, float)):
        if TLD is not None:
            if THD is None:
                val = confi.THD
            else:
                val = THD
            if TLD < val:
                confi.TLD = TLD
                aux = aux  + " TLD"
                    
    if (verificacionVariable(THD, float)):
        if THD is not None:
            if TLD is None:
                val = confi.TLD
            else:
                val = TLD
            if THD > val:
                confi.THD = THD
                aux = aux + " THD"

    #Guardo variables:
    db.session.commit()
    #guardadoVariables()

    return aux

#Funcion para cambiar valor de alarma en db de configuraciones y activar asi envio de mail
def envioAlarma():
    #Obtengo valor de alarma de db (configuraciones) 
    #Cambio valor del mismo segun estadoAlarma y las situaciones de aviso (envio de email)
    confi = configuraciones.query.get(1)
    if estadoAlarma == True:

        if temperatura is None or float(temperatura) < confi.TL or float(temperatura) > confi.TD:
            confi.alarma = "1 - 1"
        else:
            confi.alarma = "1 - 0"
        if temperatura is None or float(temperaturaD) < confi.TLD or float(temperaturaD) > confi.THD:
            confi.alarma = confi.alarma + " - 1"
        else:
            confi.alarma = confi.alarma + " - 0"
    else:
        confi.alarma = "0 - 0" 
    db.session.commit()


##Funcion de busqueda de fechas: Retorna Fechas,valorNum(temp o lux)
def buscarVals(tipo,f_desde,f_hasta,zona):

    if (tipo == "T"):
        ##strArch = "valoresT.txt"
        fechasDeseadas = valoresT.query.filter(valoresT.fecha.between(f_desde,f_hasta))
    elif (tipo == "L"):
        fechasDeseadas = valoresL.query.filter(valoresL.fecha.between(f_desde,f_hasta))
    elif (tipo == "TD"):
        fechasDeseadas = valoresTD.query.filter(valoresTD.fecha.between(f_desde,f_hasta))
    
    
    #Defino listas a devolver
    rets=[[],[],[]] #rets[0]=fechas[],rets[1]=vals[],rets[2]=zonas[]
    if fechasDeseadas.count() > 0:

    #Si en la db tengo fechas dentro de las deseadas, obtengo valores:        
        for i in fechasDeseadas:

            #Obtengo fecha y zona de i
            fecha_i=i.fecha
            zona_i=i.zona
            #Verifico que tipo de variable busco
            if tipo == 'T' or tipo == 'TD':
                val = i.temp
            else:
                val = i.lux

            if(val is None):
                valNum=None
            else:  
                valNum=val
            #Verifico si estoy dentro de valores de tiempo
            if (f_desde <= fecha_i and f_hasta >= fecha_i):
                
                if(zona_i == zona or zona == "Ambos"):                    
                    rets[0].append(fecha_i)
                    rets[1].append(valNum)
                    rets[2].append(zona_i)

    return rets

def arch_Historial(tipo,vals,fechas,zonas):
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
        for val, fecha, zona in zip(vals, fechas, zonas):
            if tipo=="T" or tipo == "TD":
                strTipo = ["Temperatura: "," grados Celcius"]
            else:
                strTipo = ["Valor de luz: "," Lux"]
            #Escribo: "Fecha: xx/xx/xxxx xx:xx:xx - Valor: xxx Lux/grados Celcius"
            arch.write("Fecha: "+str(fecha)+" - "+strTipo[0]+str(val)+strTipo[1]+" (zona: "+zona+")\n")
    #Una vez grabado el archivo, devuelvo la direccion donde se creo el archivo    
    return dirArch
