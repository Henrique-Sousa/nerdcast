from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
import time

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
    display = show_more_button.get_attribute('style').split(':')[1].strip(';').strip(' ')
    if display != 'none':
        show_more_button.click()
    else:
        break
    time.sleep(1)

podcast_list = driver.find_element(by='id', value='more-podcasts')
anchors = podcast_list.find_elements_by_css_selector('article.card-post.-rowdesktop > a')
urls = [a.get_attribute('href') for a in anchors]

time.sleep(5)
