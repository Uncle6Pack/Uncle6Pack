import streamlit as st
import os, sys

@st.experimental_singleton
def installff():
  os.system('sbase install geckodriver')
  os.system('ln -s /home/appuser/venv/lib/python3.7/site-packages/seleniumbase/drivers/geckodriver /home/appuser/venv/bin/geckodriver')

_ = installff()
from selenium import webdriver
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome('chromedriver',chrome_options=chrome_options)

#!pip install bs4
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from csv import writer
import time
import datetime

def to_csv(data_lst):
    with open(f'fp_proj.csv', 'a+', newline='', encoding='utf-8') as write_obj:
        csv_writer = writer(write_obj)
        csv_writer.writerow(data_lst)


options = Options()
options.add_argument('--incognito')
options.add_argument("--headless")
#driver = Chrome(options=options)

driver.get('https://secure.fantasypros.com/accounts/login/')
time.sleep(1)
driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/div[2]/form/input[2]').send_keys('thebtrain@hotmail.com')
time.sleep(1)
driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/div[2]/form/input[3]').send_keys('bt%jsX$eywZWI!S')
time.sleep(1)
driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/div[2]/form/button').click()
time.sleep(1)

driver.get('https://www.fantasypros.com/daily-fantasy/mlb/fanduel-cheatsheet.php?try=true&loggedin')
time.sleep(5)

soup = BeautifulSoup(driver.page_source, 'lxml')
tbody = soup.find('tbody')
trs = tbody.find_all('tr')

columns=["Player(Team Position)", "Hand", "", "", "Opp(ET)", "Opp SP", "Rain", "Spread", "O/U", "Pred Score",
             "Proj Rank", "$ Rank", "Rank Diff", "Proj PTS", "Salary", "CPP"]
to_csv(columns)

for tr in trs:
    tds = tr.find_all('td')
    print("Row Inserted!")
    to_csv([td.text for td in tds])

from bs4 import BeautifulSoup
import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from prettytable import PrettyTable
pd.set_option('display.max_columns', 500)

def call_endpoint(url, max_level=3, include_new_player_attributes=False):
    '''
    takes: 
        - url (str): the API endpoint to call
        - max_level (int): level of json normalizing to apply
        - include_player_attributes (bool): whether to include player object attributes in the returned dataframe
    returns:
        - df (pd.DataFrame): a dataframe of the call response content
    '''
    resp = requests.get(url).json()
    data = pd.json_normalize(resp['data'], max_level=max_level)
    included = pd.json_normalize(resp['included'], max_level=max_level)
    if include_new_player_attributes:
        inc_cop = included[included['type'] == 'new_player'].copy().dropna(axis=1)
        data = pd.merge(data
                        , inc_cop
                        , how='left'
                        , left_on=['relationships.new_player.data.id'
                                   ,'relationships.new_player.data.type']
                        , right_on=['id', 'type']
                        , suffixes=('', '_new_player'))
    return data

url = 'http://partner-api.prizepicks.com/leagues' # leagues that are live on our board
df = call_endpoint(url)
df

"""# MLB"""

#mlb
url = 'https://partner-api.prizepicks.com/projections?leauge_id=2&per_page=1000&single_stat=True' # use per_page=1000 to avoid pagination issues
mlbf = call_endpoint(url)
url = 'https://partner-api.prizepicks.com/projections?league_id=2&per_page=1000&single_stat=True'
mlbf = call_endpoint(url, include_new_player_attributes=True)
#url = 'https://partner-api.prizepicks.com/projections?league_id=2&single_stat=True'
mlbf = call_endpoint(url, include_new_player_attributes=True)
mlb_stat_df = mlbf[mlbf['attributes.stat_type']=='Pitcher Fantasy Score'] #attributes.stat_type	attributes.projection_type
mlb_stat_df.sort_values(by='attributes.line_score', ascending=False)
mlb_pp_df = mlb_stat_df[['attributes.name', 'attributes.line_score']]
mlb_pp_df.rename({'attributes.name': 'Name'}, axis=1, inplace=True)
mlb_pp_df['Name'].str.strip()
mlb_pp_df['attributes.line_score'] = pd.to_numeric(mlb_pp_df['attributes.line_score'])
mlb_pp_df

mlb_pp_df['Name'].str.encode('utf-8')
mlb_pp_df

mlb = pd.read_csv('fp_proj.csv')
mlb.columns = ['Player', 'Hand', 'Unnamed: 2', 'Unnamed: 3', 'Opp(ET)',
       'Opp SP', 'Rain', 'Spread', 'O/U', 'Pred Score', 'Proj Rank', '$ Rank',
       'Rank Diff', 'Proj PTS', 'Salary', 'CPP']
mlb[['Name','Team']] = mlb.Player.str.split('\(|\)', expand=True).iloc[:,[0,1]]
mlb2 = mlb[['Name','Proj PTS']]
mlb2['Name'] = mlb2['Name'].str[:-1]
mlb2['Name'].str.encode('utf-8')
#mlb2['Name'] = mlb2['Name'].astype(str)
#mlb2.to_csv('mlb2.csv')
mlb2

#mlb_pp_df2 = mlb_pp_df[['Name', 'attributes.line_score']]
mlb_pp_df3 = pd.concat([mlb_pp_df, mlb2], axis = 1)
mlb_pp_df4 = pd.merge(mlb_pp_df, mlb2, on='Name')
mlb_pp_df4['diff'] = mlb_pp_df4['Proj PTS']-mlb_pp_df4['attributes.line_score']
mlb_pp_df4['diff']
overs = mlb_pp_df4.sort_values('diff', ascending=False).head()
unders = mlb_pp_df4.sort_values('diff', ascending=True).head()
overbets = overs['diff'].round(2).to_list()
overguys = overs['Name'].to_list()
underbets = unders['diff'].round(2).to_list()
underguys = unders['Name'].to_list()

mlb_print = PrettyTable()
mlb_print.add_column('Overs', overbets)
mlb_print.add_column('Name', overguys)
mlb_print.add_column('Unders', underbets)
mlb_print.add_column('Name', underguys)
print(mlb_print)

"""
# NBA"""

nba = pd.read_csv('NBA.csv')
nba.head()

#nba = pd.read_csv('NBA3.csv') #https://yebscore.com/
#nba.columns

nba['totals'] = nba['Exp rebounds']+nba['Exp assists']+nba['Exp points']
nba.sort_values(by='totals', ascending=False)
nba.sort_values(by='totals', ascending=False)
nba.rename({'Player': 'Name'}, axis=1, inplace=True)
nba

url = 'https://partner-api.prizepicks.com/projections?league_id=7&single_stat=True'
nbadf = call_endpoint(url, include_new_player_attributes=True)
nbadf.head()

#nba
#url = 'https://partner-api.prizepicks.com/projections?league_id=7&per_page=1000&single_stat=True'
#nbadf = call_endpoint(url)
#nbadf.head()

#nba
##url = 'https://partner-api.prizepicks.com/projections?leauge_id=7&per_page=1000&single_stat=True' # use per_page=1000 to avoid pagination issues
#nbadf = call_endpoint(url)
#nbadf.head()

nba_stat_df = nbadf[nbadf['attributes.stat_type']=='Pts+Rebs+Asts'] #attributes.stat_type	attributes.projection_type
nba_pp_df = nba_stat_df[['attributes.name', 'attributes.line_score']]
nba_pp_df.rename({'attributes.name': 'Name'}, axis=1, inplace=True)
nba_pp_df

nba_proj_df3 = pd.merge(nba_pp_df5, nba, on='Name')
nba_proj_df3.dtypes

nba_proj_df2 = pd.merge(nba_pp_df, nba, on='Name')
nba_proj_df2['attributes.line_score'] = nba_proj_df2['attributes.line_score'].astype(float)
nba_proj_df2['diff'] = nba_proj_df2['totals'] - nba_proj_df2['attributes.line_score']
nba_proj_df2.sort_values('diff', ascending=False)

first_column = nba_proj_df2.pop('totals')
nba_proj_df2.insert(0, 'totals', first_column)
nba_proj_df2['attributes.line_score'] = nba_proj_df2['attributes.line_score'].astype(float)
nba_proj_df2['diff'] = nba_proj_df2['totals'] - nba_proj_df2['attributes.line_score']
second_column = nba_proj_df2.pop('diff')
nba_proj_df2.insert(1, 'diff', second_column)
nba_proj_df2.sort_values('diff', ascending=True)

diff = nba_proj_df2.sort_values('diff', ascending=False).head()
bets = diff['diff'].round(2).to_list()
guys = diff['Name'].to_list()
print(guys)
nba_print = PrettyTable()
nba_print.add_column('Diff', bets)
nba_print.add_column('Name', guys)
nba_print.align = 'l'
print(nba_print)

"""# USFL"""

usfl_df = pd.read_csv('USFL.csv')
usfl_df.columns

#usfl
url = 'https://partner-api.prizepicks.com/projections?leauge_id=191&per_page=1000&single_stat=False' # use per_page=1000 to avoid pagination issues
usfl = call_endpoint(url, include_new_player_attributes=True)
#usfl = 'https://partner-api.prizepicks.com/projections?league_id=191&per_page=1000&single_stat=False'
#usfl = call_endpoint(url, include_new_player_attributes=True)
#url = 'https://partner-api.prizepicks.com/projections?league_id=191&single_stat=False'
#usfl = call_endpoint(url, include_new_player_attributes=True)
usfl_stat_df = usfl[usfl['attributes.stat_type']=='Fantasy Score'] #attributes.stat_type	attributes.projection_type
usfl_stat_df.sort_values(by='attributes.line_score', ascending=False)
usfl_pp_df = usfl_stat_df[['attributes.position','attributes.name', 'attributes.team', 'attributes.line_score', 'attributes.stat_type']]
usfl_pp_df.rename({'attributes.name': 'Player Name'}, axis=1, inplace=True)
usfl_pp_df

#usfl
usfl_pp_df.sort_values(by='attributes.line_score', ascending=False).head()
usfl_pp_df.head()

usfl_pp_df = usfl_pp_df[['Player Name', 'attributes.line_score']]
usfl_pp_df.rename({'attributes.name': 'Player Name'}, axis=1, inplace=True)
usfl_pp_df2 = pd.merge(usfl_pp_df, usfl_df, on='Player Name')
usfl_pp_df2['attributes.line_score'] = usfl_pp_df2['attributes.line_score'].astype(float)
usfl_pp_df2['diff'] = usfl_pp_df2['DKFpts'] - usfl_pp_df2['attributes.line_score']
usfl_pp_df2.sort_values('diff', ascending=False)

usfl_print = PrettyTable()
usfl_print.title = 'USFL Best Prize Pick Bets'
bets = usfl
usfl_print.add_column('Diff', bets)
usfl_print.add_column('Player Name', guys)
print(usfl_print)



"""#NHL"""

usfl_df = pd.read_csv('NHL.csv')
usfl_df.columns

#usfl
url = 'https://partner-api.prizepicks.com/projections?leauge_id=191&per_page=1000&single_stat=True' # use per_page=1000 to avoid pagination issues
usfl = call_endpoint(url)
usfl = 'https://partner-api.prizepicks.com/projections?league_id=191&per_page=1000&single_stat=True'
usfl = call_endpoint(url, include_new_player_attributes=True)
url = 'https://partner-api.prizepicks.com/projections?league_id=191&single_stat=True'
usfl = call_endpoint(url, include_new_player_attributes=True)
usfl_stat_df = usfl[usfl['attributes.stat_type']=='Fantasy Score'] #attributes.stat_type	attributes.projection_type
usfl_stat_df.sort_values(by='attributes.line_score', ascending=False)
usfl_pp_df = usfl_stat_df[['attributes.position','attributes.name', 'attributes.team', 'attributes.line_score', 'attributes.stat_type']]
usfl_pp_df.rename({'attributes.name': 'Player Name'}, axis=1, inplace=True)
usfl_pp_df

#usfl
usfl_pp_df.sort_values(by='attributes.line_score', ascending=False).head()
usfl_pp_df.head()

usfl_pp_df = usfl_pp_df[['Player Name', 'attributes.line_score']]
usfl_pp_df.rename({'attributes.name': 'Player Name'}, axis=1, inplace=True)
usfl_pp_df2 = pd.merge(usfl_pp_df, usfl_df, on='Player Name')
usfl_pp_df2['attributes.line_score'] = usfl_pp_df2['attributes.line_score'].astype(float)
usfl_pp_df2['diff'] = usfl_pp_df2['DKFpts'] - usfl_pp_df2['attributes.line_score']
usfl_pp_df2.sort_values('diff', ascending=False)

usfl_print = PrettyTable()
usfl_print.title = 'USFL Best Prize Pick Bets'
bets = usfl
usfl_print.add_column('Diff', bets)
usfl_print.add_column('Player Name', guys)
print(usfl_print)

"""# College Basketball"""

cbb = pd.read_csv('CBB.csv')
cbb.columns

cbb_pp_df.columns

cbb['totals'] = cbb['TRB']+cbb['AST']+cbb['PTs']
cbb.sort_values(by='totals', ascending=False)
#nba['totals'] = nba['Rebounds']+nba['Assists']+nba['Points']
#nba_proj_df2 = nba
cbb.sort_values(by='totals', ascending=False)
cbb.rename({'Player': 'Name'}, axis=1, inplace=True)
cbb

#cbb
url = 'https://partner-api.prizepicks.com/projections?leauge_id=20&per_page=1000&single_stat=True' # use per_page=1000 to avoid pagination issues
cbbdf = call_endpoint(url)
url = 'https://partner-api.prizepicks.com/projections?league_id=20&per_page=1000&single_stat=True'
cbbdf = call_endpoint(url, include_new_player_attributes=True)
#url = 'https://partner-api.prizepicks.com/projections?league_id=20&single_stat=True'
cbbdf = call_endpoint(url, include_new_player_attributes=True)
cbb_stat_df = cbbdf[cbbdf['attributes.stat_type']=='Pts+Rebs+Asts'] #attributes.stat_type	attributes.projection_type
cbb_stat_df.sort_values(by='attributes.line_score', ascending=False)
cbb_pp_df = cbb_stat_df[['attributes.position','attributes.name', 'attributes.team', 'attributes.line_score', 'attributes.stat_type']]
cbb_pp_df.rename({'attributes.name': 'Name'}, axis=1, inplace=True)
cbb_pp_df

cbb_proj_df2 = pd.merge(cbb_pp_df, cbb, on='Name')
cbb_proj_df2['attributes.line_score'] = cbb_proj_df2['attributes.line_score'].astype(float)
cbb_proj_df2['diff'] = cbb_proj_df2['totals'] - cbb_proj_df2['attributes.line_score']
cbb_proj_df2.sort_values('diff', ascending=False)
