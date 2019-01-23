#!./run.sh fb_suggestions.py
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.keys import Keys
import pyotp
import time
import json

username = 'username'
password = 'password'
totp_secret = 'secret'

pymk = []
try:
    with open('fb_suggestions.txt', 'r') as fin:
        for line in fin:
            id = line.split(',')[0]
            pymk.append(id)
except:
    pass

def view_page(d):
    print(d.title)
    for form in d.find_elements_by_xpath('//form'):
        print(form.tag_name, form.get_property('action'))
        for e in form.find_elements_by_css_selector('*'):
            if e.tag_name in ['a', 'div', 'span', 'img', 'table', 'td', 'tr', 'tbody', 'i', 'strong', 'article', 'section', 'label']:
                continue
            print(' ', e.tag_name, e.get_property('type'), e.get_property('id'), e.get_property('name'))

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--no-sandbox')
#chrome_options.add_argument('--window-size=1420,1080')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
driver = webdriver.Chrome(options=chrome_options)
driver.implicitly_wait(5)

# get non-existent page on same domain to set cookie
driver.get('https://m.facebook.com/no_page')
# load cookies
try:
    with open('fb_cookies.txt', 'r') as fin:
        for line in fin:
            driver.add_cookie(json.loads(line))
except Exception as err:
    print(err)

driver.get('https://m.facebook.com/friends/center/suggestions/')

while True:
    WebDriverWait(driver, 10).until(lambda d: d.execute_script('return document.readyState == "complete";'))

#    print(driver.title)
#    print(driver.current_url)

    if driver.current_url.startswith('https://m.facebook.com/login.php') and \
       driver.title == 'Вход на Facebook | Facebook':
        e = driver.find_element_by_name('email')
        e.send_keys(username)
        e = driver.find_element_by_name('pass')
        e.send_keys(password)
        e = driver.find_element_by_name('login')
        old_html = driver.find_element_by_tag_name('html')
        e.click()
        WebDriverWait(driver, 10).until(ec.staleness_of(old_html))
        continue

    if driver.current_url.startswith('https://m.facebook.com/checkpoint/') and \
       driver.title == 'Введите код для входа, чтобы продолжить':
        e = driver.find_element_by_name('approvals_code')
        totp = pyotp.TOTP(totp_secret)
        e.send_keys(totp.now())
        e = driver.find_element_by_name('submit[Submit Code]')
        old_html = driver.find_element_by_tag_name('html')
        e.click()
        WebDriverWait(driver, 10).until(ec.staleness_of(old_html))
        continue

    if driver.current_url.startswith('https://m.facebook.com/login/checkpoint/') and \
       driver.title == 'Запомнить браузер':
        e = driver.find_element_by_name('submit[Continue]')
        old_html = driver.find_element_by_tag_name('html')
        e.click()
        WebDriverWait(driver, 10).until(ec.staleness_of(old_html))
        continue

    if driver.current_url.startswith('https://m.facebook.com/login/checkpoint/') and \
       driver.title == 'Посмотреть недавний вход':
        e = driver.find_element_by_id('checkpointSubmitButton-actual-button')
        old_html = driver.find_element_by_tag_name('html')
        e.click()
        WebDriverWait(driver, 10).until(ec.staleness_of(old_html))
        continue

    if driver.current_url.startswith('https://m.facebook.com/friends/center/suggestions/') and \
       driver.title == 'Найти друзей':
        driver.execute_script('window.scrollBy(0, 10000);')
        time.sleep(5)
        with open('fb_suggestions.html', 'w') as fout:
            fout.write(driver.page_source)
        friends_table = driver.find_element_by_id('friends_center_main')
        friends = friends_table.find_elements_by_xpath('./div/div')
        with open('fb_suggestions.txt', 'a') as fout:
            for friend in friends:
                id = friend.get_attribute('data-pymk-id')
                name = friend.find_element_by_xpath('./div/div/*/a').get_property('text')
                if id not in pymk:
                    print(id, name)
                    fout.write(id + ', ' + name + '\n')
        break

    print('Unknown page url: ' + driver.current_url)
    print('Unknown page title: ' + driver.title)
    with open('fb_src.html', 'w') as fout:
        fout.write(driver.page_source)
    view_page(driver)
    break

# save cookies
with open('fb_cookies.txt', 'w') as fout:
    for d in driver.get_cookies():
        fout.write(json.dumps(d) + '\n')

driver.quit()
