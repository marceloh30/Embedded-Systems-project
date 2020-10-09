import RPi.GPIO as GPIO
import variablesWeb
from datetime import date
from datetime import datetime
from flask import Flask, render_template, redirect,request, url_for
app = Flask(__name__)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
#define actuators GPIOs
ledRed = 17
#initialize GPIO status variables
ledRedSts = 0
valorT = 0
# Define led pins as output
GPIO.setup(ledRed, GPIO.OUT)    
# turn leds OFF 
GPIO.output(ledRed, GPIO.LOW)
app.secret_key = 'obligatorio'

##Ejecuto otros programas necesarios para el buen funcionamiento del sist:
#Lectura analogica de temperatura:
exec(lecturaAnalogica.py,"T")

#Funcion para leer valores num (Temp o Lux) de sus respectivos txt
def leerValor(tipo, pos): #Devuelve largo de linea y valNum
	rets=[0,0]
	if(tipo=="T"):
		strArch="valoresT.txt"
	else:
		strArch="valoresL.txt"
	try:
		with open(strArch,"r") as f:
			#Lo llevo a la posicion del ultimo ingreso
			f.seek(pos)
			#Leo el ultimo valor
			linea = f.readline()
			rets[1]=length(linea) 		#Guardo bytes leidos de linea		
			rets[0]=linea.split(",")[1]	#Guardo valNum
	except Exception as e:
		# get line number and error message
		with open(strArch, 'x') as f:
			print(e,"\nArchivo no existe. Creo el archivo",strArch,".")
	return rets

#Ruta principal	
def accionesIndex():
	# Read Sensors Status
	[valorT,len_linea]  = leerValor("T",variablesWeb.posicionLectura)
	if len(valorT) != 0:
		variablesWeb.temp = valorT
	#Sumo los bytes para la nueva posicion de lectura (actualmente solo de T, habria que agregar posicionLecturaL)	
	variablesWeb.posicionLectura = variablesWeb.posicionLectura + len_linea

	ledRedSts = GPIO.input(ledRed)
	templateData = {
              'title' : 'GPIO output Status!',
              'ledRed'  : ledRedSts,
              'valorT'  : variablesWeb.temperatura,
			  'estadoAlarma' : variablesWeb.estadoAlarma
        }
	return datosTemplate

@app.route("/")
def index():
	''' Pruebo hacerlo funcion para usarlo tambien en ruta /<devicename>/<action>
	# Read Sensors Status
	[valorT,len_linea]  = leerValor("T",variablesWeb.posicionLectura)
	if len(valorT) != 0:
		variablesWeb.temp = valorT
	#Sumo los bytes para la nueva posicion de lectura	
	variablesWeb.posicionLectura = variablesWeb.posicionLectura + len_linea

	ledRedSts = GPIO.input(ledRed)
	templateData = {
              'title' : 'GPIO output Status!',
              'ledRed'  : ledRedSts,
              'valorT'  : variablesWeb.temperatura,
			  'estadoAlarma' : variablesWeb.estadoAlarma
        }
	'''
	templateData = accionesIndex()
	
	return render_template('index.html', **templateData)

#Ruta para acciones con Alarma y Led
@app.route("/<deviceName>/<action>")
def action(deviceName, action):
	if deviceName == 'ledRed':
		actuator = ledRed
		if action == "on":
			GPIO.output(actuator, GPIO.HIGH)
		else:
			GPIO.output(actuator, GPIO.LOW)
	if deviceName == 'alarma':
		if action == "on":
			variablesWeb.estadoAlarma = True
		else:
			variablesWeb.estadoAlarma = False
	
	ledRedSts = GPIO.input(ledRed)

	#Realizo la actualizacion de datos para index:
	templateData = accionesIndex()

	return render_template('index.html', **templateData)

#Ruta de envio y recepcion de parametros
@app.route("/envioParametros" , methods = ["GET", "POST"])
def tomaDatos():
	if request.method == 'POST':
		TL = request.form['TL']
		TH = request.form['TH']
		ts = request.form['ts']
		destino = request.form['destino']
		tA = request.form['tA']
		#Valores de Rt y Ct para lecturaAnalogica de temp.
		Rt = request.form.get('Rt', type=float)
		Ct = request.form.get('Ct', type=float)
		#Valores de Rl y Cl para lecturaAnalogica de lux
		Rl = request.form.get('Rl', type=float)
		Cl = request.form.get('Cl', type=float)

		#Verifico si concuerda con los valores maximos y minimos y en ese caso guardo las variables recibidas
		if variablesWeb.verificacionVariables(TL, TH, ts, destino, tA, Rt, Ct, Rl, Cl):
			variablesWeb.guardadoVariables(TL, TH, ts, destino, tA, Rt, Ct, Rl, Cl)
		
		return redirect(url_for('index'))
	return render_template('parametrosConfi.html')

##Funcion de busqueda de fechas: Retorna Fechas,valorNum(temp o lux)
def buscarVals(tipo,fecha_desde,fecha_hasta):
	
    if (tipo=="T"):
        strArch = "valoresT.txt"
    else:
        strArch = "valoresL.txt"

	with open(strArch,"r") as archTL:
		
        #Defino listas a devolver    
        fechas=[]
        vals=[]

        for linea in archTL.readlines():
            #Separo fecha para hacer un datetime
            arr=linea.split(",")
            fh_array=arr[0].split(" ")
            dte=fh_array[0].split("-")
            hr=fh_array[1].split(":")
            #Creo datetime con valores de la linea
        	fecha_l=datetime(int(dte[0]),int(dte[1]),int(dte[2]),int(hr[0]),int(hr[1]),int(hr[2]),0)
			valNum=float(arr[1])
            #Verifico si estoy dentro de valores de tiempo
            if ((f_desde <= fecha_l) and (f_hasta >= fecha_l)):
                fechas.append(fecha_l)
                vals.append(valNum)
    
    return [[fechas],[vals]] 

#Funcion para verificar si el string contiene numeros
def str_conNums(str_in):
	return any(char.isdigit() for char in str_in)

##Ruta de recepcion de intervalos de tiempo para Temps-Luxs
@app.route("/historial" , methods = ["GET", "POST"])
def recTiempos():
	templateData = [[],[]] #Datos para pagina que muestre valores
	if request.method == 'POST':
		tipo = str(requst.form['tipo']) #= "T" o "L"
		t1 = str(request.form['t1'])
		fecha1 = str(request.form['fecha1'])
		t2 = str(request.form['t2'])
		fecha2 = str(request.form['fecha2'])
		#Verifico si recibi valores numericos
		if (str_conNums(t1) and str_conNums(t2) and str_conNums(fecha2) and str_conNums(fecha1)):
			##Formato -> t: '18:06', fecha: '2020-09-01'
			hm1=t1.split(':')
			dma1=fecha1.split('-')
			hm2=t2.split(':')
			dma2=fecha2.split('-')
			#args de datetime: Anio, Mes, Dia, Hora, Min, Seg, Miliseg
			f_desde=datetime(int(dma1[0]),int(dma1[1]),int(dma1[2]),int(hm1[0]),int(hm1[1]),0,0) ##seg y ms los tomo en 0
			f_hasta=datetime(int(dma2[0]),int(dma2[1]),int(dma2[2]),int(hm2[0]),int(hm2[1]),0,0) ##seg y ms los tomo en 0
			''' VERIFICACION DE FECHAS!!! Puedo probar un try en los datetime por las dudas que se pase de hora o algo d eso
			if(f_desde > 0):
				print("Si, es fecha")
			if(f_hasta > 0):
				print("El hasta tambien")
			else:
				print("wtf man")	
				flash('pifiaste.. escribi bien las fechas.')
			'''
			print("Busco desde:",f_desde,", Hasta:",f_hasta)

			#Busco valores segun tipo y escribo
			
			[temps,fechas]=buscarValores(str(tipo),f_desde,f_hasta)

			if (len(temps) != 0 and len(fechas) != 0):
				if(len(temps) <= 10): #Si tengo menos de 10 valores, los envio a la pagina 
					
					#print(temps,fechas)
				else: #Tengo mas de 10 valores, muestro arch. descargable	
		else:
			print("Error recibiendo datos")
		return redirect(url_for('index'))
	templateData = accionesIndex()
	#Ver como cambiar:
	return render_template('mostrarHistorial.html', **templateData)


if __name__ == "__main__":
   app.run(host='192.168.0.200', port=8080, debug=True)
