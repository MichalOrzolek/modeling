import requests
import pandas as pd
from bs4 import BeautifulSoup
from unidecode import unidecode
import re
import time

#functions
#function that inserts delimiter between the name of the institutions in case there is more than one
def insert_delimiter(text):
    result = []
    in_parentheses = False
    for i in range(len(text) - 1):
        result.append(text[i])
        if text[i] == '(':
            in_parentheses = True
        elif text[i] == ')':
            in_parentheses = False
        elif not in_parentheses and text[i].islower() and text[i + 1].isupper():
            result.append('; ')
    result.append(text[-1])
    return ''.join(result)

#iterate over an url from the generated data frame and assign numerical values
def iterate_over_url(url):
    def iteracja_tekst(div, _class_, id, src, href, lista_output):
        for element in soup.find_all(div, class_=_class_, id=id, src=src, href=href):
            element = element.text
            element = element.strip()
            lista_output.append(element)

    def iteracja(div, _class_, id, src, href, lista_output):
        for element in soup.find_all(div, class_=_class_, id=id, src=src, href=href):
            element = element.text
            element = element.strip()
            element = int(element)
            lista_output.append(element)

    error_value =[('H index', 'NaN'), ('i10 index', 'NaN'), ('Citations', 'NaN'), ('Lata aktywnosci', 'NaN'), ('Liczba autocytowan', 'NaN')]
    sleeptime = 2
    try:
        r = requests.get(url)
        r.raise_for_status()
        content = r.content
        soup = BeautifulSoup(content, 'lxml')

        liczby = []
        tekst = []

        iteracja('p', 'indData', None, None, None, liczby)
        iteracja_tekst('p', 'indTitle', None, None, None, tekst)

        lata_aktywnosci_tag = soup.find('img', src='/img/flecha_azul.gif')
        lata_aktywnosci = lata_aktywnosci_tag.next_sibling.strip()
        match = re.search(r'\b\d+\b', lata_aktywnosci)
        lata_aktywnosci = int(match.group())
        tekst.append('Lata aktywnosci')
        liczby.append(lata_aktywnosci)

        autocytowania_tag = soup.find('a', href='#recent')
        autocytowania = autocytowania_tag.next_sibling.strip()
        match = re.search(r'\b\d+\b', autocytowania)
        autocytowania = int(match.group())
        tekst.append('Liczba autocytowan')
        liczby.append(autocytowania)

        merged_list = list(zip(tekst, liczby))
        return merged_list
    
    except requests.exceptions.HTTPError as errh:
        print ("HTTP Error:", errh)
        time.sleep(sleeptime)
        return error_value
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:", errc)
        time.sleep(sleeptime)
        return error_value
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:", errt)
        time.sleep(sleeptime)
        return error_value
    except requests.exceptions.RequestException as err:
        print ("Something went wrong:", err)
        time.sleep(sleeptime)
        return error_value
    except AttributeError as attr_err:
        print ("AttributeError:", attr_err)
        time.sleep(sleeptime)
        return error_value

#input:
    #List of countries of choice to iterate through and download data
    #EU countries:
    #modified name Czech Republic into Czech
eu_countries = ["Austria","Belgium","Bulgaria","Croatia","Cyprus","Czech","Denmark", "Estonia","Finland","France","Germany","Greece","Hungary","Ireland","Italy","Latvia","Lithuania",
"Luxembourg","Malta","Netherlands","Poland","Portugal","Romania","Slovakia","Slovenia","Spain",
"Sweden"]

#country names to lowercase
eu_countries_lower = [x.lower() for x in eu_countries]
print(eu_countries_lower)

for country in eu_countries_lower:
    url = "https://ideas.repec.org/top/top." + country + ".html"
    
    #lists to fill in, reset after each country iteration
    name_list = []
    code_list = []
    institute_list = []
    name_link_list = []
    #________________________________________________________________________________________________#
    r = requests.get(url)
    content = r.content
    soup = BeautifulSoup(content, 'lxml')

    #access the top 25% authors from last 10 years table for current country
    target_table = soup.find('div', class_='tab-pane fade', id='authors10')
    
    print(url)
    print(country)
    #find name tag
    name_tag = target_table.find_all('td')
    #generate name list:
    for td in name_tag:
        a_tag = td.find('a')
        if a_tag:
            name = unidecode(a_tag.text)
            name_list.append(name)
        else:
            None
    #filter name list in order to exclude None
    name_list_filtered = list(filter(None, name_list))

    #generate university list:
    for td in name_tag:
        p_tag = td.find('p')
        if p_tag:
            affiliation = unidecode(p_tag.text)
            if affiliation:
                affiliation = insert_delimiter(affiliation)
                institute_list.append(affiliation)
            else:
                institute_list.append('None')
        else:
            None
    #no None filter for affiliation - some are not affiliated

    #codes list
    if target_table:
        code_list = [a['name'] for a in target_table.find_all('a', {'name': True})]
    else:
        None

    data_tuple = list(zip(name_list_filtered, code_list, institute_list))
    df = pd.DataFrame(data_tuple, columns=['Name and surname','Code','Affiliation']) #można dodać miasto poprzez wzięcie ostatniego słowa z pierwszej instytucji

    #stworzenie indywidualnego linku do citec (można dodać do data frame)
    for i in range (len(code_list)):
        name= code_list[i]
        #logic of creating a html citec link from a code name: first letter/second letter/code.html
        #ie. code = abc2137 then html link  = a/b/abc2137.html
        a = name[0]
        b = name[1]
        citec_link = ('https://citec.repec.org/' + a + '/' + b + '/' + name + '.html')
        name_link_list.append(citec_link)

    df['Citec link'] = name_link_list
    df['Country'] = country.capitalize()

    df['H index'] = ''
    df['i10 index'] = ''
    df['Citations'] = ''
    df['Lata aktywnosci'] = ''
    df['Liczba autocytowan'] = ''

    for index, row in df.iterrows():
        repec_data = iterate_over_url(row['Citec link'])
        print(repec_data)
        for key, value in repec_data:
            df.at[index, key] = value

    print(df)

    #save file 
    file_name = f"data/output_{country}.xlsx"
    with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
        df.to_excel(writer,sheet_name='Sheet_1', index=False)