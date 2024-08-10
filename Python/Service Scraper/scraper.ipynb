from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoAlertPresentException, StaleElementReferenceException, NoSuchElementException
import datetime
import time
import re
import os
import pandas as pd
import logging

from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
import requests

options = Options()
options.add_argument("--headless")

chrome_path = r"C:\Users\Mateusz\Downloads\chrome-win64\chrome-win64\chrome.exe"
options.binary_location = chrome_path
chromedriver_path = r"C:\Users\Mateusz\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"
driver = webdriver.Chrome(service=Service(chromedriver_path), options=options)
wait = WebDriverWait(driver, 10)

username = "usrnm"
password = "pswrd"

def dismiss_alert():
    try:
        alert = driver.switch_to.alert
        alert.dismiss()
    except NoAlertPresentException:
        pass

def click(driver, locator):
    wait.until(EC.presence_of_element_located(locator)).click()

def send(driver, locator, value):
    wait.until(EC.presence_of_element_located(locator)).clear()
    time.sleep(1)
    wait.until(EC.presence_of_element_located(locator)).send_keys(value)

def find(driver, locator):
    return wait.until(EC.presence_of_element_located(locator))

def login(username, password):
    cookies = driver.find_element(By.ID, "ctl00_btnAccetpCookies" )
    cookies.click()
    username_input = wait.until(EC.visibility_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_UserName")))
    password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
    submit_button = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_LoginButton")
   
    username_input.send_keys(username)
    password_input.send_keys(password)
   
    submit_button.click()

def ref_ext(text):
    match = re.search(r'RCV(\d{11})', text)
    if match:
        return match.group(1)
    return None

##LOGIN
driver.get("https://www.e-sad.gov.pl/")
login(username, password)
dismiss_alert()

## FILTER  
driver.get("https://www.e-sad.gov.pl/uzytkownik/mojeDoreczenia.aspx")
dismiss_alert()
time.sleep(3)

##current_date = datetime.datetime.now().strftime('%Y-%m-%d')
##current_date = datetime.datetime.now() - datetime.timedelta(days=7)
##week = current_date.strftime('%Y-%m-%d')
week = '2023-11-01'
send(driver, (By.ID, "ctl00_ContentPlaceHolder1_txtDataOd"), week)
time.sleep(1)
date_2_date = datetime.datetime.now() - datetime.timedelta(days=1)
#d2d = date_2_date.strftime('%Y-%m-%d')
d2d = '2023-12-31'
send(driver, (By.ID, "ctl00_ContentPlaceHolder1_txtDataDo"), d2d)
time.sleep(1)
click(driver, (By.ID, "FiltrujButton"))
time.sleep(2)

select_element = find(driver, (By.ID, "ctl00_ContentPlaceHolder1_dlZakresDanych"))
options = select_element.find_elements(By.TAG_NAME, "option")
dfs = []

for option in options:
    option_value = option.get_attribute("value")
    Select(select_element).select_by_value(option_value)
    print(f'{option_value}')
   
    click(driver, (By.ID, "ctl00_ContentPlaceHolder1_btnEksportuj"))
    time.sleep(2)
    select_element.click()  
    select_element.send_keys(Keys.ARROW_DOWN)
    select_element.send_keys(Keys.RETURN)
    time.sleep(2)

driver.close()
downloads_path = r"C:\Users\Mateusz\Downloads"

xls_files = [file for file in os.listdir(downloads_path) if file.startswith("Doreczenia") and file.endswith(".xls")]
append_files = sorted(xls_files, key=lambda x: os.path.getmtime(os.path.join(downloads_path, x)), reverse=True)[:len(options)]

for xls_file in append_files:
    xls_file_path = os.path.join(downloads_path, xls_file)
    html = pd.read_html(xls_file_path)
    df = html[0]
    print(f'Shape of DF from file', xls_file,':', df.shape)
    df.columns = df.iloc[0]
    df = df[1:]
    dfs.append(df)
    os.remove(xls_file_path)

final_df = pd.concat(dfs, ignore_index=True)
c1 = df.columns[0]
final_df[c1] = final_df[c1].str.extract(r'V(\d+)')
final_df = final_df.rename(columns={c1: 'REFERENCE'})
final_df.to_csv(rf"C:\Users\Mateusz\Desktop\EPUdoreczenia_{datetime.datetime.now().strftime('%Y-%m-%d')}.csv", sep=';', encoding='cp1250',index=False)
print(f'\nHistoria gotowa! Appended {len(append_files)} files')
