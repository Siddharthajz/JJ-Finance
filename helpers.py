import pandas as pd
import numpy as np
import pandas_datareader
import datetime
import requests
import csv
import io
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

import urllib.request
import csv

from functools import wraps
from flask import redirect, request, session

API_KEY = 'XYVLAY94HUXJCZZ4'

# def get_nifty50stocks(stocklist=True):
#     """returns a dataframe with nifty 50 stocks and stock specific industries
#         stocklist: if True, then returns the list of stock scrips only
#     """
#     url = 'https://www1.nseindia.com/content/indices/ind_niftynext50list.csv'
#     headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
#     s = requests.get(url,headers=headers).content
#     nifty50df = pd.read_csv(io.StringIO(s.decode('utf-8')))
#     nifty50list = list(nifty50df['Symbol'])
#     nifty50list = [str(row).replace('&amp;','&') for row in nifty50list]
#     if stocklist is False:
#         return nifty50df
#     else:
#         return nifty50list

def get_ohlcv(symbol,start,end='today'):
    
    ''' returns end of day open-high-low-close-volume (ohlcv) data
        symbol: symbol scrip in NSE
        start:  (dd-mm-yy format) date starting from which you want the data
        end:    (dd-mm-yy format) date ending till which you want the data, if no value is assigned to the end value, then will get stock data till today
    ''' 

    symbol = str(symbol)+'.NS'
    startdate = datetime.datetime.strptime(start,'%d-%m-%Y')
    if end=='today':
        enddate = datetime.datetime.today()  
    else:
        enddate = datetime.datetime.strptime(end,'%d-%m-%y')
    data = pandas_datareader.get_data_yahoo(symbol,startdate,enddate)
    return data

def plot_data(symbol,start,end='today',candlestick=False):
    """
        Creates a graph in a html file for looking at the history of the stock
        symbol:         symbol scrip in NSE
        start:          (dd-mm-yy format) date starting from which you want the data
        end:            (dd-mm-yy format) date ending till which you want the data, if no value is assigned to the end value, then will get stock data till today
        candlestick:    returns a candlestick graph if True, otherwise returns a line graph (default value is False)
    """
    
    DF = get_ohlcv(symbol,start,end)
    if candlestick is False:
        fig = px.line(DF, x=DF.index, y=DF['Close'])
        fig.update_xaxes(rangeslider_visible=True)
        pio.write_html(fig, file=r'templates\stockgraph.html', auto_open=False)
    else:
        fig = go.Figure(data=[go.Candlestick(x=DF.index, open=DF['Open'], high=DF['High'], low=DF['Low'], close=DF['Close'])])
        fig.update_xaxes(rangeslider_visible=True)
        pio.write_html(fig, file=r'templates\stockgraph.html', auto_open=False)


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def inr(value):
    """Format value as INR."""
    return f"₹{value:,.2f}"