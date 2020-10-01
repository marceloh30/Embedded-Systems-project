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
valorR = 0
# Define led pins as output
GPIO.setup(ledRed, GPIO.OUT)    
# turn leds OFF 
GPIO.output(ledRed, GPIO.LOW)
f = open("valorR.txt", "r")#Por ahi meter en el lugar especifico que se usa y cerrar

#Ruta principal	
@app.route("/")
def index():
	# Read Sensors Status
	valorR  = f.readline()
	if len(valorR) != 0:
		variablesWeb.resistencia = valorR
	ledRedSts = GPIO.input(ledRed)
	templateData = {
              'title' : 'GPIO output Status!',
              'ledRed'  : ledRedSts,
              'valorR'  : variablesWeb.resistencia,
			  'estadoAlarma' : variablesWeb.estadoAlarma
        }
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
	
	valorR  = f.readline()
	if len(valorR) != 0:
		variablesWeb.resistencia = valorR
	templateData = {
              'ledRed'  : ledRedSts,
              'valorR'  : valorR,
			  'estadoAlarma' : variablesWeb.estadoAlarma
	}

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
		Rt = request.form['Rt']
		Ct = request.form['Ct']

		if variablesWeb.verificacionVariables(TL, TH, ts, destino, tA, Rt, Ct):
			variablesWeb.guardadoVariables(TL, TH, ts, destino, tA, Rt, Ct)
		
		return redirect(url_for('index'))
	return render_template('parametrosConfi.html')

##Funcion de busqueda de fechas: Retorna valorNum(temp o lux) y fecha
def buscarValores(arch,fecha_desde,fecha_hasta):
	#arch = open("valorTemp.txt" o "valorLux.txt", "r")
	#Ambos tienen formato: datatime-valorNum

	#Defino variables a llenar
	valoresNum=[]
	fechas=[]

	for linea in arch.readlines():
		valLinea,fechaLinea=linea.split(',')
		##Verifico si estoy dentro de valores de tiempo
		if((fecha_desde <= fechaLinea) and (fecha_hasta >= fechaLinea)):
			fechas.append(fechaLinea)
			valoresNum.append(valLinea)
	#Una vez finalizada la lectura cierro arch??
	##arch.close() 

	return valoresNum,fechas

#Funcion para verificar si el string contiene numeros
def str_conNums(str_in):
	return any(char.isdigit() for char in str_in)

##Ruta de recepcion de intervalos de tiempo para Temps-Luxs
@app.route("/historiaTemp" , methods = ["GET", "POST"])
def recTiempos():
	if request.method == 'POST':

		t1 = str(request.form['t1'])
		fecha1 = str(request.form['fecha1'])
		t2 = str(request.form['t2'])
		fecha2 = str(request.form['fecha2'])
		#print(t1,fecha1,"... hasta:",t2,fecha2)
		#print(str_conNums(t1),str_conNums(t2),str_conNums(fecha1),str_conNums(fecha2))
		if (str_conNums(t1) and str_conNums(t2) and str_conNums(fecha2) and str_conNums(fecha1)):
			##Formato -> t: '18:06', fecha: '2020-09-01'
			hm1=t1.split(':')
			dma1=fecha1.split('-')
			hm2=t2.split(':')
			dma2=fecha2.split('-')
			#args de datetime: Anio, Mes, Dia, Hora, Min, Seg, Miliseg
			f_desde=datetime(int(dma1[0]),int(dma1[1]),int(dma1[2]),int(hm1[0]),int(hm1[1]),0,0) ##seg y ms los tomo en 0
			f_hasta=datetime(int(dma2[0]),int(dma2[1]),int(dma2[2]),int(hm2[0]),int(hm2[1]),0,0) ##seg y ms los tomo en 0
			print("Desde:",f_desde,".. Hasta:",f_hasta,"Ahora a buscarle en H_Temp.txt")

			#Abro el arch. de temperaturas, busco valores y escribo
			archTemp = open("H_Temp.txt")
			temps,fechas=buscarValores(archTemp,f_desde,f_hasta)
			archTemp.close()
			if (temps != 0):
				#Creo archivo descargable por usuario?
				print(temps,fechas)	
		else:
			print("Error recibiendo datos")
		return redirect(url_for('index'))
	return render_template('askHistTemp.html')


if __name__ == "__main__":
   app.run(host='192.168.0.200', port=8080, debug=True)
