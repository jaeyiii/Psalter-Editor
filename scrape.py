#!/usr/bin/env python3

from bs4 import BeautifulSoup
import requests

#getting the html_content of the site for Psalter songs
url = "http://www.prca.org/resources/worship-devotional/psalter/itemlist/filter?moduleId=113&Itemid=165"
response = requests.get(url)
html_content = response.text
soup = BeautifulSoup(html_content, 'lxml')

#this gets all the weblinks of all the other pages and append it to the list 'page'
page = []
div = soup.find(class_='pagination')
all_a_elements = div.find_all('a')
for a in all_a_elements:
    if a.text.isdigit() and a.text != 1:
        page.append("http://www.prca.org" + a['href'])

#this gets all the weblinks of all the songs per page
counter = 0
while counter < len(page):
    # to get the tags division for the current page 
    if soup: 
        tags = soup.find_all(class_='genericItemTitle')
        soup = 0
    # for the rest of the page
    else:
        html_text = requests.get(page[counter]).text
        text = BeautifulSoup(html_text, 'lxml')
        counter += 1
        tags = text.find_all(class_='genericItemTitle')
    #interate thru the tag that has a link of the songs
    for tag in tags:
        cleaned_text = ' '.join(tag.text.split())
        href = "http://www.prca.org" + tag.a['href']
        html_content = requests.get(href).text
        text = BeautifulSoup(html_content, "lxml")
        link = "http://www.prca.org" + text.find("div", class_ = "avDownloadLink").a["href"]
        # use the link of the song to place it in the variable "song"
        song = requests.get(link)

        if song.status_code == 200:
            #rename the song with its name in the web
            song_name = cleaned_text
            file_name = f"Psalter/{song_name}.mp3"
            song_data = song.content
            #download the song and put it in the folder "Psalter"
            with open(file_name, "wb") as file:
                file.write(song_data)
        



