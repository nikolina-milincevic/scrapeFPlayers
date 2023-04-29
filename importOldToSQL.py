import pandas as pd
import mysql.connector
from datetime import datetime
import sys

def convert_date(date_str):
    if date_str != None:
        date = datetime.strptime(date_str, '%d.%m.%Y')
        return date.strftime('%Y-%m-%d')
    else:
        return date_str
    
filename = sys.argv[1]
#'/Users/nikolinamilincevic/Downloads/CI-task/CI_data_engineers_task_data/playersData.csv'
df = pd.read_csv(filename, sep = ';', keep_default_na = False)
df.columns = ['name', 'full_name', 'date_of_birth', 'age', 'city_of_birth', 'country_of_birth', 'position', 'current_club', \
    'national_team', 'dead', 'no_data', 'player_id', 'url'] 

my_columns = ['player_id', 'url', 'name', 'full_name', 'date_of_birth', 'age', 'place_of_birth', 'city_of_birth', 'country_of_birth', \
    'position', 'current_club', 'number_of_app', 'goals', 'national_team', 'scraping_timestamp']

new_columns = []
for i in my_columns:
    if i not in df.columns:
        new_columns.append(i)
print(new_columns)

drop_columns = []
for i in df.columns:
    if i not in my_columns:
        drop_columns.append(i)
print(drop_columns)

for i in drop_columns:
    df = df.drop(i, axis = 1)
for i in new_columns:
    df[i] = None
        
for i in df.columns:
    for j in range(len(df[i])):
        if df[i][j] == '':
            df[i][j] = None
print(df.columns)

df['date_of_birth'] = df['date_of_birth'].apply(convert_date)



cnx = mysql.connector.connect(user='root', password='rootroot',
                                   host='localhost', 
                                   database='mydatabase',
                                   charset='utf8')

cursor = cnx.cursor(buffered = True)
cursor.execute('''CREATE TABLE mydatabase.players (\
    name VARCHAR(255), full_name VARCHAR(255), date_of_birth DATE, age INT, \
    city_of_birth VARCHAR(255), country_of_birth VARCHAR(255), position VARCHAR(255), \
    current_club VARCHAR(255), national_team VARCHAR(255), player_id VARCHAR(255), url VARCHAR(255), \
    place_of_birth VARCHAR(255), number_of_apps INT, goals INT, scraping_timestamp VARCHAR(255)\
    );''')

query = '''INSERT INTO mydatabase.players VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
for i, row in df.iterrows():
    values = tuple(row)
    cursor.execute(query, values)

cnx.commit()
cursor.close()
cnx.close()
