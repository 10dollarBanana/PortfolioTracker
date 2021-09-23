################################################################################
# Import
################################################################################
import pandas as pd
import codecs
from requests.auth import AuthBase
import hmac
import hashlib
import requests
import json
import time
import os

################################################################################
# Coinbase
################################################################################
# Coinbase function
def apiCoinbase(coinbase_api_key, coinbase_api_secret):
    print("Getting Coinbase")
    # Create custom authentication for Coinbase API
    class CoinbaseWalletAuth(AuthBase):
        def __init__(self, api_key, secret_key):
            self.api_key = coinbase_api_key
            self.secret_key = coinbase_api_secret
        def __call__(self, request):
            timestamp = str(int(time.time()))
            message = timestamp + request.method + request.path_url + (request.body or '')
            signature = hmac.new(codecs.encode(self.secret_key), msg=codecs.encode(message), digestmod=hashlib.sha256).hexdigest()
            request.headers.update({
                'CB-ACCESS-SIGN': signature,
                'CB-ACCESS-TIMESTAMP': timestamp,
                'CB-ACCESS-KEY': self.api_key,
            })
            return request

    api_url = 'https://api.coinbase.com/v2/'
    auth = CoinbaseWalletAuth(coinbase_api_key, coinbase_api_secret)

    # Get coinlist
    pagination  = {
        'limit': 100
    }
    accounts = requests.get(api_url + 'accounts', auth=auth, params = pagination)      
    accounts = accounts.json()
    #sorted(accounts)
    accounts = pd.DataFrame(accounts['data'])
    id = accounts[accounts.id.apply(lambda x: len(str(x)) >= 10)]

    id = id.loc[id['created_at'] != id['updated_at']]
    id = list(id['id'])

    ds = pd.DataFrame()
    for i in id:
        txn = requests.get(api_url + 'accounts/' + i + '/transactions', auth=auth, params = pagination) 
        txn = txn.json()
        txnCt = len(txn['data'])
        for i in range(txnCt):
            id = txn['data'][i]['id']   
            date = txn['data'][i]['created_at']  
            amt = txn['data'][i]['amount']['amount']
            coin = txn['data'][i]['amount']['currency']
            print(coin)
            type = txn['data'][i]['type']
            description = txn['data'][i]['description']
            try: 
                fee = txn['data'][i]['network']['transaction_fee']['amount'] 
            except KeyError:
                fee = 'NaN'
            details = txn['data'][i]['details']['header']
            txnSum = [id, date, coin, amt, type, details, fee, description]
            txnSum = pd.DataFrame(txnSum).T
            txnSum.columns=["id", "date", "coin", "amount", "type", "details", 'fee', 'description']
            ds= ds.append(txnSum)

    # Filter and prep
    ds['exchange'] = 'Coinbase'
    ds['date'] = ds['date'].str.replace('T', ' ')
    ds['date'] = ds['date'].str.replace('Z', ' ')

    #===============================================================================
    # USDC
    #===============================================================================
    temp = ds.loc[ds['coin'] == 'USDC']
    temp["price"] = "1.00"

    # CBP pro transfers
    pro = temp[temp['type'].str.contains("pro_")]
    pro['type'] = pro['type'].str.replace('pro_deposit', 'TO_CBP')
    pro['type'] = pro['type'].str.replace('pro_withdrawal', 'FROM_CBP')
    pro['cost'] = pd.to_numeric(pro['amount']) 
    pro = pro[['exchange', 'date', 'coin', 'amount', 'price', 'cost', 'type']]

    # Buys
    buys = temp[temp['type'].str.contains("buy")]
    buys['type'] = buys['type'].str.replace('buy', 'BUY')
    buys['cost'] = pd.to_numeric(buys['amount']) 
    buys = buys[['exchange', 'date', 'coin', 'amount', 'price', 'cost', 'type']]

    # Interest
    interest = temp[temp['type'].str.contains("interest")]
    interest['type'] = interest['type'].str.replace('interest', 'INTEREST')
    interest['cost'] = "0.00"
    interest['price'] = "0.00"
    interest = interest[['exchange', 'date', 'coin', 'amount', 'price', 'cost', 'type']]

    # Send Fees
    fees = temp.loc[temp['fee'] != 'NaN']
    fees = fees[fees['details'].str.contains("Sent")]
    fees['amount'] = -pd.to_numeric(fees['fee'])
    fees['type'] = "FEE_SEND"
    fees['cost'] = abs(pd.to_numeric(fees['amount']))
    fees = fees[['exchange', 'date', 'coin', 'amount', 'price', 'cost', 'type']]

    # Merge
    usdc = pd.DataFrame()
    usdc = buys.append(pro)
    usdc = usdc.append(interest)
    usdc = usdc.append(fees)

    #===============================================================================
    # Interest
    #===============================================================================
    interest = ds[ds['type'].str.contains("reward")]

    interest['type'] = "INTEREST"
    interest['cost'] = "0.00"
    interest['price'] = "0.00"
    interest = interest[['exchange', 'date', 'coin', 'amount', 'price', 'cost', 'type']]

    #===============================================================================
    # Everything else
    #===============================================================================
    txns = ds[~ds['type'].str.contains("pro_")]
    txns = txns[~txns['type'].str.contains("_reward")]
    txns = txns.loc[txns['coin'] != 'USD']
    txns = txns.loc[txns['coin'] != 'USDC']
    txns["cost"] = txns["details"].str.split('$').str[1]
    txns["cost"] = txns["cost"].str.split(')').str[0]
    txns["cost"] = pd.to_numeric(txns['cost'])
    txns["type"] = txns["details"].str.split(' ').str[0]
    txns["amount"] = pd.to_numeric(txns['amount'])

    # Pull columns
    txns = txns[["exchange", "date", "coin", "amount", "cost", "fee", "type"]]

    # Edit transactions
    temp = pd.DataFrame() 
    # Buys 
    buys = txns[txns['type'].str.contains("Bought")]
    buys["price"] = buys['cost']/buys['amount']
    buys['type'] = "BUY"
    buys = buys[['exchange', 'date', 'coin', 'amount', 'price', 'cost', 'type']]
    temp = temp.append(buys)

    # Orders
    order = txns.loc[txns['fee'] == 'NaN']
    order = order[order['type'].str.contains("Sent")]
    order["price"] = abs(order['cost']/order['amount'])
    order['type'] = "MERCHANT_SEND"
    order = order[['exchange', 'date', 'coin', 'amount', 'price', 'cost', 'type']]
    temp = temp.append(order)

    # Send fees
    fees = txns.loc[txns['fee'] != 'NaN']
    fees = fees[fees['type'].str.contains("Sent")]
    fees["price"] = abs(fees['cost']/fees['amount'])
    fees['amount'] = -pd.to_numeric(fees['fee'])
    fees['type'] = "FEE_SEND"
    fees['cost'] = abs(fees['price'] * fees['amount'])
    fees = fees[['exchange', 'date', 'coin', 'amount', 'price', 'cost', 'type']]
    temp = temp.append(fees)

    # Received
    rec = txns[txns['type'].str.contains("Received")]  
    rec["price"] = rec['cost']/rec['amount']
    rec['type'] = "FREE"
    rec['cost'] = 0
    rec = rec[['exchange', 'date', 'coin', 'amount', 'price', 'cost', 'type']]
    temp= temp.append(rec)

    # Merge
    cbase = pd.DataFrame()
    cbase = interest.append(usdc)
    cbase = cbase.append(temp)

    # Fix Celo
    cbase['coin'] = cbase['coin'].str.replace('CGLD', 'CELO')

    # Rename
    cbase.columns= ["Exchange", "Date", "Symbol", "Amount", "Cost_Basis", "Total_Spent", "Type"]

    # Write
    fileRoot = "coinbase"
    df = cbase
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
    print("Coinbase Done")


if __name__ == '__main__':
    apiCoinbase()

