#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Autores: Fco Javier del Castillo y Carlos Suárez

import RPi.GPIO as GPIO
import telebot
from telebot import types
import time
import os

# Ponemos nuestro Token generado con el @BotFather
TOKEN = "372274168:AAGZUERMxg4yh-WSheggBdhxbVLhubntyTo"

pirInput = 40

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
    GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
    GPIO.setwarnings(False)
    GPIO.setup(pirInput, GPIO.IN, GPIO.PUD_DOWN)         #Read output GPIO 21 from PIR motion sensor

def detect_movement():
    
    while True:
       i=GPIO.input(pirInput)
       if i==0:                 #When output from motion sensor is LOW
             print "No hay presencia",i
             time.sleep(0.1)
       elif i==1:               #When output from motion sensor is HIGH
             print "Presencia detectada!",i
             enviar_foto()
             time.sleep(1)

def destroy():

	GPIO.cleanup()                     # Release resource

             
if __name__ == '__main__':
    print "Activado modulo alarma\n"
    bot = telebot.TeleBot(TOKEN)
    setup()
    try:
	detect_movement()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
	destroy()
    


