import requests
import sys
 
id = "331109269"
 
token = "372274168:AAGZUERMxg4yh-WSheggBdhxbVLhubntyTo"
 
url = "https://api.telegram.org/bot" + token + "/sendMessage"
 
files = {
'document': open('texto.txt', 'rb')
}
 
params = {
'chat_id': id
}
 
requests.post(url, params=params, files=files)
