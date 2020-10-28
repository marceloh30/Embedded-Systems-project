#!/bin/bash
python3 creacionTXT.py &
pid=$!
wait $pid
echo Process $pid finished.
python3 app.py &
python3 alarma.py &
python3 lecturaAnalogica.py T &
python3 lecturaAnalogica.py L &
