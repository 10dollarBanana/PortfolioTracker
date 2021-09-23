################################################################################
# Import
################################################################################
import pandas as pd
import numpy as np
import json, requests
import hmac
import hashlib
import datetime, time
from urllib.parse import urljoin, urlencode
import os

################################################################################
# Binance 
################################################################################
def apiBinance(binance_api_key, binance_api_secret):
    print("Getting Binance.US")

    ## Binance
    API_KEY = binance_api_key
    SECRET_KEY = binance_api_secret
    BASE_URL = 'https://api.binance.us/'

    headers = {
        'X-MBX-APIKEY': API_KEY
    }

    class BinanceException(Exception):
        def __init__(self, status_code, data):
            self.status_code = status_code
            if data:
                self.code = data['code']
                self.msg = data['msg']
            else:
                self.code = None
                self.msg = None
            message = f"{status_code} [{self.code}] {self.msg}"
            # Python 2.x
            # super(BinanceException, self).__init__(message)
            super().__init__(message)


#===============================================================================
# Get available coins
#===============================================================================
    PATH = '/api/v3/account'
    timestamp = int(time.time() * 1000)
    params = {
        'timestamp': timestamp
    }

    query_string = urlencode(params)    
    params['signature'] = hmac.new(SECRET_KEY.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

    url = urljoin(BASE_URL, PATH)
    accounts = requests.get(url, headers=headers, params=params)
    coins = accounts.json()

    # Get list of available coins
    coinCt = len(coins['balances'])
    coinList = []
    for i in range(coinCt):
        val = coins['balances'][i]['asset']
        coinList.append(val+"USD")

    coinList.remove('USDUSD')

    #===============================================================================
    # Get orders
    #===============================================================================
    PATH = '/api/v3/allOrders'
    fills = pd.DataFrame()
    for i in coinList:
        timestamp = int(time.time() * 1000)
        params = {
        'symbol': i,
        'timestamp': timestamp
        }
        query_string = urlencode(params)
        params['signature'] = hmac.new(SECRET_KEY.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
        url = urljoin(BASE_URL, PATH)
        accounts = requests.get(url, headers=headers, params=params)
        temp = accounts.json()
        try:
            if temp['code'] < 0:
                print("moving on")
        except TypeError:
            if len(temp) > 0: 
                temp = pd.DataFrame(temp)
                fills = fills.append(temp)

    fills = fills.loc[fills['status'] != 'CANCELED']
    fillList = len(fills)

    #===============================================================================
    # Get fees
    #===============================================================================
    PATH = '/api/v3/myTrades'
    fees = pd.DataFrame()
    for i in range(fillList):
        timestamp = int(time.time() * 1000)
        params = {
            'symbol': fills.iloc[i]['symbol'],
            'orderId': fills.iloc[i]['orderId'],
            'recvWindow': 5000, 
            'timestamp': timestamp
        }
        query_string = urlencode(params)
        params['signature'] = hmac.new(SECRET_KEY.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
        url = urljoin(BASE_URL, PATH)
        accounts = requests.get(url, headers=headers, params=params)
        temp = accounts.json()
        try:
            if temp['code'] < 0:
                print("moving on")
        except TypeError:
            if len(temp) > 0: 
                temp = pd.DataFrame(temp)
                fees = fees.append(temp)
                
    #===============================================================================
    # Finalize
    #===============================================================================
    # Add exchange
    fees["exchange"] = "Binance.US"

    # Fix time
    fees['date']=fees['time'].apply(lambda d: datetime.datetime.fromtimestamp(int(d)/1000).strftime('%Y-%m-%d %H:%M:%S'))

    # Fix coin names
    fees['symbol'] = fees['symbol'].str.replace('USD', '')

    # New Qty column
    commCoin = fees.loc[fees['commissionAsset'] != 'BNB']
    commCoin['Qty'] = pd.to_numeric(commCoin['qty']) - pd.to_numeric(commCoin['commission'])
    commBNB = fees.loc[fees['commissionAsset'] == 'BNB']
    commBNB['Qty'] = pd.to_numeric(commBNB['qty'])

    # Merge     
    tempFees = commBNB.append(commCoin)
    tempFills = fills[["orderId", "side"]]
    txns = pd.merge(tempFees,tempFills, on=["orderId"],how='outer')

    # Set sells to reduce QTY
    txns['temp'] = np.where((txns['side'] == "SELL"), -1, 1)
    txns['Qty'] = txns['Qty'] * txns['temp']
    txns['total'] = pd.to_numeric(txns['Qty']) * pd.to_numeric(txns['price'])

    # Merge and finalize
    binance = txns[["exchange", "date", "symbol", "Qty", "price", "total", "side"]]

    # Commission
    # USD
    commUSD = fees.loc[fees['commissionAsset'] == 'USD']
    commUSD = commUSD[["exchange", "date", "symbol", "commission"]]

    # BNB
    commBNB = fees.loc[fees['commissionAsset'] == 'BNB']
    commBNB = commBNB[["exchange", "date", "commissionAsset", "commission"]]
    commBNB.columns = ["exchange", "date", "symbol", "commission"]

    # Merge
    commission = commUSD.append(commBNB)
    commission["side"] = "FEE_COMMISSION"
    commission["price"] = "NA"
    commission["total"] = "NA"
    commission['commission'] = -pd.to_numeric(commission['commission'])
    commission.columns = ["exchange", "date", "symbol", "Qty", "side", "price", "total"]

    # Merge and finalize
    binance = binance.append(commission)
    binance.columns= ["Exchange", "Date", "Symbol", "Amount", "Cost_Basis", "Total_Spent", "Type"]

    # Write
    fileRoot = "binance"
    df = binance
    mergeNames = list(df.columns)
    df.to_csv("temp/temp.csv", index=False)
    df = pd.read_csv("temp/temp.csv")
    # Summary file name
    sumFile = 'summaries/'+fileRoot+'.csv'

    if os.path.isfile(sumFile) == True:
        final = pd.read_csv(sumFile)
        final = pd.merge(final,df,on=mergeNames,how='outer')
        final = final.drop_duplicates(subset=None, keep='first', inplace=False)
        final.to_csv(sumFile, index=False)
    else:
        df.to_csv(sumFile, index=False)

    os.remove("temp/temp.csv")
    print("Binance.US Done")


if __name__ == '__main__':
    apiBinance()

