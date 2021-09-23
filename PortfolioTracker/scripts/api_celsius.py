import requests
import json
import pandas as pd
import os

# https://developers.celsius.network/swagger/

# Celsius function
def apiCelsius(celsius_api_key, celsius_partner_token):
    print("Getting Celsius")
    headers = {
        "X-Cel-Partner-Token": celsius_partner_token,
        "X-Cel-Api-Key" : celsius_api_key
    }

    PATHS = {
        'baseURL': 'https://wallet-api.celsius.network',
        'balanceSummary': '/wallet/balance',
        'interestSummary': '/wallet/interest',
        'statistics': '/util/statistics?timestamp=',
        'transactionSummary': '/wallet/transactions'
    }

    # Transactions
    # Get number of transaction
    temp = requests.get(PATHS["baseURL"] + PATHS["transactionSummary"], headers = headers)
    temp = temp.json()

    pagination  = {
        'per_page': temp['pagination']['total']
    }

    temp = requests.get(PATHS["baseURL"] + PATHS["transactionSummary"], headers = headers, params = pagination)      
    temp = temp.json()
    temp = pd.DataFrame(temp['record'])

    #list(temp.columns)
    # Select columns
    txns = temp[['time', 'coin', 'amount_precise', 'nature']]

    txns = txns.loc[txns['nature'] != 'deposit']

    txns['nature'] = txns['nature'].str.replace('interest', 'INTEREST')
    txns['nature'] = txns['nature'].str.replace('promo_code_reward', 'FREE')
    txns['time'] = txns['time'].str.replace('T', ' ')
    txns['time'] = txns['time'].str.replace('Z', ' ')

    # Finalize
    txns['exchange'] = "Celsius"
    txns['Cost_Basis'] = "0.00"
    txns['Total_Spent'] = "0.00"
    txns = txns[['exchange', 'time', 'coin', 'amount_precise', 'Cost_Basis', 'Total_Spent', 'nature']]
    txns.columns = ['Exchange','Date','Symbol','Amount','Cost_Basis','Total_Spent','Type']

    # Write
    fileRoot = "celsius"
    df = txns
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
    print("Celsius Done")


if __name__ == '__main__':
    apiCelsius()
