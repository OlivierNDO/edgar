### Import Packages
##############################################################################
import bs4 as bs
import collections
import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import re
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys  
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
from time import sleep
import urllib.request
import urllib.parse

### Web Driver Executables
###############################################################################
# Phantom JS Executable
ph_path = 'C:/tmp/phantomjs.exe'
chr_path = 'C:/tmp/chromedriver3.exe'
ff_path = 'C:/tmp/geckodriver.exe'

# Output File


### Define Functions
###############################################################################

def get_unique_count_dict(lst):
    """
    Generate and return dictionary with counts of unique items in a list
    
    Args:
        lst (list): list for which to generate unique element counts
    """
    key_values = collections.Counter(lst).keys()
    count_values = collections.Counter(lst).values()
    return dict(zip(key_values, count_values))


def semi_rand_intervals(min_time, max_time, n_nums = 1):
    """random intervals of time between requests"""
    return [i for i in np.random.choice(np.linspace(min_time, max_time, 1000), n_nums)]


def random_pause(min_time = 0.5, max_time = 2):
    """random intervals of time between requests"""
    pause_time = np.random.choice(np.linspace(min_time, max_time, 1000), 1)[0]
    time.sleep(pause_time)


def phantom_scrape(web_url, x_path, phan_path = ph_path, min_time = 0.5, max_time = 2):
    # Driver
    driver = webdriver.PhantomJS(executable_path = phan_path)
    driver.get(web_url)
    # Random Sleep Intervals
    random_pause(min_time, max_time)
    tmp_list = []
    for i in driver.find_elements_by_xpath(x_path):
        tmp_list.append(i.text)
        random_pause(min_time, max_time)
    return tmp_list


def get_links_on_page(url, chrome_driver_path = chr_path):
    chrome_options = Options()  
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(chrome_driver_path, options = chrome_options)
    driver.get(url)
    elems = driver.find_elements_by_xpath("//a[@href]")
    links = list(set([e.get_attribute("href") for e in elems]))
    driver.close()
    return links


    
class EdgarRetriever:
    def __init__(self,
                 ticker_symbol,
                 firefox_path,
                 company_search_url = 'https://www.sec.gov/edgar/searchedgar/companysearch.html',
                 search_bar_id = 'company',
                 form_xpath = '//div[(((count(preceding-sibling::*) + 1) = 9) and parent::*)]//span',
                 popup_box_xpath = """//*[contains(concat( " ", @class, " " ), concat( " ", "smart-search-entity-hints", " " ))]""",
                 yyyymmdd_pattern = """(?<!\d)(?:(?:(?:1[6-9]|[2-9]\d)?\d{2})(?:(?:(?:0[13578]|1[02])31)|(?:(?:0[1,3-9]|1[0-2])(?:29|30)))|(?:(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00)))0229)|(?:(?:1[6-9]|[2-9]\d)?\d{2})(?:(?:0?[1-9])|(?:1[0-2]))(?:0?[1-9]|1\d|2[0-8]))(?!\d).htm"""):
        """
        Retrieve financial filing information for publicly traded companies governed
        by the Securities and Exchange Commission (SEC) from their EDGAR information system
        Args:
            ticker_symbol (str): string representing publically traded company ticker symbol
            firefox_path (str): path to Firefox driver on local machine
            company_search_url (str): the starting URL of the SEC's company search website
        """
        self.ticker_symbol = ticker_symbol
        self.firefox_path = firefox_path
        self.company_search_url = company_search_url
        self.search_bar_id = search_bar_id
        self.form_xpath = form_xpath
        self.popup_box_xpath = popup_box_xpath
        self.yyyymmdd_pattern = yyyymmdd_pattern
    
    def get_10k_8k_urls(self):
        # Get to company-specific page via CIK number
        driver = webdriver.Firefox(executable_path = self.firefox_path)
        driver.get(self.company_search_url)
        ticker_search_bar = driver.find_element_by_id(self.search_bar_id)
        ticker_search_bar.send_keys(self.ticker_symbol)
        popup_box = driver.find_element_by_xpath(self.popup_box_xpath)
        random_pause()
        cik_number = popup_box.text.split('CIK')[1].split('\n')[0].strip().strip('0')
        cik_url = f'https://www.sec.gov/edgar/browse/?CIK={cik_number}&owner=exclude'
        driver.get(cik_url)
        random_pause()
        
        # Get 10-Q and 8-K Urls
        urls_in_page = list(set([x.get_attribute("href") for x in driver.find_elements_by_xpath("//a[@href]")]))
        urls_10q_8k = []
        for i, uip in enumerate(urls_in_page):
            try:
                date_pattern = re.search(self.yyyymmdd_pattern, uip).group(0)
                ticker_lower = self.ticker_symbol.lower()
                ticker_date_pattern = f'{ticker_lower}-{date_pattern}'
                if ticker_date_pattern in uip: 
                    urls_10q_8k.append(uip)
            except:
                pass
                
        # Separate 8-K, 10-Q URLs
        urls_10q = []
        urls_8k = []
        urls_10k = []
        for url in urls_10q_8k:
            html_url = url.replace('/ix?doc=', '')
            try:
                random_pause()
                driver.get(html_url)
                random_pause()
                
                form = driver.find_element_by_xpath(self.form_xpath).text
                if form == 'FORM 10-Q':
                    urls_10q.append(html_url)
                elif form == 'FORM 10-K':
                    urls_10k.append(html_url)
                elif form == 'FORM 8-K':
                    urls_8k.append(html_url)
                else:
                    pass
            except:
                print(f'Invalid URL: {html_url}')
                        
        driver.close()
        return urls_10q, urls_8k, urls_10k
    
    
    
    
edgar_mtch = EdgarRetriever(ticker_symbol = 'AAPL', firefox_path = ff_path)

urls_10q, urls_8k, urls_10k = edgar_mtch.get_10k_8k_urls()    
    

    


url = 'https://www.sec.gov/Archives/edgar/data/0000320193/000032019321000056/aapl-20210327.htm'
form_xpath = '//div[(((count(preceding-sibling::*) + 1) = 9) and parent::*)]//span'

driver = webdriver.Firefox(executable_path = ff_path)
driver.get(url)
form = driver.find_element_by_xpath(form_xpath).text
















url = 'https://www.sec.gov/edgar/searchedgar/companysearch.html'
ticker_symbol = 'AAPL'

driver = webdriver.Firefox(executable_path = ff_path)
driver.get(url)

ticker_search_bar = driver.find_element_by_id('company')
ticker_search_bar.send_keys(ticker_symbol)

popup_box = driver.find_element_by_xpath("""//*[contains(concat( " ", @class, " " ), concat( " ", "smart-search-entity-hints", " " ))]""")
random_pause()
cik_number = popup_box.text.split('CIK')[1].split('\n')[0].strip().strip('0')
cik_url = f'https://www.sec.gov/edgar/browse/?CIK={cik_number}&owner=exclude'
driver.get(cik_url)


# Expand 10-K, 10-Q Dropdown
#driver.find_element_by_xpath("""//*[contains(concat( " ", @class, " " ), concat( " ", "card", " " )) and (((count(preceding-sibling::*) + 1) = 3) and parent::*)]//*[contains(concat( " ", @class, " " ), concat( " ", "collapsible", " " ))]""").click()
random_pause()

# Get Links on Page
urls_in_page = list(set([x.get_attribute("href") for x in driver.find_elements_by_xpath("//a[@href]")]))


# Get 10-Q, 8-K Urls
urls_10q_8k = []

yyyymmdd_pattern = """(?<!\d)(?:(?:(?:1[6-9]|[2-9]\d)?\d{2})(?:(?:(?:0[13578]|1[02])31)|(?:(?:0[1,3-9]|1[0-2])(?:29|30)))|(?:(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00)))0229)|(?:(?:1[6-9]|[2-9]\d)?\d{2})(?:(?:0?[1-9])|(?:1[0-2]))(?:0?[1-9]|1\d|2[0-8]))(?!\d).htm"""

for i, uip in enumerate(urls_in_page):
    try:
        date_pattern = re.search(yyyymmdd_pattern, uip).group(0)
        ticker_date_pattern = f'{ticker_symbol.lower()}-{date_pattern}'
        if ticker_date_pattern in uip: 
            urls_10q_8k.append(uip)
    except:
        pass
    
# Separate 8-K, 10-Q URLs
urls_10q = []
urls_8k = []
for url in urls_10q_8k:
    html_url = url.replace('/ix?doc=', '')
    try:
        random_pause()
        driver.get(html_url)
        random_pause()
        pg_source = driver.page_source
        #if ('Consolidated Financial Statements' in pg_source) & ('TOTAL ASSETS' in pg_source):
        if ('Form 10-Q' in pg_source) & ('Consolidated Financial Statements' in pg_source):
            urls_10q.append(html_url)
        else:
            urls_8k.append(html_url)
    except:
        print(f'Invalid URL: {html_url}')
    
    
    
'https://www.sec.gov/Archives/edgar/data/0000320193/000032019321000010/aapl-20201226.htm' in urls_10q_8k 
'https://www.sec.gov/Archives/edgar/data/0000320193/000032019321000010/aapl-20201226.htm' in urls_in_page
    
    

    
    
    
driver.get('https://www.sec.gov//Archives/edgar/data/0000320193/000032019321000010/aapl-20201226.htm')  
    
pg_source = driver.page_source

'Form 10-Q' in pg_source
    
driver.close()
    
    
    
    