################################################################################
# Import
################################################################################
import pandas as pd

################################################################################
# Update CDC fills
################################################################################
def uploadCDC(fname, outName):
    print("Getting Crypto.com")

    # Read in file
    if '.csv' in fname:
        # Assume that the user uploaded a CSV file
        df = pd.read_csv(fname)
    elif '.xls' in fname:
        # Assume that the user uploaded an excel file
        df = pd.read_excel(fname)
    else:
        print("Unsupported file type")

    # Extra columns
    df["Trade ID"]="Crypto.com"
    df["Price"]=round(df["Native Amount"]/df["To Amount"], 5)

    # Select columns
    df = df[["To Currency", "Trade ID", "Timestamp (UTC)",  "To Amount", "Price", "Native Amount"]]

    # Rename and add
    df.columns = ["Symbol", "Exchange", "Date", "Amount", "Cost_Basis", "Total_Spent"]
    df["Type"] = "BUY"

    df = df[["Exchange", "Date", "Symbol", "Amount", "Cost_Basis", "Total_Spent", "Type"]]
    cdc = pd.DataFrame(df)

    print("Crypto.com Complete")

    # Write
    cdc.to_csv(outName, index=False)


if __name__ == '__main__':
    uploadCDC()