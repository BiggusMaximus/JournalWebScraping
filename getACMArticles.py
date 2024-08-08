import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re
import argparse
import pandas as pd
from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from threading import Thread
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import queue
import os, csv, re
from selenium import webdriver
from csv import DictWriter
import winsound
import time
frequency = 1000  # You can adjust this value
duration = 500  # 5000 milliseconds = 5 seconds

# Beep for 5 seconds


global FILE_NAME
# user input arguments
parser = argparse.ArgumentParser()
parser.add_argument('--start', type=int, required=True)
parser.add_argument('--end', type=int, required=True)
parser.add_argument('--number_of_agent', type=int, required=True)

# Webdriver Properties
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--ignore-ssl-errors')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--incognito')
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--start-maximized")
caps = DesiredCapabilities().CHROME
caps["pageLoadStrategy"] = "normal"

# Journal Scrapping Argument
information_keys = ['title', 'link', 'number_of_citation', 'article_type', 'publisher', 'publication_date', 'abstract', 'keyword']
DIGITAL_LIBRARIES_ACCEPTED = ['ieee', 'Springer', 'ACM', 'Elsevier', 'Wiley', 'Sage']
URL_ACM = '''https://dl.acm.org/action/doSearch?fillQuickSearch=false&target=advanced&field1=AllField&text1=%28%22reinforcement+learning%22+OR+%22RL%22%29+AND+%28%22protocol+routing%22+OR+%22routing+strategy%22+OR+%22routing+algorithm%22+OR+%22routing%22%29+AND+%28%22Wireless+Sensor+Network%22+OR+%22WSN%22+OR+%22Sensor+Network%22%29&searchArea%5B0%5D=SeriesKey&operator%5B0%5D=And&text%5B0%5D=&searchArea%5B1%5D=SeriesKey&operator%5B1%5D=And&text%5B1%5D=&EpubDate=&AfterMonth=1&AfterYear=2010&BeforeMonth=&BeforeYear=&pageSize=50&expand=all'''
df = {}



def split_range(_range, parts): #split a range to chunks
    chunk_size = int(len(_range)/parts)
    chunks = [_range[x:x+chunk_size] for x in range(0, len(_range), chunk_size)]
    return chunks

# Collecting title, link, number of citation, article type, and publication date
def getLinkEachPage(links):
    for link in links:
        
        count = 1
    
        driver = webdriver.Chrome(
    executable_path= ChromeDriverManager().install(), options=chrome_options)
        driver.get(link)
        allow_all_cookies_button = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"))
        )

        # Click the 'Allow all cookies' button
        allow_all_cookies_button.click()
        html = driver.page_source

        driver.quit()
        soup = BeautifulSoup(html, 'html.parser')

        # Check all the paper in div body
        count_article = 0
        for article in soup.find_all('li', class_='search__item issue-item-container'):
            df_temp = {}
            for param in information_keys:
                df_temp[param] = []
            title               = article.find('h5', class_='issue-item__title').get_text()
            link_article        = 'https://dl.acm.org' + article.find('h5', class_='issue-item__title').find('a')['href']

            # Get publisher information such as year, article type and publisher
            publication_date   = int(article.find('div', class_='bookPubDate simple-tooltip__block--b').get_text()[-4:])
            article_type       = article.find('div', class_='issue-heading').get_text()
            number_of_citation = int(article.find('span', class_='citation').get_text())

            df_temp['title'].append(title)
            df_temp['link'].append(link_article)
            df_temp['number_of_citation'].append(number_of_citation)
            df_temp['article_type'].append(article_type)
            df_temp['publication_date'].append(publication_date)
            df_temp['publisher'].append('ACM')

    
            link_article = df_temp['link'][len(df_temp['link'])-1]
            try:
                t = np.random.random()*3
                time.sleep(t)
                start_time = time.time()
                driver = webdriver.Chrome(
    executable_path= ChromeDriverManager().install(), options=chrome_options)
                driver.get(link_article)
                allow_all_cookies_button = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"))
                )

                # Click the 'Allow all cookies' button
                allow_all_cookies_button.click()
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                abstract = soup.find("div", id="abstracts").get_text()[len("Abstract"):]
                driver.close()

                df_temp['abstract'].append(abstract)
                df_temp['keyword'].append('none')
                
                count += 1
                print(f"{count*(2/100)*100:.0f}%{"-"*50}{time.time()-start_time} s")
            
            # If error or wont load, try to get
            except:
                driver.close()
                try:
                    retrieve_failed = True
                    for i in range(5):
                        print(f"Trying to retrieve iteration: {i}")
                        if retrieve_failed:
                            t = np.random.random()*3
                            time.sleep(t)
                            start_time = time.time()
                            driver = webdriver.Chrome(
    executable_path= ChromeDriverManager().install(), options=chrome_options)
                            driver.get(link_article)
                            allow_all_cookies_button = WebDriverWait(driver, 10).until(
                            EC.visibility_of_element_located((By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"))
                            )

                            # Click the 'Allow all cookies' button
                            allow_all_cookies_button.click()
                            html = driver.page_source
                            soup = BeautifulSoup(html, 'html.parser')
                            abstract = soup.find("div", id="abstracts").get_text()[len("Abstract"):]
                            driver.close()

                            df_temp['abstract'].append(abstract)
                            df_temp['keyword'].append('none')
                            
                            count += 1

                            print(f"\n{"-"*10} Successfuly retrieved at iteration: {i} {"-"*10}")
                            print(f"{count*(2/100)*100:.0f}%{"-"*50}{time.time()-start_time} ms")
                            


                            retrieve_failed = False
                except:
                    print(f"Failed to retrive at iteration-{i}")

            print(f"Scraping at page: {link[-1]} | Article number: {count_article}")
           
            
            count_article += 1

            try:
                print("\t" + "-"*100)
                df_temp = pd.DataFrame(df_temp)
                df = pd.read_csv(FILE_NAME)
                df = pd.concat([df, df_temp], ignore_index=True)
                df.to_csv(FILE_NAME, index=False)
                print(df.tail(5))
                df_temp = ''
                df = ''
            except:
                print(f"Cant input article numner: {count_article} | title: {title}")

if __name__ == '__main__':
    args = parser.parse_args()
    start = time.time()
    if ((args.end-args.start) == 1):
        print(f"\nParsing ACM Articles single page at: {args.start}") 
        FILE_NAME = f'ACM_page_single_page_{args.start}_only_{np.random.randint(10000, 99999)}.csv'
    else:
        FILE_NAME = f'ACM_page_{args.start}_{args.end}_{np.random.randint(10000, 99999)}.csv'
        print(f"\nParsing ACM Articles from page {args.start}-{args.end}") 

    for param in information_keys:
        df[param] = []

    pd.DataFrame(df).to_csv(FILE_NAME, index=False)

    # Store link for the whole pages
    URL_ACM_LIST = [f'{URL_ACM}&startPage={i-1}' for i in range(args.start, args.end)]
    count = 0
    chunks = split_range(URL_ACM_LIST, args.number_of_agent)
    
    # Creating a thread agent for opening each page.
    thread_workers = []
    for chunk in chunks:
        t = Thread(target=getLinkEachPage, args=(chunk, ))
        thread_workers.append(t)
        t.start()
    
    for t in thread_workers:
        t.join()
    
    for i in range(4):
        winsound.Beep(frequency, duration)
        time.sleep(0.05)
        winsound.Beep(frequency//2, duration)
        

    


