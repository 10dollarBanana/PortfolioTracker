################################################################################
# Import
################################################################################
import pandas as pd

################################################################################
# Upload coinbase
################################################################################
def uploadCoinbasePro(fname, outName):
    # Read in file  
    if '.csv' in fname:
        # Assume that the user uploaded a CSV file
        ds = pd.read_csv(fname)
    elif '.xls' in fname:
        # Assume that the user uploaded an excel file
        ds = pd.read_excel(fname)
    else:
        print("Unsupported file type")


    # Reformat
    ds['exchange'] = 'Coinbase Pro'
    ds = ds[["exchange", "time", "amount/balance unit", "amount", "type"]]

    # Get cost
    ds = ds.loc[ds['type'] == 'match']
    usd = ds.loc[ds['amount/balance unit'] == 'USD']
    usd.columns = ["exchange", "time", "fiat", "cost", "type"]

    txn = ds.loc[ds['amount/balance unit'] != 'USD']
    txn.columns = ["exchange", "time", "symbol", "amount", "type"]

    # Merge
    ds = pd.merge(txn,usd,on=("exchange", "time", "type"),how='outer')
    
    # Fix type
    ds['temp'] = abs(ds['cost'])
    ds['type'] = ds['cost']/ds['temp']
    ds['type'] = ds['type'].replace(-1, 'BUY')
    ds['type'] = ds['type'].replace(1, 'SELL')

    # Add price
    ds['price'] = ds['temp']/ds['amount']

    # Fix cost
    ds['cost'] = ds['cost']*-1


    # Fix time
    ds['time'] = ds['time'].str.replace('T', ' ')
    ds['time'] = ds['time'].str.replace('Z', ' ')
    ds["time"] = ds["time"].str.split('.').str[0]

    coinbasePro = ds[["exchange", "time", "symbol", "amount", "price", "cost", "type"]]
    coinbasePro.columns= ["Exchange", "Date", "Symbol", "Amount", "Cost_Basis", "Total_Spent", "Type"]

    coinbasePro.to_csv(outName, index=False)

    print("Coinbase Pro Done")
