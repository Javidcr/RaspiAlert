#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Autores: Fco Javier del Castillo y Carlos Suárez

import telebot
from telebot import types
import time
import os
import RPi.GPIO as GPIO
import LCD1602

TOKEN = "372274168:AAGZUERMxg4yh-WSheggBdhxbVLhubntyTo"  # SUSTITUIR

BtnPin = 37
#Gpin   = 12
#Rpin   = 13
pirInput = 40

DHTPIN = 11

alarma = 0

#GPIO.setmode(GPIO.BCM)
GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location

MAX_UNCHANGE_COUNT = 100

STATE_INIT_PULL_DOWN = 1
STATE_INIT_PULL_UP = 2
STATE_DATA_FIRST_PULL_DOWN = 3
STATE_DATA_PULL_UP = 4
STATE_DATA_PULL_DOWN = 5

userStep = {}
knownUsers = []

commands = {
              'start': 'Arranca el bot',
              'ayuda': 'Comandos disponibles',
              'exe': 'Ejecuta un comando'
}

menu = types.ReplyKeyboardMarkup()
menu.add("RPinfo", "Camara")

cam_menu = types.ReplyKeyboardMarkup()
cam_menu.add("Foto", "Timelapse")
cam_menu.add("Atras")

info_menu = types.ReplyKeyboardMarkup()
info_menu.add("TEMP", "Activar")
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

def setup():
    GPIO.setwarnings(False)
    GPIO.setup(pirInput, GPIO.IN)         #Read output GPIO 21 from PIR motion sensor

    #Button and LED setup
    #GPIO.setup(Gpin, GPIO.OUT)     # Set Green Led Pin mode to output
    #GPIO.setup(Rpin, GPIO.OUT)     # Set Red Led Pin mode to output
    #GPIO.setup(BtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)    # Set BtnPin's mode is input, and pull up to high level(3.3V)
    #GPIO.add_event_detect(BtnPin, GPIO.BOTH, callback=detect, bouncetime=200)

    #setup display
    LCD1602.init(0x27, 1)	# init(slave address, background light)

    

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
    
    print '    ***********************'
    print '    *   Alarma activada!  *'
    print '    ***********************'
    LCD1602.clear()
    LCD1602.write(0, 0, ' # RaspiAlert #')
    LCD1602.write(1, 1, 'Alarma activada')
    time.sleep(3)
    LCD1602.write(1, 1, 'Tiene 30s...   ')
    time.sleep(30)
    LCD1602.clear()
    
    while alarma == 1:
       i=GPIO.input(pirInput)
       if i==0:                 #When output from motion sensor is LOW
             print "No intruders",i
             time.sleep(0.1)
             
       elif i==1:               #When output from motion sensor is HIGH
             print "Intruder detected",i
             enviar_foto()
             time.sleep(1)
             
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
            bot.send_message(cid, "[+] Leyendo datos...")
            print(color.BLUE + "[+] Leyendo datos..." + color.ENDC)

            result = read_dht11_dat()
	    if result:
                
		    humidity, temperature = result
		    
		    bot.send_message(cid,"  [i]   Humedad: %s %%, Temperatura: %s C`" % (humidity, temperature))
		    print "  [i]   humidity: %s %%, Temperature: %s C`" % (humidity, temperature)
                    print "  [i]   Humedad: %s %%, Temperatura: %s C`" % (humidity, temperature)
            else:
                bot.send_message(cid,"  [i]   Lectura incorrecta...")
                print("  [i]   Lectura incorrecta...")

            
        elif txt == "Activar":  # Activar alarma
            bot.send_message(cid, "[+] Activando alarma...")
            print(color.BLUE + "[+] Activando alarma..." + color.ENDC)
            alarma = 1
            bot.send_message(cid, "  [i]   Activada!")
            detect_movement()
            
        elif txt == "RAM":  # RAM
            bot.send_message(cid, "[+] MEMORIA RAM")
            print(color.BLUE + "[+] MEMORIA RAM" + color.ENDC)
            bot.send_message(cid, "  [i]   Total: %s" % ramInfo()[0])
            print(color.GREEN + " [i] Total: %s" % ramInfo()[0] + color.ENDC)
            bot.send_message(cid, "  [i]   Usado: %s" % ramInfo()[1])
            print(color.GREEN + " [i] Usado: %s" % ramInfo()[1] + color.ENDC)
            bot.send_message(cid, "  [i]   Disponible: %s" % ramInfo()[2])
            print(color.GREEN + " [i] Disponible: %s" % ramInfo()[2] + color.ENDC)
            
        elif txt == "Desactivar":  # Desactivar alarma
            bot.send_message(cid, "[+] Desactivando alarma...")
            print(color.BLUE + "[+] Desactivando alarma..." + color.ENDC)
            alarma = 0
            bot.send_message(cid, "  [i]   Desactivada!")
            #detect_movement()
            
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
        bot.send_message(cid, 'Hasta luego, ' + str(m.from_user.first_name) + '. Vuelve pronto!.', parse_mode="Markdown")


def destroy():
	#GPIO.output(Gpin, GPIO.HIGH)       # Green led off
	#GPIO.output(Rpin, GPIO.HIGH)       # Red led off
	GPIO.cleanup()                     # Release resource
	LCD1602.clear()

def main():
	print "Bienvenido al sistema RaspiAlert\n"
	LCD1602.clear()
	#bot.polling(none_stop=True)
        bot.set_update_listener(listener)
        
	while True:
		result = read_dht11_dat()
		if result:
			humidity, temperature = result
			LCD1602.write(0, 0, ' # RaspiAlert #')
                        LCD1602.write(1, 1, 'H= %s%% T= %s C' % (humidity, temperature))
			print "humidity: %s %%, Temperature: %s C`" % (humidity, temperature)
			time.sleep(5)
			

if __name__ == '__main__':

    print 'Corriendo...'
    setup()
    try:
        main()
    except KeyboardInterrupt:
        destroy()

        
