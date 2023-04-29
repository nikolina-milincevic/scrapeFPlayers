from bs4 import BeautifulSoup
from datetime import date
import datetime
from dateutil.relativedelta import relativedelta
import requests
import csv
import mysql.connector
import sys

# funcions that return substring of a given string with ommited chars after
# of before a specific substring occurs
def get_before_sub(substring, string):
    if string.find(substring) > -1:
        string = string[:string.find(substring)]
    return string
def get_after_sub(substring, string):
    if string.find(substring) > -1:
        string = string[(string.find(substring)+1):]
    return string

# a function that finds the row of a table of the first header after the given header 
# (the argument header_name does not need to be the complete header name; just a substring)
def find_header_after(header_name, table):
    lista = []
    for i, row in enumerate(table.find_all('tr')):
        cells = row.find_all('th', class_ = 'infobox-header')
        for cell in cells:
            lista.append(cell.text)
    for i in range(len(lista)):
        if header_name in lista[i]:
            if i != len(lista)-1:
                ind = lista[i+1]
            else:
                ind = None
                number = len(table.find_all('tr'))-1
            break
        else:
            ind = None
            number = None
    if ind != None:
        number = 0
        for i, row in enumerate(table.find_all('tr')):
            for cell in row:
                if cell.text == ind:
                    number = i
                    break
            if number != 0:
                break
    return number

filename = sys.argv[1]
with open(filename) as csvfile:
    reader = csv.reader(csvfile)
    brojac = 1
    for row in reader:
        url = row[0]
        req = requests.get(url)
        soup = BeautifulSoup(req.content, 'html.parser')
        try:
            player_id = None
            print('Player ID:', player_id)
            print('URL:', url)
            
            name = get_before_sub('(', soup.find('h1', class_ = 'firstHeading').text)
            print('Name:', name)
            
            try:
                full_name = get_before_sub('[', soup.find("td", class_ = 'infobox-data nickname').get_text(strip = True))
            except AttributeError as e:
                full_name = name
            print('Full name:', full_name)
            
            try:
                date_of_birth = soup.find('span', {'class': 'bday'}).text
            except Exception:
                date_of_birth = None
            print('Date of birth:', date_of_birth)
            
            if date_of_birth != None:
                year = int(date_of_birth[0:4])
                month = int(date_of_birth[5:7])
                day = int(date_of_birth[8:])
                birthday = date(year, month, day)
                age = relativedelta(date.today(), birthday).years
            else:
                age = None
            print('Age:', age)
    
            part_table = soup.find('table', class_ = 'infobox vcard')

            try:
                place_row = part_table.find('th', string = 'Place of birth').parent
                place_of_birth = get_before_sub('[', place_row.find('td').text.strip())
                for i in range(place_of_birth.count(')')):
                    place_of_birth = get_after_sub(')', place_of_birth)
                city_of_birth = place_of_birth.split(',')[0]
                if "\n" in city_of_birth:
                    city_of_birth = get_after_sub('\n', city_of_birth)
            except AttributeError:
                try:
                    place_row = part_table.find('th', string = 'Born').parent
                    place_of_birth = get_before_sub('[', place_row.find('td').text.strip())
                    for i in range(place_of_birth.count(')')):
                        place_of_birth = get_after_sub(')', place_of_birth)
                    city_of_birth = place_of_birth.split(',')[0]
                    if "\n" in city_of_birth:
                        city_of_birth = get_after_sub('\n', city_of_birth)
                except AttributeError:
                    place_of_birth = None
                    city_of_birth = None
                    
            print('Place of birth:', place_of_birth)
            print('City of birth:', city_of_birth)
            
            try:
                origin = place_of_birth.split(',')[-1]
            except AttributeError:
                origin = None
            print('Country of origin:', origin)
            
            #height_row = part_table.find('th', string = 'Height').parent
            #height = height_row.find('td').text[1:5]
            #print("Height:", height)
            # these info were not needed, ignore
            
            try:
                position_row = part_table.find('th', string = 'Position(s)').parent
                position = get_before_sub('[', position_row.find('td').text[1:])
            except AttributeError:
                try:
                    position_row = part_table.find('th', string = 'Position').parent
                    position = get_before_sub('[', position_row.find('td').text[1:])
                except AttributeError:
                    position = None
            print('Position(s):', position)
            
            try:
                number_of_appearances = int(part_table.find_all('tr')[find_header_after('Senior', part_table)-1].text.split()[-2])
                goals = part_table.find_all('tr')[find_header_after('Senior', part_table)-1].text.split()[-1]
                goals = int(goals[1:len(goals)-1])
                club = part_table.find_all('tr')[find_header_after('Senior', part_table)-1].text.split()[1:-2]
                if isinstance(club, list) == True:
                    club = get_before_sub('[', get_after_sub('→', ' '.join(club)))
                # I assume that if number of appear. is missing, then so is the number of goals (i am not sure this holds)
            except ValueError:
                number_of_appearances = None
                goals = None
                club = part_table.find_all('tr')[find_header_after('Senior', part_table)-1].text.split()[1:]
                if isinstance(club, list) == True:
                    club = get_before_sub('[', get_after_sub('→', ' '.join(club)))
            except Exception:
                number_of_appearances = None
                goals = None
                club = None
            
            print('Number of appearances:', number_of_appearances)
            print('Goals in the current club:', goals)
            # the table in csv doesn't differentiate between active and non-active players
            # because that was not the task; but from here, that info is easily accesible
            # in case the player is not active, variable club (or current_club in sql) denotes his last club
            
            try:
                part_table.find('th', string = 'Team information').parent 
                activity = 'YES'
                print('Active:', activity)
                print('Current club:', club)
            except AttributeError:
                activity = 'NO'
                print("Active:", activity)
                print("The last club the player played for:", club)
                # i find it useful to have activity as well, but i did not use it for table creation
            
            try:
                national_team = part_table.find_all('tr')[find_header_after('International', part_table)-1].text.split()[1]
            except Exception:
                national_team = None
            
            if isinstance(national_team, str) == True and isinstance(origin, str) == True:
                if national_team in origin:
                    national_team = origin
            print('National team:', national_team)
            # say that a player is from country "x" and belongs to the national_team of country "y z w"
            # my variable national_team would print only value "y" -> i am aware of that.
            # the solution would be similar as in the case of club where i first check appearance and goals.
            # in the whole data, sometimes there is a space on the first position
            # -> that is also something that I could've worked on, but at the moment there is no need
            
            scraping_time = datetime.datetime.now()
            scraping_time = scraping_time.strftime('%Y/%m/%d %H:%M:%S')
            print('Scraping timestamp:', scraping_time)
            print(brojac)
            brojac += 1

        except AttributeError as e:
            #print(e)
            #print(brojac)
            # i skip unvalid links for example
            continue
        
        my_values = (name, full_name, date_of_birth, age, city_of_birth, origin, position, club, national_team, \
                player_id, url, place_of_birth, number_of_appearances, goals, scraping_time)
        
        cnx = mysql.connector.connect(user='root', password='rootroot',
                                    host='localhost', 
                                    database='mydatabase',
                                    charset='utf8')
        cursor = cnx.cursor(buffered = True)

        select_query = '''SELECT 1 FROM mydatabase.players WHERE url = %(url)s;'''
        cursor.execute(select_query, {'url' : url})
        line = cursor.fetchall()
        print(list(line))
        
        column_names = ['name', 'full_name', 'date_of_birth', 'age', 'city_of_birth', 'country_of_birth', 'position', 'current_club', \
                'national_team', 'player_id', 'url', 'place_of_birth', 'number_of_apps', 'goals', \
                'scraping_timestamp']
        
        if len(line) == 0:
            insert_query = '''INSERT INTO mydatabase.players VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);'''
            cursor.execute(insert_query, my_values)
        else:
            if name != None:
                ubaci = (name, url)
                cursor.execute('''UPDATE mydatabase.players SET name = %s WHERE url = %s;''', ubaci)
            if full_name != None:
                ubaci = (full_name, url)
                cursor.execute('''UPDATE mydatabase.players SET full_name = %s WHERE url = %s;''', ubaci)
            if date_of_birth != None:
                ubaci = (date_of_birth, url)
                cursor.execute('''UPDATE mydatabase.players SET date_of_birth = %s WHERE url = %s;''', ubaci)  
            if age != None:
                ubaci = (age, url)
                cursor.execute('''UPDATE mydatabase.players SET age = %s WHERE url = %s;''', ubaci) 
            if city_of_birth != None:
                ubaci = (city_of_birth, url)
                cursor.execute('''UPDATE mydatabase.players SET city_of_birth = %s WHERE url = %s;''', ubaci)
            if origin != None:
                ubaci = (origin, url)
                cursor.execute('''UPDATE mydatabase.players SET country_of_birth = %s WHERE url = %s;''', ubaci)
            if position != None:
                ubaci = (position, url)
                cursor.execute('''UPDATE mydatabase.players SET position = %s WHERE url = %s;''', ubaci)
            if club != None:
                ubaci = (club, url)
                cursor.execute('''UPDATE mydatabase.players SET current_club = %s WHERE url = %s;''', ubaci)
            if national_team != None:
                ubaci = (national_team, url)
                cursor.execute('''UPDATE mydatabase.players SET national_team = %s WHERE url = %s;''', ubaci)
            if place_of_birth != None:
                ubaci = (place_of_birth, url)
                cursor.execute('''UPDATE mydatabase.players SET place_of_birth = %s WHERE url = %s;''', ubaci)
            if number_of_appearances != None:
                ubaci = (number_of_appearances, url)
                cursor.execute('''UPDATE mydatabase.players SET number_of_apps = %s WHERE url = %s;''', ubaci)
            if goals != None:
                ubaci = (goals, url)
                cursor.execute('''UPDATE mydatabase.players SET goals = %s WHERE url = %s;''', ubaci)
            if scraping_time != None:
                ubaci = (scraping_time, url)
                cursor.execute('''UPDATE mydatabase.players SET scraping_timestamp = %s WHERE url = %s;''', ubaci)
                
        # this here is for writing this into a new csv file:
        #with open('players-mydata.csv', 'w', encoding = 'utf-8') as f:
        #    for row in cursor:
        #        f.write(';;'.join(str(x) for x in row) + '\n')


        cnx.commit()

        cursor.close()
        cnx.close()
