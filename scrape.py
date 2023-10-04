#!/usr/bin/env python3

from bs4 import BeautifulSoup
import requests

url = "http://www.prca.org/resources/worship-devotional/psalter/itemlist/filter?moduleId=113&Itemid=165"
response = requests.get(url)
html_content = response.text
soup = BeautifulSoup(html_content, 'lxml')


page = []
div = soup.find(class_='pagination')
all_a_elements = div.find_all('a')
for a in all_a_elements:
    if a.text.isdigit() and a.text != 1:
        page.append("http://www.prca.org" + a['href'])

info = {}
tags = soup.find_all(class_='genericItemTitle')
for tag in tags:
    cleaned_text = ' '.join(tag.text.split())
    href = "http://www.prca.org" + tag.a['href']
    info[cleaned_text] = href

for i in range(len(page)):
    html_text = requests.get(page[i]).text
    text = BeautifulSoup(html_text, 'lxml')
    tags = text.find_all(class_='genericItemTitle')
    for tag in tags:
        cleaned_text = ' '.join(tag.text.split())
        phref = "http://www.prca.org" + tag.a['href']
        info[cleaned_text] = href


