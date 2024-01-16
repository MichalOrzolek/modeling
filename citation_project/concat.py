import pandas as pd

eu_countries = ["Austria","Belgium","Bulgaria","Croatia","Cyprus","Czech","Denmark","Estonia","Finland","France","Germany","Greece","Hungary","Ireland","Italy","Latvia","Lithuania",
"Luxembourg","Malta","Netherlands","Poland","Portugal","Romania","Slovakia","Slovenia","Spain",
"Sweden"]

#country names to lowercase
eu_countries_lower = [x.lower() for x in eu_countries]

previous_country = None

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

merge_function(eu_countries_lower)