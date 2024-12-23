#Imports
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import numpy as np
import pandas as pd
from random import randint
from requests import get
from time import sleep
from warnings import warn

# Variables
DATA_DIR = ('/Users/chrislee/PyCharmProjects/NHL-Draft-Analysis')
START_YEAR = 2005
END_YEAR = 2020
draft_stats = pd.DataFrame()

if START_YEAR == END_YEAR:
    title_year_text = START_YEAR
else:
    title_year_text = '{}-{}'.format(START_YEAR, END_YEAR)

# Functions
def get_html(year):
    # Get website
    url = ('https://www.hockey-reference.com/draft/NHL_{}_entry.html'.format(year))
    response = get(url, timeout=5)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Warning for non-200 status codes
    if response.status_code != 200:
        warn('Error: Status code {}'.format(response.status_code))
    return soup

# Get variable headers for the statistics from the page
def get_header(soup):
    header = [i.text for i in soup.find_all('tr')[1].find_all('th')]
    header.extend(['Year', 'Player_ID'])
    header = [item.replace('/', '_').replace(' ', '_').replace('.', '').replace('+', 'Plus').replace('-', 'Minus') for item in header]
    return header

# Get the player statistics for the stat type
def get_stats(soup, headers):
    stats = []
    rows = soup.find_all('tbody')[0].find_all('tr', class_=None)
    for i in range(len(rows)):
        player_id = [a['href'] for a in rows[i].find_all('td')[1].find_all('a', href=True) if a.text][0]
        stats.append([j.text for j in rows[i].find_all(['th', 'td'])])
        stats[i].extend([year, player_id[11:][:-5]])
    stats = pd.DataFrame(stats, columns=headers)
    return stats

# Clean up and format dataframe
def format_dataframe(draft_stats):
    # Move important columns up
    col_name1 = 'Year'
    save_col = draft_stats.pop(col_name1)
    draft_stats.insert(1, col_name1, save_col)
    col_name2 = 'Player_ID'
    save_col = draft_stats.pop(col_name2)
    draft_stats.insert(4, col_name2, save_col)

    # Choose which columns to keep
    draft_stats = draft_stats.iloc[:, 0:16]
    draft_stats = draft_stats.copy()

    # Convert numerical columns to numeric
    cols = [i for i in draft_stats.columns if i not in ['Team', 'Player', 'Nat', 'Pos', 'Amateur_Team', 'Player_ID']]
    for col in cols:
        draft_stats[col] = pd.to_numeric(draft_stats[col])

    # Fill blanks
    draft_stats = draft_stats.fillna(0)


    draft_stats['Round'] = draft_stats.apply(lambda x: (x['Overall'] // 31.01) + 1
    if x['Year'] >= 2017 else (x['Overall'] // 30.01) + 1, axis=1)

    # Save to csv
    draft_stats.to_csv('{}/nhl_draft_stats.csv'.format(DATA_DIR), index=False)

# Main loop to get draft statistics for years of interest
for year in range(START_YEAR, END_YEAR + 1):
    # Slow down the web scrape
    sleep(randint(1, 3))

    # Get website
    html_soup = get_html(year)

    # Get header
    if year == START_YEAR:
        headers = get_header(html_soup)

    # Get player stats
    draft_stats = pd.concat([draft_stats, pd.DataFrame(get_stats(html_soup, headers))], ignore_index=True)

    print('Completed {}'.format(year))

# Format the datatframe
format_dataframe(draft_stats)

# Read in data
draft_data = pd.read_csv('{}/nhl_draft_stats.csv'.format(DATA_DIR))

# Setup data for analysis
draft_data = draft_data[draft_data['Round'] <= 7]
draft_data['Ind'] = [1 if i >= 82 else 0 for i in draft_data['GP']]
draft_data['One'] = 1

# Setup data for 1st graph
a_data = draft_data[['Round', 'Ind', 'One']].groupby('Round').agg('sum').reset_index()
a_data['Percentage'] = a_data['Ind'] / a_data['One']
a_xlabels = ['Round {}'.format(int(i)) for i in a_data['Round']]

########################################################################################################################
# Probability of Finding an NHL Player by Draft Round
########################################################################################################################
# Create 1st graph
plt.figure(figsize=(4.5, 4), dpi=300)
a_data.groupby('Round')['Percentage'].sum().plot(kind='bar')
plt.title('Probability of Finding an NHL Player \n by Draft Round ({})'.format(title_year_text),
          fontdict={'fontsize': 9, 'fontweight': 'bold'})
plt.xlabel(None)
plt.ylabel('Percentage', fontsize=8)
plt.xticks(np.arange(len(a_xlabels)), labels=a_xlabels, rotation='horizontal', fontsize=5)
plt.yticks(fontsize=7)
plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
plt.ylim(0, 1)
plt.text(4.8, 70, ' NHL player is defined \n as having played more \n than 82 NHL games.', fontsize=5)
plt.savefig('{}/Results/Probability of Finding an NHL Player by Draft Round'.format(DATA_DIR))
# plt.show()

########################################################################################################################
# Probability of Finding an NHL Player by Draft Position
########################################################################################################################
# Setup data for 2nd graph
b_data = draft_data[['Overall', 'Ind', 'One']].groupby('Overall').agg('sum').reset_index()
b_data['Percentage'] = b_data['Ind'] / b_data['One']

# Create 2nd graph
plt.figure(figsize=(6, 4), dpi=300)
plt.scatter(b_data['Overall'], b_data['Percentage'], s=1, c=[(0.60, 0.60, 0.60)])
plt.title('Probability of Finding an NHL Player \n by Draft Position ({})'.format(title_year_text),
          fontdict={'fontsize': 9, 'fontweight': 'bold'})
plt.xlabel('Draft Position', fontsize=8)
plt.ylabel('Percentage', fontsize=8)
plt.xticks(np.arange(211)[::10], np.array([i for i in range(1, 212)])[::10], fontsize=5)
plt.yticks(fontsize=7)
plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
plt.ylim(0, 1)
plt.text(180, 90, ' NHL player is defined \n as having played more \n than 82 NHL games.', fontsize=5)
# Line of best fit
curve_fit = np.polyfit(b_data['Overall'], b_data['Percentage'], 8)
p = np.poly1d(curve_fit)
plt.plot(b_data['Overall'], p(b_data['Overall']))
plt.savefig('{}/Results/Probability of Finding an NHL Player by Draft Position'.format(DATA_DIR))
# plt.show()

########################################################################################################################
# NHL Players by Draft Round
########################################################################################################################
# Setup data for 3rd graph
c_data = draft_data.groupby(['Round']).sum().reset_index()
c_labels = ['Round {}'.format(int(i)) for i in c_data['Round'].unique()]

# Create 3rd graph
plt.figure(figsize=(4, 4), dpi=300)
plt.pie(c_data['Ind'], autopct='%.1f%%', textprops=dict(fontsize=7))
plt.title('NHL Players by Draft Round \n ({})'.format(title_year_text),
          fontdict={'fontsize': 9, 'fontweight': 'bold'})
plt.legend(c_labels, loc="upper left", fontsize=4, frameon=False)
plt.text(0.7, 1, ' NHL player is defined \n as having played more \n than 82 NHL games.', fontsize=5)
plt.savefig('{}/Results/NHL Players by Draft Round'.format(DATA_DIR))
# plt.show()