import pandas as pd
import numpy as np
import os
import subprocess
import math
import matplotlib.pyplot as plt
from scipy.interpolate import *
# from plyntywidgets import *
from blsFunctions import *

import plotly
import plotly.plotly as py
import plotly.graph_objs as go
plotly.tools.set_credentials_file(username='adyke', api_key='wSGAvFQyxDbbXm8etral')

print("Dependencies Loaded...")

year = "15"
filesToRead = ["fmli", "mtbi"]
singleIncomeBrackets = [-10000000, 15000, 20000, 25000, 30000, 40000, 50000, 65000, 9995000]
familyIncomeBrackets = [-10000000, 5000, 15000, 20000, 25000, 30000, 120000, 145000, 190000, 9995000]
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
DStub = pd.read_csv(pathToStubFileDir+"DStub.csv")
IStub = pd.read_csv(pathToStubFileDir+"IStub.csv")
IntStub = pd.read_csv(pathToStubFileDir+"IntStub.csv")

# removing the index from the stufile
DStub = DStub.drop(DStub.columns[0], axis=1)
IStub = IStub.drop(IStub.columns[0], axis=1)
IntStub = IntStub.drop(IntStub.columns[0], axis=1)

# replacing * with 0 in the level columns
DStub.loc[DStub.level == "*", 'level'] = 0
IStub.loc[IStub.level == "*", 'level'] = 0
IntStub.loc[IntStub.level == "*", 'level'] = 0

# creating UCC rollups for the interview files for plynty categories
iTotalExp = categoricalUCCRollUp(IStub,["TOTALE"])
iFoodAtHome = categoricalUCCRollUp(IStub, ["FOODHO", "ALCHOM"])
iFoodAway = categoricalUCCRollUp(IStub, ["FOODAW", "ALCAWA"])
iHousing = categoricalUCCRollUp(IStub, ["HOUSIN"], ignoreUCCs = categoricalUCCRollUp(IStub, ["UTILS"]))
iUtilites = categoricalUCCRollUp(IStub, ["UTILS"])
iClothingAndBeauty = categoricalUCCRollUp(IStub, ["APPARE","PERSCA"])
iTransportation = categoricalUCCRollUp(IStub, ["TRANS"])
iHealthcare = categoricalUCCRollUp(IStub, ["HEALTH"])
iEntertainment = categoricalUCCRollUp(IStub, ["ENTRTA","READIN"])
iMiscellaneous = categoricalUCCRollUp(IStub, ["MISC","TOBACC"])
iCharitableAndFamilyGiving = categoricalUCCRollUp(IStub, ["CASHCO"])
iInsurance = categoricalUCCRollUp(IStub, ["LIFEIN"])
iEducation = categoricalUCCRollUp(IStub, ["EDUCAT"])
iHousingPrinciple = categoricalUCCRollUp(IStub,["MRTPRI"])


rollupNames = ["iTotalExp","iFoodAtHome","iFoodAway","iHousing","iUtilites","iClothingAndBeauty","iTransportation","iHealthcare","iEntertainment","iMiscellaneous","iCharitableAndFamilyGiving","iInsurance","iEducation","iHousingPrinciple"]
rollups = [iTotalExp,iFoodAtHome,iFoodAway,iHousing,iUtilites,iClothingAndBeauty,iTransportation,iHealthcare,iEntertainment,iMiscellaneous,iCharitableAndFamilyGiving,iInsurance,iEducation,iHousingPrinciple]

mtbiRolledUp = rollUpDataframe(mtbi, rollupNames, rollups, negativeColumns=["iHousingPrinciple"], multiple=4)

mtbiTrimmed = mtbiRolledUp.loc[: , ['NEWID','iTotalExp','iFoodAtHome','iFoodAway','iHousing','iUtilites','iClothingAndBeauty','iTransportation','iHealthcare','iEntertainment','iMiscellaneous','iCharitableAndFamilyGiving','iInsurance','iEducation','iHousingPrinciple']]


# adding up all columns for each new id
iExpensesByNewID = mtbiTrimmed.groupby(['NEWID'],as_index=False).sum()
# removing rows with zero values in key categories
nonZeroColumns = ['iFoodAtHome','iFoodAway','iHousing','iUtilites']
for column in nonZeroColumns:
    iExpensesByNewID = iExpensesByNewID[iExpensesByNewID[column] != 0]
iExpensesByNewID['iHousing'] = iExpensesByNewID['iHousing']+iExpensesByNewID['iHousingPrinciple']

# subsetting for the age bracket
fmliAge = subsetDataframe(dataframe=fmli, columnName="AGE_REF", minValue=minAge, maxValue=maxAge)
fmliAge = fmliAge.reset_index()

fmliFamilyAge = subsetDataframe(dataframe=fmliAge, columnName="FAM_SIZE", minValue = 2, maxValue = 100)
fmliSingleAge = subsetDataframe(dataframe=fmliAge, columnName="FAM_SIZE", minValue = 1)

# creating family and single incomebrackets
fmliFamilyRecoded = binColumn(dataframe=fmliFamilyAge, toBinColumnName="FINCBTXM", binValues=familyIncomeBrackets, binnedColumnName="INCLASS", labels=range(1,len(familyIncomeBrackets)))

fmliSingleRecoded = binColumn(dataframe=fmliSingleAge, toBinColumnName="FINCBTXM", binValues=singleIncomeBrackets, binnedColumnName="INCLASS", labels=range(1,len(singleIncomeBrackets)))

# ### Adding the Income class colum to the ExpensesByNewID dataframe

# In[12]:

# Family
inclassExpensesFamily = pd.merge(left=fmliFamilyRecoded[['NEWID','INCLASS','FINCBTXM']],right=iExpensesByNewID, on=['NEWID'])
# Single
inclassExpensesSingle = pd.merge(left=fmliSingleRecoded[['NEWID','INCLASS','FINCBTXM']],right=iExpensesByNewID, on=['NEWID'])


# ### Averaging the expenditures based on incomebrackets
# inclassAverages is average money spent for each incomeclass

# In[13]:

# Family
inclassAveragesFamily = round(inclassExpensesFamily.ix[: ,inclassExpensesFamily.columns != 'NEWID'].groupby(['INCLASS'],as_index=False).mean(),2)
# Single
inclassAveragesSingle = round(inclassExpensesSingle.ix[: ,inclassExpensesSingle.columns != 'NEWID'].groupby(['INCLASS'],as_index=False).mean(),2)


# ### Converting the Average expenditures for income classes into percentages of expenditures
# percentages is the percent of total expenditure for each category for each incomeclass 

# In[14]:

# creating new dataframe for the percentages that only includes the plynty categories
percentagesFamily = inclassAveragesFamily.loc[:,rollupNames[1:]]
percentagesSingle = inclassAveragesSingle.loc[:,rollupNames[1:]]
for column in rollupNames[1:]:
    percentagesFamily[column] = inclassAveragesFamily[column]/inclassAveragesFamily.iTotalExp
    percentagesSingle[column] = inclassAveragesSingle[column]/inclassAveragesSingle.iTotalExp

# Family
percentagesFamily['ExpInc'] = inclassAveragesFamily['iTotalExp']/inclassAveragesFamily['FINCBTXM']
# Single
percentagesSingle['ExpInc'] = inclassAveragesSingle['iTotalExp']/inclassAveragesSingle['FINCBTXM']

# Family
percentagesFamily.ExpInc.ix[percentagesFamily['ExpInc']>1] = 1
# Single
percentagesSingle.ExpInc.ix[percentagesSingle['ExpInc']>1] = 1


# Family or Single
outliersFamily = inclassExpensesFamily.copy()
outliersSingle = inclassExpensesSingle.copy()

# Family or Single
outerFenceFamily = []
outerFenceSingle = []

for column in outliersFamily.columns[4:len(outliersFamily.columns)-1]:
    # Family or Single
    Q1 = outliersFamily[column].quantile(0.25)
    Q3 = outliersFamily[column].quantile(0.75)
    IQR = Q3 - Q1
    outerFenceFamily.extend(outliersFamily[outliersFamily[column] < (Q1 - (3 * IQR))].index.tolist())
    outerFenceFamily.extend(outliersFamily[outliersFamily[column] > (Q3 + (3 * IQR))].index.tolist())
    
    Q1 = outliersSingle[column].quantile(0.25)
    Q3 = outliersSingle[column].quantile(0.75)
    IQR = Q3 - Q1
    outerFenceSingle.extend(outliersSingle[outliersSingle[column] < (Q1 - (3 * IQR))].index.tolist())
    outerFenceSingle.extend(outliersSingle[outliersSingle[column] > (Q3 + (3 * IQR))].index.tolist())
    
# Family or Single
cleanFamily = outliersFamily.drop(outliersFamily.index[outerFenceFamily])
cleanSingle = outliersSingle.drop(outliersSingle.index[outerFenceSingle])


# ### Creating the percentage output for cleaned dataframe

# In[17]:

# Family
inclassCleanAveragesFamily = cleanFamily.ix[: ,cleanFamily.columns != 'NEWID'].groupby(['INCLASS'],as_index=False).mean()
# creating new dataframe for the percentages that only includes the plynty categories
cleanPercentagesFamily = inclassCleanAveragesFamily.loc[:,rollupNames[1:]]
for column in rollupNames[1:]:
    cleanPercentagesFamily[column] = round(inclassCleanAveragesFamily[column]/inclassCleanAveragesFamily.iTotalExp,3)
cleanPercentagesFamily['ExpInc'] = round(inclassCleanAveragesFamily['iTotalExp']/inclassCleanAveragesFamily['FINCBTXM'],3)
# truncate the max ExpInc
cleanPercentagesNonTruncatedFamily = cleanPercentagesFamily.copy()
cleanPercentagesFamily.ExpInc.ix[cleanPercentagesFamily['ExpInc']>1] = 1
# cleanPercentagesFamily

# Single
inclassCleanAveragesSingle = cleanSingle.ix[: ,cleanSingle.columns != 'NEWID'].groupby(['INCLASS'],as_index=False).mean()
# creating new dataframe for the percentages that only includes the plynty categories
cleanPercentagesSingle = inclassCleanAveragesSingle.loc[:,rollupNames[1:]]
for column in rollupNames[1:]:
    cleanPercentagesSingle[column] = round(inclassCleanAveragesSingle[column]/inclassCleanAveragesSingle.iTotalExp,3)
cleanPercentagesSingle['ExpInc'] = round(inclassCleanAveragesSingle['iTotalExp']/inclassCleanAveragesSingle['FINCBTXM'],3)
# truncate the max ExpInc
cleanPercentagesNonTruncatedSingle = cleanPercentagesSingle.copy()
cleanPercentagesSingle.ExpInc.ix[cleanPercentagesSingle['ExpInc']>1] = 1
# cleanPercentagesSingle



print(cleanPercentagesFamily)
cleanPercentagesFamily.to_csv("familyPercentages.csv")

print(cleanPercentagesSingle)
cleanPercentagesSingle.to_csv("singlePercentages.csv")
