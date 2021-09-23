################################################################################
# Import
################################################################################
import pandas as pd
import numpy as np
import glob
import json
import os

from scripts.merge_coingecko import coinData
from scripts.merge_txnSum import txnSum

################################################################################
# Import
################################################################################
    
def mergeSum():   
    # Get summary data
    if os.path.isfile("jsonUser/txnSummary.json") == True:
        with open('jsonUser/txnSummary.json') as json_file:
            txns = json.load(json_file)
    else:
        txnSum()
        with open('jsonUser/txnSummary.json') as json_file:
            txns = json.load(json_file)

    txns = pd.DataFrame.from_dict(txns, orient='index')

    # Get coin data
    if os.path.isfile("jsonUser/coinData.json") == True:
        with open('jsonUser/coinData.json') as json_file:
            gecko = json.load(json_file)
    else:
        coinData()
        with open('jsonUser/coinData.json') as json_file:
            gecko = json.load(json_file)

    gecko = pd.DataFrame.from_dict(gecko, orient='index')

    # Merge to dataframe
    txns = pd.merge(txns,gecko,on=["symbol"],how='left')

    # Update stablecoin prices
    txns.loc[txns['class'] == 'Stablecoin', 'current_price'] = 1.00

    # Additional columns
    txns['current_value'] = round(txns['current_price'] * txns['amount'], 2)
    txns['interest_value'] = round(txns['current_price'] * txns['amt_interest'], 2)

    totalSpent = txns.sum(axis = 0, skipna = True)['total_spent']
    totalPortfolio = txns.sum(axis = 0, skipna = True)['current_value']

    txns['pct_invested'] = txns['total_spent']/totalSpent
    txns['pct_portfolio'] = txns['current_value']/totalPortfolio

    txns['gl'] = (txns['current_value']+ txns['sell_profits']) - txns['total_spent']
    txns['pct_gl'] = txns['gl'] / txns['total_spent']

    gainLoss = txns.sum(axis = 0, skipna = True)['gl']
    pct_gainLoss = (totalPortfolio - totalSpent)/totalSpent

    # Write portfolio summary
    summary = {"total_spent" : totalSpent, "total_value" : totalPortfolio, "total_GL" : gainLoss, "total_pctGL" : pct_gainLoss}
    with open('jsonUser/portfolioSum.json', 'w') as outfile:
            json.dump(summary, outfile, indent=4)

    # Update columns
    txns['cost_basis'] = round(txns['cost_basis'], 2)

    # Update stablecoin prices
    txns.loc[txns['class'] == 'Stablecoin', 'current_price'] = '{:.2f}'.format(1.00)


    # Fix percents
    txns['pct_gl'] = round((txns['pct_gl']*100),2)
    txns['pct_gl'][np.isinf(txns['pct_gl'])] = "NaN"
    txns['pct_invested'] = round(txns['pct_invested']*100,2)
    txns['pct_portfolio'] = round(txns['pct_portfolio']*100,2)

    # Add trailing zeros to dollar columns
    txns['total_spent'] = txns.total_spent.map('{:.2f}'.format)
    txns['current_value'] = txns.current_value.map('{:.2f}'.format)
    txns['cost_basis'] = txns.cost_basis.map('{:.2f}'.format)
    txns['gl'] = txns.gl.map('{:.2f}'.format)
    txns['sell_profits'] = txns.sell_profits.map('{:.2f}'.format)
    txns['interest_value'] = txns.interest_value.map('{:.2f}'.format)

    return(txns)

if __name__ == '__main__':
    mergeSum()