from app import configuraciones, db, datosSinEnviar

##Podria ver parametros: N envios y tiempo de sleep en confi... cambiar luego
N=20
t_sleep=1*60 ##1 minuto

##Loop principal
while True:
    n_datos=datosSinEnviar.query.all()
    for dato in datosSinEnviar.query.order_by(User.id)[1:20]
    print(dato)

