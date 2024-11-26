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
draft_stats = pd.DataFrame()

url = 'https://www.hockey-reference.com/draft/NHL_2014_entry.html'
response = get(url, timeout=5)
soup = BeautifulSoup(response.text, 'html.parser')

# Warning for non-200 status codes
if response.status_code != 200:
    warn('Error: Status code {}'.format(response.status_code))
# print(soup)
# header = soup.find_all('tbody')[0].find_all('tr', class_=None)[0].find_all('td')
header = [i.text for i in soup.find_all('tr')[1].find_all('th')]
print(header)

# Just player ID
x = soup.find_all('tbody')[0].find_all('tr', class_=None)
for i in range(len(x)):
    # print([a['href'] for a in x[i].find_all('td')[1].find_all('a', href=True) if a.text][0])
    player_id = [a['href'] for a in x[i].find_all('td')[1].find_all('a', href=True) if a.text][0]
    print(player_id[11:][:-5])

# Player ID and team ID
# x = soup.find_all('tbody')[0].find_all('tr', class_=None)
# for i in range(len(x)):
#     print([a['href'] for a in x[i].find_all('a', href=True) if a.text])

# print(soup.find_all('tbody')[0].find_all('tr', class_=None)[0].find_all('td')[1])
# print(soup.find_all('tbody')[0].find_all('tr', class_=None)[0].find_all(attrs={'class': 'left'}))
# print(soup.find_all('tbody')[0].find_all('tr', class_=None)[0].find_all('a'))

# Get variable headers for the statistics from the page
def get_header(soup):
    header = [i.text for i in soup.find_all('tr')[1].find_all('th')]
    header.append('Year')
    header = [item.replace('/', '_').replace(' ', '_').replace('.', '') for item in header]
    return header

# Get the player statistics for the stat type
def get_stats(soup, headers):
    stats = []
    rows = soup.find_all('tbody')[0].find_all('tr', class_=None)
    for i in range(len(rows)):
        stats.append([j.text for j in rows[i].find_all(['th', 'td'])])
        stats[i].append(year)
    stats = pd.DataFrame(stats, columns=headers)
    return stats
