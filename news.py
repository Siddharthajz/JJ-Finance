import requests
from bs4 import BeautifulSoup

URL = 'https://in.finance.yahoo.com/'
page = requests.get(URL)

soup = BeautifulSoup(page.content, 'html.parser')

results = soup.find(class_='My(0) Ov(h) P(0) Wow(bw)')

job_elems = results.find_all('li', class_='js-stream-content')

links = []
titles = []
for p_job in job_elems:
    links.append(URL + p_job.find('a')['href'])
    titles.append(p_job.find('a').text)
    
def get_links():
    return links

def get_titles():
    return titles