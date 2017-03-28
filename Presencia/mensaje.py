#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Autores: Fco Javier del Castillo y Carlos Suárez

import telebot
from telebot import types
import time
import os

# Ponemos nuestro Token generado con el @BotFather
TOKEN = "372274168:AAGZUERMxg4yh-WSheggBdhxbVLhubntyTo"

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
    
bot = telebot.TeleBot(TOKEN)
enviar_foto()


