################################################################################
# Import
################################################################################
import pandas as pd
import json
import requests
import json
import base64
import hmac
import hashlib
import datetime, time
from requests.auth import AuthBase
import os

################################################################################
# Coinbase Pro
################################################################################
def apiCoinbasePro(cbp_key, cbp_secret, cbp_passphrase):
    # Coinbase pro
    print("Getting Coinbase Pro")


    # Create custom authentication for Exchange
    class CoinbaseExchangeAuth(AuthBase):
        def __init__(self, api_key, secret_key, passphrase):
            self.api_key = cbp_key
            self.secret_key = cbp_secret
            self.passphrase = cbp_passphrase
        def __call__(self, request):
            timestamp = str(time.time())
            message = timestamp + request.method + request.path_url + (request.body or b'').decode()
            hmac_key = base64.b64decode(self.secret_key)
            signature = hmac.new(hmac_key, message.encode(), hashlib.sha256)
            signature_b64 = base64.b64encode(signature.digest()).decode()
            request.headers.update({
                'CB-ACCESS-SIGN': signature_b64,
                'CB-ACCESS-TIMESTAMP': timestamp,
                'CB-ACCESS-KEY': self.api_key,
                'CB-ACCESS-PASSPHRASE': self.passphrase,
                'Content-Type': 'application/json'
            })
            return request

    api_url = 'https://api.pro.coinbase.com/'
    auth = CoinbaseExchangeAuth(cbp_key, cbp_secret, cbp_passphrase)

    # Pause
    time.sleep(2)

    # Get coinlist
    accounts = requests.get(api_url + 'accounts', auth=auth)    
    accounts = accounts.json()
    accounts = pd.DataFrame(accounts)

    # Get coin pairs
    accounts['USD'] = accounts['currency'] + "-USD"
    accounts['USDC'] = accounts['currency'] + "-USDC"
    product_id = list(accounts['USD'])
    temp = list(accounts['USDC'])
    product_id = product_id + temp
    # Pause
    time.sleep(2)

    # Parameters
    params  = {
        'limit': 1000
    }

    # Loop through coins and get fills
    error = {'message': 'product_id is not a valid product'}
    fills = pd.DataFrame()
    for i in product_id:
        print(i)
        temp = requests.get(api_url + 'fills/?product_id=' + i, auth=auth, params = params) 
        temp = temp.json()
        if len(temp) > 0 and temp != error:
            temp = pd.DataFrame(temp)
            fills = fills.append(temp)

    coinbasePro = fills

    # Reformat
    coinbasePro['exchange'] = 'Coinbase Pro'
    coinbasePro = coinbasePro[["exchange", "created_at", "product_id", "size", "price", "side"]]

    # Update buy and sell
    coinbasePro['side'] = coinbasePro['side'].str.replace('buy', 'BUY')
    coinbasePro['side'] = coinbasePro['side'].str.replace('sell', 'SELL')

    coinbasePro['total'] = pd.to_numeric(coinbasePro['price'])*pd.to_numeric(coinbasePro['size'])
    coinbasePro['product_id'] = coinbasePro['product_id'].str.replace('-USDC', '')
    coinbasePro['product_id'] = coinbasePro['product_id'].str.replace('-USD', '')
    coinbasePro['created_at'] = coinbasePro['created_at'].str.replace('T', ' ')
    coinbasePro['created_at'] = coinbasePro['created_at'].str.replace('Z', ' ')
    coinbasePro["created_at"] = coinbasePro["created_at"].str.split('.').str[0]

    coinbasePro = coinbasePro[["exchange", "created_at", "product_id", "size", "price", "total", "side"]]
    coinbasePro.columns= ["Exchange", "Date", "Symbol", "Amount", "Cost_Basis", "Total_Spent", "Type"]

    # Write
    fileRoot = "coinbasePro"
    df = coinbasePro
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
    print("Coinbase Pro Done")

if __name__ == '__main__':
    apiCoinbasePro()