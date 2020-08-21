import requests
import datetime 
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import bs4 
from bs4 import BeautifulSoup
import re
import codecs

def requests_retry_session(retries=5,backoff_factor=0.3,status_forcelist=(500, 502, 504),session=None,):
    """
        Used instead of requests, this function tries to get to the url a number of times with a time lag.
        retries:          The maximum number of retries after the first failed attempt. default retries are 5
        backoff_factor:   Time waited before retires, waits by factor*2 seconds. default wait after first 0.6 secconds
        status_forcelist: The errors for which a retry is enforced
    """
    session = session or requests.Session()
    retry = Retry(total=retries,read=retries,connect=retries,backoff_factor=backoff_factor,status_forcelist=status_forcelist,)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

url = 'https://in.finance.yahoo.com/'
header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}
r = requests_retry_session().get(url,headers=header).content
soup = BeautifulSoup(r,'html.parser')

script = soup.find("script",text=re.compile("root.App.main"))
script = str(script)


summary_list = []
summaries = re.finditer('"is_eligible":',script)
summary_positions = [summary.start() for summary in summaries]
for i in summary_positions:
    link = script[script.index('"url"',i)+7:script.index('"property"',i)-2]
    title = script[script.index('"title"',i)+9:script.index('"',script.index('"title"',i)+9)]
    summary_list.append([codecs.decode(link, 'unicode-escape'),title])

final_list = [i for i in summary_list if ('summary' not in i[0])]

print(final_list)


def get_news():

    return final_list

