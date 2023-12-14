import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

def wiekszeodzera(number):
    for n in number:
        if len(number) > 0:
            return number

def WezCene(url):
    r = requests.get(url)
    content = r.content
    soup = BeautifulSoup(content, 'lxml')
    properties = soup.find_all('p', class_="css-10b0gli er34gjf0")
    for property in properties:
        prices = property.text[0:9]
        numbers = [int(i) for i in prices.split() if i.isdigit()]
        numbers_str = ''.join(map(str, numbers))
        wynik = wiekszeodzera(numbers_str)
        if wynik is not None:
            lista_cen.append(wynik)

current_date = datetime.now().strftime("%Y-%m-%d")
file_name = f"data/warszawa/output_warszawa_{current_date}.xlsx"
url = 'https://www.olx.pl/nieruchomosci/mieszkania/sprzedaz/warszawa/?page='

lista_nazw = []
lista_cen = []
lista_lokalizacji = []
lista_powierzchni = []
lista_miast = []
lista_dzielnic =[]

for i in range(1,26):
    next_page = i
    strona = (url + str(next_page))
    current_page = strona

    try:
        r = requests.get(current_page, allow_redirects=False, timeout=10)
    except requests.exceptions.Timeout as err:
        print(err)
    r = requests.get(current_page)
    content = r.content
    soup = BeautifulSoup(content, 'lxml')

    powierzchnia = soup.find_all('span', class_='css-643j0o')

    for nazwa in soup.find_all('h6', class_="css-16v5mdi er34gjf0"):
        nazwa = nazwa.text
        lista_nazw.append(nazwa)

    for cena in soup.find_all('p', class_="css-10b0gli er34gjf0"):
        cena = cena.text
        numbers = [str(i) for i in cena.split() if i.isdigit()]
        numbers_str = ''.join(map(str, numbers))
        numbers_str = float(numbers_str)
        if numbers_str is not None:
            lista_cen.append(numbers_str)

    for powierzchnia in soup.find_all('span', class_='css-643j0o'):
        powierzchnia = powierzchnia.text[:3]
        powierzchnia = powierzchnia.replace(',','.')
        powierzchnia = powierzchnia.replace(' ', '')
        powierzchnia = float(powierzchnia)
        if powierzchnia is not None:
            lista_powierzchni.append(powierzchnia)

    for lokalizacja in soup.find_all('p', class_='css-veheph er34gjf0'):
        lokalizacja = lokalizacja.text
        lokalizacja = lokalizacja.partition(" - ")[0]
        miasto = lokalizacja.partition(', ')[0]
        dzielica = lokalizacja.partition(', ')[2]

        #lista_lokalizacji.append(lokalizacja)
        lista_miast.append(miasto)
        lista_dzielnic.append(dzielica)

data_tuple = list(zip(lista_nazw, lista_cen, lista_powierzchni, lista_miast, lista_dzielnic))
df = pd.DataFrame(data_tuple, columns=['Nazwa','Cena','Powierzchnia', 'Miasto', 'Dzielnica'])
df['Cena za m2'] = df['Cena']/df['Powierzchnia']
df2 = df['Cena za m2'].describe(percentiles=[0.05, 0.25, 0.75, 0.95])
print(df2)
df3 = df.loc[df['Dzielnica'] == 'Mokotów']
df4 = df3['Cena za m2'].describe(percentiles=[0.05, 0.25, 0.75, 0.95])
print(df4)

with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
    df.to_excel(writer,sheet_name='Sheet_1', index=False)
    df2.to_excel(writer, sheet_name='Sheet_1', startcol=10, startrow=2, header=True, index=True)
    df4.to_excel(writer, sheet_name='Sheet_1', startcol=10, startrow=15, header=True, index=True)