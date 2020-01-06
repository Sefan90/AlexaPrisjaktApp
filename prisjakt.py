from flask import Flask
from flask_ask import Ask, statement, question, session
import bs4 as bs
import urllib.request
import requests
import json
from lxml import html
from random import randint

app = Flask(__name__)
ask = Ask(app, "/")
listofresults = None
result = 0
item = 0
atquestion = 0


def searchResults(slotProduct):
	try:
	    url1 = "https://www.prisjakt.nu/ajax/server.php?class=Search_Supersearch&method=search&skip_login=1&modes=product,raw_sorted,raw&limit=12&q="+slotProduct.replace(" ", "")
	    req1 = urllib.request.Request(url1, headers={'User-Agent': 'Mozilla/5.0'})
	    url_read1 = urllib.request.urlopen(req1).read()
	    soup1 = bs.BeautifulSoup(url_read1,'lxml')
	    product =  json.loads(str(soup1.find("p").get_text()))
	except:
		product = None
	return product

def searchItems(listofresults, result):
	storeprice = []
	try:
	    url2 = str(listofresults["message"]["product"]["items"][result]["url"])
	    req2 = urllib.request.Request(url2, headers={'User-Agent': 'Mozilla/5.0'})
	    url_read2 = urllib.request.urlopen(req2).read()
	    soup2 = bs.BeautifulSoup(url_read2,'lxml')
	    #productprice = soup2.find("span", class_="price").get_text()
	    productprice = soup2.find("table", id="prislista")#.get_text()
	    storeprice.append(productprice.find_all("span", class_="store-name-span"))
	    storeprice.append(productprice.find_all("a", class_="js-ga-event-track text_svag strong price"))
	except Exception as e:
		storeprice.append(0)
		storeprice.append(0)
		print (e)
	return storeprice

@ask.launch
def launched():
    return question('What product do you want to serch for?')

@ask.intent('intentProduct', mapping={'slotProduct': 'slotProduct'})
def intentProduct(slotProduct):
	listofresults = searchResults(slotProduct)
	try:
		returnquestion = 'Searched for {} and found {} items. Did you mean {}?'.format(slotProduct,len(listofresults),listofresults["message"]["product"]["items"][result]["name"])
		atquestion = 1
	except:
		returnquestion = 'I did not understand you'
		atquestion = 0		
	return question(returnquestion)

@ask.intent('intentProductStore', mapping={'slotProduct': 'slotProduct', 'slotStores': 'slotStores'})
def intentProductStore(slotProduct,slotStores):
	listofresults = searchResults(slotProduct)
	listofitems = searchItems(listofresults, result)
	print(listofitems)
	findStore = -1
	for i in range(0,len(listofitems)):
		if listofitems[i][0] == slotStores:
			findStore = i
			break
	try:
		returnquestion = 'Price for {} is {} swedish kronor on {}'.format(listofresults["message"]["product"]["items"][result]["name"],listofitems[0][1],listofitems[0][0])
		atquestion = 2
	except:
		returnquestion = 'I did not understand you'
		atquestion = 0
	return statement(returnquestion)

@ask.intent('AMAZON.YesIntent')
def intentYes():
	if atquestion == 0:
		return question('What product do you want to serch for?')
	elif atquestion == 1:
		listofitems = searchItems(listofresults, result)
		print(listofitems)
		try:
			returnquestion = 'Price for {} is {} swedish kronor on {}'.format(listofresults["message"]["product"]["items"][result]["name"],listofitems[0][1],listofitems[0][0])
			atquestion = 2
		except:
			returnquestion = 'I did not understand you'
			atquestion = 0
		return statement(returnquestion)

@ask.intent('AMAZON.NoIntent')
def intentNo():
	if atquestion == 0:
		return question('What product do you want to serch for?')
	elif atquestion == 1:
		result = result + 1
		try:
			returnquestion = 'Searched for {} and found {} items. Did you mean {}?'.format(slotProduct,len(listofresults),listofresults["message"]["product"]["items"][result]["name"])
		except:
			returnquestion = 'No more products found'		
		return question(returnquestion)

listofresults = searchResults('nintendo switch')
listofitems = searchItems(listofresults,0)
print(listofresults["message"]["product"]["items"][0]["name"])
print(listofresults["message"]["product"]["items"][0]["url"])
print(listofitems[0][0].get_text())
print(listofitems[1][0].get_text())
print(listofitems[0][1].get_text())
print(listofitems[1][1].get_text())
app.run(debug=True)

#1 Frågar vad du vill köpa
#2 Får ett svar
#3 Söker upp det och ger de 3 översta alternativen
#4 Får ett svar vilket den ska välja
#5 Svarar med priet på varan och frågar om du vill veta fler priser
#6 Får ett ja
#7 Läser upp priset på för de 3 billigaste butikerna