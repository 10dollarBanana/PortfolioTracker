# Import packages
import pandas as pd
import json
import requests
import json
import base64
import hmac
import hashlib
import datetime, time
import numpy as np
import os

# Define gemini function
def apiGemini(gemini_api_key, gemini_api_secret):
    print("Getting Gemini")

    # API setup
    # https://docs.gemini.com/rest-api/
    url = "https://api.gemini.com/v1/mytrades"
    gemini_api_key = gemini_api_key 
    gemini_api_secret = gemini_api_secret.encode()


    # Header prep
    t = datetime.datetime.now()
    payload_nonce =  str(int(time.mktime(t.timetuple())*1000))
    payload =  {
        "request": "/v1/mytrades",
        "nonce": payload_nonce, 
        'limit_trades': 500
    }
    encoded_payload = json.dumps(payload).encode()
    b64 = base64.b64encode(encoded_payload)
    signature = hmac.new(gemini_api_secret, b64, hashlib.sha384).hexdigest()

    # Headers
    request_headers = {
        'Content-Type': "text/plain",
        'Content-Length': "0",
        'X-GEMINI-APIKEY': gemini_api_key,
        'X-GEMINI-PAYLOAD': b64,
        'X-GEMINI-SIGNATURE': signature,
        'Cache-Control': "no-cache"
        }

    # Get transaction history
    response = requests.post(url, headers=request_headers)
    my_trades = response.json()
    gemini = pd.DataFrame(my_trades)
    
    # Reformat
    gemini = gemini[["exchange", "timestamp", "symbol", "amount", "price", "type"]]
    gemini['total'] = pd.to_numeric(gemini['price'])*pd.to_numeric(gemini['amount'])
    
    # Fix time
    gemini['date']=gemini['timestamp'].apply(lambda d: datetime.datetime.fromtimestamp(int(d)).strftime('%Y-%m-%d %H:%M:%S'))
    
    # Update buy and sell
    gemini['type'] = gemini['type'].str.replace('Buy', 'BUY')
    gemini['type'] = gemini['type'].str.replace('Sell', 'SELL')
    gemini['symbol'] = gemini['symbol'].str.replace('USD', '', 1)
    gemini['exchange'] = "Gemini"

    gemini['test'] = np.where(gemini['type']=='SELL', -1, 1)
    gemini['total'] =  gemini['total'] *  gemini['test']
    gemini['amount'] =  pd.to_numeric(gemini['amount']) * gemini['test']

    #gemini['type'] = np.where(gemini['symbol']=='GUSD', "STABLECOIN", gemini['type'])

    gemini = gemini[["exchange", "date", "symbol", "amount", "price", "total", "type"]]
    gemini.columns= ["Exchange", "Date", "Symbol", "Amount", "Cost_Basis", "Total_Spent", "Type"]

    # Write
    fileRoot = "gemini"
    df = gemini
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
    print("Gemini Done")

if __name__ == '__main__':
    apiGemini()


