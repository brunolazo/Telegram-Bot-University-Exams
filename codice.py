import Costanti
import telebot 
import bs4, requests 

API_KEY=Costanti.API_KEY 
bot=telebot.TeleBot(API_KEY) 
LINK = "https://www.unistudium.unipg.it/cercacorso.php?p=1"

@bot.message_handler(commands=['start'])
def inputUtenteStart(input_text):
  bot.send_message(input_text.chat.id, "Lista di comandi:\n/start ti permetterà di visulizzare questa lista di comandi\n/cerca ti pemetterà di ricercare l'insegnamento e/o nome del docente ed ottenere i relativi risultati\n/prof ti pemetterà di ricercare il nome del docente e data la possibilità di visulizzare solo i risultati di un determinato corso di laurea nel quale il professore insegna")

def settaggio():
  if(len(messaggioInput.text)<=200):
    response = requests.post(LINK, data={'query': messaggioInput.text})  
    response.raise_for_status()  
    soup = bs4.BeautifulSoup(response.text,'html.parser') 
    return soup
  else:
    bot.send_message(messaggioInput.chat.id, "Il testo inserito non deve superare i 200 caratteri")
    return 0

@bot.message_handler(commands=['cerca'])
def inputUtenteCerca(input_text):
  sent = bot.send_message(input_text.chat.id, "Digita il nome dell'insegnamento e/o nome del docente")
  bot.register_next_step_handler(sent, cerca)  

def cerca(message):
  global messaggioInput
  global htmlRighe
  messaggioInput = message
  soup=settaggio()
  if soup!=0:
    if soup.find('table'):  
      htmlOrario = soup.find('table')
      htmlRighe = htmlOrario.find_all('tr') 
      del htmlRighe[0]  
      tastieraCerca = telebot.types.InlineKeyboardMarkup() 
      tastieraCerca.add(telebot.types.InlineKeyboardButton('mostrare', callback_data='mostrare')) 
      tastieraCerca.add(telebot.types.InlineKeyboardButton('non mostrare', callback_data='non mostrare'))
      bot.send_message(messaggioInput.chat.id,"Sono state trovate " + str(len(htmlRighe)) + " corrispondenze, mostrarle o non mostrarle?",reply_markup=tastieraCerca) 
    else:
      bot.send_message(messaggioInput.chat.id,'Non è stata trovata nessuna corrispondenza.\nInserisci nuovamente il comando /cerca ed effettua una nuova ricerca')

def mostraEsamiC():
  for htmlRiga in htmlRighe:
    htmlCaselle = htmlRiga.find_all('td') 
    testoRiga = '' 
    linkEsame = '' 
    for htmlCasella in htmlCaselle:
      if htmlCasella.find('a'): 
        htmlEsame = htmlCasella.find('a') 
        linkEsame = str(htmlEsame.get('href'))
      else: 
        testoCasella = str(htmlCasella.text)
        testoRiga += (testoCasella + '\n')
    tastieraCercaEsame = telebot.types.InlineKeyboardMarkup() 
    tastieraCercaEsame.add(telebot.types.InlineKeyboardButton(testoRiga, url=linkEsame))
    bot.send_message(messaggioInput.chat.id, testoRiga, reply_markup=tastieraCercaEsame)

@bot.message_handler(commands=['prof'])
def inputUtenteProf(input_text):
  sent = bot.send_message(input_text.chat.id, "Digita il nome del docente")
  bot.register_next_step_handler(sent, prof)  

@bot.message_handler(func=lambda message: True)
def inputNonRiconosciuto(message):
 bot.send_message(message.chat.id, "Inserire un comando valido, per maggiori informazioni riguardo ai comandi disponibili digita il comando /start")

def prof(message):
  global messaggioInput
  global htmlRighe
  global listaCorsi
  messaggioInput = message
  soup = settaggio()
  if soup != 0:
    if soup.find('table'):  
      htmlOrario = soup.find('table')
      htmlRighe = htmlOrario.find_all('tr')
      del htmlRighe[0]  
      listaCorsi = []
      mostraEsamiP()
      bot.send_message(message.chat.id, "I corsi relativi al docente ricercato sono:", reply_markup=makeTastieraProf())
    else:
      bot.send_message(message.chat.id,'Non è stata trovata nessuna corrispondenza.\nInserisci nuovamente il comando /prof ed effettua una nuova ricerca')

def mostraEsamiP(): 
  for htmlRiga in htmlRighe:
    htmlCaselle = htmlRiga.find_all('td')
    numeroColonna = 0
    for htmlCasella in htmlCaselle:
      numeroColonna += 1
      testoCasella = str(htmlCasella.text)
      if numeroColonna == 3: 
        presente = 0
        for corsoPresenteLista in listaCorsi:
          if corsoPresenteLista == testoCasella: 
            presente += 1
        if presente == 0: 
          listaCorsi.append(testoCasella)

def makeTastieraProf():
  tastieraProf = telebot.types.InlineKeyboardMarkup() 
  for corsoPresenteLista in listaCorsi:
    corsoPresenteLista = corsoPresenteLista[:64] 
    tastieraProf.add(telebot.types.InlineKeyboardButton(text=str(corsoPresenteLista), callback_data=str(corsoPresenteLista)))
  return tastieraProf

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
  if call.data == "mostrare":
    mostraEsamiC()
  elif call.data == "non mostrare":
    bot.send_message(messaggioInput.chat.id,"Inserisci nuovamente il comando /cerca e prova ad essere più specifico nella ricerca")
  else:
    for htmlRiga in htmlRighe:
      htmlCaselle = htmlRiga.find_all('td') 
      testoRiga = '' 
      linkEsame = ''
      numeroColonna = 0
      corso = '' 
      for htmlCasella in htmlCaselle:
        numeroColonna += 1
        if htmlCasella.find('a'):
          htmlEsame = htmlCasella.find('a') 
          linkEsame = str(htmlEsame.get('href')) 
        else: 
          testoCasella = str(htmlCasella.text)
          testoRiga += (testoCasella + '\n')
          if numeroColonna == 3: 
            corso = testoCasella
            corso = corso[:64] 
      if call.data == corso:
        tastieraProfEsame = telebot.types.InlineKeyboardMarkup()
        tastieraProfEsame.add(telebot.types.InlineKeyboardButton(testoRiga, url=linkEsame)) 
        bot.send_message(messaggioInput.chat.id, testoRiga, reply_markup=tastieraProfEsame) 

bot.polling() 