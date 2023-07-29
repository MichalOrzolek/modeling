import pandas as pd
import numpy as np
import csv
start_date = '2023-06-01'
end_date = '2023-12-31'

date_index = pd.date_range(start = start_date, end = end_date, freq = 'D')
sales_data = pd.DataFrame(index=date_index, columns=['sales'])

for date in date_index:
    if date.weekday() < 5:
        mean = 100
        std_dev = 10
    else:
        mean = 130
        std_dev = 30

    sales = np.random.normal(mean, std_dev)
    sales_data.loc[date] = round(sales)

print(sales_data)

sales_data.to_csv('C:/Users/micha/OneDrive/Pulpit/Wszystko/matlab/data_arima_sales.csv', header=False)
