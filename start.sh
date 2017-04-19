#!/bin/bash
python Presencia/alarma.py&
PID=$!
echo $PID | tee pid
exit 0
