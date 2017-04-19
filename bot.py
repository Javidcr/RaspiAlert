#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Autores: Fco Javier del Castillo y Carlos Suárez

import telebot
from telebot import types
import time
import os

TOKEN = "372274168:AAGZUERMxg4yh-WSheggBdhxbVLhubntyTo"  # SUSTITUIR

userStep = {}
knownUsers = []

commands = {
              'start': 'Arranca el bot',
              'ayuda': 'Comandos disponibles',
              'exe': 'Ejecuta un comando'
}

menu = types.ReplyKeyboardMarkup()
menu.add("Menu", "Camara")

cam_menu = types.ReplyKeyboardMarkup()
cam_menu.add("Foto", "Timelapse")
cam_menu.add("Atras")

info_menu = types.ReplyKeyboardMarkup()
info_menu.add("TEMP_Sistema", "Activar")
info_menu.add("TEMP_Habitacion", "Desactivar")
info_menu.add("Atras")


# COLOR TEXTO
class color:
    RED = '\033[91m'
    BLUE = '\033[94m'
    GREEN = '\033[32m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# USER STEP
def get_user_step(uid):
    if uid in userStep:
        return userStep[uid]
    else:
        knownUsers.append(uid)
        userStep[uid] = 0
        print(color.RED + " [¡] ¡¡NUEVO USUARIO!!" + color.ENDC)


# LISTENER
def listener(messages):
    for m in messages:
        if m.content_type == 'text':
            print("[" + str(m.chat.id) + "] " + str(m.chat.first_name) + ": " + m.text)

bot = telebot.TeleBot(TOKEN)
bot.set_update_listener(listener)


# START
@bot.message_handler(commands=['start'])
def command_start(m):
    cid = m.chat.id
    userStep[cid] = 0
    bot.send_message(cid, "Usuario conectado: " + str(m.chat.first_name))


# AYUDA
@bot.message_handler(commands=['ayuda'])
def command_help(m):
    cid = m.chat.id
    help_text = "Grabar sesion: TermRecord -o /tmp/botlog.html\n"
    help_text += "Comandos disponibles: \n"
    for key in commands:
        help_text += "/" + key + ": "
        help_text += commands[key] + "\n"
    bot.send_message(cid, help_text)


# EXEC COMANDO
@bot.message_handler(commands=['exe'])
def command_exec(m):
    cid = m.chat.id
    if cid == 331109269:  # SUSTITUIR
        bot.send_message(cid, "Ejecutando: " + m.text[len("/exe"):])
        bot.send_chat_action(cid, 'typing')
        time.sleep(2)
        f = os.popen(m.text[len("/exe"):])
        result = f.read()
        bot.send_message(cid, "Resultado: " + result)
    else:
        bot.send_message(cid, " ¡¡PERMISO DENEGADO!!")
        print(color.RED + " ¡¡PERMISO DENEGADO!! " + color.ENDC)


# MENU PRINCIPAL
@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 0)
def main_menu(m):
    cid = m.chat.id
    text = m.text
    if text == "Menu":  # RPINFO
        bot.send_message(cid, "Acciones disponibles:", reply_markup=info_menu)
        userStep[cid] = 1
    elif text == "Camara":  # CAMARA
        bot.send_message(cid, "Opciones de la camara:", reply_markup=cam_menu)
        userStep[cid] = 2
    elif text == "Atras":  # ATRAS
        userStep[cid] = 0
        bot.send_message(cid, "Menu Principal:", reply_markup=menu)
    else:
        command_text(m)


# MENU INFO
@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 1)
def info_opt(m):
        cid = m.chat.id
        txt = m.text
        if txt == "TEMP_Sistema":  # TEMP
            bot.send_message(cid, "[+] Leyendo datos...")
            print(color.BLUE + "[+] Leyendo datos..." + color.ENDC)
            # cpu temp
            tempFile = open( "/sys/class/thermal/thermal_zone0/temp" )
            cpu_temp = tempFile.read()
            tempFile.close()
            cpu_temp = round(float(cpu_temp)/1000)
            bot.send_message(cid, "  [i]   CPU: %s" % cpu_temp)
            print(color.GREEN + " [i] CPU: %s" % cpu_temp + color.ENDC)
            # gpu temp
            gpu_temp = os.popen('/opt/vc/bin/vcgencmd measure_temp').read().split("=")[1][:-3]
            bot.send_message(cid, "  [i]   GPU: %s" % gpu_temp)
            print(color.GREEN + " [i] GPU: %s" % gpu_temp + color.ENDC)
        elif txt == "Activar":  # Activar la alarma
            if cid == 331109269:  # SUSTITUIR
                bot.send_message(cid, "[+] Activando alarma...")
                print(color.BLUE + "[+] Activando alarma..." + color.ENDC)
                bot.send_message(cid, "  [i]   Activada!, tiene 30 seg para abandonar la habitación...")
                time.sleep(30)
                os.system('./start.sh')
            else:
                bot.send_message(cid, " ¡¡PERMISO DENEGADO!!")
                print(color.RED + " ¡¡PERMISO DENEGADO!! " + color.ENDC)
            
            
        elif txt == "TEMP_Habitacion":  # Temperatura del sensor
            if cid == 331109269:  # SUSTITUIR
                bot.send_message(cid, "[+] Leyendo datos...")
                print(color.BLUE + "[+] Leyendo datos..." + color.ENDC)
                lectura = open('temp','r')
                bot.send_message(cid,"[i] %s" % lectura.read())
                print ("  [i]   %s " % lectura.read())
                lectura.close()
            else:
                bot.send_message(cid, " ¡¡PERMISO DENEGADO!!")
                print(color.RED + " ¡¡PERMISO DENEGADO!! " + color.ENDC)
            
        elif txt == "Desactivar":  # Desactivar la alarma
            if cid == 331109269:  # SUSTITUIR
                bot.send_message(cid, "[+] Desactivando alarma...")
                print(color.BLUE + "[+] Desactivando alarma..." + color.ENDC)
                os.system('./stop.sh')
                bot.send_message(cid, "  [i]   Desactivada!")
            else:
                bot.send_message(cid, " ¡¡PERMISO DENEGADO!!")
                print(color.RED + " ¡¡PERMISO DENEGADO!! " + color.ENDC)
            
        elif txt == "Atras":  # ATRAS
            userStep[cid] = 0
            bot.send_message(cid, "Menu Principal:", reply_markup=menu)
        else:
            command_text(m)


# MENU CAMARA
@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 2)
def cam_opt(m):
        cid = m.chat.id
        text = m.text
        if cid == 331109269:  # SUSTITUIR
            if text == "Foto":  # FOTO
                bot.send_message(cid, "Tomando foto ...")
                bot.send_chat_action(cid, 'upload_photo')
                foto = "/home/pi/webcam/" + (time.strftime("%H%M%S-%d%m%y")) + ".jpeg"
                os.system('fswebcam -r 1280x720  %s' % foto)
                bot.send_photo(cid, open(foto, 'rb'))
                print(color.BLUE + " [i] Foto enviada!!" + color.ENDC)
            elif text == "Timelapse":  # TIMELAPSE
                bot.send_message(cid, "Nº Fotos?: ")
                bot.register_next_step_handler(m, timelapse)
            elif text == "Atras":  # ATRAS
                userStep[cid] = 0
                bot.send_message(cid, "Menu Principal:", reply_markup=menu)
            else:
                command_text(m)
        else:
            bot.send_message(cid, " ¡¡PERMISO DENEGADO!!")
            print(color.RED + " ¡¡PERMISO DENEGADO!! " + color.ENDC)


# TIMELAPSE
def timelapse(m):
    cid = m.chat.id
    start = 0
    end = m.text
    print(color.BLUE + "Nº FOTOS: " + str(end) + color.ENDC)
    if end.isdigit():
        bot.send_message(cid, "Comienza la captura de fotos...")
        print(color.BLUE + "[+] Comienza la captura de fotos..." + color.ENDC)
        while start < int(end):
            print(color.BLUE + " [i] Capturando imagen %i" % start + color.ENDC)
            bot.send_chat_action(cid, 'typing')
            os.system("fswebcam -i 0 -d /dev/video0 -r 640x480 -q --no-banner /tmp/%d%m%y_%H%M%S.jpg")
            start = start + 1
            time.sleep(10)
        print(color.BLUE + "[-] Proceso TIMELAPSE finalizado!!" + color.ENDC)
        bot.send_message(cid, "Proceso TIMELAPSE finalizado!!")

        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('SI', 'NO')
        msg = bot.reply_to(m, "Enviar fotos?: ", reply_markup=markup)
        bot.register_next_step_handler(msg, tarFotos)
    else:
        bot.send_message(cid, "Introduce numero de fotos")
        bot.register_next_step_handler(m, timelapse)
        return


# TAR FOTOS
def tarFotos(m):
    cid = m.chat.id
    msg = m.text
    if msg == "SI":
        bot.send_message(cid, "Comprimiendo fotos...")
        print(color.BLUE + "[+] Comprimiendo fotos..." + color.ENDC)
        bot.send_chat_action(cid, 'typing')
        os.system("tar -cvf /tmp/timelapse.zip /tmp/*.jpg")
        bot.send_message(cid, "Fotos comprimidas. Enviando...")
        bot.send_chat_action(cid, 'upload_document')
        tar = open('/tmp/timelapse.zip', 'rb')
        bot.send_document(cid, tar)
        print(color.BLUE + " [+] Fotos Enviadas!!" + color.ENDC)
        userStep[cid] = 0
        bot.send_message(cid, "Menu Principal:", reply_markup=menu)
    else:
        userStep[cid] = 0
        bot.send_message(cid, "Menu Principal:", reply_markup=menu)


# FILTRAR MENSAJES
@bot.message_handler(func=lambda message: True, content_types=['text'])
def command_text(m):
    cid = m.chat.id
    if (m.text.lower() in ['hola', 'hi', 'buenas', 'buenos dias']):
        bot.send_message(cid, 'Muy buenas, ' + str(m.from_user.first_name) + '. Me alegra verte de nuevo.', parse_mode="Markdown")
    elif (m.text.lower() in ['adios', 'aios', 'adeu', 'ciao']):
        bot.send_message(cid, 'Hasta luego, ' + str(m.from_user.first_name) + '. Te echaré de menos.', parse_mode="Markdown")


print 'Corriendo...'
bot.polling(none_stop=True)
