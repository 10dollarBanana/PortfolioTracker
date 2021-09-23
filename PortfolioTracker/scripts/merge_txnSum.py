################################################################################
# Import
################################################################################
import pandas as pd
import numpy as np
import glob
import json
import os

################################################################################
# Merge in transactions
################################################################################
def txnSum():   
    print("Getting Summaries")

    flist = glob.glob("summaries/*.csv")

    df = pd.DataFrame()
    for f in flist:
        fills = pd.read_csv(f)
        fills = fills[['Exchange', 'Date', 'Symbol', 'Amount', 'Cost_Basis', 'Total_Spent', 'Type']]
        df = df.append(fills)

    df.to_csv('detailed.csv', index=False)

    coinList = pd.unique(df['Symbol'])

    # Summarize
    txns = pd.DataFrame()
    for coin in coinList:
        tkn = df.loc[df['Symbol'] == coin]
        # Fix Crypto
        amt = round(tkn.sum(axis = 0, skipna = True)['Amount'], 10)
        # Get cost basis 
        buys = tkn[tkn['Type'].str.contains("BUY|INTEREST|FREE|TRADE", regex = True)]
        loss = tkn[tkn['Type'].str.contains("_SEND", regex = True)]
        cbAmt = round(buys.sum(axis = 0, skipna = True)['Amount'] + loss.sum(axis = 0, skipna = True)['Amount'], 10)
        cost = round(buys.sum(axis = 0, skipna = True)['Total_Spent'], 2)
        cb = cost/cbAmt
        # Sell Profits
        sells = tkn[tkn['Type'].str.contains("SELL", regex = True)]
        if len(sells) == 0: 
            sellAmt = 0
            profit = 0
        else:
            sellAmt = abs(sum(sells['Amount']))
            profit = round(abs(sum(sells['Total_Spent'])), 2)
        # Interest Earned
        ie = tkn[tkn['Type'].str.contains("INTEREST", regex = True)]
        ie = abs(sum(ie['Amount']))
        grp = "Crypto"
        # Fix stablecoin
        if coin == "GUSD" or coin == "USDC":
            cb = 1.00
            buys = tkn[~tkn['Type'].str.contains("INTEREST|BONUS_PAYMENT|FEE", regex = True)]
            profit = 0.00
            cost = round(buys.sum(axis = 0, skipna = True)['Amount'], 2) 
            grp = "Stablecoin"
        summary = [grp, coin, amt, cost, cb, sellAmt, profit, ie]
        summary = pd.DataFrame(summary).T
        txns = txns.append(summary)

    txns.columns=["class", "symbol", "amount", "total_spent", "cost_basis", "amt_sold", "sell_profits", "amt_interest"]

    # Sort
    txns = txns.loc[txns['amount'] != 0]
    txns = txns.loc[txns['symbol'] != "USD"]
    txns = txns.sort_values(by=['class', 'total_spent'], ascending=(True, False))

    txns.index = txns.symbol
    txns = txns.to_dict(orient='index')

    # Check if json file exists
    if os.path.isfile("jsonUser/txnSummary.json") == True:
        with open('jsonUser/txnSummary.json') as json_file:
            data = json.load(json_file)
            data.update(txns)
        with open('jsonUser/txnSummary.json', 'w') as outfile:
            json.dump(data, outfile, indent=4)
    else:     
        with open('jsonUser/txnSummary.json', 'w') as outfile:
            json.dump(txns, outfile, indent=4)


if __name__ == '__main__':
    txnSum()