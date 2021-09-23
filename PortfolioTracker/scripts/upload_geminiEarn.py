################################################################################
# Import
################################################################################
import pandas as pd

################################################################################
# Update Gemini Earn
################################################################################
def uploadGeminiEarn(fname, outName):
    print("Gemini Earn")

    # Read in file  
    if '.csv' in fname:
        # Assume that the user uploaded a CSV file
        apy = pd.read_csv(fname)
    elif '.xls' in fname:
        # Assume that the user uploaded an excel file
        apy = pd.read_excel(fname)
    else:
        print("Unsupported file type")
    

    apy = apy.loc[apy['Type'] == 'Interest Credit']
    finalCols = ['Date', 'Type', 'Symbol']

    # Get columns
    coinCols = list(filter(lambda x:'Amount' in x, list(apy.columns)))
    finalCols.extend(coinCols)
    apy = apy[finalCols]

    # Drop NA columns
    apy = apy.dropna(axis=1, how='all')

    # Merge Amount columns
    coinCols = list(filter(lambda x:'Amount' in x, list(apy.columns)))
    source_col_loc = apy.columns.get_loc(coinCols[0]) 
    apy['N'] = apy.iloc[:,source_col_loc:source_col_loc+len(coinCols)].apply(
        lambda x: ",".join(x.dropna().astype(str)), axis=1)

    apy = apy[["Symbol", "N", "Date"]]
    apy["Exchange"] = "Gemini"

    apy = apy[["Symbol", "N", "Date", "Exchange"]]

    # Finalize
    apy['Cost_Basis'] = "0.00"
    apy['Total_Spent'] = "0.00"
    apy['type'] = "INTEREST"
    apy = apy[['Exchange', 'Date', 'Symbol', 'N', 'Cost_Basis', 'Total_Spent', 'type']]
    apy.columns = ['Exchange','Date','Symbol','Amount','Cost_Basis','Total_Spent','Type']
    
    # Write
    apy.to_csv(outName, index=False)


if __name__ == '__main__':
    uploadGeminiEarn()