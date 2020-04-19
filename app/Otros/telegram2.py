## -*- coding: utf-8 -*-
 
import telebot # Librería de la API del bot.
from telebot import types # Tipos para la API del bot.
import time # Librería para hacer que el programa que controla el bot no se acabe.
import random
import datetime
import token
import os
import commands
TOKEN = '372274168:AAGZUERMxg4yh-WSheggBdhxbVLhubntyTo' #Nuestro token del bot
 
bot = telebot.TeleBot(TOKEN) # Creamos el objeto de nuestro bot.
#############################################
#Listener
def listener(messages): # Con esto, estamos definiendo una función llamada 'listener', que recibe como parámetro un dato llamado 'messages'.
    for m in messages: # Por cada dato 'm' en el dato 'messages'
        cid = m.chat.id # Almacenaremos el ID de la conversación.
        if m.content_type == 'text':
            print "[" + str(cid) + "]: " + m.text # Y haremos que imprima algo parecido a esto -> [52033876]: /start
 
bot.set_update_listener(listener) # Así, le decimos al bot que utilice como función escuchadora nuestra función 'listener' declarada arriba.
#############################################
#Funciones
@bot.message_handler(commands=['help']) 
def command_ayuda(m): 
    cid = m.chat.id 
    bot.send_message( cid, "Comandos Disponibles: /help, /temp, /foto")
@bot.message_handler(commands=['temp'])
def command_temp(m):
	cid = m.chat.id
	#temp = os.system('sudo /opt/vc/bin/vcgencmd measure_temp')
	temp = commands.getoutput('sudo /opt/vc/bin/vcgencmd measure_temp')	
	bot.send_message(cid, temp)
@bot.message_handler(commands=['foto'])
def command_temp(m):
        cid = m.chat.id
	foto = commands.getoutput('./take_photo.sh')
        bot.send_message(cid, foto)
#############################################
#Peticiones
bot.polling(none_stop=True) # Con esto, le decimos al bot que siga funcionando incluso si encuentra algun fallo.
