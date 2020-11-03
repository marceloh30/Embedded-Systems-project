import RPi.GPIO as GPIO
from datetime import date
from datetime import datetime
from flask import Flask, render_template, redirect,request, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
import subprocess
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///obligatorio.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
#inicar la base de datos

db = SQLAlchemy(app)

class configuraciones(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    TL = db.Column(db.Integer)
    TH = db.Column(db.Integer)
    ts = db.Column(db.Integer)
    destino = db.Column(db.String(64))
    tA = db.Column(db.Integer)
    #Valores de Rt y Ct para lecturaAnalogica de temp.
    Rt = db.Column(db.Integer)
    Ct = db.Column(db.Integer)
    #Valores de Rl y Cl para lecturaAnalogica de lux
    Rl = db.Column(db.Integer)
    Cl = db.Column(db.Integer)

    def __repr__(self):
        return '<configuraciones %r>' % self.TL

class valoresT(db.Model):
	id = db.Column(db.Integer, primary_key = True)

	#Obtengo fecha actual sin microsegundos
	fechaPredet= datetime.now()
	fechaPredet= fechaPredet.replace(microsecond=0)

	#Atributos de valoresT
	fecha = db.Column(db.DateTime, default = fechaPredet)
	temp = db.Column(db.Float)

	def __repr__(self):
		return '<valoresT %r>' % self.temp

class valoresL(db.Model):
	id = db.Column(db.Integer, primary_key = True)

	#Obtengo fecha actual sin microsegundos
	fechaPredet= datetime.now()
	fechaPredet= fechaPredet.replace(microsecond=0)

	#Atributos de valoresL
	fecha = db.Column(db.DateTime, default = fechaPredet)
	lux = db.Column(db.Float)

	def __repr__(self):
		return '<valoresT %r>' % self.lux

import variablesWeb #Parece que este import TIENE que ir aca 



GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
#Defino nro GPIO del led
pin_led = 17
#Inicializo estados a mostrar
estado_led = 0
valorT = 0
valorL = 0
# Defino como output el pin del led y lo dejo en off
GPIO.setup(pin_led, GPIO.OUT)     
GPIO.output(pin_led, GPIO.LOW)

app.secret_key = 'obligatorio' #Necesario para usar flash

##Ejecuto otros programas necesarios para el buen funcionamiento del sist:
#Lectura analogica de temperatura:

def accionesIndex():
	#Leo valores de temperatura actuales
	#valoresT.query.all()
	#print(valoresT.query.order_by(valoresT.id.desc()))
	valorT = valoresT.query.get(len(valoresT.query.all()))
	print(valorT)

	valorL = valoresL.query.get(len(valoresL.query.all()))
	print(valorL)

	if valorT is not None: 
	# Dejo que sea None para poder activar alarma (no necesario en L)
		variablesWeb.temperatura = valorT.temp
	#if valorL is not None:
	#	variablesWeb.lux = valorL

	estado_led = GPIO.input(pin_led)
	templateData = {
		
		'led' : estado_led,
		'valorT' : variablesWeb.temperatura,
		'valorL' : valorL.lux,
		'estadoAlarma' : variablesWeb.estadoAlarma
	}
	return templateData

@app.route("/")
def index():
	variablesWeb.envioAlarma()
	templateData = accionesIndex()
	return render_template('index.html', **templateData)

#Ruta para acciones con Alarma y Led
@app.route("/<deviceName>/<action>")
def action(deviceName, action):
	if deviceName == 'led':
		#actuador = pin_led
		if action == "on":
			GPIO.output(pin_led, GPIO.HIGH)
		else:
			GPIO.output(pin_led, GPIO.LOW)
	if deviceName == 'alarma':
		if action == "on":
			variablesWeb.estadoAlarma = True
		else:
			variablesWeb.estadoAlarma = False
	
	#Realizo la actualizacion de datos para index:
	templateData = accionesIndex()
	variablesWeb.envioAlarma()
	return render_template('index.html', **templateData)

#Ruta de envio y recepcion de parametros
@app.route("/envioParametros" , methods = ["GET", "POST"])
def tomaDatos():
	if request.method == 'POST':
		TL = request.form.get('TL', type=float)
		TH = request.form.get('TH', type=float)
		ts = request.form.get('ts', type=float)
		destino = request.form['destino']
		tA = request.form.get('tA', type=float )
		#Valores de Rt y Ct para lecturaAnalogica de temp.
		Rt = request.form.get('Rt', type=float)
		Ct = request.form.get('Ct', type=float)
		#Valores de Rl y Cl para lecturaAnalogica de lux
		Rl = request.form.get('Rl', type=float)
		Cl = request.form.get('Cl', type=float)

		#Verifico si concuerda con los valores maximos y minimos y en ese caso guardo las variables recibidas
		aux = variablesWeb.cambioValores(TL, TH, ts, destino, tA, Rt, Ct, Rl, Cl)
		if len(aux) > 0:
			flash('Se ingresaron de forma correcta el/los parametro/s: ' + aux)
			print(aux)	
			
		return redirect(url_for('index'))
	return render_template('parametrosConfi.html')



#Funcion para verificar si el string contiene numeros
def str_conNums(str_in):
	return any(char.isdigit() for char in str_in)

##Ruta de recepcion de intervalos de tiempo para Temps-Luxs
@app.route("/historial" , methods = ["GET", "POST"])
def recTiempos():
	tipoVal = "Temperatura/Iluminancia"	
	templateData= {
		"numLineas":0,
		"temps":[],
		"fechas":[],
		"arch": None,
		"tipoVal": tipoVal
	}
	if request.method == 'POST':
		#Recibo valores desde pagina web
		tipo = str(request.form['tipo']) #= "T" o "L"
		t1 = str(request.form['t1'])
		fecha1 = str(request.form['fecha1'])
		t2 = str(request.form['t2'])
		fecha2 = str(request.form['fecha2'])
		print(tipo)
		#Tomo tipoVal segun tipo:
		if (tipo=="T"):
			tipoVal="Temperatura (°C)"
		elif (tipo=="L"):
			tipoVal="Iluminancia (Lux)"

		#Verifico si recibi valores numericos
		if (str_conNums(t1) and str_conNums(t2) and str_conNums(fecha2) and str_conNums(fecha1) and (tipo is "T" or tipo is "L")):

			##Formato -> t: '18:06', fecha: '2020-09-01'
			#Obtengo hora y fecha de cada valor obtenido por pagina web
			hm1=t1.split(':')
			dma1=fecha1.split('-')
			hm2=t2.split(':')
			dma2=fecha2.split('-')

			yr_actual=datetime.now().year

			if (int(dma1[0])>yr_actual or int(dma2[0])>yr_actual):
				str_flash="Error al recibir años: no se predice futuro, estamos en el año " + str(2020)
				flash(str_flash)
			else:
				#args de datetime: Anio, Mes, Dia, Hora, Min, Seg, Miliseg
				f_desde=datetime(int(dma1[0]),int(dma1[1]),int(dma1[2]),int(hm1[0]),int(hm1[1]),0,0) ##seg y ms los tomo en 0
				f_hasta=datetime(int(dma2[0]),int(dma2[1]),int(dma2[2]),int(hm2[0]),int(hm2[1]),0,0) ##seg y ms los tomo en 0
				print("Busco desde:",f_desde,", Hasta:",f_hasta)

				#Busco valores segun tipo y fechas y obtengo temps y fechas que se encuentren entre f_desde y f_hasta
				numLineas=0
				[fechas,vals] = variablesWeb.buscarVals(str(tipo),f_desde,f_hasta)
				if len(vals) == len(fechas):
					numLineas = len(vals)
				else:	#No deberia de ocurrir, pero si ocurre, con esto evito errores:
					print(len(vals),"diferente a ",len(fechas))
					numLineas = min(map(len,[vals,fechas]))
				
				if (len(vals) != 0 and len(fechas) != 0):
					if(len(vals) <= 10): #Si tengo menos de 10 valores, los envio a la pagina 
						print(vals,fechas)
						templateData= {
							"numLineas":numLineas,
							"vals":vals,
							"fechas":fechas,
							"arch": None,
							"tipoVal": tipoVal
						}
					else: #Tengo mas de 10 valores, muestro arch. descargable	
						print("Mas de 10 valores, crear archivo pa descargar")
						#Obtengo dirArch y creo archivo con arch_Historial(tipo,vals,fechas)
						dirArch = variablesWeb.arch_Historial(str(tipo),vals,fechas)
						templateData = {
							"numLineas":numLineas,
							"temps":vals,
							"fechas":fechas,
							"arch": dirArch,
							"tipoVal": tipoVal
						}
		else:
			flash("Error al recibir fechas: valores no numericos!")
		return render_template('Historial.html', **templateData)

	return render_template('askHistTemp.html')
#Muestra del historial de las fechas pedidas
@app.route('/download')
def downloadFile():
	return send_file("/tmp/archivoHistorial.txt", as_attachment=True)


##"Main":

#Verifico configuracion.txt:
#variablesWeb.ver_archConf()
#Corro el servidor web Flask:
if __name__ == "__main__":
	db.create_all()
	app.run(host='192.168.0.200', port=8080, debug=True)
