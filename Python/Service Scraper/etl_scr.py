import os
import re
import time
import datetime
import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoAlertPresentException, StaleElementReferenceException, NoSuchElementException, ElementClickInterceptedException, TimeoutException

# Configuration
username = "ursnm"
password = "pswrd"
chrome_path = r"C:\Users\Mateusz\Downloads\chrome-win64\chrome-win64\chrome.exe"
chromedriver_path = r"C:\Users\Mateusz\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"
downloads_path = r"C:\Users\Mateusz\Downloads"
pdf_path = r"C:\Users\Mateusz\Documents\epu_arch"

# Set up Chrome options
options = Options()
options.add_argument("--headless")
options.binary_location = chrome_path
options.add_experimental_option("prefs", {
    "plugins.always_open_pdf_externally": True,
    "download.default_directory": pdf_path
})

# Initialize WebDriver
service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 30)

def dismiss_alert():
    try:
        alert = driver.switch_to.alert
        alert.dismiss()
    except NoAlertPresentException:
        pass

def click(driver, locator):
    try:
        wait.until(EC.presence_of_element_located(locator)).click()
    except ElementClickInterceptedException:
        time.sleep(20)
        wait.until(EC.presence_of_element_located(locator)).click()

def send(driver, locator, value):
    wait.until(EC.presence_of_element_located(locator)).clear()
    time.sleep(1)
    wait.until(EC.presence_of_element_located(locator)).send_keys(value)

def find(driver, locator):
    return wait.until(EC.presence_of_element_located(locator))

def login(username, password):
    click(driver, (By.ID, "ctl00_btnAccetpCookies"))
    send(driver, (By.ID, "ctl00_ContentPlaceHolder1_UserName"), username)
    send(driver, (By.CSS_SELECTOR, "input[type='password']"), password)
    click(driver, (By.ID, "ctl00_ContentPlaceHolder1_LoginButton"))

def get(driver):
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    rows = soup.find_all('tr', class_=['even', 'odd'])
    if rows:
        sygnatura_td = rows[0].find_all('td')[2]
        return sygnatura_td.get_text(strip=True)
    return None

def etl():
    # Login
    driver.get("https://www.e-sad.gov.pl/")
    print("Logging...")
    login(username, password)
    dismiss_alert()

    # Extract data
    driver.get("https://www.e-sad.gov.pl/uzytkownik/mojeDoreczenia.aspx")
    dismiss_alert()
    time.sleep(3)

    # Set date range     
    current_date = datetime.datetime.now() - datetime.timedelta(days=7)
    week = current_date.strftime('%Y-%m-%d')
    send(driver, (By.ID, "ctl00_ContentPlaceHolder1_txtDataOd"), week)
    time.sleep(1)
    date_2_date = datetime.datetime.now() - datetime.timedelta(days=1)
    d2d = date_2_date.strftime('%Y-%m-%d')
    send(driver, (By.ID, "ctl00_ContentPlaceHolder1_txtDataDo"), d2d)
    time.sleep(1)
    click(driver, (By.ID, "FiltrujButton"))
    time.sleep(2)
    try:
        select_element = find(driver, (By.ID, "ctl00_ContentPlaceHolder1_dlZakresDanych"))
    except TimeoutException:
        print(f"No data. End.")
        driver.quit()
        return False
        
    # Extract data for each option     
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
    
    # Append
    downloads_path = r"C:\Users\Mateusz\Downloads"
    xls_files = [file for file in os.listdir(pdf_path) if file.startswith("Doreczenia") and file.endswith(".xls")]
    append_files = sorted(xls_files, key=lambda x: os.path.getmtime(os.path.join(pdf_path, x)), reverse=True)[:len(options)]

    for xls_file in append_files:
        xls_file_path = os.path.join(pdf_path, xls_file)
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
    final_df.to_csv(rf"C:\Users\Mateusz\Desktop\EPUdoreczenia_{datetime.datetime.now().strftime('%Y-%m-%d')}.csv", sep=';', encoding='cp1250', index=False)

    # Download PDFs
    existing_files = [file for file in os.listdir(pdf_path) if file.endswith('.pdf')]
    existing_name = set(os.listdir(pdf_path))
    df = final_df.drop_duplicates(subset=['REFERENCE']).reset_index(drop=True)
    time.sleep(1)
    driver.refresh()
    dismiss_alert()
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    span = soup.find('span', class_='form_check')
    checkbox = span.find('input', id='ctl00_ContentPlaceHolder1_chkFiltrPoDacie')
    time.sleep(1)
    if checkbox and checkbox.has_attr('checked') and checkbox['checked'] == 'checked':
        selenium_checkbox = find(driver, (By.ID, 'ctl00_ContentPlaceHolder1_chkFiltrPoDacie'))
        if selenium_checkbox.is_selected():
            try:
                time.sleep(1)
                click(driver, (By.ID, 'ctl00_ContentPlaceHolder1_chkFiltrPoDacie'))
            except ElementClickInterceptedException:
                time.sleep(20)
                click(driver, (By.ID, 'ctl00_ContentPlaceHolder1_chkFiltrPoDacie'))

    for _, row in tqdm(df.iterrows(), total=len(df)):
        syg_0 = get(driver)
        ref = str(row['REFERENCE'])
        time.sleep(1)
        send(driver, (By.ID, "ctl00_ContentPlaceHolder1_tbOznaczeniePowoda"), ref)
        time.sleep(1)
        try:
            click(driver, (By.ID, "FiltrujButton"))
        except ElementClickInterceptedException:
            time.sleep(20)
            click(driver, (By.ID, "FiltrujButton"))

        try:
            wait.until(lambda x: get(x) != syg_0)
        except TimeoutException:
            continue

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        rows = soup.find_all('tr', class_=['even', 'odd'])
        
        for i, row in enumerate(rows, 1):
            td_name = row.find_all('td')[1]
            input_button = td_name.find('input', {'type': 'image'})
            sygnatura_td = row.find_all('td')[2]
            sygnatura = sygnatura_td.get_text(strip=True).replace('/', '_')
            opis_td = row.find_all('td')[5]
            opis = opis_td.get_text(strip=True).replace('/', '.').split("- ", 1)[-1]
            if len(ref) > 9:
                ref = ref[:-2] + "_" + ref[-2:]
            file_name = f"{ref} - {sygnatura} - {opis}.pdf"
            
            if file_name in existing_name:
                continue
            
            if input_button and 'name' in input_button.attrs:
                button_name = input_button['name']
                button_xpath = f"//input[@name='{button_name}']"
                time.sleep(2)
                click(driver, (By.XPATH, button_xpath))
                time.sleep(2)
                files = [f for f in os.listdir(pdf_path) if f.endswith('.pdf') and f.startswith('plik')]
                
                if files:
                    og = os.path.join(pdf_path, files[0])
                    file_path = os.path.join(pdf_path, file_name)
                    i = 0
                    while True:
                        try:
                            os.rename(og, file_path)
                            existing_name.add(file_name)
                            break
                        except FileExistsError:
                            i += 1
                            file_name = f"{ref} - {sygnatura}_{i} - {opis}.pdf"
                if files:
                    og = os.path.join(pdf_path, files[0])
                    file_path = os.path.join(pdf_path, file_name)
                    i = 0
                    while os.path.exists(file_path):
                        i += 1
                        file_name = f"{ref} - {sygnatura}_{i} - {opis}.pdf"
                        file_path = os.path.join(pdf_path, file_name)
                    os.rename(og, file_path)
                    existing_name.add(file_name)
                    
    driver.close()
    driver.quit()
    print('ETL process completed!')

if __name__ == "__main__":
    etl()
