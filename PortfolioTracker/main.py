import dearpygui.dearpygui as dpg
import dearpygui.logger as dpg_logger
import pandas as pd
import os
from datetime import datetime
import json

# Exchanges
from scripts.api_binance import apiBinance 
from scripts.api_celsius import apiCelsius 
from scripts.api_coinbase import apiCoinbase 
from scripts.api_coinbasepro import apiCoinbasePro 
from scripts.api_gemini import apiGemini 

from scripts.upload_blockfi import uploadBlockFi 
from scripts.upload_crypto_com import uploadCDC
from scripts.upload_geminiEarn import uploadGeminiEarn
from scripts.upload_lednBTC import uploadLednBTC
from scripts.upload_uphold import uploadUphold

from scripts.merge_summary import mergeSum
from scripts.merge_temp import mergeTemp
from scripts.merge_coingecko import coinData, top500
from scripts.merge_txnSum import txnSum

################################################################################
# Load gui settings
################################################################################
# Font
with dpg.font_registry():

    # add font (set as default for entire app)
    dpg.add_font("fonts/Roboto-Regular.ttf", 20, default_font=True)

################################################################################
# Variables
################################################################################
with open('jsonApp/addManual.json') as json_file:
    manualData = json.load(json_file)

################################################################################
# Set layout
################################################################################   
dpg.enable_docking(dock_space=True)

dpg.load_init_file(file="custom_layout.ini")

cryptosummary = dpg.generate_uuid()
txnupdate = dpg.generate_uuid()

def _test(sender, add_data, user_data):
    #sender, add_data, user_data
    print(sender)
    print(dpg.get_value(sender))
    print(dpg.get_item_label(sender))
    print(add_data)
    print(dpg.get_value(add_data))
    print(dpg.get_item_info(add_data))
    print(user_data)
    print(dpg.get_value(user_data))
    print(dpg.get_item_info(user_data))

################################################################################
# File prep
################################################################################
def _loadTable():
    df = mergeSum()
    with open('jsonApp/sumCols.json') as json_file:
        data = json.load(json_file)
        
    selected = data['selected']
    # Fix column order and name
    colSelect = ['name', 'symbol'] + list(selected.keys())
    df = df[colSelect]
    df.columns = ['Name', 'Symbol'] + list(selected.values())
    return(df)

################################################################################
# Functions cryptosummary window
################################################################################
def _portfolioSummary():
    dpg.delete_item(folioStats, children_only=True)  
    with open('jsonUser/portfolioSum.json') as json_file:
            folio = json.load(json_file)
    dpg.add_text("Portfolio Summary:", parent = folioStats)
    dpg.add_text(("Total Spent($): " + str(round(folio['total_spent'], 2)) +
                "   " +
                "Total Value($): " + str(round(folio['total_value'], 2)) +
                "   " +                
                "Total Gain/Loss($): " + str(round(folio['total_GL'], 2)) +
                "   " +                
                "Total Gain/Loss(%): " + str(round(folio['total_pctGL']*100, 2))),
                parent = folioStats)

def _refresh():
    dpg.delete_item(tbl_id, children_only=True)  
    ds = _loadTable()
    for i in range(len(ds.columns)):
        col = ds.columns[i]
        dpg.add_table_column(label=col, parent=tbl_id, id=(tableData+i))

    for i in range(len(ds.index)):
        for j in range(len(ds.columns)):
            colname = ds.columns[j]
            value = ds[colname].iloc[i]
            dpg.add_text(value, parent=tbl_id)
            dpg.add_table_next_column(parent=tbl_id)

    _portfolioSummary()
    print("Table refreshed")

def _refreshAll():
    with dpg.window(label="Syncing...", modal=True, pos=(600, 500), no_close=True) as syncWindow: 
        dpg.add_loading_indicator(style=1, color=(150, 240, 240, 250))
        print("coin data")
        coinData()
        print("txn data")
        txnSum()
        print("refresh")
        _refresh()
    dpg.configure_item(syncWindow, show=False)   


#=============================================================================== 
# Delete data
#===============================================================================
def _deleteTxns():
    dir = 'summaries/'
    for f in os.listdir(dir):
        os.remove(os.path.join(dir, f))
    os.remove('jsonUser/coinData.json')
    os.remove('jsonUser/portfolioSum.json')
    os.remove('jsonUser/txnSummary.json')

def _deleteCSV(sender, add_data, user_data):
    value = dpg.get_value("summaryDelete")
    if value == "Binance.US":
        os.remove('summaries/binance.csv')
        txnSum()
        _refresh()
    elif value == "BlockFi":
        os.remove('summaries/blockfi.csv')
        txnSum()
        _refresh()
    elif value == "Celsius":
        os.remove('summaries/celsius.csv')
        txnSum()
        _refresh()
    elif value == "Coinbase":
        os.remove('summaries/coinbase.csv')
        txnSum()
        _refresh()
    elif value == "Coinbase Pro":
        os.remove('summaries/coinbasePro.csv')
        txnSum()
        _refresh()
    elif value == "Crypto.com":
        os.remove('summaries/cdc.csv')
        txnSum()
        _refresh()
    elif value == "Gemini":
        os.remove('summaries/gemini.csv')
        txnSum()
        _refresh()
    elif value == "Gemini Earn":
        os.remove('summaries/geminiEarn.csv')
        txnSum()
        _refresh()
    elif value == "Ledn BTC":
        os.remove('summaries/lednBTC.csv')
        txnSum()
        _refresh()
    elif value == "Manual":
        os.remove('summaries/manualTxns.csv')
        txnSum()
        _refresh()
    elif value == "Uphold":
        os.remove('summaries/uphold.csv')
        txnSum()
        _refresh()

def _deleteAPIs():
    os.remove('jsonUser/APIkeys.json')


#===============================================================================
# Save output
#===============================================================================
def _writeFile(sender, add_data, user_data):
    value = dpg.get_item_label(sender)
    fpath = add_data['file_path_name']
    if value == "Export Summary":
        df = _loadTable()
    elif value == "Export Detailed":
        df = pd.read_csv("detailed.csv")
    df.to_csv(fpath, index=False)

def _exportSum():
    with dpg.file_dialog(label="Export Summary", default_filename="summary", callback=_writeFile):
        dpg.add_file_extension(".csv", color=(255, 255, 255, 255))

def _exportDet():
    with dpg.file_dialog(label="Export Detailed", default_filename="detailed", callback=_writeFile):
        dpg.add_file_extension(".csv", color=(255, 255, 255, 255))

#===============================================================================
# Make table Sortable
#===============================================================================
def _sortCallback(sender, app_data, user_data):
    ds = _loadTable()
    # Get column positions
    colID = (app_data[0][0] - sender - 1) * 2 # Needs to be even, starts at 0
    colIndex = app_data[0][0] - sender - 1 # starts at 0, goes up by one    print(colIndex)
    children = dpg.get_item_info(sender)["children"][1]
    oldList = []
    col2sort = []
    i = 0
    j = 0

    while i < len(children)-(len(ds.columns)*2-1):
        row = []
        # Get column to sort
        col2sort.append(children[i+colID])
        # Get value index
        for val in range(len(ds.columns)*2):
            row.append(children[i+val])

        row.append(j)
        oldList.append(row)
        i+=len(ds.columns)*2
        j+=1

    colvalues = dpg.get_values(col2sort)

    # Allow numeric and character to be sortable
    def col_sorter(e):
        try:
            return float(colvalues[e[len(ds.columns)*2]])
        except ValueError:
            return colvalues[e[len(ds.columns)*2]]
    # Sort
    reverse = False
    if app_data[0][1] < 0:
        reverse = True

    if app_data[0][0] == dpg.get_item_info(sender)["children"][0][colIndex]:
        oldList.sort(key=col_sorter, reverse=reverse)

    single_list = []
    for row in oldList:
        for cell in range(0, len(row)-1):
            single_list.append(row[cell])

    dpg.reorder_items(sender, 1, single_list)

################################################################################
# Functions transactions window
################################################################################
#===============================================================================
# API Sync
#===============================================================================
def _sync(sender, add_data, user_data):
    siteSync = dpg.get_item_label(sender)
    with dpg.window(label="Syncing...", modal=True, pos=(600, 500), no_close=True) as syncWindow: 
        with open('jsonUser/APIkeys.json') as json_file:
            apiKeys = json.load(json_file)
        dpg.add_loading_indicator(style=1, color=(150, 240, 240, 250))
        if siteSync == "Binance.US Sync":
            site = "Binance"
            api_key = apiKeys[site]['key']
            api_secret = apiKeys[site]['secret']
            apiBinance(api_key, api_secret)        
        elif siteSync == "Celsius Sync":
            site = "Celsius"
            api_key = apiKeys[site]['key']
            api_secret = apiKeys[site]['secret']
            apiCelsius(api_key, api_secret)
        elif siteSync == "Coinbase Sync":
            site = "Coinbase"
            api_key = apiKeys[site]['key']
            api_secret = apiKeys[site]['secret']
            apiCoinbase(api_key, api_secret)
        elif siteSync == "CoinbasePro Sync":
            site = "Coinbase Pro"
            api_key = apiKeys[site]['key']
            api_secret = apiKeys[site]['secret']
            passphrase = apiKeys[site]['passphrase']
            apiCoinbasePro(api_key, api_secret, passphrase)
        elif siteSync == "Gemini Sync":
            site = "Gemini"
            api_key = apiKeys[site]['key']
            api_secret = apiKeys[site]['secret']
            apiGemini(api_key, api_secret) 
        elif siteSync == "Summarize All":
            cryptoSum("summaries/")
        else:
            print("error")
    txnSum()
    _refresh()
    dpg.configure_item(syncWindow, show=False)   
    print("Done")
     
#===============================================================================
# Upload file
#===============================================================================
def _readFile(sender, add_data, user_data):
    site = user_data
    fpath = add_data['current_path']
    fname = list(add_data['selections'])
    fLength = len(fname)
    for i in range(fLength):
        tempPath = (fpath + "/" + fname[i])
        outName=("temp/" + site + "_temp" + str(i) + ".csv")
        if site == "blockfi":
            uploadBlockFi(tempPath, outName)
            mergeTemp(site)
        elif site == "cdc":
            uploadCDC(tempPath, outName)
            mergeTemp(site)
        elif site == "geminiEarn":
            uploadGeminiEarn(tempPath, outName)
            mergeTemp(site)
        elif site == "lednBTC":
            uploadLednBTC(tempPath, outName)
            mergeTemp(site)
        elif site == "uphold":
            uploadUphold(tempPath, outName)
            mergeTemp(site)
        else: 
            print("error")
    txnSum()
    _refresh()
    print("Done")

def _chooseFile(sender, add_data, user_data):
    site=user_data
    with dpg.file_dialog(label="Choose File(s) to Sync", user_data=site, callback=_readFile):
        dpg.add_file_extension(".*", color=(255, 255, 255, 255))

#===============================================================================
# Add Manually
#===============================================================================
def _manualBUY(sender, add_data, user_data):
    txnData = {}
    txnData['Exchange'] = dpg.get_value(("exchange"+str(user_data)))
    # Get calendar date
    date = dpg.get_value(("date"+str(user_data)))
    year = date['year'] - 100 + 2000
    month = date['month'] + 1
    day = date['month_day']
    # Get time
    time = dpg.get_value(("time"+str(user_data)))
    hour = "{:02d}".format(time['hour'])
    min = "{:02d}".format(time['min'])
    sec = "{:02d}".format(time['sec'])
    txnData['Date'] = (str(year) + "-" + str(month) + "-" + str(day)+" "+str(hour)+":"+str(min)+":"+str(sec))
    txnData['Symbol'] = dpg.get_value(("symbol"+str(user_data))).strip()
    txnData['Amount'] = float(dpg.get_value(("amount"+str(user_data))))
    txnData['Cost_Basis'] = float(dpg.get_value(("price"+str(user_data))))
    txnData['Total_Spent'] = round(txnData['Amount'] * txnData['Cost_Basis'], 2)
    txnData['Type'] = "BUY"
    temp = pd.DataFrame.from_dict(txnData, orient='index').T
    sumFile = 'summaries/manualTxns.csv'
    mergeNames = list(temp.columns)
    if os.path.isfile(sumFile) == True:
        final = pd.read_csv(sumFile)
        final = pd.merge(final,temp,on=mergeNames,how='outer')
        final.to_csv(sumFile, index=False)
    else:
        temp.to_csv(sumFile, index=False)
    txnSum()
    _refresh()
    dpg.configure_item(user_data, show=False)   

def _manualSELL(sender, add_data, user_data):
    txnData = {}
    txnData['Exchange'] = dpg.get_value(("exchange"+str(user_data)))
    # Get calendar date
    date = dpg.get_value(("date"+str(user_data)))
    year = date['year'] - 100 + 2000
    month = date['month'] + 1
    day = date['month_day']
    # Get time
    time = dpg.get_value(("time"+str(user_data)))
    hour = "{:02d}".format(time['hour'])
    min = "{:02d}".format(time['min'])
    sec = "{:02d}".format(time['sec'])
    txnData['Date'] = (str(year) + "-" + str(month) + "-" + str(day)+" "+str(hour)+":"+str(min)+":"+str(sec))
    txnData['Symbol'] = dpg.get_value(("symbol"+str(user_data))).strip()
    txnData['Amount'] = -float(dpg.get_value(("amount"+str(user_data))))
    txnData['Cost_Basis'] = float(dpg.get_value(("price"+str(user_data))))
    txnData['Total_Spent'] = round(txnData['Amount'] * txnData['Cost_Basis'], 2)
    txnData['Type'] = "SELL"
    temp = pd.DataFrame.from_dict(txnData, orient='index').T
    sumFile = 'summaries/manualTxns.csv'
    mergeNames = list(temp.columns)
    if os.path.isfile(sumFile) == True:
        final = pd.read_csv(sumFile)
        final = pd.merge(final,temp,on=mergeNames,how='outer')
        final.to_csv(sumFile, index=False)
    else:
        temp.to_csv(sumFile, index=False)
    txnSum()
    _refresh()
    dpg.configure_item(user_data, show=False)   

def _manualFEE(sender, add_data, user_data):
    txnData = {}
    txnData['Exchange'] = dpg.get_value(("exchange"+str(user_data)))
    # Get calendar date
    date = dpg.get_value(("date"+str(user_data)))
    year = date['year'] - 100 + 2000
    month = date['month'] + 1
    day = date['month_day']
    # Get time
    time = dpg.get_value(("time"+str(user_data)))
    hour = "{:02d}".format(time['hour'])
    min = "{:02d}".format(time['min'])
    sec = "{:02d}".format(time['sec'])
    txnData['Date'] = (str(year) + "-" + str(month) + "-" + str(day)+" "+str(hour)+":"+str(min)+":"+str(sec))
    txnData['Symbol'] = dpg.get_value(("symbol"+str(user_data))).strip()
    txnData['Amount'] = -float(dpg.get_value(("amount"+str(user_data))))   
    txnData['Cost_Basis'] = float(0)
    txnData['Total_Spent'] = float(0)
    txnData['Type'] = manualData[dpg.get_value(("reason"+str(user_data)))]
    temp = pd.DataFrame.from_dict(txnData, orient='index').T
    sumFile = 'summaries/manualTxns.csv'
    mergeNames = list(temp.columns)
    if os.path.isfile(sumFile) == True:
        final = pd.read_csv(sumFile)
        final = pd.merge(final,temp,on=mergeNames,how='outer')
        final.to_csv(sumFile, index=False)
    else:
        temp.to_csv(sumFile, index=False)
    txnSum()
    _refresh()
    dpg.configure_item(user_data, show=False)   

def _manualINTEREST(sender, add_data, user_data):
    txnData = {}
    txnData['Exchange'] = dpg.get_value(("exchange"+str(user_data)))
    # Get calendar date
    date = dpg.get_value(("date"+str(user_data)))
    year = date['year'] - 100 + 2000
    month = date['month'] + 1
    day = date['month_day']
    # Get time
    time = dpg.get_value(("time"+str(user_data)))
    hour = "{:02d}".format(time['hour'])
    min = "{:02d}".format(time['min'])
    sec = "{:02d}".format(time['sec'])
    txnData['Date'] = (str(year) + "-" + str(month) + "-" + str(day)+" "+str(hour)+":"+str(min)+":"+str(sec))
    txnData['Symbol'] = dpg.get_value(("symbol"+str(user_data))).strip()
    txnData['Amount'] = float(dpg.get_value(("amount"+str(user_data))))   
    txnData['Cost_Basis'] = float(0)
    txnData['Total_Spent'] = float(0)
    txnData['Type'] = "INTEREST"
    temp = pd.DataFrame.from_dict(txnData, orient='index').T
    sumFile = 'summaries/manualTxns.csv'
    mergeNames = list(temp.columns)
    if os.path.isfile(sumFile) == True:
        final = pd.read_csv(sumFile)
        final = pd.merge(final,temp,on=mergeNames,how='outer')
        final.to_csv(sumFile, index=False)
    else:
        temp.to_csv(sumFile, index=False)
    txnSum()
    _refresh()
    dpg.configure_item(user_data, show=False) 

def _manualSWAP(sender, add_data, user_data):
    start = {}
    end = {}
    # Get calendar date
    date = dpg.get_value(("date"+str(user_data)))
    year = date['year'] - 100 + 2000
    month = date['month'] + 1
    day = date['month_day']
    # Get time
    time = dpg.get_value(("time"+str(user_data)))
    hour = "{:02d}".format(time['hour'])
    min = "{:02d}".format(time['min'])
    sec = "{:02d}".format(time['sec'])
    # start
    start['Date'] = (str(year) + "-" + str(month) + "-" + str(day)+" "+str(hour)+":"+str(min)+":"+str(sec))
    start['Symbol'] = dpg.get_value(("startSymbol"+str(user_data))).strip()
    start['Amount'] = float(dpg.get_value(("startAmount"+str(user_data))))   
    start = pd.DataFrame.from_dict(start, orient='index').T
    # end
    end['Date'] = (str(year) + "-" + str(month) + "-" + str(day)+" "+str(hour)+":"+str(min)+":"+str(sec))
    end['Symbol'] = dpg.get_value(("endSymbol"+str(user_data))).strip()
    end['Amount'] = float(dpg.get_value(("endAmount"+str(user_data))))   
    end = pd.DataFrame.from_dict(end, orient='index').T
    # merged
    txns = start.append(end)
    txns['Exchange'] = dpg.get_value(("exchange"+str(user_data)))
    txns['Cost_Basis'] = float(0)
    txns['Total_Spent'] = float(0)
    txns['Type'] = "SWAP"
    txns = txns[['Exchange', 'Date', 'Symbol', 'Amount', 'Cost_Basis', 'Total_Spent', 'Type']]
    sumFile = 'summaries/manualTxns.csv'
    mergeNames = list(txns.columns)
    if os.path.isfile(sumFile) == True:
        final = pd.read_csv(sumFile)
        final = pd.merge(final,txns,on=mergeNames,how='outer')
        final.to_csv(sumFile, index=False)
    else:
        txns.to_csv(sumFile, index=False)
    txnSum()
    _refresh()
    dpg.configure_item(user_data, show=False) 

def _addManual(sender, add_data, user_data):
    addTxn = user_data
    now = datetime.now()
    # Get current date and time
    current_year = int(now.strftime("%y")) + 100
    current_month = int(now.strftime("%m")) - 1 # python indexes at 0
    current_day = int(now.strftime("%d"))
    current_hour =  int(now.strftime("%H"))
    current_minute = int(now.strftime("%M"))
    if addTxn == "BUY":
        with dpg.window(label="Add Buy", modal=True, pos=(600, 300)) as manualWindow: 
            dpg.add_date_picker(id=("date"+str(manualWindow)), default_value={'month_day': current_day, 'year': current_year, 'month':current_month})
            dpg.add_time_picker(id=("time"+str(manualWindow)), default_value={'hour': current_hour, 'min': current_minute, 'sec': 00}, hour24=True)
            dpg.add_combo(id=("exchange"+str(manualWindow)), width = 100, label = "Exchange", items=manualData['sites'])
            dpg.add_input_text(id=("symbol"+str(manualWindow)), width = 100, label="Symbol")
            dpg.add_input_text(id=("amount"+str(manualWindow)), width = 100, label="Amount")
            dpg.add_input_text(id=("price"+str(manualWindow)), width = 100, label="Purchase Price")
            dpg.add_button(label="Submit", width=75, callback=_manualBUY, user_data=manualWindow)
            dpg.add_same_line()
            dpg.add_button(label="Cancel", width=75, callback=lambda: dpg.configure_item(manualWindow, show=False))
    elif addTxn == "SELL":
        with dpg.window(label="Add Sell", modal=True, pos=(600, 300)) as manualWindow: 
            dpg.add_date_picker(id=("date"+str(manualWindow)), default_value={'month_day': current_day, 'year': current_year, 'month':current_month})
            dpg.add_time_picker(id=("time"+str(manualWindow)), default_value={'hour': current_hour, 'min': current_minute, 'sec': 00}, hour24=True)
            dpg.add_combo(id=("exchange"+str(manualWindow)), width = 100, label = "Exchange", items=manualData['sites'])
            dpg.add_input_text(id=("symbol"+str(manualWindow)), width = 100, label="Symbol")
            dpg.add_input_text(id=("amount"+str(manualWindow)), width = 100, label="Amount")
            dpg.add_input_text(id=("price"+str(manualWindow)), width = 100, label="Purchase Price")
            dpg.add_button(label="Submit", width=75, callback=_manualSELL, user_data=manualWindow)
            dpg.add_same_line()
            dpg.add_button(label="Cancel", width=75, callback=lambda: dpg.configure_item(manualWindow, show=False))
    elif addTxn == "FEE":
        with dpg.window(label="Add Sell", modal=True, pos=(600, 300)) as manualWindow: 
            dpg.add_date_picker(id=("date"+str(manualWindow)), default_value={'month_day': current_day, 'year': current_year, 'month':current_month})
            dpg.add_time_picker(id=("time"+str(manualWindow)), default_value={'hour': current_hour, 'min': current_minute, 'sec': 00}, hour24=True)
            dpg.add_combo(id=("exchange"+str(manualWindow)), width = 100, label = "Exchange", items=manualData['sites'])
            dpg.add_input_text(id=("symbol"+str(manualWindow)), width = 100, label="Symbol")
            dpg.add_input_text(id=("amount"+str(manualWindow)), width = 100, label="Amount")
            dpg.add_combo(id=("reason"+str(manualWindow)), items=("Sending Fee", "Other"), width = 100, label = "Description")
            dpg.add_button(label="Submit", callback=_manualFEE, user_data=manualWindow) 
            dpg.add_same_line()
            dpg.add_button(label="Cancel", width=75, callback=lambda: dpg.configure_item(manualWindow, show=False))
    elif addTxn == "INTEREST":
        with dpg.window(label="Add Interest", modal=True, pos=(600, 300)) as manualWindow: 
            dpg.add_date_picker(id=("date"+str(manualWindow)), default_value={'month_day': current_day, 'year': current_year, 'month':current_month})
            dpg.add_time_picker(id=("time"+str(manualWindow)), default_value={'hour': current_hour, 'min': current_minute, 'sec': 00}, hour24=True)
            dpg.add_combo(id=("exchange"+str(manualWindow)), width = 100, label = "Exchange", items=manualData['sites'])
            dpg.add_input_text(id=("symbol"+str(manualWindow)), width = 100, label="Symbol")
            dpg.add_input_text(id=("amount"+str(manualWindow)), width = 100, label="Amount")
            dpg.add_button(label="Submit", callback=_manualINTEREST, user_data=manualWindow)
            dpg.add_same_line()
            dpg.add_button(label="Cancel", width=75, callback=lambda: dpg.configure_item(manualWindow, show=False))
    elif addTxn == "SWAP":
        with dpg.window(label="Add Interest", modal=True, pos=(600, 300)) as manualWindow: 
            dpg.add_date_picker(id=("date"+str(manualWindow)), default_value={'month_day': current_day, 'year': current_year, 'month':current_month})
            dpg.add_time_picker(id=("time"+str(manualWindow)), default_value={'hour': current_hour, 'min': current_minute, 'sec': 00}, hour24=True)
            dpg.add_combo(id=("exchange"+str(manualWindow)), width = 100, label = "Exchange", items=manualData['sites'])
            dpg.add_input_text(id=("startSymbol"+str(manualWindow)), width = 100, label="Start Token (Symbol)")
            dpg.add_input_text(id=("startAmount"+str(manualWindow)), width = 100, label="Start Amount (in Crypto)")
            dpg.add_text("To:")        
            dpg.add_input_text(id=("endSymbol"+str(manualWindow)), width = 100, label="End Token (Symbol)")
            dpg.add_input_text(id=("endAmount"+str(manualWindow)), width = 100, label="End Amount (in Crypto")
            dpg.add_button(label="Submit", callback=_manualSWAP, user_data=manualWindow)
            dpg.add_same_line()
            dpg.add_button(label="Cancel", width=75, callback=lambda: dpg.configure_item(manualWindow, show=False))
    else:
        print("error")

################################################################################
# Add API
################################################################################
def _commitAPI(sender, add_data, user_data):
    exchange = user_data
    apiData = {}
    apiData[exchange] = {}
    apiData[exchange]['site'] = user_data
    apiData[exchange]['key'] = dpg.get_value(("key"+user_data))
    apiData[exchange]['secret'] = dpg.get_value(("secret"+user_data))
    apiData[exchange]['passphrase'] = dpg.get_value(("passphrase"+user_data)) 
    if os.path.isfile("jsonUser/APIkeys.json") == True:
        with open('jsonUser/APIkeys.json') as json_file:
            data = json.load(json_file)
            data.update(apiData)
        with open('jsonUser/APIkeys.json', 'w') as outfile:
            json.dump(data, outfile, indent=4)
    else:     
        with open('jsonUser/APIkeys.json', 'w') as outfile:
            json.dump(apiData, outfile, indent=4)
    apiData.clear()

def _add2API(site):
    dpg.add_text("Fill in API info")
    dpg.add_input_text(id=("key"+site), label="Key")
    dpg.add_input_text(id=("secret"+site), label= "Secret")
    dpg.add_separator()
    dpg.add_button(label="OK", width=75, user_data=site, callback=_commitAPI)

def _add3API(site):
    dpg.add_text("Fill in API info")
    dpg.add_input_text(id=("key"+site), label = "Key")
    dpg.add_input_text(id=("secret"+site), label="Secret")
    dpg.add_input_text(id=("passphrase"+site),  label="Passphrase")
    dpg.add_separator()
    dpg.add_button(label="OK", width=75, user_data=site, callback=_commitAPI)

################################################################################
# Columns
################################################################################
def get_key(val, myDict):
    for key, value in myDict.items():
        if val == value:
            return key

def _colUpdate(sender, add_data, user_data):
    value = dpg.get_item_label(sender)
    available = "available"
    selected = "selected"
    unselected = "unselected"
    if dpg.get_value(sender) == True:
        with open('jsonApp/sumCols.json') as json_file:
            data = json.load(json_file)
        # Add value
        keyID = get_key(value, data[available])
        colUpdate = {keyID: value}
        data[selected].update(colUpdate)
        # Remove
        del data[unselected][keyID]
        with open('jsonApp/sumCols.json', 'w') as outfile:
            json.dump(data, outfile, indent=4)    
    elif dpg.get_value(sender) == False:
        with open('jsonApp/sumCols.json') as json_file:
            data = json.load(json_file)
        # Add value
        keyID = get_key(value, data[available])
        colUpdate = {keyID: value}
        data[unselected].update(colUpdate)
        # Remove
        del data[selected][keyID]
        with open('jsonApp/sumCols.json', 'w') as outfile:
            json.dump(data, outfile, indent=4)
    _refresh()    
    _colRefresh()

def _colRefresh():
    dpg.delete_item(colPick, children_only=True)  
    with open('jsonApp/sumCols.json') as json_file:
        data = json.load(json_file)
    selected = data['selected']
    unselected = data['unselected']
    for val in selected.values():
        _colSelector(val, True)
    for val in unselected.values():
        _colSelector(val, False)
    print("done")

def _colSelector(val, bool):
    dpg.add_checkbox(label=val, callback=_colUpdate, default_value=bool, parent=colPick)

################################################################################
# App
################################################################################
buttonWidth=250
with dpg.window(label="Portfolio Summary", no_close=True) as portfolioSummary:
    summaryTable = dpg.generate_uuid()
    tableData = dpg.generate_uuid()
    with dpg.menu_bar():
        with dpg.menu(label="File"):
            dpg.add_menu_item(label="Update Prices", callback=_refreshAll)
            dpg.add_menu_item(label="Export Summary", callback=_exportSum)
            dpg.add_menu_item(label="Export Detailed", callback=_exportDet)
    with dpg.child(label="summaryLabel", height=60, border=False) as folioStats:
        fileCheck = 'jsonUser/portfolioSum.json'
        if os.path.isfile(fileCheck) == True:
            with open('jsonUser/portfolioSum.json') as json_file:
                    folio = json.load(json_file)
            dpg.add_text("Portfolio Summary:", parent = folioStats)
            dpg.add_text(("Total Spent($): " + str(round(folio['total_spent'], 2)) +
                        "   " +
                        "Total Value($): " + str(round(folio['total_value'], 2)) +
                        "   " +                
                        "Total Gain/Loss($): " + str(round(folio['total_GL'], 2)) +
                        "   " +                
                        "Total Gain/Loss(%): " + str(round(folio['total_pctGL']*100, 2))),
                        parent = folioStats)
        else:
            dpg.add_text("Import transactions to view summary")         

    with dpg.child(label="table", horizontal_scrollbar=True):
        with dpg.table(id=summaryTable,
                    header_row=True, 
                    policy=dpg.mvTable_SizingFixedFit,
                    reorderable=True,
                    resizable=True,
                    sortable=True, 
                    callback=_sortCallback,
                    scrollY=True, 
                    scrollX=True,
                    delay_search=True,
                    freeze_rows=1, 
                    freeze_columns=1, 
                    no_host_extendX=True, 
                    row_background=True,
                    borders_innerH=True, 
                    borders_outerH=True, 
                    borders_innerV=True,
                    borders_outerV=True) as tbl_id:
            fileCheck = 'jsonUser/portfolioSum.json'
            if os.path.isfile(fileCheck) == True:
                ds = _loadTable()
                for i in range(len(ds.columns)):
                    col = ds.columns[i]
                    dpg.add_table_column(label=col, parent=tbl_id, id=(tableData+i))

                for i in range(len(ds.index)):
                    for j in range(len(ds.columns)):
                        colname = ds.columns[j]
                        value = ds[colname].iloc[i]
                        dpg.add_text(value, parent=tbl_id)
                        dpg.add_table_next_column(parent=tbl_id)
            else:
                dpg.add_text("")         

pass

with dpg.window(label="Update Transactions", id = "txnupdate", no_close=True):
    selectedColumn = dpg.generate_uuid()
    manualWindow = dpg.generate_uuid()
    with dpg.tab_bar():
        with dpg.tab(label="Sync"):
            now = datetime.now()
            # Get current date and time
            current_year = int(now.strftime("%y")) + 100
            current_month = int(now.strftime("%m")) - 1 # python indexes at 0
            current_day = int(now.strftime("%d"))
            current_hour =  int(now.strftime("%H"))
            current_minute = int(now.strftime("%M"))
            dpg.add_dummy(height=5)
            dpg.add_text("Sync with API:")
            dpg.add_button(label="Binance.US Sync", width=buttonWidth, height=30, callback=_sync)
            dpg.add_button(label="Celsius Sync", width=buttonWidth, height=30, callback=_sync)
            dpg.add_button(label="Coinbase Sync", width=buttonWidth, height=30, callback=_sync)
            dpg.add_button(label="CoinbasePro Sync", width=buttonWidth, height=30, callback=_sync)
            dpg.add_button(label="Gemini Sync", width=buttonWidth, height=30, callback=_sync)
            dpg.add_dummy(height=10)
            dpg.add_separator()
            dpg.add_separator()
            dpg.add_dummy(height=10)    
            dpg.add_text("Upload Statement:")        
            dpg.add_button(label="Upload Blockfi Statement", user_data="blockfi", width=buttonWidth, height=30, callback=_chooseFile)
            dpg.add_button(label="Upload Crypto.com Statement", user_data="cdc", width=buttonWidth, height=30, callback=_chooseFile)
            dpg.add_button(label="Upload Gemini Earn Statement", user_data="geminiEarn", width=buttonWidth, height=30, callback=_chooseFile)
            dpg.add_button(label="Upload Ledn Bitcoin Statement", user_data="lednBTC", width=buttonWidth, height=30, callback=_chooseFile)
            dpg.add_button(label="Upload Uphold Statement", user_data="uphold", width=buttonWidth, height=30, callback=_chooseFile)
            dpg.add_dummy(height=10)
            dpg.add_separator()
            dpg.add_separator()
            dpg.add_dummy(height=10)    
            dpg.add_text("Add transaction manually:")         
            dpg.add_button(label="Add Buy", user_data="BUY", width=buttonWidth, height=30, callback=_addManual)
            dpg.add_button(label="Add Sell", user_data="SELL", width=buttonWidth, height=30, callback=_addManual)
            dpg.add_button(label="Add Fee", user_data="FEE", width=buttonWidth, height=30, callback=_addManual)
            dpg.add_button(label="Add Interest", user_data="INTEREST", width=buttonWidth, height=30, callback=_addManual)
            dpg.add_button(label="Add Swap", user_data="SWAP", width=buttonWidth, height=30, callback=_addManual)
  
 
        with dpg.tab(label="Choose columns") as colPick:
            with open('jsonApp/sumCols.json') as json_file:
                data = json.load(json_file)
            selected = data['selected']
            unselected = data['unselected']
            for val in selected.values():
                _colSelector(val, True)
            for val in unselected.values():
                _colSelector(val, False)
        with dpg.tab(label="Options"):
            dpg.add_text("Add API keys:")        
            with dpg.tree_node(label="Add Binance.US"):
                _add2API(site='Binance')
            with dpg.tree_node(label="Add Celsius"):
                _add2API(site='Celsius')
            with dpg.tree_node(label="Add Coinbase"):
                _add2API(site='Coinbase')
            with dpg.tree_node(label="Add Coinbase Pro"):
                _add3API(site='Coinbase Pro')       
            with dpg.tree_node(label="Add Gemini"):
                _add2API(site='Gemini') 
            dpg.add_dummy(height=10)
            dpg.add_separator()
            dpg.add_separator()
            dpg.add_dummy(height=10)    
            dpg.add_text("Delete:")  
            dpg.add_button(label="Delete API Keys", width=buttonWidth, height=30, callback=_deleteAPIs)   
            dpg.add_text("Delete transactions:")  
            dpg.add_combo(items=manualData['summaries'], width = 100, id="summaryDelete")
            dpg.add_same_line()
            dpg.add_button(label="Delete", width=142, height=30, callback=_deleteCSV) 
            dpg.add_button(label="Delete All Transactions", width=buttonWidth, height=30, callback=_deleteTxns)     
       
pass


with dpg.window(label="Temporary Window"):
    dpg.add_button(label="Save Ini File", callback=lambda: dpg.save_init_file("custom_layout.ini"))

dpg.start_dearpygui()