#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
              'exec': 'Ejecuta un comando'
}

menu = types.ReplyKeyboardMarkup()
menu.add("RPinfo", "Camara")

cam_menu = types.ReplyKeyboardMarkup()
cam_menu.add("Foto", "Timelapse")
cam_menu.add("Atras")

info_menu = types.ReplyKeyboardMarkup()
info_menu.add("TEMP", "HD")
info_menu.add("RAM", "CPU")
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
    bot.send_message(cid, "Wake up " + str(m.chat.first_name) + "...")
    time.sleep(1)
    bot.send_message(cid, "Fwhibbit has you...")
    time.sleep(1)
    bot.send_message(cid, "Follow the white rabbit...\n", reply_markup=menu)


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
@bot.message_handler(commands=['exec'])
def command_exec(m):
    cid = m.chat.id
    if cid == "331109269":  # SUSTITUIR
        bot.send_message(cid, "Ejecutando: " + m.text[len("/exec"):])
        bot.send_chat_action(cid, 'typing')
        time.sleep(2)
        f = os.popen(m.text[len("/exec"):])
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
    if text == "RPinfo":  # RPINFO
        bot.send_message(cid, "Informacion disponible:", reply_markup=info_menu)
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
        if txt == "TEMP":  # TEMP
            bot.send_message(cid, "[+] TEMPERATURAS")
            print(color.BLUE + "[+] TEMPERATURAS" + color.ENDC)
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
        elif txt == "HD":  # HD
            bot.send_message(cid, "[+] DISCO DURO")
            print(color.BLUE + "[+] DISCO DURO" + color.ENDC)
            bot.send_message(cid, "  [i]   Total: %s" % diskSpace()[0])
            print(color.GREEN + " [i] Total: %s" % diskSpace()[0] + color.ENDC)
            bot.send_message(cid, "  [i]   Usado: %s" % diskSpace()[1])
            print(color.GREEN + " [i] Usado: %s" % diskSpace()[1] + color.ENDC)
            bot.send_message(cid, "  [i]   Disponible: %s" % diskSpace()[2])
            print(color.GREEN + " [i] Disponible: %s" % diskSpace()[2] + color.ENDC)
        elif txt == "RAM":  # RAM
            bot.send_message(cid, "[+] MEMORIA RAM")
            print(color.BLUE + "[+] MEMORIA RAM" + color.ENDC)
            bot.send_message(cid, "  [i]   Total: %s" % ramInfo()[0])
            print(color.GREEN + " [i] Total: %s" % ramInfo()[0] + color.ENDC)
            bot.send_message(cid, "  [i]   Usado: %s" % ramInfo()[1])
            print(color.GREEN + " [i] Usado: %s" % ramInfo()[1] + color.ENDC)
            bot.send_message(cid, "  [i]   Disponible: %s" % ramInfo()[2])
            print(color.GREEN + " [i] Disponible: %s" % ramInfo()[2] + color.ENDC)
        elif txt == "CPU":  # CPU
            bot.send_message(cid, "[+] CPU")
            print(color.BLUE + "[+] CPU" + color.ENDC)
            cpu = os.popen('mpstat | grep -A 5 "%idle" | tail -n 1 | awk -F " " \'{print 100 - $ 12}\'a').read()
            bot.send_message(cid, "  [i]   Usado: %s" % cpu)
            print(color.GREEN + " [i] Usado: %s" % cpu + color.ENDC)
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
        if "331109269" == "331109269":  # SUSTITUIR
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


# INFO HD
def diskSpace():
    p = os.popen("df -h /")
    i = 0
    while 1:
        i += 1
        line = p.readline()
        if i == 2:
            return(line.split()[1:5])


# INFO RAM
def ramInfo():
    p = os.popen('free -o -h')
    i = 0
    while 1:
        i += 1
        line = p.readline()
        if i == 2:
            return(line.split()[1:4])


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
        os.system("tar -cvf /tmp/timelapse.tar /tmp/*.jpg")
        bot.send_message(cid, "Fotos comprimidas. Enviando...")
        bot.send_chat_action(cid, 'upload_document')
        tar = open('/tmp/timelapse.tar', 'rb')
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
