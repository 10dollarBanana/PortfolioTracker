################################################################################
# Import
################################################################################
import pandas as pd

################################################################################
# BlockFi
################################################################################
def uploadBlockFi(fname, outName):

    fname="transactions.csv"
    # Blockfi
    print("Getting BlockFi")

    # Read in file
    if '.csv' in fname:
        # Assume that the user uploaded a CSV file
        ds = pd.read_csv(fname)
    elif '.xls' in fname:
        # Assume that the user uploaded an excel file
        ds = pd.read_excel(fname)
    else:
        print("Unsupported file type")
    
    # Extra columns
    ds["Exchange"]="BlockFi"
    #list(apy.columns.values) # Get column names
    ds = ds[['Cryptocurrency', 'Amount', 'Confirmed At', "Exchange", 'Transaction Type']]
    ds.columns = ["Symbol", "Amount", "Date", "Exchange", "Type"]

    # Bonus
    bonus = ds[ds.Type.isin(["Bonus Payment"])]
    bonus = bonus[["Symbol", "Amount", "Date", "Exchange"]]
    bonus["Type"] = "BONUS_PAYMENT"
    bonus['Cost_Basis'] = "0.00"
    bonus['Total_Spent'] = "0.00"
    bonus = bonus[["Exchange", "Date", "Symbol", "Amount", "Cost_Basis", "Total_Spent", "Type"]]

    # Interest
    apy = ds[ds.Type.isin(["Interest Payment"])]
    apy = apy[["Symbol", "Amount", "Date", "Exchange"]]
    apy["Type"] = "INTEREST"
    apy['Cost_Basis'] = "0.00"
    apy['Total_Spent'] = "0.00"
    apy = apy[["Exchange", "Date", "Symbol", "Amount", "Cost_Basis", "Total_Spent", "Type"]]

    # Purchases
    buys = ds.loc[ds['Type'] == 'Ach Deposit']
    buys['Type'] = 'BUY'
    buys['Cost_Basis'] = "1.00"
    buys['Total_Spent'] = pd.to_numeric(buys['Cost_Basis']) * pd.to_numeric(buys['Amount'])
    buys = buys[["Exchange", "Date", "Symbol", "Amount", "Cost_Basis", "Total_Spent", "Type"]]

    # Trades
    # Add new columns
    trade = ds.loc[ds['Type'] == 'Trade']
    trade['Total_Spent'] = 0
    trade['Cost_Basis'] = 0
    trade['Type'] = 'TRADE'
    trade = trade[["Exchange", "Date", "Symbol", "Amount", "Cost_Basis", "Total_Spent", "Type"]]

    # Merge
    bf = pd.DataFrame()
    bf = apy.append(bonus)
    bf = bf.append(buys)
    bf = bf.append(trade)
    bf = bf[["Exchange", "Date", "Symbol", "Amount", "Cost_Basis", "Total_Spent", "Type"]]

    bf.to_csv(outName, index=False)

if __name__ == '__main__':
    uploadBlockFi()