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
START_YEAR = 2016
END_YEAR = 2016
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
    print(header)
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
    col_name1 = 'Year'
    save_col = draft_stats.pop(col_name1)
    draft_stats.insert(1, col_name1, save_col)
    col_name2 = 'Player_ID'
    save_col = draft_stats.pop(col_name2)
    draft_stats.insert(4, col_name2, save_col)

    draft_stats = draft_stats.iloc[:, 0:16]
    draft_stats = draft_stats.copy()

    # Convert numerical columns to numeric
    cols = [i for i in draft_stats.columns if i not in ['Team', 'Player', 'Nat', 'Pos', 'Amateur_Team', 'Player_ID']]
    for col in cols:
        draft_stats[col] = pd.to_numeric(draft_stats[col])

    # Fill blanks
    draft_stats = draft_stats.fillna(0)

    draft_stats['Round'] = (draft_stats['Overall'] // 30.01) + 1

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
