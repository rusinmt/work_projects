from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
import time
 
options = Options()
options.add_argument("--headless")
 
chrome_path = r"C:\Users\Mateusz\Downloads\chrome-win64\chrome-win64\chrome.exe"
options.binary_location = chrome_path
chromedriver_path = r"C:\Users\Mateusz\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"
driver = webdriver.Chrome(service=Service(chromedriver_path), options=options)
wait = WebDriverWait(driver, 10)

username = usrnm
password = pswrd
 
def click(driver, locator):
    wait.until(EC.presence_of_element_located(locator)).click()
 
def send(driver, locator, value):
    wait.until(EC.presence_of_element_located(locator)).clear()
    driver.implicitly_wait(0.5)
    wait.until(EC.presence_of_element_located(locator)).send_keys(value)
 
def dropdown(driver, locator, value):
    wait.until(EC.presence_of_element_located(locator)).send_keys(value)
 
def find(driver, locator):
    return wait.until(EC.presence_of_element_located(locator))
 
def login(username, password):
    url = "https://portal.wroclaw.sa.gov.pl/#/login"
    driver.get(url)
    send(driver, (By.ID, "username"), username)
    send(driver, (By.ID, "password"), password)
    click(driver, (By.XPATH, "//button[@class='btn btn-primary']/span[text()='Zaloguj']"))
 
def nowa_apelacja():
    click(driver,(By.XPATH, "//mat-select[@placeholder='Wybierz apelację']"))
    dropdown(driver, (By.XPATH, "//mat-select[@placeholder='Wybierz apelację']"), Keys.ARROW_UP)
    dropdown(driver, (By.XPATH, "//mat-select[@placeholder='Wybierz apelację']"), Keys.ENTER)
    driver.get('https://portal.wroclaw.sa.gov.pl/#/mojprofil/subkonta')
    click(driver, (By.XPATH, "//button[@class='btn btn-info ng-star-inserted']"))
 
def filtry():
    select_element = find(driver, (By.ID, "itemsPerPage"))
    Select(select_element).select_by_value("200")
    click(driver, (By.XPATH, "//button[@class='sort-position']/span[text()='przyznany dostęp']"))
   
def clicker():
    if driver.find_elements(By.XPATH, "//button[@class='btn btn-success float-right ng-star-inserted' and text()='Przyznaj dostęp']"):
        greens = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//button[@class='btn btn-success float-right ng-star-inserted' and text()='Przyznaj dostęp']")))
        for _ in greens:
            click(driver, (By.XPATH, "//button[@class='btn btn-success float-right ng-star-inserted' and text()='Przyznaj dostęp']"))
            time.sleep(3)
    else:
        pass
 
#login
login(username, password)
 
#close popup
if find(driver, (By.XPATH, "//span[@class='ui-dialog-title ng-tns-c1-0 ng-star-inserted']")):
    click(driver, (By.XPATH, "//span[@class='pi pi-fw pi-times']"))
else:
    pass
 
driver.get('https://portal.wroclaw.sa.gov.pl/#/mojprofil/subkonta')
 
#first appeal
click(driver, (By.XPATH, "//button[@class='btn btn-info ng-star-inserted']")) ##menu apelacji
filtry()
driver.implicitly_wait(1)
clicker()
 
for i in range(11):
    nowa_apelacja()
    filtry()
    driver.implicitly_wait(1)
    clicker()
 
driver.quit()
print('Ready!')
