# [2014 interview zip file](https://www.bls.gov/cex/pumd/data/comma/intrvw14.zip)
# 
# [2013 interview zip file](https://www.bls.gov/cex/pumd/data/comma/intrvw13.zip)
# 
# [2015 IntStub file](https://www.bls.gov/cex/pumd/2014/csxintstub.txt)
# 
# [2015 IStub file](https://www.bls.gov/cex/pumd/2014/csxistub.txt)
# 
# [2015 DStub file](https://www.bls.gov/cex/pumd/2014/csxdstub.txt)
# 
# ### This Scripts Goals for Plynty
# - Create an easy to use analysis script for the BLS CE PUMD 
# - Create csv files that has average percentages spent on plynty categories for certain income classes
# - Compare the Family CUs vs the Single person CUs

# #### Importing Dependencies



print("Importing Dependencies")

import pandas as pd
import numpy as np
import os
import subprocess
from copy import deepcopy
import matplotlib.pyplot as plt
from BLSFunctions import *


# # Setting Variables



print("Setting Variables")

years = ["13","14","15"]
filesToRead = ["fmli", "mtbi"]

minAge = 60
maxAge = 75

minNumberCUsIncomeBrackets = 175

bigIncomeBrackets = list(range(-10000000, 9990000, 10000))
familyIncomeBrackets = bigIncomeBrackets
singleIncomeBrackets = bigIncomeBrackets

def createSizedIncomeBrackets(incomeBrackets, fmli, numCUs):
    sizedIncomeBrackets = [incomeBrackets[len(incomeBrackets)-1]]
    # current low and current high are indexes of incomeBrackets
    currentHigh = len(incomeBrackets)-1
    currentLow = currentHigh-1
    while not currentLow == 0:
        if len(getSubsetNEWIDs(dataframe=fmli, columnName="FINCBTXM",minValue = incomeBrackets[currentLow], maxValue = incomeBrackets[currentHigh])) >= numCUs:
            sizedIncomeBrackets.append(incomeBrackets[currentLow])
            currentHigh = currentLow
        currentLow -= 1
    sizedIncomeBrackets.append(incomeBrackets[0])
    sizedIncomeBrackets.sort()
    return(sizedIncomeBrackets)


pumdDir = "./CE_PUMD/"


# # Reading in Stubfiles



print("Reading in Stubfiles")

# Directory where stubfiles are located
pathToStubFileDir = "./Stubfiles/"
rScriptStubfilePathAndName = "./creatingStubCsvs.R"

stubFileDict = {}
stubFileDict["IStub"] =  "IStub2015.txt"
stubFileDict["DStub"] =  "DStub2015.txt"
stubFileDict["IntStub"] =  "IntStub2015.txt"

if os.path.isfile(pathToStubFileDir+"DStub.csv") and os.path.isfile(pathToStubFileDir+"IStub.csv") and os.path.isfile(pathToStubFileDir+"IntStub.csv"):
    print("Stubfiles Exist")
else:
    # converting the stub files via R 
    subprocess.call("Rscript "+rScriptStubfilePathAndName+" "+pathToStubFileDir+" "+stubFileDict["IStub"]+" "+stubFileDict["DStub"]+" "+stubFileDict["IntStub"], shell=True)
    print("Stubfile Csvs created in "+pathToStubFileDir)
    
# reading and cleaning the stubfiles    
for key in stubFileDict.keys():
    stubFileDict[key] = pd.read_csv(pathToStubFileDir+key+".csv")
    stubFileDict[key] = stubFileDict[key].drop(stubFileDict[key].columns[0], axis=1)
    stubFileDict[key].loc[stubFileDict[key].level == "*", 'level'] = 0


# # Creating the Data dictionary
# output:
#    - data (dictionary)
#       - key: filenameYear
#       - value: dataframe



print("Creating the Data dictionary")

data = {}
for year in years:
    yearDir = pumdDir+"intrvw"+year+"/intrvw"+year+"/"
    for file in filesToRead:
        print("Reading "+file+year)
        dataframe = readFileSet(file,yearDir)
        data[file+year] = dataframe
        
fmli = pd.concat([value for key,value in data.items() if 'fmli' in key.lower()], ignore_index=True)


# # Creating Subset NEWID dictionary
# output:
# - subsetNEWIDs
#  - key: Subset Category
#  - value: dictionary or list of NEWIDs associated with the subset

print("Creating subset NEWIDs dictionary")
subsetNEWIDs = {}
subsetNEWIDs["Age"] = []
subsetNEWIDs["Family"] = []
subsetNEWIDs["Single"] = []
subsetNEWIDs["Year"] = {}
subsetNEWIDs["Month"] = {}
subsetNEWIDs["FamilyIncome"] = {}
subsetNEWIDs["SingleIncome"] = {}

# creating empty lists within dictionaries
for month in range(1,13):
    subsetNEWIDs["Month"][month] = []
for year in years:
    subsetNEWIDs["Year"][2000+int(year)] = []
    
# filling in lists
for year in years:
    fmliYear = "fmli"+year
    subsetNEWIDs["Age"].extend(getSubsetNEWIDs(dataframe=data[fmliYear], columnName="AGE_REF", minValue=minAge, maxValue=maxAge))
    subsetNEWIDs["Family"].extend(getSubsetNEWIDs(dataframe=data[fmliYear], columnName="FAM_SIZE", minValue = 2, maxValue = 100))
    subsetNEWIDs["Single"].extend(getSubsetNEWIDs(dataframe=data[fmliYear], columnName="FAM_SIZE", minValue = 1))
    for year1 in years:
        subsetNEWIDs["Year"][2000+int(year1)].extend(getSubsetNEWIDs(dataframe=data[fmliYear], columnName = "QINTRVYR", minValue = 2000+int(year1)))
    for month in subsetNEWIDs["Month"].keys():
        subsetNEWIDs["Month"][month].extend(getSubsetNEWIDs(dataframe=data[fmliYear], columnName = "QINTRVMO",  minValue = month))


# ### Creating Human Readable Income bracket dictionaries

getSingleIncomeBracket = {}
for bracket in subsetNEWIDs["SingleIncome"].keys():
    getSingleIncomeBracket[bracket] = str(singleIncomeBrackets[bracket-1])+"-"+str(singleIncomeBrackets[bracket])

getFamilyIncomeBracket = {}
for bracket in subsetNEWIDs["FamilyIncome"].keys():
    getFamilyIncomeBracket[bracket] = str(familyIncomeBrackets[bracket-1])+"-"+str(familyIncomeBrackets[bracket])

# creating the correctly sized income brackets
print("Creating correctly sized Income brackets")
Single = subsetDictionary(subsetNEWIDs, ["Age","Single","Year"])
sizedIncomeBracketNEWIDs = set()
for newIDset in Single.values():
    sizedIncomeBracketNEWIDs = sizedIncomeBracketNEWIDs.union(newIDset)
singleIncomeBrackets = createSizedIncomeBrackets(singleIncomeBrackets, fmli[fmli.NEWID.isin(sizedIncomeBracketNEWIDs)], minNumberCUsIncomeBrackets)
del singleIncomeBrackets[1]
print("Single, properly sized income brackets are: ")
print(singleIncomeBrackets)

Family = subsetDictionary(subsetNEWIDs, ["Age","Family","Year"])
sizedIncomeBracketNEWIDs = set()
for newIDset in Family.values():
    sizedIncomeBracketNEWIDs = sizedIncomeBracketNEWIDs.union(newIDset)
familyIncomeBrackets = createSizedIncomeBrackets(familyIncomeBrackets, fmli[fmli.NEWID.isin(sizedIncomeBracketNEWIDs)], minNumberCUsIncomeBrackets)
del familyIncomeBrackets[1]
print("Family, properly sized income brackets are: ")
print(familyIncomeBrackets)

for bracket in range(1,len(familyIncomeBrackets)):
    subsetNEWIDs["FamilyIncome"][bracket] = []
for bracket in range(1,len(singleIncomeBrackets)):
    subsetNEWIDs["SingleIncome"][bracket] = []
for year in years:
    fmliYear = "fmli"+year
    for bracket in subsetNEWIDs["FamilyIncome"].keys():
        subsetNEWIDs["FamilyIncome"][bracket].extend(getSubsetNEWIDs(dataframe=data[fmliYear], columnName="FINCBTXM",minValue = familyIncomeBrackets[bracket-1], maxValue = familyIncomeBrackets[bracket]-1))
    for bracket in subsetNEWIDs["SingleIncome"].keys():
        subsetNEWIDs["SingleIncome"][bracket].extend(getSubsetNEWIDs(dataframe=data[fmliYear], columnName="FINCBTXM",minValue = singleIncomeBrackets[bracket-1], maxValue = singleIncomeBrackets[bracket]-1))



# # Subsetting NEWIDs based on SubsetNEWIDs dictionary
# outputs:
# - Single (dictionary)
#  - key: tuple of subset category
#  - value: set of NEWIDs assocaiated with tuple
# - Family (dictionary)
#  - key: tuple of subset category
#  - value: set of NEWIDs assocaiated with tuple



print("Subsetting NEWIDs")

Single = subsetDictionary(subsetNEWIDs, ["Age","Single","Year","Month","SingleIncome"])
Family = subsetDictionary(subsetNEWIDs, ["Age","Family","Year","Month","FamilyIncome"])


# ## Medical Emergencies



print("Medical Emergency analysis")

allSingleNEWIDs = set()
for newIDset in Single.values():
    allSingleNEWIDs = allSingleNEWIDs.union(newIDset)
allFamilyNEWIDs = set()
for newIDset in Family.values():
    allFamilyNEWIDs = allFamilyNEWIDs.union(newIDset)

allNEWIDs = allFamilyNEWIDs.union(allSingleNEWIDs)

# UCC of Hospital
emergencyUCCs = [570111]

mtbi = pd.concat([value for key,value in data.items() if 'mtbi' in key.lower()], ignore_index=True)
subsetMtbi = mtbi[mtbi.NEWID.isin(allNEWIDs)]
subsetMtbi = subsetMtbi[subsetMtbi.UCC.isin(emergencyUCCs)]
subsetMtbi = subsetMtbi.groupby(['NEWID'],as_index=False).sum()
subsetMtbi = subsetMtbi[subsetMtbi.COST > 300]
oneTimeSubsetMtbi = subsetMtbi[subsetMtbi.REF_YR < 3000]
print("The Hospital expense max value is: "+str(round(oneTimeSubsetMtbi.COST.max(),2)))
print("The Hospital expense mean value is: "+str(round(oneTimeSubsetMtbi.COST.mean(),2)))


# # Creating Categorical UCC rollups
# outputs:
# - rollupDict (dictionary)
#  - key: Rollup category name
#  - value: list of NEWIDs associated with rollup



print("Creating Categorical UCC rollups")

MonthlyHousing = ["220311","220313","880110","210110","800710","210901","220312","220314","880310","210902","220211","230901","340911","220901","220212","230902","340912","220902","210310"]
MonthlyHousing.extend(categoricalUCCRollUp(stubFileDict["IStub"], ["UTILS"]))

rollupDict = {"TotalExp":(categoricalUCCRollUp(stubFileDict["IStub"],["TOTALE"])),
"FoodAtHome":(categoricalUCCRollUp(stubFileDict["IStub"], ["FOODHO", "ALCHOM"])),
"FoodAway":(categoricalUCCRollUp(stubFileDict["IStub"], ["FOODAW", "ALCAWA"])),
"Housing":(["220311","220313","880110","210110","800710","210901","220312","220314","880310","210902","220211","230901","340911","220901","220212","230902","340912","220902","210310"]),
"OtherHousing":(categoricalUCCRollUp(stubFileDict["IStub"], ["HOUSIN"], ignoreUCCs = MonthlyHousing)),
"Utilities":(categoricalUCCRollUp(stubFileDict["IStub"], ["UTILS"])),
"ClothingAndBeauty":(categoricalUCCRollUp(stubFileDict["IStub"], ["APPARE","PERSCA"])),
"Transportation":(categoricalUCCRollUp(stubFileDict["IStub"], ["TRANS"])),
"Healthcare":(categoricalUCCRollUp(stubFileDict["IStub"], ["HEALTH"])),
"Entertainment":(categoricalUCCRollUp(stubFileDict["IStub"], ["ENTRTA","READIN"])),
"Miscellaneous":(categoricalUCCRollUp(stubFileDict["IStub"], ["MISC","TOBACC"])),
"CharitableAndFamilyGiving":(categoricalUCCRollUp(stubFileDict["IStub"], ["CASHCO"])),
"Insurance":(categoricalUCCRollUp(stubFileDict["IStub"], ["LIFEIN"])),
"Education":(categoricalUCCRollUp(stubFileDict["IStub"], ["EDUCAT"])),
"HousingPrinciple":(categoricalUCCRollUp(stubFileDict["IStub"],["MRTPRI"]))}

# converting rollupDict to ints
for key,value in rollupDict.items():
    rollupDict[key] = list(map(int, value))


# # Rolling up MTBI files into plynty categories
# - creates columns in the mtbi files that correspond with the rollup categories
# - fills new rollup columns based on mtbi observations



print("Rolling up MTBI files into Plynty Categories")

negativeColumns = ["HousingPrinciple"]
multiple = 1
for dataframe in [key for key in data.keys() if 'mtbi' in key.lower()]:
    for key,value in rollupDict.items():
        if(key in negativeColumns):
            multiple *= -1
        data[dataframe][key] = np.where(data[dataframe].UCC.isin(rollupDict[key]), data[dataframe].COST * multiple, 0)
        multiple = abs(multiple)


# #### Cleaning the MTBI dataframes



keepColumns = list(rollupDict.keys())
keepColumns.append("NEWID")

for dataframe in [key for key in data.keys() if 'mtbi' in key.lower()]:
    data[dataframe] = data[dataframe][keepColumns]


# # Adding up all the expenses by each NEWID
# - Sums for each NEWID
# - Adds HousingPrinciple into Housing
# - Adds HousingPrinciple into TotalExp
# - Drops the HousingPrinciple column



print("Adding up all the expenses by NEWIDs")

for dataframe in [key for key in data.keys() if 'mtbi' in key.lower()]:
    data[dataframe] = data[dataframe].groupby(['NEWID'],as_index=False).sum()
    data[dataframe]['Housing'] += data[dataframe]['HousingPrinciple']
    data[dataframe]['TotalExp'] += data[dataframe]['HousingPrinciple']
    data[dataframe] = data[dataframe].drop('HousingPrinciple',axis=1)


# ### Subsetting MTBI files with subset NEWIDs



print("Subsetting MTBI files")

expensesByNEWIDSingle = expensesSumByNEWID(Single, data)
expensesByNEWIDFamily = expensesSumByNEWID(Family, data)


# ### Saving the pre-weight expenses by NEWID for the regression



nonWeightedExpensesByNEWIDSingle = deepcopy(expensesByNEWIDSingle)
nonWeightedExpensesByNEWIDFamily = deepcopy(expensesByNEWIDFamily)


# ## Weighting the Samples



print("Weighting the Samples... This may take a while.")

weightSeries = fmli["FINLWT21"]/12
weightSeries.index = fmli["NEWID"]

expensesesByNEWIDSingle = weightExpensesByNEWID(expensesByNEWIDSingle, weightSeries)
expensesByNEWIDFamily = weightExpensesByNEWID(expensesByNEWIDFamily, weightSeries)


# ## Combining Data frames by Income Class



IncomeClassesSingle = {}
for income in subsetNEWIDs["SingleIncome"]:
    incomeClass = pd.DataFrame()
    for year in subsetNEWIDs["Year"]:
        for month in subsetNEWIDs["Month"]:
            incomeClass = incomeClass.append(expensesByNEWIDSingle[(year,month,income)], ignore_index=True)
    IncomeClassesSingle[income] = incomeClass
    
IncomeClassesFamily = {}
for income in subsetNEWIDs["FamilyIncome"]:
    incomeClass = pd.DataFrame()
    for year in subsetNEWIDs["Year"]:
        for month in subsetNEWIDs["Month"]:
            incomeClass = incomeClass.append(expensesByNEWIDFamily[(year,month,income)], ignore_index=True)
    IncomeClassesFamily[income] = incomeClass


# ### Sum of all the columns
# - Adding up all the columns of a dataframe into totals contained in a dictionary 



plyntySingleSumDict = dictionarySum(IncomeClassesSingle)
plyntyFamilySumDict = dictionarySum(IncomeClassesFamily)


# ### Creating the Percentage dictionaries



print("Creating the percentage dictionaries")

# fixing the TotalExp
for income in plyntySingleSumDict.keys():
    total = 0
    for key,value in plyntySingleSumDict[income].items():
        if not key == 'TotalExp':
            total += value
    plyntySingleSumDict[income]['TotalExp'] = total

for income in plyntyFamilySumDict.keys():
    total = 0
    for key,value in plyntyFamilySumDict[income].items():
        if not key == 'TotalExp':
            total += value
    plyntyFamilySumDict[income]['TotalExp'] = total




plyntySingleDict = incomeSumToPercent(plyntySingleSumDict, "TotalExp")
plyntyFamilyDict = incomeSumToPercent(plyntyFamilySumDict, "TotalExp")


# ### Deleting the TotalExp Column
# This column at this point will be all 1s



for key in plyntySingleDict.keys():
    del plyntySingleDict[key]['TotalExp']
for key in plyntyFamilyDict.keys():
    del plyntyFamilyDict[key]['TotalExp']


# # Creating and printing out the plynty Dataframes



plyntySingle = pd.DataFrame.from_dict(plyntySingleDict,orient='index')
plyntyFamily = pd.DataFrame.from_dict(plyntyFamilyDict,orient='index')




plyntySingle




plyntyFamily


# # Outputing Dataframes to Csv



print("Creating the csvs filled with plynty categories percentages")

plyntySingle.to_csv("plyntySinglePercentages.csv")
plyntyFamily.to_csv("plyntyFamilyPercentages.csv")


# 
# ### Making Dataframe of NEWID,TotalExp, and income before taxes
# outputs:
# - incomeRegressionSingle (dataframe)
#  - contains NEWID, TotalExp, and IncomeBeforeTaxes for each NEWID in single subset
# - incomeRegressionFamily (dataframe)
#  - contains NEWID, TotalExp, and IncomeBeforeTaxes for each NEWID in family subset



print("Creating the Income Spent Regression")

incomeRegressionSingle = pd.DataFrame()
for value in nonWeightedExpensesByNEWIDSingle.values():
    incomeRegressionSingle = incomeRegressionSingle.append(value[["NEWID","TotalExp"]], ignore_index=True)

incomeRegressionFamily = pd.DataFrame()
for value in nonWeightedExpensesByNEWIDFamily.values():
    incomeRegressionFamily = incomeRegressionFamily.append(value[["NEWID","TotalExp"]], ignore_index=True)

fmli = pd.concat([value for key,value in data.items() if 'fmli' in key.lower()], ignore_index=True)[["NEWID","FINCBTXM"]]    

incomeRegressionSingle = pd.merge(incomeRegressionSingle, fmli, on='NEWID', how='inner')
incomeRegressionSingle['TotalExp'] = incomeRegressionSingle['TotalExp'] * 4
incomeRegressionSingle = incomeRegressionSingle[incomeRegressionSingle > 0].dropna()

incomeRegressionFamily = pd.merge(incomeRegressionFamily, fmli, on='NEWID', how='inner')
incomeRegressionFamily['TotalExp'] = incomeRegressionFamily['TotalExp'] * 4
incomeRegressionFamily = incomeRegressionFamily[incomeRegressionFamily > 0].dropna()




def getExpendPercent(income, regressionDf, truncation = None):
    if income <= 0:
        return(1)
    coefficients = np.polyfit(regressionDf.FINCBTXM, regressionDf.TotalExp, deg = 3)
    p = np.poly1d(coefficients)
#     print(p)
    np.seterr(divide='ignore')
    percent = p(income)/income
    if percent > 1:
        percent = 1
    if (not truncation == None) and len(truncation) == 2:
        truncationIncome = truncation[0]
        truncationPercent = truncation[1]
        if income > truncationIncome:
            return(truncationPercent)
    elif not truncation == None:
        print("Truncation is not correct")
    return(percent)

def oldRegression(income):
    if income > 53000:
        output = ((-7.6108*(10**(-17)))*(income**3))+((4.2009*(10**(-11)))*(income**2))+((-7.90256*(10**-6))*income)+1.21112
    else:
        output = 1
    return(output)


# # Plotting



print("Plotting")


# ### Creating the Percent of Income Spent Graph



xSingleRegression = range(0,400000,1000)
xFamilyRegression = range(0,400000,1000)
xOldRegression = range(0,350000,1000)
ySingleRegression = []
yFamilyRegression = []
yOldRegression = []
for income in xSingleRegression:
    ySingleRegression.append(getExpendPercent(income, incomeRegressionSingle))
for income in xFamilyRegression:
    yFamilyRegression.append(getExpendPercent(income, incomeRegressionFamily))
for income in xOldRegression:
    yOldRegression.append(oldRegression(income))


# ### Trucation point for regressions



SingleTruncation = [ySingleRegression.index(min(ySingleRegression)) * 1000, round(min(ySingleRegression),2)]
FamilyTruncation = [yFamilyRegression.index(min(yFamilyRegression)) * 1000, round(min(yFamilyRegression),2)]
ySingleRegression = []
yFamilyRegression = []
for income in xSingleRegression:
    ySingleRegression.append(getExpendPercent(income, incomeRegressionSingle, SingleTruncation))
for income in xFamilyRegression:
    yFamilyRegression.append(getExpendPercent(income, incomeRegressionFamily, FamilyTruncation))




plt.plot(xOldRegression,yOldRegression, color = "g", label = "Old Regression")
plt.plot(xSingleRegression,ySingleRegression, color = "b", label = "Single Regression")
plt.plot(xFamilyRegression,yFamilyRegression, color = "r", label = "Family Regression")
plt.title("Income Spent Regressions")
plt.xlabel("Income")
plt.ylabel("Percent of Income Spent")
plt.legend()
plt.show()


# ### Income vs Expenditure plots



sortedIncomeSingleRegression = sorted(list(set(incomeRegressionSingle.FINCBTXM)))
singleIncomeRegressionExamples = []
for income in sortedIncomeSingleRegression:
    singleIncomeRegressionExamples.append(income * getExpendPercent(income, incomeRegressionSingle))
    
sortedIncomeFamilyRegression = sorted(list(set(incomeRegressionFamily.FINCBTXM)))
familyIncomeRegressionExamples = []
for income in sortedIncomeFamilyRegression:
    familyIncomeRegressionExamples.append(income * getExpendPercent(income, incomeRegressionFamily))




plt.scatter(incomeRegressionSingle.FINCBTXM, incomeRegressionSingle.TotalExp, color='b', s=3)
plt.plot(sortedIncomeSingleRegression, singleIncomeRegressionExamples, color = "black")
plt.xlabel("Income before Taxes")
plt.ylabel("Dollars Spent on Plynty categories")
plt.title("Single person CUs Income vs Expenditure")
plt.xlim(0,700000)
plt.ylim(0,1000000)
plt.show()




plt.scatter(incomeRegressionFamily.FINCBTXM, incomeRegressionFamily.TotalExp, color='r', s=3)
plt.plot(sortedIncomeFamilyRegression, familyIncomeRegressionExamples, color = "black")
plt.xlabel("Income before Taxes")
plt.ylabel("Dollars Spent on Plynty categories")
plt.title("Multiple person CUs Income vs Expenditure")
plt.xlim(0,700000)
plt.ylim(0,1000000)
plt.show()


# ### Number of Users



singleCountNEWIDs = {}
for income in subsetNEWIDs["SingleIncome"]:
    newidSet = set()
    for year in subsetNEWIDs["Year"]:
        for month in subsetNEWIDs["Month"]:
            newidSet = newidSet.union(Single[(year,month,income)])
    singleCountNEWIDs[income] = len(newidSet)
    
familyCountNEWIDs = {}
for income in subsetNEWIDs["FamilyIncome"]:
    newidSet = set()
    for year in subsetNEWIDs["Year"]:
        for month in subsetNEWIDs["Month"]:
            newidSet = newidSet.union(Family[(year,month,income)])
    familyCountNEWIDs[income] = len(newidSet)




plt.bar(range(len(singleCountNEWIDs)), singleCountNEWIDs.values(), align='center', color='b')
plt.xticks(range(len(singleCountNEWIDs)), singleCountNEWIDs.keys())
plt.xlabel("Income Class")
plt.ylabel("Count of CUs")
plt.title("Count of Single Person CUs")
plt.show()




plt.bar(range(len(familyCountNEWIDs)), familyCountNEWIDs.values(), align='center', color='r')
plt.xticks(range(len(familyCountNEWIDs)), familyCountNEWIDs.keys())
plt.xlabel("Income Class")
plt.ylabel("Count of CUs")
plt.title("Count of Family CUs")
plt.show()


# # Get Example Expenditures



income = 50000
single = True

if single:
    regressionDf = incomeRegressionSingle
    theIncomeBrackets = singleIncomeBrackets
    plyntyDf = plyntySingle
    truncation = SingleTruncation
else:
    regressionDf = incomeRegressionFamily
    theIncomeBrackets = familyIncomeBrackets
    plyntyDf = plyntyFamily
    truncation = FamilyTruncation

def getIncomeBracketIndex(income, theIncomeBrackets):
    incomebracket = 0
    for i in range(0,len(theIncomeBrackets)):
        if income <= theIncomeBrackets[i]:
            return(i-1)
    return(len(theIncomeBrackets)-1)

round((plyntyDf.iloc[getIncomeBracketIndex(income, theIncomeBrackets),:] * getExpendPercent(income, regressionDf, truncation) * income)/ 12, 2)


# ## Hospital room and services



plt.boxplot(list(oneTimeSubsetMtbi.COST))
plt.title("Boxplot of Hospital Costs")
plt.ylabel("Dollars")
plt.show()