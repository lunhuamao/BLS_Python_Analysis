import pandas as pd
import numpy as np
import os
import subprocess
import math
import matplotlib.pyplot as plt
from scipy.interpolate import *
from plyntywidgets import *
from blsFunctions import *
print("Dependencies Loaded...")


# creating income brackets that have a certain number of CUs in them
def createSizedIncomeBrackets(incomeBrackets, df, numCUs):
    x = 0

    while True:
        try:
            lowValue = incomeBrackets[x]
            highValue = incomeBrackets[x+1]
        except IndexError:
            break
        if len(df.loc[(df['FINCBTAX'] >= lowValue) & (df['FINCBTAX'] < highValue)]) < numCUs:
            if highValue == incomeBrackets[-1]:
                incomeBrackets.remove(lowValue)
            else:
                incomeBrackets.remove(highValue)
        else:
            x += 1

perferedNumIncomeBrackets = 9
minNumOfCUs = 150
significanceLevel = 0.005

year = "15"
filesToRead = ["fmli", "mtbi"]
minAge = 60
maxAge = 75

# directory in which the diary and interview folders are held is located
diaryDir = "/Users/adyke/Vizuri/CE_PUMD/diary15/"
interviewDir = "/Users/adyke/Vizuri/CE_PUMD/intrvw15/"

# Directory where stubfiles are located
pathToStubFileDir = "/Users/adyke/Vizuri/Stubfiles/"
rScriptStubfilePathAndName = "/Users/adyke/Vizuri/BLS_Python_Analysis/creatingStubCsvs.R"

# Filenames of the Stubfiles
IStubFileName = "IStub2015.txt"
DStubFileName = "DStub2015.txt"
IntStubFileName = "IntStub2015.txt"

# name of interview dir within the interview dir
insideIntrvwDirName = "intrvw"

# name of the directory where you want the output percentages csv
outputDir = "/Users/adyke/Vizuri/outputFiles/"

if(len(filesToRead)==0):
    print("The files to read variable is empty.")

# looping through each file to read
for file in filesToRead:
    if file == "dtbd" or file == "all" or file == "diary":
        dtbd = readFileSet("dtbd", diaryDir)
    if file == "expd" or file == "all" or file == "diary":
        expd = readFileSet("expd", diaryDir)
    if file == "fmld" or file == "all" or file == "diary":
        fmld = readFileSet("fmld", diaryDir)
    if file == "memd" or file == "all" or file == "diary":
        memd = readFileSet("memd", diaryDir)
    if file == "fmli" or file == "all" or file == "interview":
        fmli = readFileSet("fmli", interviewDir+insideIntrvwDirName+year+"/")
    if file == "itbi" or file == "all" or file == "interview":
        itbi = readFileSet("itbi", interviewDir+insideIntrvwDirName+year+"/")
    if file == "itii" or file == "all" or file == "interview":
        itii = readFileSet("itii", interviewDir+insideIntrvwDirName+year+"/")
    if file == "memi" or file == "all" or file == "interview":
        memi = readFileSet("memi", interviewDir+insideIntrvwDirName+year+"/")
    if file == "mtbi" or file == "all" or file == "interview":
        mtbi = readFileSet("mtbi", interviewDir+insideIntrvwDirName+year+"/")
        mtbi.UCC = mtbi.UCC.astype(str)
    if file == "ntaxi" or file == "all" or file == "interview":
        ntaxi = readFileSet("ntaxi", interviewDir+insideIntrvwDirName+year+"/")
# does not read form the expn or para subdirectories

if os.path.isfile(pathToStubFileDir+"DStub.csv") and os.path.isfile(pathToStubFileDir+"IStub.csv") and os.path.isfile(pathToStubFileDir+"IntStub.csv"):
    print("Stubfiles Exist")
else:
    # converting the stub files via R 
    subprocess.call("Rscript "+rScriptStubfilePathAndName+" "+pathToStubFileDir+" "+IStubFileName+" "+DStubFileName+" "+IntStubFileName, shell=True)
    print("Stubfile Csvs created in "+pathToStubFileDir)

# reading in the stubfiles
# DStub = pd.read_csv(pathToStubFileDir+"DStub.csv")
IStub = pd.read_csv(pathToStubFileDir+"IStub.csv")
# IntStub = pd.read_csv(pathToStubFileDir+"IntStub.csv")

# removing the index from the stufile
# DStub = DStub.drop(DStub.columns[0], axis=1)
IStub = IStub.drop(IStub.columns[0], axis=1)
# IntStub = IntStub.drop(IntStub.columns[0], axis=1)

# replacing * with 0 in the level columns
# DStub.loc[DStub.level == "*", 'level'] = 0
IStub.loc[IStub.level == "*", 'level'] = 0
# IntStub.loc[IntStub.level == "*", 'level'] = 0

monthlyHousing = ["220311","220313","880110","210110","800710","210901","220312","220314","880310","210902"]
monthlyHousing.extend(categoricalUCCRollUp(IStub, ["UTILS"]))

rollupDict = {"iTotalExp":(categoricalUCCRollUp(IStub,["TOTALE"])),
"iFoodAtHome":(categoricalUCCRollUp(IStub, ["FOODHO", "ALCHOM"])),
"iFoodAway":(categoricalUCCRollUp(IStub, ["FOODAW", "ALCAWA"])),
"iHousing":(["220311","220313","880110","210110","800710","210901","220312","220314","880310","210902"]),
"otherHousing":(categoricalUCCRollUp(IStub, ["HOUSIN"], ignoreUCCs = monthlyHousing)),
"iUtilites":(categoricalUCCRollUp(IStub, ["UTILS"])),
"iClothingAndBeauty":(categoricalUCCRollUp(IStub, ["APPARE","PERSCA"])),
"iTransportation":(categoricalUCCRollUp(IStub, ["TRANS"])),
"iHealthcare":(categoricalUCCRollUp(IStub, ["HEALTH"])),
"iEntertainment":(categoricalUCCRollUp(IStub, ["ENTRTA","READIN"])),
"iMiscellaneous":(categoricalUCCRollUp(IStub, ["MISC","TOBACC"])),
"iCharitableAndFamilyGiving":(categoricalUCCRollUp(IStub, ["CASHCO"])),
"iInsurance":(categoricalUCCRollUp(IStub, ["LIFEIN"])),
"iEducation":(categoricalUCCRollUp(IStub, ["EDUCAT"])),
"iHousingPrinciple":(categoricalUCCRollUp(IStub,["MRTPRI"]))}

################################################################################################################################################################################
# there is a multiple of 4 because each survey lasts for 3 months 
# multiplying by 4 gives a estimate for each year (3 * 4 = 12)
mtbiRolledUp = rollUpDataframeDict(mtbi, rollupDict, negativeColumns=["iHousingPrinciple"], multiple=4)
        
mtbiTrimmed = mtbiRolledUp.loc[: , ['NEWID','iTotalExp','iFoodAtHome','iFoodAway','iHousing','otherHousing','iUtilites','iClothingAndBeauty','iTransportation','iHealthcare','iEntertainment','iMiscellaneous','iCharitableAndFamilyGiving','iInsurance','iEducation','iHousingPrinciple']]

# adding up all columns for each new id
iExpensesByNewID = mtbiTrimmed.groupby(['NEWID'],as_index=False).sum()
# removing rows with zero values in key categories
nonZeroColumns = ['iFoodAtHome','iFoodAway','iHousing','iUtilites']
for column in nonZeroColumns:
    iExpensesByNewID = iExpensesByNewID[iExpensesByNewID[column] != 0]
iExpensesByNewID['iHousing'] += iExpensesByNewID['iHousingPrinciple']
iExpensesByNewID['iTotalExp'] += iExpensesByNewID['iHousingPrinciple']

# subsetting for the age bracket
fmliAge = subsetDataframe(dataframe=fmli, columnName="AGE_REF", minValue=minAge, maxValue=maxAge)
fmliAge = fmliAge.reset_index()

fmliFamilyAge = subsetDataframe(dataframe=fmliAge, columnName="FAM_SIZE", minValue = 2, maxValue = 100)
fmliSingleAge = subsetDataframe(dataframe=fmliAge, columnName="FAM_SIZE", minValue = 1)

familyIncomeBrackets = list(range(-10000000, 10000000, 10000))
singleIncomeBrackets = list(range(-10000000, 10000000, 10000))

createSizedIncomeBrackets(familyIncomeBrackets, fmliFamilyAge, minNumOfCUs)
createSizedIncomeBrackets(singleIncomeBrackets, fmliSingleAge, minNumOfCUs)

while len(familyIncomeBrackets)-1 > perferedNumIncomeBrackets or len(singleIncomeBrackets)-1 > perferedNumIncomeBrackets:
    if(len(familyIncomeBrackets)-1 > perferedNumIncomeBrackets):
        # combine family bracket
        fmliFamilyRecoded = binColumn(dataframe=fmliFamilyAge, toBinColumnName="FINCBTXM", binValues=familyIncomeBrackets, binnedColumnName="INCLASS", labels=range(1,len(familyIncomeBrackets)))
        inclassExpensesFamily = pd.merge(left=fmliFamilyRecoded[['NEWID','INCLASS','FINCBTXM']],right=iExpensesByNewID, on=['NEWID'])
        inclassAveragesFamily = round(inclassExpensesFamily.ix[: ,inclassExpensesFamily.columns != 'NEWID'].groupby(['INCLASS'],as_index=False).mean(),2)
        percentagesFamily = inclassAveragesFamily.loc[:,rollupDict.keys()]
        for column in rollupDict.keys():
            percentagesFamily[column] = inclassAveragesFamily[column]/inclassAveragesFamily.iTotalExp
        percentagesFamily['ExpInc'] = inclassAveragesFamily['iTotalExp']/inclassAveragesFamily['FINCBTXM']
        percentagesFamily.ExpInc.ix[percentagesFamily['ExpInc']>1] = 1
        outliersFamily = inclassExpensesFamily.copy()
        outerFenceFamily = []
        for column in outliersFamily.columns[4:len(outliersFamily.columns)-1]:
            Q1 = outliersFamily[column].quantile(0.25)
            Q3 = outliersFamily[column].quantile(0.75)
            IQR = Q3 - Q1
            outerFenceFamily.extend(outliersFamily[outliersFamily[column] < (Q1 - (3 * IQR))].index.tolist())
            outerFenceFamily.extend(outliersFamily[outliersFamily[column] > (Q3 + (3 * IQR))].index.tolist())
        cleanFamily = outliersFamily.drop(outliersFamily.index[outerFenceFamily])
        inclassCleanAveragesFamily = round(cleanFamily.ix[: ,cleanFamily.columns != 'NEWID'].groupby(['INCLASS'],as_index=False).mean(),2)
        # creating new dataframe for the percentages that only includes the plynty categories
        cleanPercentagesFamily = inclassCleanAveragesFamily.loc[:,rollupDict.keys()]
        for column in rollupDict.keys():
            cleanPercentagesFamily[column] = inclassCleanAveragesFamily[column]/inclassCleanAveragesFamily.iTotalExp
        cleanPercentagesFamily['ExpInc'] = inclassCleanAveragesFamily['iTotalExp']/inclassCleanAveragesFamily['FINCBTXM']
        # truncate the max ExpInc
        cleanPercentagesNonTruncatedFamily = cleanPercentagesFamily.copy()
        cleanPercentagesFamily.ExpInc.ix[cleanPercentagesFamily['ExpInc']>1] = 1

        differencesFamily = []
        for row in range(len(cleanPercentagesFamily)-1):
            differenceFamily = 0
            for column in range(len(cleanPercentagesFamily.columns)-1):
                if (cleanPercentagesFamily.ix[:,column].mean() * abs(cleanPercentagesFamily.ix[row,column] - cleanPercentagesFamily.ix[row+1,column])) > significanceLevel:
                    differenceFamily += (cleanPercentagesFamily.ix[:,column].mean() * abs(cleanPercentagesFamily.ix[row,column] - cleanPercentagesFamily.ix[row+1,column]))

            differencesFamily.append(differenceFamily)
        familyIncomeBrackets.remove(familyIncomeBrackets[differencesFamily.index(min(differencesFamily))+1])
        cleanPercentagesFamily.reset_index
    else:
        # combine family bracket
        fmliFamilyRecoded = binColumn(dataframe=fmliFamilyAge, toBinColumnName="FINCBTXM", binValues=familyIncomeBrackets, binnedColumnName="INCLASS", labels=range(1,len(familyIncomeBrackets)))
        inclassExpensesFamily = pd.merge(left=fmliFamilyRecoded[['NEWID','INCLASS','FINCBTXM']],right=iExpensesByNewID, on=['NEWID'])
        inclassAveragesFamily = round(inclassExpensesFamily.ix[: ,inclassExpensesFamily.columns != 'NEWID'].groupby(['INCLASS'],as_index=False).mean(),2)
        percentagesFamily = inclassAveragesFamily.loc[:,rollupDict.keys()]
        for column in rollupDict.keys():
            percentagesFamily[column] = inclassAveragesFamily[column]/inclassAveragesFamily.iTotalExp
        percentagesFamily['ExpInc'] = inclassAveragesFamily['iTotalExp']/inclassAveragesFamily['FINCBTXM']
        percentagesFamily.ExpInc.ix[percentagesFamily['ExpInc']>1] = 1
        outliersFamily = inclassExpensesFamily.copy()
        outerFenceFamily = []
        for column in outliersFamily.columns[4:len(outliersFamily.columns)-1]:
            Q1 = outliersFamily[column].quantile(0.25)
            Q3 = outliersFamily[column].quantile(0.75)
            IQR = Q3 - Q1
            outerFenceFamily.extend(outliersFamily[outliersFamily[column] < (Q1 - (3 * IQR))].index.tolist())
            outerFenceFamily.extend(outliersFamily[outliersFamily[column] > (Q3 + (3 * IQR))].index.tolist())
        cleanFamily = outliersFamily.drop(outliersFamily.index[outerFenceFamily])
        inclassCleanAveragesFamily = round(cleanFamily.ix[: ,cleanFamily.columns != 'NEWID'].groupby(['INCLASS'],as_index=False).mean(),2)
        # creating new dataframe for the percentages that only includes the plynty categories
        cleanPercentagesFamily = inclassCleanAveragesFamily.loc[:,rollupDict.keys()]
        for column in rollupDict.keys():
            cleanPercentagesFamily[column] = inclassCleanAveragesFamily[column]/inclassCleanAveragesFamily.iTotalExp
        cleanPercentagesFamily['ExpInc'] = inclassCleanAveragesFamily['iTotalExp']/inclassCleanAveragesFamily['FINCBTXM']
        # truncate the max ExpInc
        cleanPercentagesNonTruncatedFamily = cleanPercentagesFamily.copy()
        cleanPercentagesFamily.ExpInc.ix[cleanPercentagesFamily['ExpInc']>1] = 1

    if(len(singleIncomeBrackets)-1 > perferedNumIncomeBrackets):
        # combine single bracket
        fmliSingleRecoded = binColumn(dataframe=fmliSingleAge, toBinColumnName="FINCBTXM", binValues=singleIncomeBrackets, binnedColumnName="INCLASS", labels=range(1,len(singleIncomeBrackets)))
        inclassExpensesSingle = pd.merge(left=fmliSingleRecoded[['NEWID','INCLASS','FINCBTXM']],right=iExpensesByNewID, on=['NEWID'])
        inclassAveragesSingle = round(inclassExpensesSingle.ix[: ,inclassExpensesSingle.columns != 'NEWID'].groupby(['INCLASS'],as_index=False).mean(),2)
        percentagesSingle = inclassAveragesSingle.loc[:,rollupDict.keys()]
        for column in rollupDict.keys():
            percentagesSingle[column] = inclassAveragesSingle[column]/inclassAveragesSingle.iTotalExp
        percentagesSingle['ExpInc'] = inclassAveragesSingle['iTotalExp']/inclassAveragesSingle['FINCBTXM']
        percentagesSingle.ExpInc.ix[percentagesSingle['ExpInc']>1] = 1
        outliersSingle = inclassExpensesSingle.copy()
        outerFenceSingle = []
        for column in outliersSingle.columns[4:len(outliersSingle.columns)-1]:
            Q1 = outliersSingle[column].quantile(0.25)
            Q3 = outliersSingle[column].quantile(0.75)
            IQR = Q3 - Q1
            outerFenceSingle.extend(outliersSingle[outliersSingle[column] < (Q1 - (3 * IQR))].index.tolist())
            outerFenceSingle.extend(outliersSingle[outliersSingle[column] > (Q3 + (3 * IQR))].index.tolist())
        cleanSingle = outliersSingle.drop(outliersSingle.index[outerFenceSingle])
        inclassCleanAveragesSingle = round(cleanSingle.ix[: ,cleanSingle.columns != 'NEWID'].groupby(['INCLASS'],as_index=False).mean(),2)
        # creating new dataframe for the percentages that only includes the plynty categories
        cleanPercentagesSingle = inclassCleanAveragesSingle.loc[:,rollupDict.keys()]
        for column in rollupDict.keys():
            cleanPercentagesSingle[column] = inclassCleanAveragesSingle[column]/inclassCleanAveragesSingle.iTotalExp
        cleanPercentagesSingle['ExpInc'] = inclassCleanAveragesSingle['iTotalExp']/inclassCleanAveragesSingle['FINCBTXM']
        # truncate the max ExpInc
        cleanPercentagesNonTruncatedSingle = cleanPercentagesSingle.copy()
        cleanPercentagesSingle.ExpInc.ix[cleanPercentagesSingle['ExpInc']>1] = 1

        differencesSingle = []
        for row in range(len(cleanPercentagesSingle)-1):
            differenceSingle = 0
            for column in range(len(cleanPercentagesSingle.columns)-1):
                if (cleanPercentagesSingle.ix[:,column].mean() * abs(cleanPercentagesSingle.ix[row,column] - cleanPercentagesSingle.ix[row+1,column])) > significanceLevel:
                    differenceSingle += (cleanPercentagesSingle.ix[:,column].mean() * abs(cleanPercentagesSingle.ix[row,column] - cleanPercentagesSingle.ix[row+1,column]))

            differencesSingle.append(differenceSingle)
        singleIncomeBrackets.remove(singleIncomeBrackets[differencesSingle.index(min(differencesSingle))+1])
        cleanPercentagesSingle.reset_index
    else:
        fmliSingleRecoded = binColumn(dataframe=fmliSingleAge, toBinColumnName="FINCBTXM", binValues=singleIncomeBrackets, binnedColumnName="INCLASS", labels=range(1,len(singleIncomeBrackets)))
        inclassExpensesSingle = pd.merge(left=fmliSingleRecoded[['NEWID','INCLASS','FINCBTXM']],right=iExpensesByNewID, on=['NEWID'])
        inclassAveragesSingle = round(inclassExpensesSingle.ix[: ,inclassExpensesSingle.columns != 'NEWID'].groupby(['INCLASS'],as_index=False).mean(),2)
        percentagesSingle = inclassAveragesSingle.loc[:,rollupDict.keys()]
        for column in rollupDict.keys():
            percentagesSingle[column] = inclassAveragesSingle[column]/inclassAveragesSingle.iTotalExp
        percentagesSingle['ExpInc'] = inclassAveragesSingle['iTotalExp']/inclassAveragesSingle['FINCBTXM']
        percentagesSingle.ExpInc.ix[percentagesSingle['ExpInc']>1] = 1
        outliersSingle = inclassExpensesSingle.copy()
        outerFenceSingle = []
        for column in outliersSingle.columns[4:len(outliersSingle.columns)-1]:
            Q1 = outliersSingle[column].quantile(0.25)
            Q3 = outliersSingle[column].quantile(0.75)
            IQR = Q3 - Q1
            outerFenceSingle.extend(outliersSingle[outliersSingle[column] < (Q1 - (3 * IQR))].index.tolist())
            outerFenceSingle.extend(outliersSingle[outliersSingle[column] > (Q3 + (3 * IQR))].index.tolist())
        cleanSingle = outliersSingle.drop(outliersSingle.index[outerFenceSingle])
        inclassCleanAveragesSingle = round(cleanSingle.ix[: ,cleanSingle.columns != 'NEWID'].groupby(['INCLASS'],as_index=False).mean(),2)
        # creating new dataframe for the percentages that only includes the plynty categories
        cleanPercentagesSingle = inclassCleanAveragesSingle.loc[:,rollupDict.keys()]
        for column in rollupDict.keys():
            cleanPercentagesSingle[column] = inclassCleanAveragesSingle[column]/inclassCleanAveragesSingle.iTotalExp
        cleanPercentagesSingle['ExpInc'] = inclassCleanAveragesSingle['iTotalExp']/inclassCleanAveragesSingle['FINCBTXM']
        # truncate the max ExpInc
        cleanPercentagesNonTruncatedSingle = cleanPercentagesSingle.copy()
        cleanPercentagesSingle.ExpInc.ix[cleanPercentagesSingle['ExpInc']>1] = 1

print("Single Income brackets")
print(singleIncomeBrackets)
print("Single Percentage Dataframe")
print(cleanPercentagesSingle)
print()
print("Family Income Brackets")
print(familyIncomeBrackets)
print("Family Percentage Dataframe")
print(cleanPercentagesFamily)


cleanFamily.to_csv("cleanFamily.csv",index=False, encoding='utf-8')
cleanSingle.to_csv("cleanSingle.csv",index=False, encoding='utf-8')
cleanPercentagesFamily.to_csv("cleanPercentagesFamily.csv",index=False, encoding='utf-8')
cleanPercentagesSingle.to_csv("cleanPercentagesSingle.csv",index=False, encoding='utf-8')