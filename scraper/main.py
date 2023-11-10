import pandas as pd
import requests
from bs4 import BeautifulSoup
import wget
import os
import time


def get_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.find_all('a')

def get_data_links(links):
    data_links = []
    for link in links:
        if link.get('href').startswith('AIS'):
            data_links.append('https://coast.noaa.gov/htdata/CMSP/AISDataHandler/2022/' + link.get('href'))
    return data_links

def download_data(data_links):
    for link in data_links:
        print('Downloading', link)
        wget.download(link, out='scraper/csv/')
        os.system('unzip scraper/csv/*.zip -d scraper/csv/')
        os.system('rm scraper/csv/*.zip')
        for element in os.listdir('scraper/csv/'):
            if element.__contains__('AIS'):
                pd.read_csv('scraper/csv/'+element).to_csv('scraper/csv/complete.csv', mode='a', header=False)
                os.remove('scraper/csv/'+element)

        print('Done')
        time.sleep(1)
        break

def main():
    # Create the data folder if it doesn't exist
    if not os.path.exists('scraper/csv/'):
        os.makedirs('scraper/csv/')
    # Get all links from the webpage
    links = get_links('https://coast.noaa.gov/htdata/CMSP/AISDataHandler/2022/index.html')
    data_links = get_data_links(links)
    download_data(data_links)

main()
