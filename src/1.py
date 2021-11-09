# encoding: utf-8
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
import time
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import re
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum, auto
from datetime import date

HTTP_USER_AGENT = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
driver.get('https://jovemnerd.com.br/nerdcast')

time.sleep(2)
cookie_button = driver.find_element_by_class_name('text-button-cookie')
cookie_button.click()
ad_x_button = driver.find_element(by='id', value='markClose')
ad_x_button.click()

actions = ActionChains(driver)

# pra selecionar a categoria manualmente (ex. pra teste)
time.sleep(3)

show_more_button = driver.find_element(by='id', value='show-more-podcasts')
actions.move_to_element(show_more_button).perform()

while True: 
    display = show_more_button.get_attribute('style').split(':')[1].strip(';').strip()
    if display != 'none':
        show_more_button.click()
    else:
        break
    time.sleep(1)

podcast_cards = driver.find_elements_by_css_selector('#more-podcasts article.card-post.-rowdesktop')
for card in podcast_cards:
    url = card.find_element_by_css_selector('div.info h2 a').get_attribute('href')
    little_thumb_url = card.find_element_by_css_selector('a.image img').get_attribute('src')
    mytime = card.find_element_by_css_selector('div.info time').text
    length = mytime.split('•')[0].strip()
    date_text = mytime.split('•')[1].strip()
    title = card.find_element_by_css_selector('div.info h2 a').text.strip()
    podcast_and_number = card.find_element_by_css_selector('div.info > a').text.strip()
    podcast_text = re.findall(r'^([^\d]+) (\d+)', podcast_and_number)[0][0]
    number = int(re.findall(r'^([^\d]+) (\d+)', podcast_and_number)[0][1])

    req = Request(url, data=None, headers={'User-Agent': HTTP_USER_AGENT})
    html = urlopen(req)
    episode_page = BeautifulSoup(html, 'html.parser')
    big_thumb_url = episode_page.select('#main article.card-custom a.image img')[0]['src'].strip()
    audio_url = episode_page.select('button.play-podcast.button-default.-primary')[0]['data-podcast-url'].strip()
    guests = map(lambda e: e.text.strip(), episode_page.select('.item.guest_item'))
    content_text = episode_page.select('#main .main-content div.content')[0].text.strip()

time.sleep(5)
driver.quit()
