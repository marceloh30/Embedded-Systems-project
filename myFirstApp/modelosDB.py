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

    def __repr__(self):
        return '<configuraciones %r>' % self.TL
