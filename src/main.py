# encoding: utf-8
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
import time
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import re
from datetime import date
import psycopg
import env
from enums import *

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

show_more_button = driver.find_element(by='id', value='show-more-podcasts')
actions.move_to_element(show_more_button).perform()

while True: 
    display = show_more_button.get_attribute('style').split(':')[1].strip(';').strip()
    if display != 'none':
        show_more_button.click()
    else:
        break
    time.sleep(1)

connection = psycopg.connect(
        user=env.user,
        host=env.host,
        password=env.password,
        dbname=env.dbname)
cursor = connection.cursor()

podcast_cards = driver.find_elements_by_css_selector('#more-podcasts article.card-post.-rowdesktop')
podcast_cards.reverse()
for card in podcast_cards:
    url = card.find_element_by_css_selector('div.info h2 a').get_attribute('href')
    little_thumb_url = card.find_element_by_css_selector('a.image img').get_attribute('src')
    mytime = card.find_element_by_css_selector('div.info time').text
    length_str = mytime.split('•')[0].strip()
    date_str = mytime.split('•')[1].strip()
    title = card.find_element_by_css_selector('div.info h2 a').text.strip()
    podcast_and_number = card.find_element_by_css_selector('div.info > a').text.strip()
    number_str = re.search(r'(\d+[A-Za-z]?)?$', podcast_and_number).group().strip()
    podcast_str = podcast_and_number.rstrip(number_str).strip().replace('á', 'a').replace(' ', '_').upper()
    if podcast_str in Podcast.__members__:
        podcast = Podcast[podcast_str].value
    else:
        podcast = None
    if number_str.isdigit():
        number = int(number_str)
    else:
        number = None

    hours_match = re.match(r'\d{1,2} horas? ', length_str)
    if hours_match:
        hours = hours_match[0].strip().split(' ')[0].zfill(2)
    else:
        hours = '00'
    minutes_match = re.search(r'\d{1,2} minutos?$' , length_str)
    if minutes_match:
        minutes = minutes_match[0].strip().split(' ')[0].zfill(2)
    else:
        minutes = '00'
    length = f'{hours}:{minutes}' 

    day = int(re.match(r'\d{1,2}', date_str)[0])
    month_str = re.search(r'de (\w+)', date_str).groups(0)[0].strip()
    month = Month[month_str.upper()].value
    year = int(re.search(r'20\d\d$', date_str)[0])
    mydate = date(year, month, day).isoformat()

    req = Request(url, data=None, headers={'User-Agent': HTTP_USER_AGENT})
    html = urlopen(req)
    episode_page = BeautifulSoup(html, 'html.parser')

    big_thumb_url = episode_page.select('#main article.card-custom a.image img')[0]['src'].strip()
    audio_url = episode_page.select('button.play-podcast.button-default.-primary')[0]['data-podcast-url'].strip()
    guests = episode_page.select('.item.guest_item')
    content_text = episode_page.select('#main .main-content div.content')[0].text.strip()

    print(podcast_str, number)

    cursor.execute("""
        insert into episode (
            little_thumb_url, big_thumb_url,
            podcast_id,
            number, title, 
            length, date, 
            audio_url, content_text)
        values ( %s, %s, %s, %s, %s, %s, %s, %s, %s) 
        on conflict do nothing """, (
        little_thumb_url, big_thumb_url, 
        podcast, 
        number, title, 
        length, mydate, 
        audio_url, content_text))
    
    cursor.execute("""
        insert into episode_url (episode_id, url)
        select episode_id, %s
        from episode where title = %s
        on conflict do nothing """, (url, title))

    for guest in guests:
        guest_name = guest.text.strip()
        guest_url = guest.select('.name a')[0]['href'].strip()
        if guest_url == '' or guest_url.strip('/') == 'https://twitter.com':
            guest_url = None
        guest_photo_url = guest.select('.image img')[0]['src'].strip()
        if guest_photo_url == '':
            guest_photo_url = None

        cursor.execute("""
            insert into person (name, url, photo_url)
            values (%s, %s, %s)
            on conflict do nothing
            """, (guest_name, guest_url, guest_photo_url))
        cursor.execute("""
            insert into episode_guest (episode_id, guest_id)
            select episode.episode_id, person.person_id as guest_id
            from episode join person on episode.title = %s and person.name = %s
            on conflict do nothing
            """, (title, guest_name))
            
    connection.commit()

driver.quit()
