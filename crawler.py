# coding=utf-8
import logging
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import re

logging.basicConfig(
    format='%(asctime)s %(levelname)s:%(message)s',
    level=logging.INFO)

def parse_tables(soup):
    tables = soup.find_all("table")
    available_appointments = ""
    for table in tables:
        #get month
        month = table.find("th",{"class":"month"}).text
        days = table.find_all("td", { "class": "buchbar" })
        if len(days) > 0:
            for day in days:
                available_appointments+=day.text + " " + month + "\n"
    return available_appointments

def crawl(link):
    s = requests.Session()
    html = s.get(link)
    if(html.status_code != 200):
        print("Website Error")
        return
    soup = BeautifulSoup(html.text, 'html.parser')
    av_app =  parse_tables(soup)
    #get the 2 tables representing a month
    
  #try next month too
    logging.info("Trying next month")
    a = soup.find_all('a', {'title': re.compile(r'nächster.*')})
    next_path = urljoin(link,'/').strip('/') + a[0]['href']
    html = s.get(next_path)
    soup = BeautifulSoup(html.text, 'html.parser')
    av_app+=parse_tables(soup)
    s.close()
    return av_app
