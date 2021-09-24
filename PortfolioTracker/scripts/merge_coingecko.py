################################################################################
# Import
################################################################################
import pandas as pd
import requests
import json
import os
import time

def top500():
    server = "https://api.coingecko.com/api/v3"
    ext = "/coins/markets"
    time.sleep(1)
    querystring = {"vs_currency":"usd","page":"1","per_page":"100","order":"market_cap_desc"}
    time.sleep(1)
    coins = pd.DataFrame()
    for i in range(5):
        print(i)
        time.sleep(1)
        pageIndex = i+1
        time.sleep(1)
        querystring = {"vs_currency":"usd","page":str(pageIndex),"per_page":"100","order":"market_cap_desc"}
        time.sleep(1)
        temp = requests.get(server+ext, params=querystring).json()
        temp = pd.DataFrame(temp)
        temp['page'] = pageIndex
        coins = coins.append(temp)
    # Go through duplicate symbols, keep first (higher marketcap)
    coins = coins.drop_duplicates(subset=['symbol'], keep="first")
    # Get and fix columns
    df = coins[['name', 'id', 'symbol']]
    df['symbol'] = df['symbol'].str.upper()
    df.index = df.symbol
    # To dictionary
    df = df.to_dict(orient='index')
    # Check if json file exists
    if os.path.isfile("jsonApp/top500.json") == True:
        with open('jsonApp/top500.json') as json_file:
            data = json.load(json_file)
            data.update(df)
        with open('jsonApp/top500.json', 'w') as outfile:
            json.dump(data, outfile, indent=4)
    else:     
        with open('jsonApp/top500.json', 'w') as outfile:
            json.dump(df, outfile, indent=4)


def coinData():
    with open('jsonUser/txnSummary.json') as json_file:
        txnData = json.load(json_file)
    with open('jsonApp/top500.json') as json_file:
        coinInfo = json.load(json_file)
    # Turn into tables
    txnData = pd.DataFrame.from_dict(txnData, orient='index')
    coinInfo = pd.DataFrame.from_dict(coinInfo, orient='index')
    txns = pd.merge(txnData,coinInfo,on=["symbol"],how='left')
    coinList = list(txns['id'])
    # Get data from coingecko
    server = "https://api.coingecko.com/api/v3"
    ext = "/coins/markets"
    coins = pd.DataFrame()
    for coin in coinList:
        print(coin)
        querystring = {"vs_currency":"usd", "ids": coin,"order":"market_cap_desc"}
        temp = requests.get(server+ext, params=querystring).json()
        temp = pd.DataFrame(temp)
        coins = coins.append(temp)
    # Subset
    df = coins[['name', 'id', 'symbol', 'ath', 'ath_date', 'market_cap_rank', 'current_price']]
    df['symbol'] = df['symbol'].str.upper()
    df.index = df.symbol
    # To dictionary
    df = df.to_dict(orient='index')
    if os.path.isfile("jsonUser/coinData.json") == True:
        with open('jsonUser/coinData.json') as json_file:
            data = json.load(json_file)
            data.update(df)
        with open('jsonUser/coinData.json', 'w') as outfile:
            json.dump(data, outfile, indent=4)
    else:     
        with open('jsonUser/coinData.json', 'w') as outfile:
            json.dump(df, outfile, indent=4)

