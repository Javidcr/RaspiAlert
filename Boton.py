#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Autores: Fco Javier del Castillo y Carlos Suárez
import RPi.GPIO as GPIO
import commands
import os

BtnPin = 35
Gpin   = 32
Rpin   = 37
control = 0

def setup():
        GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
	GPIO.setup(Gpin, GPIO.OUT)     # Set Green Led Pin mode to output
	GPIO.setup(Rpin, GPIO.OUT)     # Set Red Led Pin mode to output
	GPIO.setup(BtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)    # Set BtnPin's mode is input, and pull up to high level(3.3V)
	GPIO.add_event_detect(BtnPin, GPIO.BOTH, callback=detect, bouncetime=200)

def Led(x):
	if x == 0:
		GPIO.output(Rpin, 1)
		GPIO.output(Gpin, 0)
		if control == 0:
                        os.system('./raspialert.sh')
                        control = 1
	if x == 1:
		GPIO.output(Rpin, 0)
		GPIO.output(Gpin, 1)
		os.system('./raspialert_stop.sh')

def Print(x):
	if x == 0:
		print '    ***********************'
		print '    * ¡Sistema arrancado! *'
		print '    ***********************'
                #resultado = commands.getoutput('./raspialert.sh')

def detect(chn):
	Led(GPIO.input(BtnPin))
	Print(GPIO.input(BtnPin))

def loop():
	while True:
		pass

def destroy():
	GPIO.output(Gpin, GPIO.HIGH)       # Green led off
	GPIO.output(Rpin, GPIO.HIGH)       # Red led off
	GPIO.cleanup()                     # Release resource

if __name__ == '__main__':     # Program start from here
	setup()
	try:
		loop()
	except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
		destroy()

