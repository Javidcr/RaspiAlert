#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Autores: Fco Javier del Castillo y Carlos Suárez

import RPi.GPIO as GPIO
import telebot
from telebot import types
import time
import os
import LCD1602

# Ponemos nuestro Token generado con el @BotFather
TOKEN = "372274168:AAGZUERMxg4yh-WSheggBdhxbVLhubntyTo"

BtnPin = 37
#Gpin   = 12
#Rpin   = 13
pirInput = 40

DHTPIN = 11

#GPIO.setmode(GPIO.BCM)
GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location

MAX_UNCHANGE_COUNT = 100

STATE_INIT_PULL_DOWN = 1
STATE_INIT_PULL_UP = 2
STATE_DATA_FIRST_PULL_DOWN = 3
STATE_DATA_PULL_UP = 4
STATE_DATA_PULL_DOWN = 5


# COLOR TEXTO
class color:
    RED = '\033[91m'
    BLUE = '\033[94m'
    GREEN = '\033[32m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
def enviar_foto():
    cid = 331109269
    bot.send_message(cid, "¡¡¡HA SIDO PILLADO UN INTRUSO!!!")
    bot.send_chat_action(cid, 'upload_photo')
    try:
        foto = "/home/pi/webcam/" + (time.strftime("%H%M%S-%d%m%y")) + ".jpeg"
        os.system('fswebcam -r 1280x720  %s' % foto)
        bot.send_photo(cid, open(foto, 'rb'))
        print(color.BLUE + " [i] Foto enviada!!" + color.ENDC)
    except NameError:
        bot.send_message(cid, "La cámara no está conectada...")

def setup():
    GPIO.setwarnings(False)
    GPIO.setup(pirInput, GPIO.IN)         #Read output GPIO 21 from PIR motion sensor

    #Button and LED setup
    #GPIO.setup(Gpin, GPIO.OUT)     # Set Green Led Pin mode to output
    #GPIO.setup(Rpin, GPIO.OUT)     # Set Red Led Pin mode to output
    GPIO.setup(BtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)    # Set BtnPin's mode is input, and pull up to high level(3.3V)
    GPIO.add_event_detect(BtnPin, GPIO.BOTH, callback=detect, bouncetime=200)

    #setup display
    LCD1602.init(0x27, 1)	# init(slave address, background light)

def read_dht11_dat():
	GPIO.setup(DHTPIN, GPIO.OUT)
	GPIO.output(DHTPIN, GPIO.HIGH)
	time.sleep(0.05)
	GPIO.output(DHTPIN, GPIO.LOW)
	time.sleep(0.02)
	GPIO.setup(DHTPIN, GPIO.IN, GPIO.PUD_UP)

	unchanged_count = 0
	last = -1
	data = []
	while True:
		current = GPIO.input(DHTPIN)
		data.append(current)
		if last != current:
			unchanged_count = 0
			last = current
		else:
			unchanged_count += 1
			if unchanged_count > MAX_UNCHANGE_COUNT:
				break

	state = STATE_INIT_PULL_DOWN

	lengths = []
	current_length = 0

	for current in data:
		current_length += 1

		if state == STATE_INIT_PULL_DOWN:
			if current == GPIO.LOW:
				state = STATE_INIT_PULL_UP
			else:
				continue
		if state == STATE_INIT_PULL_UP:
			if current == GPIO.HIGH:
				state = STATE_DATA_FIRST_PULL_DOWN
			else:
				continue
		if state == STATE_DATA_FIRST_PULL_DOWN:
			if current == GPIO.LOW:
				state = STATE_DATA_PULL_UP
			else:
				continue
		if state == STATE_DATA_PULL_UP:
			if current == GPIO.HIGH:
				current_length = 0
				state = STATE_DATA_PULL_DOWN
			else:
				continue
		if state == STATE_DATA_PULL_DOWN:
			if current == GPIO.LOW:
				lengths.append(current_length)
				state = STATE_DATA_PULL_UP
			else:
				continue
	if len(lengths) != 40:
		print "NA"
		return False

	shortest_pull_up = min(lengths)
	longest_pull_up = max(lengths)
	halfway = (longest_pull_up + shortest_pull_up) / 2
	bits = []
	the_bytes = []
	byte = 0

	for length in lengths:
		bit = 0
		if length > halfway:
			bit = 1
		bits.append(bit)
	#print "bits: %s, length: %d" % (bits, len(bits))
	for i in range(0, len(bits)):
		byte = byte << 1
		if (bits[i]):
			byte = byte | 1
		else:
			byte = byte | 0
		if ((i + 1) % 8 == 0):
			the_bytes.append(byte)
			byte = 0
	#print the_bytes
	checksum = (the_bytes[0] + the_bytes[1] + the_bytes[2] + the_bytes[3]) & 0xFF
	if the_bytes[4] != checksum:
		print "NA"
		return False

	return the_bytes[0], the_bytes[2]

def detect_movement():
    
    while True:
       i=GPIO.input(pirInput)
       if i==0:                 #When output from motion sensor is LOW
             print "No intruders",i
             time.sleep(0.1)
       elif i==1:               #When output from motion sensor is HIGH
             print "Intruder detected",i
             enviar_foto()
             time.sleep(1)
#def Led(x):
#    if x == 0:
#	GPIO.output(Rpin, 1)
#	GPIO.output(Gpin, 0)
#    if x == 1:
#	GPIO.output(Rpin, 0)
#	GPIO.output(Gpin, 1)

def Print(x):
	if x == 0:
            #if ActivarAlarma == 0:
		print '    ***********************'
		print '    *   Button Pressed!   *'
		print '    ***********************'
		LCD1602.clear()
                LCD1602.write(0, 0, ' # RaspiAlert #')
                LCD1602.write(1, 1, 'Alarma activada')
                time.sleep(3)
                LCD1602.write(1, 1, 'Tiene 30s...   ')
                time.sleep(30)
                LCD1602.clear()
                detect_movement()
		
def detect(chn):
	#Led(GPIO.input(BtnPin))
	Print(GPIO.input(BtnPin))
	
#def loop():
#	while True:
#		pass

def destroy():
	#GPIO.output(Gpin, GPIO.HIGH)       # Green led off
	#GPIO.output(Rpin, GPIO.HIGH)       # Red led off
	GPIO.cleanup()                     # Release resource
	LCD1602.clear()

def main():
	print "Bienvenido al sistema RaspiAlert\n"
	LCD1602.clear()
	while True:
		result = read_dht11_dat()
		if result:
			humidity, temperature = result
			LCD1602.write(0, 0, ' # RaspiAlert #')
                        LCD1602.write(1, 1, 'H= %s%% T= %s C' % (humidity, temperature))
			print "humidity: %s %%, Temperature: %s C`" % (humidity, temperature)
			time.sleep(5)

             
if __name__ == '__main__':
    
    bot = telebot.TeleBot(TOKEN)
    setup()
    try:
	main()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
	destroy()
    


