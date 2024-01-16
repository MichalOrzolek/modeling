import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')


def gini_index(x):
    #compute Gini coefficient of array of values
    diffsum = 0
    for i, xi in enumerate(x[:-1], 1):
        diffsum += np.sum(np.abs(xi - x[i:]))
    return diffsum / (len(x)**2 * np.mean(x))


#data collected from Eurostat, spending according to 2012 year
tertiary_spending = [
    ('Austria', 16235, 8956000),
    ('Belgium', 16476, 11590000),
    ('Bulgaria', 3883, 6878000),
    ('Croatia', 4614, 3899000),
    ('Czech', 7648, 10510000),
    ('Denmark', 20551, 5857000),
    ('Finland', 16117, 5541000),
    ('France', 13306, 67750000),
    ('Germany', 15051, 83200000),
    ('Greece', 2361, 10640000),
    ('Hungary', 4909, 9710000),
    ('Italy', 8202, 59110000),
    ('Luxembourg', 40990, 640064),
    ('Netherlands', 16610, 17530000),
    ('Poland', 5378, 37750000),
    ('Portugal', 9371, 10330000),
    ('Romania', 3297, 19120000),
    ('Slovakia', 7648, 5447000),
    ('Spain', 8793, 47420000),
    ('Sweden', 21543, 10420000)
]

#tertiary spending on R&D as % of GDP - data is sorted according to regression df output - Germany, France, Italy, Spain etc.
rd_educ = [0.57, 0.45, 0.33, 0.37, 0.63, 0.04, 0.59, 0.75, 0.47, 0.53, 0.44, 0.74, 0.31, 0.942, 0.21, 0.71, 0.05, 0.4, 0.25]
#government spending on R&D as % od GDP
rd_gov = [0.37, 0.25, 0.2, 0.25, 0.11, 0.13, 0.31, 0.14, 0.03, 0.07, 0.31, 0.24, 0.05, 0.094, 0.17, 0.22, 0.19, 0.25, 0.17]
rd_zipped = tuple(zip(rd_educ, rd_gov))
rd_df = pd.DataFrame(rd_zipped, columns=['rd_educ', 'rd_gov'])
print(rd_df)

df_spending = pd.DataFrame(tertiary_spending, columns = ['Country', 'Spending', 'Population'])
#print(df_spending)
file_name = f'spending.xlsx'
with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
    df_spending.to_excel(writer,sheet_name='Sheet_1', index=False)

file_path = f'output_wszyscy_naukowcy.xlsx'
df = pd.read_excel(file_path)

sum_by_country = df.groupby('Country')['Citations'].sum().reset_index()
merged_sum = pd.merge(df_spending, sum_by_country, on='Country', how='left')

merged_sum['Efficiency'] = merged_sum['Citations'] / merged_sum['Spending']

#count countries
country_counts = df['Country'].value_counts()

df_counts = df['Country'].value_counts().reset_index()
df_counts.columns = ['Country', 'Count']
print(df_counts)

#filter out countries with less than 40 positions
valid_countries = country_counts[country_counts >= 40].index
df = df[df['Country'].isin(valid_countries)]

df['Cytowania adj'] = df.apply(lambda row: row['Citations'] - row['Liczba autocytowan'], axis=1)


gini_results_citations = df.groupby('Country')['Citations'].apply(lambda x: gini_index(x)).reset_index()
gini_results_citations.columns = ['Country', 'Citations_Gini']
merged_df = pd.merge(df, gini_results_citations, on='Country', how='left')

gini_results_hindex = df.groupby('Country')['H index'].apply(lambda x: gini_index(x)).reset_index()
gini_results_hindex.columns = ['Country', 'H Gini']
merged_df = pd.merge(merged_df, gini_results_hindex, on='Country', how='left')

gini_results_i10index = df.groupby('Country')['i10 index'].apply(lambda x: gini_index(x)).reset_index()
gini_results_i10index.columns = ['Country', 'i10 Gini']
merged_df = pd.merge(merged_df, gini_results_i10index, on='Country', how='left')

#prepare regression df
regression_df = pd.merge(df_counts, gini_results_citations, on='Country', how='left')
regression_df = pd.merge(regression_df, gini_results_hindex, on='Country', how='left')
regression_df = pd.merge(regression_df, gini_results_i10index, on='Country', how='left')
regression_df = pd.merge(regression_df, df_spending, on='Country', how='left')

#multiplication because only 25% of top scientists from a given country are included
regression_df['Per mln'] = (regression_df['Count']/regression_df['Population'])*4000000 
regression_df = regression_df.dropna()
regression_df = regression_df.drop([18])

#sort and merge with R&D spending data
regression_df = pd.merge(regression_df, rd_df, how='inner', left_index=True, right_index=True)

print(regression_df)

file_name = f'regression_data.xlsx'
with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
    regression_df.to_excel(writer,sheet_name='Sheet_2', index=False)

#save results to excel file
file_name = f'filtered_gini.xlsx'
with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
    merged_df.to_excel(writer,sheet_name='Sheet_1', index=False)
    gini_results_citations.to_excel(writer,sheet_name='Sheet_2', index=False)
    gini_results_hindex.to_excel(writer,sheet_name='Sheet_3', index=False)
    gini_results_i10index.to_excel(writer,sheet_name='Sheet_4', index=False)
    regression_df.to_excel(writer, sheet_name='Sheet_5', index=False)
