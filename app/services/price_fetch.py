import requests
from bs4 import BeautifulSoup
import json

mystocks = ['AAPL', 'TWTR']  # Liste des actions à récupérer
stockdata = []

def getData(symbol):
    headers = { 
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    url = f'https://finance.yahoo.com/quote/{symbol}' 
    r = requests.get(url, headers=headers)
    
    if r.status_code != 200:
        print(f"Erreur lors de la récupération des données pour {symbol}: {r.status_code}")
        return None

    soup = BeautifulSoup(r.text, 'html.parser')

    # Trouver le conteneur pour le prix
    price_tag = soup.find('fin-streamer', {'data-field': 'regularMarketPrice'})
    change_tag = soup.find('fin-streamer', {'data-field': 'regularMarketChangePercent'})
    
    if not price_tag or not change_tag:
        print(f"Erreur : impossible de trouver les données pour {symbol}")
        return None

    stock = {
        'symbol': symbol,
        'price': price_tag.text,
        'change': change_tag.text,
    }
    return stock

# Récupérer les données pour chaque action
for item in mystocks:
    stock_info = getData(item)
    if stock_info:
        stockdata.append(stock_info)
        print('Getting:', stock_info)

# Sauvegarder les données dans un fichier JSON
with open('stockdata.json', 'w') as f:
    json.dump(stockdata, f, indent=4)

print("Données des actions sauvegardées dans stockdata.json")
