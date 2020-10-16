import RPi.GPIO as GPIO
import variablesWeb
from datetime import date
from datetime import datetime
from flask import Flask, render_template, redirect,request, url_for, flash, send_file
import subprocess
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
app.secret_key = 'obligatorio' #Nesesario para usar flash

##Ejecuto otros programas necesarios para el buen funcionamiento del sist:
#Lectura analogica de temperatura:


def accionesIndex():
    # Read Sensors Status
    [valorT,len_linea]  = variablesWeb.leerValor("T",variablesWeb.posicionLectura)
    if (valorT) != 0:
        variablesWeb.temperatura = valorT
        #Sumo los bytes para la nueva posicion de lectura
        variablesWeb.posicionLectura = variablesWeb.posicionLectura + len_linea

    ledRedSts = GPIO.input(ledRed)
    templateData = {
        'title' : 'GPIO output Status!',
        'ledRed'  : ledRedSts,
        'valorT'  : variablesWeb.temperatura,
        'estadoAlarma' : variablesWeb.estadoAlarma
    }
    return templateData


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
		aux = variablesWeb.cambioValores(TL, TH, ts, destino, tA, Rt, Ct, Rl, Cl)
		if len(aux) > 0:
			flash('Se ingresaron de forma incorrecta los parametros: ' + aux)
			print(aux)	
			
		return redirect(url_for('index'))
	return render_template('parametrosConfi.html')



#Funcion para verificar si el string contiene numeros
def str_conNums(str_in):
	return any(char.isdigit() for char in str_in)

##Ruta de recepcion de intervalos de tiempo para Temps-Luxs

@app.route("/historial" , methods = ["GET", "POST"])
def recTiempos():	
	templateData= {
		"numLineas":0,
		"temps":[],
		"fechas":[],
		"arch": None	
	}
	if request.method == 'POST':
		#Recibo valores desde pagina web
		tipo = str(request.form['tipo']) #= "T" o "L"
		t1 = str(request.form['t1'])
		fecha1 = str(request.form['fecha1'])
		t2 = str(request.form['t2'])
		fecha2 = str(request.form['fecha2'])

		#Verifico si recibi valores numericos
		if (str_conNums(t1) and str_conNums(t2) and str_conNums(fecha2) and str_conNums(fecha1)):

			##Formato -> t: '18:06', fecha: '2020-09-01'
			#Obtengo hora y fecha de cada valor obtenido por pagina web
			hm1=t1.split(':')
			dma1=fecha1.split('-')
			hm2=t2.split(':')
			dma2=fecha2.split('-')

			#args de datetime: Anio, Mes, Dia, Hora, Min, Seg, Miliseg
			f_desde=datetime(int(dma1[0]),int(dma1[1]),int(dma1[2]),int(hm1[0]),int(hm1[1]),0,0) ##seg y ms los tomo en 0
			f_hasta=datetime(int(dma2[0]),int(dma2[1]),int(dma2[2]),int(hm2[0]),int(hm2[1]),0,0) ##seg y ms los tomo en 0
			print("Busco desde:",f_desde,", Hasta:",f_hasta)

			#Busco valores segun tipo y fechas y obtengo temps y fechas que se encuentren entre f_desde y f_hasta
			numLineas=0
			[fechas,temps] = variablesWeb.buscarVals(str(tipo),f_desde,f_hasta)
			if len(temps) == len(fechas):
				numLineas = len(temps)
			else:
				print(len(temps),"diferente a ",len(fechas))
				numLineas = min(map(len,[temps,fechas]))
			
			if (len(temps) != 0 and len(fechas) != 0):
				if(len(temps) <= 10): #Si tengo menos de 10 valores, los envio a la pagina 
					print(temps,fechas)
					templateData= {
						"numLineas":numLineas,
						"temps":temps,
						"fechas":fechas,
						"arch": None	
					}
				else: #Tengo mas de 10 valores, muestro arch. descargable	
					print("Mas de 10 valores, crear archivo pa descargar")
					#Obtengo dirArch y creo archivo con arch_Historial(tipo,vals,fechas)
					dirArch = variablesWeb.arch_Historial(str(tipo),temps,fechas)
					templateData = {
						"numLineas":numLineas,
						"temps":temps,
						"fechas":fechas,
						"arch": dirArch	
					}
		else:
			flash("Error al recibir fechas: valores no numericos!")
		return render_template('Historial.html', **templateData)

	return render_template('askHistorial.html')
#Muestra del historial de las fechas pedidas
@app.route('/download')
def downloadFile():
	return send_file("/tmp/archivoHistorial.txt", as_attachment=True)


if __name__ == "__main__":
   app.run(host='192.168.0.200', port=8080, debug=True)
