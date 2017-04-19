#!/bin/bash

read pid < pid ;

echo $pid;
kill -9 $pid;
#killall python
exit 0;
