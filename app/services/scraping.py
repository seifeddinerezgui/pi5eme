from newsapi import NewsApiClient
from bs4 import BeautifulSoup
import json
import requests
import html
import re 
import xml.etree.ElementTree 
import itertools
import os
import tempfile
import newspaper
import pathlib

abspath = pathlib.Path(__file__).parent.resolve()

# Replace this with your single API key
apikey = 'YOUR_API_KEY_HERE'

# Writing data to JSON file
def writeDataToJson(company, news_list):
    try:
        with open(f'{company}_news.json', 'w', encoding='utf-8') as json_file:
            json.dump(news_list, json_file, ensure_ascii=False, indent=4)
        # Returning the path of the JSON file
        return f'{company}_news.json'
    except Exception as e:
        raise Exception(f'Output Error: Error writing data to JSON file {e}')

# De-contracting English phrases
def decontracted(phrase):
    phrase = re.sub(r"won\'t", "will not", phrase)
    phrase = re.sub(r"can\'t", "can not", phrase)
    phrase = re.sub(r"n\'t", " not", phrase)
    phrase = re.sub(r"\'re", " are", phrase)
    phrase = re.sub(r"\'s", " is", phrase)
    phrase = re.sub(r"\'d", " would", phrase)
    phrase = re.sub(r"\'ll", " will", phrase)
    phrase = re.sub(r"\'t", " not", phrase)
    phrase = re.sub(r"\'ve", " have", phrase)
    phrase = re.sub(r"\'m", " am", phrase)
    return str(phrase)

def clean_text(text):
    text = html.unescape(text)
    text = re.sub(r'https?:\/\/.\S+', "", text)
    text = re.sub(r'#', '', text)
    text = re.sub(r'\"', '', text)
    text = re.sub(r'’','\'',text)
    text = re.sub(r'”','',text)
    text = re.sub(r'“','',text)
    text = re.sub(r'^RT[\s]+', '', text)
    text = ''.join(''.join(s)[:2] for _, s in itertools.groupby(text))
    return decontracted(text)

def remove_tags(text):
    try:
        output = ''.join(xml.etree.ElementTree.fromstring(text).itertext())
    except Exception:
        output = text
    return output

def basicScrapper(url):
    try:
        article = newspaper.Article(url=url, language='en')
        article.download()
        article.parse()
    except Exception as e:
        print(f'Error in Basic Scrapper using NewsPaper3K: {e}')
        return ''
    return str(article.text)

# Function to scrape news
def getNews(company, writeJson=False):
    try:
        print(f'Trying API Key for NewsAPI request: {apikey}')
        newsapi = NewsApiClient(api_key=apikey)
        news = newsapi.get_top_headlines(category='business', language='en')
    except Exception as e:
        raise Exception(f'NewsAPI Error: {e}')

    company = company.strip()
    queries = ['Stock', 'Investors', 'Profits', 'Finances', 'Performance', '']
    output_obj = []
    titles = []
    print('Started Top Business Headlines Scraping!')

    for query in queries:
        news = newsapi.get_top_headlines(q=(company + ' ' + query).strip(), category='business', language='en')
        for article in news['articles']:
            if article['title'] not in titles and company.lower() in article['title'].lower():
                del article['source'], article['author'], article['urlToImage']
                if len(titles) == 10:
                    break
                article['content'] = getFullArticleContent(company=company, url=article['url'])
                if len(article['content']) != 0 and len(article['description']) != 0:
                    output_obj.append(article)
                    titles.append(article['title'])

    if not len(titles) == 10:
        print('Started Full News Scraping!')
        news = newsapi.get_everything(q=(company).strip(), language='en')
        for article in news['articles']:
            if article['title'] not in titles and company.lower() in article['title'].lower():
                del article['source'], article['author'], article['urlToImage']
                if len(titles) == 10:
                    break
                article['content'] = getFullArticleContent(company=company, url=article['url'])
                if len(article['content']) != 0 and len(article['description']) != 0:
                    output_obj.append(article)
                    titles.append(article['title'])

    if not len(titles) == 10:
        print('Started Basic Scraping!')
        for article in news['articles']:
            if len(titles) == 10:
                break
            if article['title'] not in titles and company.lower() in article['title'].lower():
                content = basicScrapper(article['url'])
                if len(content) == 0:
                    article['content'] = clean_text(remove_tags(article['content'].split('… [')[0]))
                else:
                    article['content'] = content
                if len(article['content']) != 0 and len(article['description']) != 0:
                    output_obj.append(article)
                    titles.append(article['title'])

    if writeJson:
        url = writeDataToJson(company, output_obj)
        return url
    return titles, output_obj

def getFullArticleContent(company, url, pre_content=''):
    if not pre_content:
        pre_content = ''
    content = ''
    try:
        response = requests.get(url)
    except Exception:
        print(f'URL not reachable: {url}')
        return ''
    if response.status_code == 200:
        body = response.content
        soup1 = BeautifulSoup(body, 'html.parser')
        news = soup1.find_all('script')

        for article in news:
            try:
                if article.has_attr('type'):
                    if 'json' in article['type']:
                        obj = json.loads(article.contents[0])
                        if '@type' in obj.keys() and obj['@type'] == 'NewsArticle':
                            content += ' ' + str(obj["articleBody"])
            except Exception:
                pass

        news_div = soup1.find_all('div')
        for div in news_div:
            try:
                paras = div.find_all('p')
                for para in paras:
                    data = str(remove_tags(str(para)))
                    if company.lower() in data.lower() and data.lower() not in content.lower():
                        content += ' ' + data
            except Exception:
                pass
            
    else:
        content = ''
    return clean_text(content)

# getNews for all companies on a daily basis
def getAllNews():
    companies = ['Apple', 'Microsoft', 'Amazon', 'Walmart', 'Alphabet', 'Meta', 'Tesla', 'NVIDIA', 'Pfizer', 'Netflix']
    urls = []
    for company in companies:
        try:
            url = getNews(company=company, writeJson=True)
        except Exception as e:
            raise Exception(f'Error in {company} Company due to Error: {e}')
        print(url)
        urls.append(url)

    return urls

if __name__ == '__main__':
    # Replace this with your single API key
    apikey = '9529f5bef2b04ddcb3965ba5774a45a0'
    companies = ['Apple', 'Microsoft', 'Amazon', 'Walmart', 'Alphabet', 'Meta', 'Tesla', 'NVIDIA', 'Pfizer', 'Netflix']
    for company in companies:
        url = getNews(company=company, writeJson=True)
        print(url)
