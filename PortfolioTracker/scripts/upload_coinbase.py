################################################################################
# Import
################################################################################
import pandas as pd

################################################################################
# Upload coinbase
################################################################################
def uploadCoinbase(fname, outName):


fname="CSVreport.csv"
# Read in file  
if '.csv' in fname:
    # Assume that the user uploaded a CSV file
    ds = pd.read_csv(fname, skiprows=7)
elif '.xls' in fname:
    # Assume that the user uploaded an excel file
    ds = pd.read_excel(fname, skiprows=7)
else:
    print("Unsupported file type")


# Reformat
ds['exchange'] = 'Coinbase'
ds = ds[["exchange", "Timestamp", "Asset", "Quantity Transacted", "USD Spot Price at Transaction", "USD Subtotal", "USD Total (inclusive of fees)", "Transaction Type", "Notes"]]
ds.columns = ["exchange", "date", "coin", "amount", "price", "cost", "costTotal", "type", "Notes"]

# Fix
ds['date'] = ds['date'].str.replace('T', ' ')
ds['date'] = ds['date'].str.replace('Z', ' ')

# # Get cost
# ds = ds.loc[ds['type'] == 'match']
# usd = ds.loc[ds['amount/balance unit'] == 'USD']
# usd.columns = ["exchange", "time", "fiat", "cost", "type"]

# txn = ds.loc[ds['amount/balance unit'] != 'USD']
# txn.columns = ["exchange", "time", "symbol", "amount", "type"]






#===============================================================================
# USDC
#===============================================================================
temp = ds.loc[ds['coin'] == 'USDC']

# Buys
buys = temp[temp['type'].str.contains("Buy")]
buys['type'] = buys['type'].str.replace('Buy', 'BUY')
buys = buys[['exchange', 'date', 'coin', 'amount', 'price', 'cost', 'type']]

# Interest
interest = temp[temp['type'].str.contains("Rewards")]
interest['type'] = 'INTEREST'
interest['cost'] = "0.00"
interest['price'] = "0.00"
interest = interest[['exchange', 'date', 'coin', 'amount', 'price', 'cost', 'type']]

# Send Fees
fees = temp.loc[temp['type'] == 'Send']
fees['amount'] = -pd.to_numeric(fees['amount'])
fees['type'] = "FEE_SEND"
fees['cost'] = abs(pd.to_numeric(fees['amount']))
fees = fees[['exchange', 'date', 'coin', 'amount', 'price', 'cost', 'type']]

# Merge
usdc = pd.DataFrame()
usdc = buys.append(interest)
usdc = usdc.append(fees)

#===============================================================================
# Interest
#===============================================================================
interest = ds[ds['type'].str.contains("Rewards")]
interest = interest.loc[ds['coin'] != 'USDC']

interest['type'] = "INTEREST"
interest['cost'] = "0.00"
interest['price'] = "0.00"
interest = interest[['exchange', 'date', 'coin', 'amount', 'price', 'cost', 'type']]

    #===============================================================================
    # Everything else
    #===============================================================================
    txns = ds.loc[ds['coin'] != 'USD']
    txns = txns.loc[txns['coin'] != 'USDC']
    txns = txns[~txns['type'].str.contains("Rewards")]
    txns["amount"] = pd.to_numeric(txns['amount'])

    # Pull columns
    txns = txns[["exchange", "date", "coin", "amount", "price", "cost", "type", "Notes"]]

    # Edit transactions
    temp = pd.DataFrame() 
    # Buys BSV isn't correct
    buys = txns[txns['type'].str.contains("Buy")]
    buys['type'] = "BUY"
    buys = buys[['exchange', 'date', 'coin', 'amount', 'price', 'cost', 'type']]
    temp = temp.append(buys)

    # Orders
    order = txns[txns['type'].str.contains("Paid")]
    order["amount"] = -order['amount']
    order["cost"] = order['price']*order['amount']
    order['type'] = "MERCHANT_SEND"
    order = order[['exchange', 'date', 'coin', 'amount', 'price', 'cost', 'type']]
    temp = temp.append(order)

    # Send fees
    fees = txns.loc[txns['cost'] != 'NaN']
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


    cbase.to_csv(outName, index=False)

print("Coinbase Pro Done")
