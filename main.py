# coding=utf-8
import logging
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import time
import re
from config import url, interval_time

logging.basicConfig(
    format='%(asctime)s %(levelname)s:%(message)s',
    level=logging.INFO)


def handle_found_appointments(num_found):
    # you can add your own handler (e.g. sounds, telegram) here
    print("Yeah! %d possible appointments" % num_found)
    # This Character plays the default error sound on Ubuntu. I don't know if it works for Windows though
    print("\a")

def crawl():
    s = requests.Session()
    html = s.get(url)
    if(html.status_code != 200):
        print("Website Error")
        return
    soup = BeautifulSoup(html.text, 'html.parser')
    logging.info("Occupied: %d" % len(soup.find_all("td", { "class": "nichtbuchbar" })))
    found = len(soup.find_all("td", { "class": "buchbar" }))
    if found > 0:
        logging.info("FOUND %d POSSIBLE APPOINTMENTS!" % found)
        handle_found_appointments(found)
    else: #try next month too
        logging.info("Trying next month")
        a = soup.find_all('a', {'title': re.compile(r'nächster.*')})
        next_path = urljoin(url,'/').strip('/') + a[0]['href']
        html = s.get(next_path)
        soup = BeautifulSoup(html.text, 'html.parser')
        logging.info("Occupied: %d" % len(soup.find_all("td", { "class": "nichtbuchbar" })))
        found = len(soup.find_all("td", { "class": "buchbar" }))
        if found > 0:
            logging.info("FOUND %d POSSIBLE APPOINTMENTS!" % found)
            handle_found_appointments(found)
    s.close()
if url == "enter-url-here":
    logging.error("You have to enter a URL (get from Bürgeramt 'Termin Berlinweit suchen')")
    exit()

while True:
    crawl()
    time.sleep(interval_time)

