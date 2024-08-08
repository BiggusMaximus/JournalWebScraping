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
# chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--start-maximized")
caps = DesiredCapabilities().CHROME
caps["pageLoadStrategy"] = "normal"

# Journal Scrapping Argument
information_keys = ['title', 'link', 'number_of_citation', 'article_type', 'publisher', 'publication_date', 'abstract', 'keyword']
DIGITAL_LIBRARIES_ACCEPTED = ['ieee', 'Springer', 'ACM', 'Elsevier', 'Wiley', 'Sage']

 
df = {}

def split_range(_range, parts): #split a range to chunks
    chunk_size = int(len(_range)/parts)
    chunks = [_range[x:x+chunk_size] for x in range(0, len(_range), chunk_size)]
    return chunks

def getAllArticles(links):
    soups = []
    for link in links:
        try:
            count = 1
            driver = webdriver.Chrome(
                executable_path= ChromeDriverManager().install(), 
                options=chrome_options
            )
            driver.get(link)
            allow_cookies_button = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located(
                    (
                        By.CSS_SELECTOR, "button[data-cc-action='accept']"
                    )
                )
            )
            allow_cookies_button.click()
            html = driver.page_source
            driver.close()
            soups.append(BeautifulSoup(html, 'html.parser'))
        except:
            driver.close()
            retrieve_failed = True
            i = 1
            while ((retrieve_failed) and i<4):
                try:
                    print(f"\nTrying to retrieve all articles at iteration: {i}\n")
                    driver = webdriver.Chrome(
                        executable_path= ChromeDriverManager().install(), 
                        options=chrome_options
                    )
                    driver.get(link)
                    allow_cookies_button = WebDriverWait(driver, 10).until(
                        EC.visibility_of_element_located(
                            (
                                By.CSS_SELECTOR, "button[data-cc-action='accept']"
                            )
                        )
                    )
                    allow_cookies_button.click()
                    html = driver.page_source
                    driver.close()
                    retrieve_failed = False
                    print(f"Successfully retrieve all articles at iteration: {i}")
                    soups.append(BeautifulSoup(html, 'html.parser'))
                except:
                    driver.close()
                    print(f"Fail to retrieve all articles at iteration: {i}")
                
                i+=1
    return soups

def getInfoArticle(soups):
    if len(soups) == 0:
        print(f"Failed to retrieve anything")
        return None
    else:
        for soup in soups:
            count_article = 0
            for article in soup.find('ol', id='results-list').find_all('li'):
                t = np.random.random()*3
                time.sleep(t)
                start_time = time.time()

                title = article.find('h2').get_text()[1:-1]
                article_type = article.find('p', class_='content-type').get_text(strip=True)
                link_article = 'https://link.springer.com' + article.find('h2').find('a')['href']
                publication_date   = int(article.find('span', class_='year').get_text()[-5:-1])

                try:
                    count = 1
                    driver = webdriver.Chrome(
                        executable_path= ChromeDriverManager().install(), 
                        options=chrome_options
                    )
                    driver.get(link_article)
                    allow_cookies_button = WebDriverWait(driver, 10).until(
                        EC.visibility_of_element_located(
                            (
                                By.CSS_SELECTOR, "button[data-cc-action='accept']"
                            )
                        )
                    )
                    allow_cookies_button.click()

                    html = driver.page_source
                    soup = BeautifulSoup(html, 'html.parser')
                    driver.close()
                except:
                    driver.close()
                    retrieve_failed = True
                    i = 1
                    while ((retrieve_failed) and i<4):
                        try:
                            print(f"\nTrying to retrieve iteration: {i}\n")
                            driver = webdriver.Chrome(
                                executable_path= ChromeDriverManager().install(), 
                                options=chrome_options
                            )
                            driver.get(link_article)
                            allow_cookies_button = WebDriverWait(driver, 10).until(
                                EC.visibility_of_element_located(
                                    (
                                        By.CSS_SELECTOR, "button[data-cc-action='accept']"
                                    )
                                )
                            )
                            allow_cookies_button.click()

                            html = driver.page_source
                            soup = BeautifulSoup(html, 'html.parser')
                            driver.close()
                            retrieve_failed = False
                            print(f"Successfully retrieve at itration: {i}")
                            
                        except:
                            driver.close()
                            print(f"Fail to retrieve at iteration: {i}")
                        
                        i+=1


                try:
                    number_of_citation = soup.find_all('p', class_="app-article-metrics-bar__count")
                    if number_of_citation != None:
                        if (len(number_of_citation) > 1):
                            number_of_citation = number_of_citation[1].get_text(strip=True)
                            if 'Citations' in number_of_citation:
                                number_of_citation = int(re.search(r'\d+', number_of_citation).group())
                        else:
                            number_of_citation = 'none'
                    else:
                        number_of_citation = 'none'
                        
                    abstract = soup.find('div', class_="c-article-section__content").get_text()
                    keyword = soup.find('ul', class_="c-article-subject-list").find_all('li')
                    keyword = [f"{i.get_text()}" for i in keyword]
                    keyword = ','.join(keyword)
                    df_temp = {}
                    for param in information_keys:
                        df_temp[param] = []

                    df_temp['title'].append(title)
                    df_temp['link'].append(link_article)
                    df_temp['number_of_citation'].append(number_of_citation)
                    df_temp['article_type'].append(article_type)
                    df_temp['publication_date'].append(publication_date)
                    df_temp['publisher'].append('Springer')
                    df_temp['abstract'].append(abstract)
                    df_temp['keyword'].append(keyword)
                    print("\t" + "-"*100)
                    df_temp = pd.DataFrame(df_temp)
                    df = pd.read_csv(FILE_NAME)
                    count = len(df.index)
                    df = pd.concat([df, df_temp], ignore_index=True)
                    df.to_csv(FILE_NAME, index=False)
                    print(df.tail(5))
                    df_temp = ''
                    df = ''
                    print(f"{count*(5/100)*100:.0f}%{"-"*50}{time.time()-start_time}")
                except:
                    print(f"Cant input article numner: {count_article} | title: {title}")
                


def main(links):
    soup = getAllArticles(links)
    getInfoArticle(soup)
    for i in range(4):
        winsound.Beep(frequency, duration)
        time.sleep(0.05)
        winsound.Beep(frequency//2, duration)

if __name__ == '__main__':
    args = parser.parse_args()
    start = time.time()
    if ((args.end-args.start) == 1):
        print(f"\nParsing Springer Articles single page at: {args.start}") 
        FILE_NAME = f'Springer_page_single_page_{args.start}_only_{np.random.randint(10000, 99999)}.csv'
    else:
        FILE_NAME = f'Springer_page_{args.start}_{args.end}_{np.random.randint(10000, 99999)}.csv'
        print(f"\nParsing Springer Articles from page {args.start}-{args.end}")
    
    for param in information_keys:
        df[param] = []

    pd.DataFrame(df).to_csv(FILE_NAME, index=False)
    URL_SPRINGER_LIST = [
        f'https://link.springer.com/search/page/{i}?query=%28%22reinforcement+learning%22+OR+%22RL%22%29+AND+%28%22protocol+routing%22+OR+%22routing+strategy%22+OR+%22routing+algorithm%22+OR+%22routing%22%29+AND+%28%22Wireless+Sensor+Network%22+OR+%22WSN%22+OR+%22Sensor+Network%22%29&facet-content-type=%22Article%22' for i in range(args.start, args.end)]

    count = 0
    chunks = split_range(URL_SPRINGER_LIST, args.number_of_agent)
    
    # Creating a thread agent for opening each page.
    thread_workers = []
    for chunk in chunks:
        t = Thread(target=main, args=(chunk, ))
        thread_workers.append(t)
        t.start()
    
    for t in thread_workers:
        t.join()
    
    