import requests
from bs4 import BeautifulSoup

URL = 'https://in.finance.yahoo.com/'
page = requests.get(URL)

soup = BeautifulSoup(page.content, 'html.parser')

results = soup.find(class_='My(0) Ov(h) P(0) Wow(bw)')

job_elems = results.find_all('li', class_='js-stream-content Pos(r)')

links = []
titles = []

for p_job in job_elems:
    print("#############",p_job)
    links.append(URL + p_job.find('a')['href'])
    titles.append(p_job.find('a').text)


links = links[1:]
titles = titles[1:]

newslist = {}

for x in range(len(links)):

    newslist[titles[x]] = links[x] 




def get_news():

    return newslist

