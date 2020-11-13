from datetime import date
from datetime import datetime
from app import db

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
    alarma = db.Column(db.String(8), default = "0 - 0")
    def __repr__(self):
        return '<configuraciones %r>' % self.TL

class valoresT(db.Model):
	id = db.Column(db.Integer, primary_key = True)

	#Obtengo fecha actual sin microsegundos
	#fechaPredet= datetime.now().replace(microsecond=0)
	#fechaPredet= fechaPredet.replace(microsecond=0)

	#Atributos de valoresT
	fecha = db.Column(db.DateTime, default = datetime.now)
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
		return '<valoresL %r>' % self.lux