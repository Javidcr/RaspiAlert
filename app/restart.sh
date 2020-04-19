#!/bin/bash

./raspialert_stop.sh
echo "Sistema apagado\n"
./raspialert.sh
echo "Sistema arrancado\n"

exit 0
