################################################################################
# Import
################################################################################
import pandas as pd

################################################################################
# Update Gemini Earn
################################################################################
def uploadGemini(fname, outName):
    print("Gemini Earn")
    # Read in file  
    if '.csv' in fname:
        # Assume that the user uploaded a CSV file
        ds = pd.read_csv(fname)
    elif '.xls' in fname:
        # Assume that the user uploaded an excel file
        ds = pd.read_excel(fname)
    else:
        print("Unsupported file type")

    # Intial drops
    ds = ds.loc[ds['Specification'] != 'Earn Transfer']
    ds = ds.loc[ds['Type'] != 'Credit']
    ds = ds.loc[ds['Type'] != 'Debit']
    ds = ds.loc[ds['Symbol'] != 'USD']
    ds['Symbol'] = ds['Symbol'].str.replace('USD', '', 1)

    # Get column list
    ds['Cost'] = ds['USD Amount USD']
    finalCols = ['Date', 'Type', 'Symbol', 'Cost']

    # Get coin columns
    coinCols = list(filter(lambda x:'Amount' in x, list(ds.columns)))
    coinCols = [n for n in coinCols if n != "USD Amount USD"]
    finalCols.extend(coinCols)
    ds = ds[finalCols]

    # Drop NA columns and rows
    ds = ds.dropna(subset=['Symbol'])
    ds = ds.dropna(axis=1, how='all')

    # Merge Amount columns
    coinCols = list(filter(lambda x:'Amount' in x, list(ds.columns)))
    source_col_loc = ds.columns.get_loc(coinCols[0]) 
    ds['N'] = ds.iloc[:,source_col_loc:source_col_loc+len(coinCols)].apply(
        lambda x: ",".join(x.dropna().astype(str)), axis=1)

    # Fix Date
    ds['Date'] = ds['Date'].astype(str)
    ds["Date"] = ds["Date"].str.split('.').str[0]

    # Fix cost and amount
    ds['Cost'] = -ds['Cost']
    ds['N'] = abs(pd.to_numeric(ds['N']))

    # Fix buy and sell
    ds['Type'] = ds['Type'].str.replace('Buy', 'BUY')
    ds['Type'] = ds['Type'].str.replace('Sell', 'SELL')

    # Cost Basis
    ds["Cost_Basis"] = abs(ds['Cost']/ds['N'])

    # Add exchange 
    ds["Exchange"] = "Gemini"

    # Finalize
    ds = ds[['Exchange', 'Date', 'Symbol', 'N', 'Cost_Basis', 'Cost', 'Type']]
    ds.columns = ['Exchange','Date','Symbol','Amount','Cost_Basis','Total_Spent','Type']

    ds.to_csv(outName, index=False)


if __name__ == '__main__':
    uploadGemini()