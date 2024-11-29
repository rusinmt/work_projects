import scrapy
from scrapy.http import FormRequest
from scrapy.crawler import CrawlerProcess
import pandas as pd
from openpyxl.workbook import Workbook
import json
from io import BytesIO
from datetime import datetime, timedelta
import os
import shutil
from datetime import datetime, timedelta
import pytz
import psycopg2
import paramiko
import socket

pl_holidays = [
    "2025-01-01",  # New Year's Day
    "2025-01-06",  # Epiphany
    "2025-04-21",  # Easter Monday
    "2025-05-01",  # Labor Day
    "2025-05-03",  # Constitution Day
    "2025-06-19",  # Corpus Christi
    "2025-08-15",  # Assumption of Mary
    "2025-11-01",  # All Saints' Day
    "2025-11-11",  # Independence Day
    "2025-12-25",  # Christmas Day
    "2025-12-26",  # Second Day of Christmas
]

class ESADSpider(scrapy.Spider):
    name = 'esad_spider'
    start_urls = ['https://www.e-sad.gov.pl/']
        
    def __init__(self, username=None, password=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.username = "user"
        self.password = "pass"

        now_cet = datetime.now(pytz.timezone('CET'))
        if now_cet.strftime('%Y-%m-%d') in pl_holidays:
            raise Exception("HoliDAY_OFF!")
        elif now_cet.weekday() in range(0, 5):
            self.start_date = now_cet.strftime('%Y-%m-%d')
            self.end_date = now_cet.strftime('%Y-%m-%d')
        elif now_cet.weekday() in range(5,7):
            raise Exception("Waiting torugh the weekend.")
            
        self.temp_dir = os.path.join(os.getcwd(), 'temp_folder')
        os.makedirs(self.temp_dir, exist_ok=True)

    def parse(self, response):
        return FormRequest.from_response(
            response,
            formdata={'ctl00$btnAccetpCookies': 'Akceptuję'},
            callback=self.login
        )

    def login(self, response):
        return FormRequest.from_response(
            response,
            formdata={
                'ctl00$ContentPlaceHolder1$UserName': self.username,
                'ctl00$ContentPlaceHolder1$Password': self.password,
                'ctl00$ContentPlaceHolder1$LoginButton': 'Zaloguj się'
            },
            callback=self.after_login
        )

    def after_login(self, response):
        if "Moje doręczenia" in response.text:
            self.logger.info("Login successful!")
            return scrapy.Request(
                'https://www.e-sad.gov.pl/uzytkownik/mojeDoreczenia.aspx',
                callback=self.parse_doreczenia
            )
        else:
            self.logger.error("Login failed!")
            return

    def parse_doreczenia(self, response):
        return FormRequest.from_response(
            response,
            formdata={
                'ctl00$ContentPlaceHolder1$txtDataOd': self.start_date,
                'ctl00$ContentPlaceHolder1$txtDataDo': self.end_date,
                'ctl00$ContentPlaceHolder1$btnSzukaj': 'Szukaj'
            },
            callback=self.filter_results
        )

    def filter_results(self, response):
        self.logger.info("Applying filter...")
        return FormRequest.from_response(
            response,
            formdata={
                '__EVENTTARGET': 'ctl00$ContentPlaceHolder1$FiltrujButton',
                '__EVENTARGUMENT': '',
            },
            callback=self.export_results
        )

    def export_results(self, response):
        self.logger.info("Exporting results...")
        return FormRequest.from_response(
            response,
            formdata={
                '__EVENTTARGET': 'ctl00$ContentPlaceHolder1$btnEksportuj',
                '__EVENTARGUMENT': '',
            },
            callback=self.df_read,
            dont_filter=True
        )

    def df_read(self, response):
        ref = None
        try:
            tables = pd.read_html(BytesIO(response.body))
            if tables:
                df = tables[0]
                self.logger.info(f"Shape: {df.shape}")
                df = df.dropna(subset=[0])
                df = df[df[df.columns[4]].astype(str).str.contains('Zarządzenie o wezwaniu do uzupełnienia adresu', case=False, na=False)]
                df = df[df.columns[0]].astype(str).str.extract(r'V(\d+)')
                df['ref'] = df[df.columns[0]].astype(str).str[:9]
                ref = tuple(df['ref'])
                with open(os.path.join(os.path.join(os.getcwd(), 'temp_folder'), 'ref_tuple.json'), 'w') as f:
                    json.dump(str(ref), f)
                return ref
            else:
                self.logger.error("No tables found in the HTML response.")
                return None
        except Exception as e:
            self.logger.error(f"Error : {e}")
            return None
        finally:
            if not ref:
                print("No deliveries")

def run_scraper(username, password):
    settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'ROBOTSTXT_OBEY': False,
        'LOG_LEVEL': 'INFO',
        'DOWNLOAD_DELAY': 1,
        'REQUEST_FINGERPRINTER_IMPLEMENTATION': '2.7'
    }

    process = CrawlerProcess(settings)
    process.crawl(ESADSpider, username=username, password=password)
    process.start()

def read_db():
    with open(os.path.join(os.path.join(os.getcwd(), 'temp_folder'), 'ref_tuple.json'), 'r') as f:
        ref_str = json.load(f)      
    ref = eval(ref_str)
    
    conn = psycopg2.connect(
        dbname='poland',
        user='user',
        password='pass',
        host='192.111.00.11',
        port='2222'
    )

    cur = conn.cursor()
    query = f'''
    SELECT
        INITCAP(SPLIT_PART(k.name,' ', 1)) AS "IMIĘ",
        CASE WHEN ARRAY_LENGTH(STRING_TO_ARRAY(k.name, ' '), 1) > 2
            THEN SPLIT_PART(k.name, ' ', 3)
            ELSE SPLIT_PART(k.name, ' ', 2)
        END AS "NAZWISKO",
        CASE WHEN LENGTH(pesel) = 11 THEN pesel ELSE NULL END AS "PESEL",
        'adres' AS "Co pozyskać",
        (SELECT INITCAP(street) FROM adress WHERE client_id=k.counter ORDER BY updated_at DESC LIMIT 1) AS "ulica",
        (SELECT house FROM adress WHERE client_id=k.counter ORDER BY updated_at DESC LIMIT 1) AS "nr domu",
        (SELECT apt FROM adress WHERE client_id=k.counter ORDER BY updated_at DESC LIMIT 1) AS "nr lokalu",
        (SELECT postal FROM adress WHERE client_id=k.counter ORDER BY updated_at DESC LIMIT 1) AS "kod pocztowy",
        (SELECT INITCAP(city) FROM adress WHERE client_id=k.counter ORDER BY updated_at DESC LIMIT 1) AS "miejscowość",
        TO_CHAR(NOW() + '6 days', 'yyyy-mm-dd') AS "Termin"
    FROM main l
    JOIN cliendid k ON l.debtor = k.counter
    WHERE l.id IN %s
    AND k.type = 'P'
    '''
    cur.execute(query, (ref,))
    result = cur.fetchall()
    cur.close()
    conn.close()

    df2 = pd.DataFrame(result, columns=[desc[0] for desc in cur.description])
    date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d') 
    excel_filename = f'excel_{date}.xlsx'
    ## Excel Temp File
    excel_path = os.path.join(os.path.join(os.getcwd(), 'temp_folder'), excel_filename)
    df2.to_excel(excel_path, index=False)

    ## SFTP
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    sftp_path = f'/OUT/{excel_filename}'

    try:
        ssh.connect(
            hostname = '195.000.11.00', 
            username = 'user', 
            password = r"pass" ,
            port = 11111
        )
        sftp = ssh.open_sftp()
        sftp.put(excel_path, os.path.join(sftp_path))
        print(f"File copied successfully to {sftp_path}")
        
    except FileNotFoundError as e:
        print(f"FileNotFoundError: {e}")
        print(f"{str(e)}")
    except IOError as e:
        print(f"IOError: {e}")
        print(f"{str(e)}")
    except Exception as e:
        print(f"Error type: {type(e)}")
        print(f"Error copying file: {e}")
        print(f"{str(e)}")
    finally:
        sftp.close()
        ssh.close()
        shutil.rmtree(os.path.join(os.getcwd(), 'temp_folder'))
    
    
if __name__ == "__main__":
    run_scraper(username='username', password='password')
    read_db()
