import RPi.GPIO as GPIO
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
	
@app.route("/")
def index():
	# Read Sensors Status
	aux  = f.readline()
	if aux.strip():
		valorR = aux
	ledRedSts = GPIO.input(ledRed)
	templateData = {
              'title' : 'GPIO output Status!',
              'ledRed'  : ledRedSts,
              'valorR'  : valorR,
        }
	return render_template('index.html', **templateData)
	
@app.route("/<deviceName>/<action>")
def action(deviceName, action):
	if deviceName == 'ledRed':
		actuator = ledRed
	#if deviceName == 'envioParametros':
	#	return render_template('parametrosConfi.html')
	if action == "on":
		GPIO.output(actuator, GPIO.HIGH)
	if action == "off":
		GPIO.output(actuator, GPIO.LOW)
	ledRedSts = GPIO.input(ledRed)
   	aux  = f.readline()
	if aux.strip():
		valorR = aux
	templateData = {
              'ledRed'  : ledRedSts,
              'valorR'  : valorR,
	}
	return render_template('index.html', **templateData)
@app.route("/envioParametros" , methods = ["GET", "POST"])
def tomaDatos():
	if request.method == 'POST':
		TL = request.form['TL']
		TH = request.form['TH']
		ts = request.form['ts']
		#destino = request.form['destino']
		#tA = request.form['tA']
		#Rt = request.form['Rt']
		#Ct = request.form['Ct']
		#Rl = request.form['Rl']
		#Cl = request.form['Cl']
		pc = open("configuracion.txt", "w")
		pc.write("TL = "+str(TL)+'\n')
		pc.write("TH = "+str(TH)+'\n')
		pc.write("ts = "+str(ts)+'\n')
		pc.close()
		return redirect(url_for('index'))
	return render_template('parametrosConfi.html')


if __name__ == "__main__":
   app.run(host='192.168.0.200', port=8080, debug=True)
