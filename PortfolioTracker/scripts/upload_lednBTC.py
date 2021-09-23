################################################################################
# Import
################################################################################
import pandas as pd

################################################################################
# Update CDC fills
################################################################################
def uploadLednBTC(fname, outName):
    print("Getting Ledn BTC")

    # Read in file
    if '.csv' in fname:
        # Assume that the user uploaded a CSV file
        df = pd.read_csv(fname)
    elif '.xls' in fname:
        # Assume that the user uploaded an excel file
        df = pd.read_excel(fname)
    else:
        print("Unsupported file type")


    df = df.loc[df['Source'] == 'Interest']

    # Extra columns
    df["Exchange"]="Ledn"
    df["Symbol"]="BTC"
    df["Cost_Basis"]="0.00"
    df["Total_Spent"]="0.00"
    df["Type"]="INTEREST"

    # Fix Date
    date = df["Posted Date"].str.split("-", n = 5, expand = True)
    months = dict(Jan='1', Feb='2', Mar='3', Apr='4', May='5', Jun='6', Jul='7', Aug='8', Sep='9', Oct='10', Nov='11', Dec='12')
    month = date[1]
    month = month.apply(lambda m: months[m])
    year = date[0]
    time = date[2]
    df['Date'] = year+"-"+month+"-"+time

    df = df[["Exchange", "Date", "Symbol", "Amount", "Cost_Basis", "Total_Spent", "Type"]]


    print("Ledn BTC Complete")

    # Write
    df.to_csv(outName, index=False)


if __name__ == '__main__':
    uploadLednBTC()