import pandas as pd
import numpy as np


# You will need to download this code onto your machine to scrape the data with selenium
# also you will need a webdriver.  Follow instructions for your system. I use Arch BTW
from selenium import webdriver
driver=webdriver.Firefox()
driver.set_page_load_timeout(20)
driver.get('https://www.caranddriver.com/features/a42387169/lightning-lap-2023/')

car_windows = driver.find_elements('xpath','.//div[@data-embed="embed-gallery"]/div/div/div')
cars_and_prices = {i.find_element('xpath','.//img').get_attribute('alt').split('lightning lap 2023 ')[1].replace('bmw i4 m50','2022 bmw i4 m50'):i.find_elements(
    'xpath','.//p')[1].text.replace(' • ','\n').split('\n') for i in car_windows}
car_times = [i.text.lower() for i in driver.find_elements('xpath','.//h2/a/../../h2')][1:-6]
car_times = dict([car_times[i:i+2] for i in range(0,32,2)])
t= dict(zip(sorted(car_times),sorted(cars_and_prices)))



# Make the dataframe; I like comprehension for comprehenison in all_comprehensions.
df = pd.DataFrame({i:dict([(lambda x: x.split(': ') if ':' in x else x.split()[::-1])(k.replace(',','').replace('$','')) for k in cars_and_prices[t[i]]+[j]])
 for i,j in car_times.items()}).T
for col in df.columns[:5]: df[col] = df[col].astype(float if '/' in col else int)
df = df.sort_values('Base Price') # sort
df['lap time'] = df['lap time'].map(lambda i:int(i.split(':')[0])*60+float(i.split(':')[1]) )  # parses the time into seconds
df['speed'] = 3600/df['lap time']*4.1 #4.1 mile track, 3600 s/hour
df['speed'] = df['speed'].round(2) # make it pretty
# df=df.insert(0,'short name',[' '.join(i.split(' ')[2:]) for i in df.index])

# price data
df.insert(2,'Alex Adj',pd.Series({'2022 subaru wrx': 0,
 '2022 hyundai elantra n': 0,
 '2022 hyundai kona n': 0,
 '2022 volkswagen golf gti': 0,
 '2023 honda civic type r': 25000,
 '2023 toyota gr corolla morizo edition': 18000,
 '2022 bmw m240i xdrive': 0,
 '2023 toyota gr supra 3.0 manual': 25000,
 '2022 audi rs3': 0,
 '2022 bmw i4 m50': 0,
 '2023 cadillac ct4-v blackwing': 15000,
 '2023 chevrolet corvette z06': 80000,
 '2023 bmw m4 csl': 50000,
 '2023 porsche 718 cayman gt4 rs': 60000,
 '2022 mercedes-amg sl63': 0,
 '2023 lamborghini huracán tecnica': 100000}))
df.insert(3,'Final Price',df['As-Tested Price']+df['Alex Adj'])

# calculations
df['$/mph']=df['Final Price']/df['speed']
df['log($)/mph']=(lambda x:((x-np.min(x))/(np.max(x)-np.min(x))).round(3))(np.log(df['As-Tested Price'])/df['speed'])
df['value champs'] = df[['log($)/mph']].sort_values('log($)/mph')['log($)/mph'].argsort()+1

# plot the data
df.plot('Final Price','$/mph')
df.plot('Final Price','log($)/mph')

# to sort it out (does not save sorting changes)

df.sort_values('log($)/mph')['log($)/mph']

# to csv

df.to_csv('cars_value_prices.csv')

