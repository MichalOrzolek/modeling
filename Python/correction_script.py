import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
import time

#second script in order to 
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
        r.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        content = r.content
        soup = BeautifulSoup(content, 'lxml')

        numbers = []
        text = []

        iteracja('p', 'indData', None, None, None, numbers)
        iteracja_tekst('p', 'indTitle', None, None, None, text)

        years_active_tag = soup.find('img', src='/img/flecha_azul.gif')
        years_active = years_active_tag.next_sibling.strip()
        match = re.search(r'\b\d+\b', years_active)
        years_active = int(match.group())
        text.append('Lata aktywnosci')
        numbers.append(years_active)

        autocitations_tag = soup.find('a', href='#recent')
        autocitations = autocitations_tag.next_sibling.strip()
        match = re.search(r'\b\d+\b', autocitations)
        autocitations = int(match.group())
        text.append('Liczba autocytowan')
        numbers.append(autocitations)

        merged_list = list(zip(text, numbers))
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

def merge_function(lowercase_country_list):
    for element in lowercase_country_list:
        country = element
        file_path = f'data/output_{country}.xlsx'
        print('Current country: ', country)
        print('Previous country: ', previous_country)
        if previous_country:
            previous_file_path = f'data/output_{previous_country}.xlsx'
            df_current = pd.read_excel(file_path)
            df_previous = pd.read_excel(previous_file_path)
            frames = [df_previous, df_current]
            result = pd.concat(frames)
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                result.to_excel(writer,sheet_name='Sheet_1', index=False)
        else:
            None
        previous_country = country


    #___________________CODE______________________#


eu_countries = ["Austria","Belgium","Bulgaria","Croatia","Cyprus","Czech","Denmark", "Estonia","Finland","France","Germany","Greece","Hungary","Ireland","Italy","Latvia","Lithuania",
"Luxembourg","Malta","Netherlands","Poland","Portugal","Romania","Slovakia","Slovenia","Spain",
"Sweden"]

#country names to lowercase
eu_countries_lower = [x.lower() for x in eu_countries]

for country in eu_countries_lower:
    number_of_NaN = 0
    total = 0
    file_path = f'data/output_{country}.xlsx'
    print(country)
    df = pd.read_excel(file_path)
    
    for index, row in df.iterrows():
        total += 1
        # Check if the 'h index' value is NaN
        if pd.isna(row['H index']):
            # If NaN, call the iterate_over_url function on the 'Citec link'
            number_of_NaN += 1
            repec_data = iterate_over_url(row['Citec link'])
            print(repec_data)
            for key, value in repec_data:
                df.at[index, key] = value
    print('Missing rows: ', number_of_NaN)
    file_name = f'data/output_{country}.xlsx'
    with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
            df.to_excel(writer,sheet_name='Sheet_1', index=False)

#merge all the corrected files into one table for all countries
merge_function(eu_countries_lower)
