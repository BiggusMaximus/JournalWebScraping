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
chrome_options.add_argument("--start-maximized")
caps = DesiredCapabilities().CHROME
caps["pageLoadStrategy"] = "normal"

# Journal Scrapping Argument
information_keys = ['title', 'link', 'number_of_citation', 'article_type', 'publisher', 'publication_date', 'abstract', 'keyword']
DIGITAL_LIBRARIES_ACCEPTED = ['ieee', 'Springer', 'ACM', 'Elsevier', 'Wiley', 'Sage']
URL_IEEE = '''https://ieeexplore.ieee.org/search/searchresult.jsp?queryText=(reinforcement%20learning%20OR%20RL)%20AND%20(protocol%20routing%20OR%20routing%20strategy%20OR%20routing%20algorithm%20OR%20routing)%20AND%20(Wireless%20Sensor%20Network%20OR%20WSN%20OR%20Sensor%20Network)&highlight=true&returnFacets=ALL&returnType=SEARCH&matchPubs=true&ranges=2010_2024_Year'''
df = {}



def split_range(_range, parts): #split a range to chunks
    chunk_size = int(len(_range)/parts)
    chunks = [_range[x:x+chunk_size] for x in range(0, len(_range), chunk_size)]
    return chunks

# Collecting title, link, number of citation, article type, and publication date
def getLinkEachPage(links):
    for link in links:
        print(f"Scraping at page: {link[-1]}")
        count = 1
        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(link)
            article_bodies = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, "List-results-items"))
            )
            html = driver.page_source
            driver.quit()
            soup = BeautifulSoup(html, 'html.parser')
            df_temp = {}
            for param in information_keys:
                df_temp[param] = []

            # Check all the paper in div body
            for article in soup.find_all('div', class_='List-results-items'):
                title               = article.find('h3', class_='text-md-md-lh').get_text()
                link_article        = 'https://ieeexplore.ieee.org' + article.find('h3', class_='text-md-md-lh').find('a')['href']

                # Get publisher information such as year, article type and publisher
                publisher_information   = article.find('div', class_='publisher-info-container').find_all('span')
                publisher_information   = [i.get_text() for i in publisher_information if '|' not in i.get_text()]
                publication_date        = publisher_information[0][-4:]
                article_type            = 'other'

                for i in publisher_information:
                    if ((i == 'Conference Paper') or (i == 'Journal Article')):
                        article_type = i
                
                citations = [citation.get_text() for citation in article.find('div', class_='description text-base-md-lh').find_all('span')]

                for citation in citations:
                    if 'Papers' in citation:
                        number_of_citation = int(re.search(r'\d+', citation).group())
                    else:
                        number_of_citation = 0
                
                df_temp['title'].append(title)
                df_temp['link'].append(link_article)
                df_temp['number_of_citation'].append(number_of_citation)
                df_temp['article_type'].append(article_type)
                df_temp['publication_date'].append(publication_date)
                df_temp['publisher'].append('IEEE')

            
            for link_article in df_temp['link']:
                driver = webdriver.Chrome(options=chrome_options)
                driver.get(link_article)
                title = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="xplMainContentLandmark"]/div/xpl-document-details/div/div[1]/section[2]/div/xpl-document-header/section/div[2]/div/div/div[1]/div/div[1]/h1'))
                )
                button = driver.find_element(By.ID, 'keywords')
                driver.execute_script("arguments[0].scrollIntoView(true);", button)
                button.click()
                button = WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="keywords"]/xpl-document-keyword-list/section/div/ul/li[1]/strong')))

                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')

                abstract = soup.find_all('div', class_='u-mb-1')
                abstract = abstract[1].get_text()[len('Abstract:')+1:]
                keyword = soup.find_all('li', class_='doc-keywords-list-item')[1]
                keyword = keyword.get_text()[len("Index Terms"):]

                df_temp['abstract'].append(abstract)
                df_temp['keyword'].append(keyword)
                print(f"\tAt page {link[-1]} Paper found: {count} - {title.text}")
                

                driver.close()
                count += 1

            df_temp = pd.DataFrame(df_temp)
            df = pd.read_csv(FILE_NAME)
            df = pd.concat([df, df_temp], ignore_index=True)
            df.to_csv(FILE_NAME, index=False)
            print(df.tail(5))

        except Exception as e:
            print(f"Error at page: {link[-1]} at paper: {count} \n {e}")

if __name__ == '__main__':
    args = parser.parse_args()
    start = time.time()
    if ((args.end-args.start) == 1):
        print(f"\nParsing IEEE Articles single page at: {args.start}") 
        FILE_NAME = str(np.random.randint(0, 100000)) + f'IEEE_page_single_page_{args.start}_only.csv'
    else:
        FILE_NAME = str(np.random.randint(0, 100000)) + f'IEEE_page_{args.start}_{args.end}.csv'
        print(f"\nParsing IEEE Articles from page {args.start}-{args.end}") 

    for param in information_keys:
        df[param] = []

    pd.DataFrame(df).to_csv(FILE_NAME, index=False)

    # Store link for the whole pages
    URL_IEEE_LIST = [f'{URL_IEEE}&pageNumber={i}' for i in range(args.start, args.end)]
    count = 0
    chunks = split_range(URL_IEEE_LIST, args.number_of_agent)
    
    # Creating a thread agent for opening each page.
    thread_workers = []
    for chunk in chunks:
        t = Thread(target=getLinkEachPage, args=(chunk, ))
        thread_workers.append(t)
        t.start()
    
    for t in thread_workers:
        t.join()
        

    


