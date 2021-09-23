################################################################################
# Import
################################################################################
import pandas as pd
import glob
import os
################################################################################
# Merge temp files
################################################################################

def mergeTemp(fileRoot):
    fileList = glob.glob('temp/'+ fileRoot +'_temp*', recursive=True)
    
    # Read first file
    df = pd.read_csv(fileList[0])
    mergeNames = list(df.columns)

    for f in fileList[1:len(fileList)]:
        fills = pd.read_csv(f)
        df = pd.merge(df,fills,on=mergeNames,how='outer')

    # Summary file name
    sumFile = 'summaries/'+fileRoot+'.csv'

    if os.path.isfile(sumFile) == True:
        final = pd.read_csv(sumFile)
        final = pd.merge(final,df,on=mergeNames,how='outer')
        final = final.drop_duplicates(subset=None, keep='first', inplace=False)
        final.to_csv(sumFile, index=False)
    else:
        df.to_csv(sumFile, index=False)

    # Clean temp
    fileList = glob.glob('temp/*.csv', recursive=True)
    for filePath in fileList:
        try:
            os.remove(filePath)
        except OSError:
            print("Error while deleting file")


   

