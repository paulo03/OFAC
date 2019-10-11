import requests
import pandas as pd
import datetime
import sqlite3

r = requests.get('https://www.treasury.gov/ofac/downloads/sdn.pip')
lines = str(r.text).split("\r\n")

matrix = []
for line in lines:
    entry = line.split("|")
    matrix.append(entry)

ind = []
corp = []

count = 0
while count < len(matrix):
    if len(matrix[count]) > 1:
        if matrix[count][2] == '"individual"':
            ind.append(matrix[count])
        else:
            corp.append(matrix[count])
    count += 1

f_ind = [] # f for final list for ind
for entry in ind:
    try:
        last_name = entry[1].split(',')[0].strip('"')
        first_name = entry[1].split(',')[1].strip('"')
    except IndexError as e:
        last_name = entry[1].split(',')[0].strip('"')
        first_name = ""
    f_ind.append([
        int(entry[0]), 
        last_name,
        first_name[1:],
        entry[2].strip('"'),
        entry[3].strip('"'),
        entry[4].strip('"'),
        entry[11].strip('"')
    ])
            
f_corp = [] # f for final list for corp
for entry in corp:
    f_corp.append([
        int(entry[0]), 
        entry[1].strip('"'),
        entry[2].strip('"'),
        entry[3].strip('"'),
        entry[11].strip('"')
    ])

df_ind = pd.DataFrame(f_ind,
                      columns=["#",
                               "Last Name",
                               "First Name",
                               "Ind/Entity",
                               "Global Tag",
                               "Note",
                               "Extra"])

df_corp = pd.DataFrame(f_corp, columns=["#",
                                        "Name",
                                        "Type",
                                        "Country",
                                        "Extra"])

conn = sqlite3.connect('SDN_List.db')
c = conn.cursor()
 
def create_table_IND():
    c.execute('''CREATE TABLE IF NOT EXISTS SDNindividual(num INTEGER,
                                                          lastname VARCHAR, 
                                                          firstname VARCHAR,
                                                          globaltag VARCHAR,
                                                          note TEXT,
                                                          extra TEXT)
              ''')
def create_table_CORP():
    c.execute('''CREATE TABLE IF NOT EXISTS SDNcorporation(num INTEGER,
                                                           name VARCHAR, 
                                                           type VARCHAR,
                                                           country VARCHAR,
                                                           extra TEXT)
              ''')

def ind_entry(df_ind):
    count = 0
    while count < len(df_ind):
        c.execute('''INSERT OR IGNORE INTO SDNindividual(num,
                                                         lastname,
                                                         firstname,
                                                         globaltag,
                                                         note,
                                                         extra) 
                     VALUES(?, ?, ?, ?, ?, ?)''',
              (df_ind['#'][count],
               df_ind['Last Name'][count],
               df_ind['First Name'][count], 
               df_ind['Global Tag'][count],
               df_ind['Note'][count],
               df_ind['Extra'][count]))
        conn.commit()
        count += 1
        
def corp_entry(df_corp):
    count = 0
    while count < len(df_corp):
        c.execute('''INSERT OR IGNORE INTO SDNcorporation(num,
                                                          name,
                                                          type,
                                                          country,
                                                          extra) 
                     VALUES(?, ?, ?, ?, ?)''',
              (df_corp['#'][count],
               df_corp['Name'][count],
               df_corp['Type'][count],
               df_corp['Country'][count],
               df_corp['Extra'][count]))
        conn.commit()
        count += 1

create_table_IND()
ind_entry(df_ind)
create_table_CORP()
corp_entry(df_corp)

# IF NOT SQLITE DB - YOU CAN USE CSV EXPORT - UNCOMMENT BELOW
'''
date = str(datetime.date.today())
csv_ind = 'OFAC_INDIV_MATRIX_' + date + '.csv'
csv_corp = 'OFAC_CORP_MATRIX_' + date + '.csv'
csv1 = df_ind.to_csv(csv_ind, index=False)
csv2 = df_corp.to_csv(csv_corp, index=False)
'''
