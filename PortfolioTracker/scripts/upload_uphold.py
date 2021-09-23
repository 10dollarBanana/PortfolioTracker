################################################################################
# Import
################################################################################
import pandas as pd

################################################################################
# Merge in transactions
################################################################################
def uploadUphold(fname, outName):

    print("Getting Uphold")
    # Read in file
    if '.csv' in fname:
        # Assume that the user uploaded a CSV file
        df = pd.read_csv(fname)
    elif '.xls' in fname:
        # Assume that the user uploaded an excel file
        df = pd.read_excel(fname)
    else:
        print("Unsupported file type")

    df = df[['Date', 'Destination', 'Destination Amount', 'Destination Currency',  'Fee Amount', 'Fee Currency', 'Origin',  'Origin Amount', 'Origin Currency', 'Type']]

    df['Start'] = df['Origin Currency']
    df['Start_Amt'] = -pd.to_numeric(df['Origin Amount'])
    df['End'] = df['Destination Currency']
    df['End_Amt'] = pd.to_numeric(df['Destination Amount'])

    #===============================================================================
    # Rewards
    #===============================================================================
    temp = df.loc[df['Type'] == 'in']

    earn = temp[['Date', 'End', 'End_Amt']]
    earn['Total_Spent'] = 0
    earn['Cost_Basis'] = 0
    earn['Type'] = 'FREE'
    earn = earn[['Date', 'End', 'End_Amt', 'Cost_Basis', 'Total_Spent', 'Type']]
    earn.columns = ['Date', 'Symbol', 'Amount', 'Cost_Basis', 'Total_Spent', 'Type']

    #===============================================================================
    # Get transactions
    #===============================================================================
    temp = df.loc[df['Destination'] == df['Origin']]
    temp = temp.loc[temp['Start'] != temp['End']]

    # Start
    start= temp[['Date', 'Start', 'Start_Amt']]
    start['Total_Spent'] = 0
    start['Cost_Basis'] = 0
    start['Type'] = 'TRADE'
    start = start[['Date', 'Start', 'Start_Amt', 'Cost_Basis', 'Total_Spent', 'Type']]
    start.columns = ['Date', 'Symbol', 'Amount', 'Cost_Basis', 'Total_Spent', 'Type']

    # End
    end = temp[['Date', 'End', 'End_Amt']]
    end['Total_Spent'] = 0
    end['Cost_Basis'] = 0
    end['Type'] = 'TRADE'
    end = end[['Date', 'End', 'End_Amt', 'Cost_Basis', 'Total_Spent', 'Type']]
    end.columns = ['Date', 'Symbol', 'Amount', 'Cost_Basis', 'Total_Spent', 'Type']

    # Merge
    txns = start.append(end)

    #===============================================================================
    # Sent back to Brave
    #===============================================================================
    temp = df.loc[df['Type'] == 'out']
    temp = temp.loc[temp['Destination Currency'] == temp['Origin Currency']]
    temp = temp.loc[temp['Destination'] == temp['Origin']]

    sends = temp[['Date', 'Start', 'Start_Amt']]
    sends['Total_Spent'] = 0
    sends['Cost_Basis'] = 0
    sends['Type'] = 'SEND'
    sends = sends[['Date', 'Start', 'Start_Amt', 'Cost_Basis', 'Total_Spent', 'Type']]
    sends.columns = ['Date', 'Symbol', 'Amount', 'Cost_Basis', 'Total_Spent', 'Type']

    #===============================================================================
    # Withdrawl fees
    #===============================================================================
    temp = df.dropna(subset=['Fee Amount'])
    temp = temp.loc[temp['Destination'] != temp['Origin']]

    fees = temp[['Date', 'Fee Currency', 'Fee Amount']]
    fees['Fee Amount'] = -fees['Fee Amount']
    fees['Total_Spent'] = 0
    fees['Cost_Basis'] = 0
    fees['Type'] = 'FEE_SEND'
    fees = fees[['Date', 'Fee Currency', 'Fee Amount', 'Cost_Basis', 'Total_Spent', 'Type']]
    fees.columns = ['Date', 'Symbol', 'Amount', 'Cost_Basis', 'Total_Spent', 'Type']

    # Merge
    uphold = earn.append(txns)
    uphold = uphold.append(sends)
    uphold = uphold.append(fees)

    uphold['Exchange'] = "Uphold"
    uphold = uphold[['Exchange', 'Date', 'Symbol', 'Amount', 'Cost_Basis', 'Total_Spent', 'Type']]

    # Fix Date
    date = uphold["Date"].str.split(" ", n = 5, expand = True)
    months = dict(Jan='1', Feb='2', Mar='3', Apr='4', May='5', Jun='6', Jul='7', Aug='8', Sep='9', Oct='10', Nov='11', Dec='12')
    month = date[1]
    month = month.apply(lambda m: months[m])
    day = date[2]
    year = date[3]
    time = date[4]
    uphold['Date'] = year+"-"+month+"-"+day+" "+time

    # Write
    uphold.to_csv(outName, index=False)


if __name__ == '__main__':
    uploadUphold()



