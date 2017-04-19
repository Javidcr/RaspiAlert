#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Autores: Fco Javier del Castillo y Carlos Suárez
import RPi.GPIO as GPIO
import LCD1602
import time


GPIO.setmode(GPIO.BCM)


def setup():
	LCD1602.init(0x27, 1)	# init(slave address, background light)
	LCD1602.write(0, 0, ' # RaspiAlert #')
	LCD1602.write(1, 1, '##############')
	time.sleep(3)
	

def destroy():
        LCD1602.clear()

if __name__ == '__main__':
	try:
                setup()
	except KeyboardInterrupt:
		destroy() 
