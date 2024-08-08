import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

def scrape_google_scholar(query, num_results=10):
    query = query.replace(' ', '+')
    url = f'https://scholar.google.com/scholar?hl=en&q={query}'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    articles = soup.find_all('div', class_='gs_r gs_or gs_scl', limit=num_results)
    results = []

    for article in articles:
        title = article.find('h3', class_='gs_rt')
        title = title.text if title else 'N/A'

        publication_info = article.find('div', class_='gs_a').text
        authors, publication_title, date = parse_publication_info(publication_info)

        abstract = article.find('div', class_='gs_rs')
        abstract = abstract.text if abstract else 'N/A'

        keywords = 'N/A'  # Google Scholar does not provide keywords in search results
        countries = 'N/A'  # Country information is not provided in search results

        citation_info = article.find('div', class_='gs_fl').find_all('a')
        num_citations = 0
        for ci in citation_info:
            if 'Cited by' in ci.text:
                num_citations = int(re.findall(r'\d+', ci.text)[0])

        publication_type = 'N/A'  # Publication type is not provided in search results

        data = {
            'article_title': title,
            'publication_title': publication_title,
            'date': date,
            'abstract': abstract,
            'keywords': keywords,
            'countries': countries,
            'number_of_citations': num_citations,
            'authors': authors,
            'publication_type': publication_type
        }
        results.append(data)

    return pd.DataFrame(results)

def parse_publication_info(info):
    parts = info.split(' - ')
    if len(parts) == 3:
        authors = parts[0]
        publication_title = parts[1]
        date = parts[2]
    else:
        authors = 'N/A'
        publication_title = 'N/A'
        date = 'N/A'
    return authors, publication_title, date

query = "YOLOv9 object localization"
num_results = 10
df = scrape_google_scholar(query, num_results)
print(df)
