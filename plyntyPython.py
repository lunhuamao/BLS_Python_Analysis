
# coding: utf-8

# # Plynty Bureau of Labor Statistics Consumer Expenditure Analysis
# 
# [BLS Comsumer Expenditure Survey](https://www.bls.gov/cex/home.htm)
# 
# [Interview Data Dictionary](https://www.bls.gov/cex/2015/csxintvwdata.pdf)
# 
# [Diary Data Dictionary](https://www.bls.gov/cex/2015/csxdiarydata.pdf)
# 
# ### Where to download the BLS CE PUMD
# - The zip files download automatically
# - To download the Stub files open the links then right click and choose "Save As..."
# 
# [2015 interview zip file](https://www.bls.gov/cex/pumd/data/comma/intrvw15.zip)
# 
# [2015 diary zip file](https://www.bls.gov/cex/pumd/data/comma/diary15.zip)
# 
# [2015 IntStub file](https://www.bls.gov/cex/pumd/2014/csxintstub.txt)
# 
# [2015 IStub file](https://www.bls.gov/cex/pumd/2014/csxistub.txt)
# 
# [2015 DStub file](https://www.bls.gov/cex/pumd/2014/csxdstub.txt)
# 
# ### This Scripts Goals for Plynty
# - Create an easy to use analysis engine for the BLS CE PUMD 
# - Create a csv files that has average percentages spent on plynty categories for certain income classes
# - Create incomeclasses that are stastically significant

# ##### Importing Libraries 

# In[719]:

import pandas as pd
import numpy as np
import glob
import os
import subprocess
import math
import matplotlib.pyplot as plt


# ### Setting Parameters
# - year: the last two number associated with the year of the data
#     for example for data from 2015: year = "15"
# - minAge: the low bound (inclusive) of the age range you wish to subset by
# - maxAge: the high bound (inclusive) of the age range you wish to subset by
# - incomeBrackets: array of numbers that you wish to create the new income classes
#     the bracketing works as follows (1,2], (2,3], (3,4]
# - filesToRead: the strings of the abbreviations associated with the files you wish to read
#     options are: "all", "diary", "interview", "dtbd", "expd", "fmld", "memd", "fmli", "itbi", "memi", "mtbi", "ntaxi"

# In[720]:

year = "15"
minAge = 55
maxAge = 64
incomeBrackets = [-math.inf,11000,20000,30000,43000,55000,69000,80000,100000,120000,150000,200000,250000,300000,math.inf]
filesToRead = ["fmli", "mtbi"]


# ### Setting Directory locations and FileNames on your Local Machine

# In[721]:

# directory in which the diary and interview folders are held is located
diaryDir = "/Users/adyke/Vizuri/CE_PUMD/diary15/"
interviewDir = "/Users/adyke/Vizuri/CE_PUMD/intrvw15/"

# Directory where stubfiles are located
pathToStubFileDir = "/Users/adyke/Vizuri/Stubfiles/"
rScriptStubfilePathAndName = "/Users/adyke/Vizuri/rFiles/creatingStubCsvs.R"

# Filenames of the Stubfiles
IStubFileName = "IStub2015.txt"
DStubFileName = "DStub2015.txt"
IntStubFileName = "IntStub2015.txt"

# name of interview dir within the interview dir
insideIntrvwDirName = "intrvw"

# name of the directory where you want the output percentages csv
outputDir = "/Users/adyke/Vizuri/outputFiles/"


# ### Read File Set Function
# Function that was built to easily read in and concatinate multiple files that start with the same abbreviation.
# 
# #### Parameters:
# - fileabbreviation: The four letters associated with the files you wish to read in (ex. "fmli")
# - directory: path to the directory that holds files that should be read in.
# 
# #### Returns:
# - pandas dataframe of all the files that start with the fileabbreviation

# In[722]:

def readFileSet(fileabbreviation, directory):
	# finding all the files with names that start with the fileabbreviation
	filenames = glob.glob(directory+fileabbreviation+"*.csv")
	dfs = []
	for filename in filenames:
		dfs.append(pd.read_csv(filename, na_values=["."]))
	largeDataframe = pd.concat(dfs,ignore_index=True)
	return largeDataframe
   


# ### Reading in the files specified by FilesToRead

# In[723]:

if(len(filesToRead)>0):
	print("Reading in files...")
else:
	print("The files to read variable is empty.")

# looping through each file to read
for file in filesToRead:
	if file == "dtbd" or file == "all" or file == "diary":
		print("dtbd")
		dtbd = readFileSet("dtbd", diaryDir)
	if file == "expd" or file == "all" or file == "diary":
		print("expd")
		expd = readFileSet("expd", diaryDir)
	if file == "fmld" or file == "all" or file == "diary":
		print("fmld")
		fmld = readFileSet("fmld", diaryDir)
	if file == "memd" or file == "all" or file == "diary":
		print("memd")
		memd = readFileSet("memd", diaryDir)
	if file == "fmli" or file == "all" or file == "interview":
		print("fmli")
		fmli = readFileSet("fmli", interviewDir+insideIntrvwDirName+year+"/")
	if file == "itbi" or file == "all" or file == "interview":
		print("itbi")
		itbi = readFileSet("itbi", interviewDir+insideIntrvwDirName+year+"/")
	if file == "itii" or file == "all" or file == "interview":
		print("itii")
		itii = readFileSet("itii", interviewDir+insideIntrvwDirName+year+"/")
	if file == "memi" or file == "all" or file == "interview":
		print("memi")
		memi = readFileSet("memi", interviewDir+insideIntrvwDirName+year+"/")
	if file == "mtbi" or file == "all" or file == "interview":
		print("mtbi")
		mtbi = readFileSet("mtbi", interviewDir+insideIntrvwDirName+year+"/")
	if file == "ntaxi" or file == "all" or file == "interview":
		print("ntaxi")
		ntaxi = readFileSet("ntaxi", interviewDir+insideIntrvwDirName+year+"/")
	# does not read form the expn or para subdirectories


# ### Using R to convert the Stub files into csv files

# In[724]:

# converting the stub files via R 
subprocess.call("Rscript "+rScriptStubfilePathAndName+" "+pathToStubFileDir+" "+IStubFileName+" "+DStubFileName+" "+IntStubFileName, shell=True)
print("Stubfile Csvs created in "+pathToStubFileDir)


# ### Reading and Cleaning the stubfile CSVs into pandas dataframes

# In[725]:

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


# ### subsetDataframe function
# Used to subset any dataframe based on certain parameters
# #### Parameters:
# - dataframe: the pandas dataframe to subset
# - columnName: 
# - minValue: this has 3 different uses
#   1. the single value you wish to subset by
#   2. the array of values that you wish to subset by
#   3. the minimum value (inclusive) in a range of values you wish to subset by
# - secondColumnName: the name of the second column if you wish to subest the dataframe
# - maxValue: the highest value in a range of values you wish to subset by
# 
# #### Returns:
# 
# - subset pandas dataframe
#  

# In[726]:

def subsetDataframe(dataframe, columnName,  minValue, secondColumnName = None, maxValue = None):
	if columnName in dataframe.columns:
		# only subsetting based off one column
		if secondColumnName == None:
			# subsetting not within a range
			if maxValue == None:
				value = minValue
				# value is a list
				if isinstance(value, list):
					dataframe = dataframe[dataframe[columnName].isin(value)]
				# value is scalar
				else:
					dataframe = dataframe[dataframe[columnName]==value]
			# the subsetting is within a range
			else:
				dataframe = dataframe[(dataframe[columnName]>=minValue) & (dataframe[columnName]<=maxValue)]
		# subsetting based on two columns
		else:
			# subsetting not within a range
			if maxValue == None:
				value = minValue
				# value is a list
				if isinstance(value, list):
					dataframe = dataframe[(dataframe[columnName].isin(value)) & (dataframe[secondColumnName].isin(value))]
				# value is scalar
				else:
					dataframe = dataframe[(dataframe[columnName]==value) & (dataframe[secondColumnName]==value)]
			# the subsetting is within a range
			else:
				dataframe = dataframe[((dataframe[columnName]>=minValue) & (dataframe[columnName]<=maxValue)) & ((dataframe[secondColumnName]>=minValue) & (dataframe[secondColumnName]<=maxValue)) ]
		return(dataframe)
	else:
		print("Could not a column named "+columnName+" in the dataframe")


# ### binColumn function
# This function is used in the plynty analysis to recode the income classes to specified incomeclasses
# #### Parameters:
# - dataframe: the pandas dataframe that you wish to bin a column of
# - toBinColumnName: name of column you wish use use as values to bin
# - binValues: array of values that are the ranges of the bins
# - binLabels: labels assocaiated with the bins you wish to create
# - binnedColumnName: name of the column that you wish to replace or create
# 
# #### Returns:
# - dataframe with the binned column

# In[727]:

def binColumn(dataframe, toBinColumnName, binValues, binnedColumnName, labels=None):
    if labels==None:
        dataframe[binnedColumnName] = pd.cut(dataframe.loc[:,toBinColumnName], bins=binValues)
    else:
        dataframe[binnedColumnName] = pd.cut(dataframe.loc[:,toBinColumnName], bins=binValues, labels=labels)
    return(dataframe)


# ### RepresentInts function
# function that determines if a string can be repesented as an integer
# 
# Created by stackoverflow user [Triptych](https://stackoverflow.com/users/43089/triptych) and posted in [this](https://stackoverflow.com/questions/1265665/python-check-if-a-string-represents-an-int-without-using-try-except) stackoverflow question
# 
# #### Parameters:
# - s: the string that you wish to check
# 
# #### Returns:
# - boolean: retruns true if the string can be represented as an integer

# In[728]:

def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False


# ### Categorical UCC Roll Up function
# 
# #### Parameters:
# - stubfile: the stubfile you are using to create the roll up
# - abbreviations: an array of strings taht contain the abbreviations that you wish to roll up 
# - ignoreUCCs: an array that you wish to not add into your roll up
# 
# #### Returns:
# - an array of the uccs associated with your abbreviations

# In[729]:

def categoricalUCCRollUp(stubfile,abbreviations,ignoreUCCs=None):
	uccs = []
	for abbreviation in abbreviations:
		startingRows = stubfile[stubfile['ucc']==abbreviation].index.tolist()
		for startingRow in startingRows:
			startingLevel = stubfile.at[startingRow,'level']
			currentRow = startingRow+1
			currentLevel = stubfile.at[currentRow,'level']
			while int(startingLevel) < int(currentLevel):
				if RepresentsInt(stubfile.at[currentRow,'ucc']):
					if ignoreUCCs==None:
						uccs.append(stubfile.at[currentRow,'ucc'])
					else:
						if not(stubfile.at[currentRow,'ucc'] in ignoreUCCs):
							uccs.append(stubfile.at[currentRow,'ucc'])
						
				currentRow += 1
				currentLevel = stubfile.at[currentRow,'level']
	return(uccs)


# ### Creating the UCC roll ups for Plynty

# In[730]:

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


# ### Cleaning and reseting the indecies of the MTBI file

# In[731]:

# restting the index
mtbi.reset_index()

# Change mtbi UCC column to string
# needed for the loop through rollups
mtbi.UCC = mtbi.UCC.astype(str)


# ### Adding and Rolling up the Categories into the mtbi Dataframe

# In[732]:

rollupNames = ["iTotalExp","iFoodAtHome","iFoodAway","iHousing","iUtilites","iClothingAndBeauty","iTransportation","iHealthcare","iEntertainment","iMiscellaneous","iCharitableAndFamilyGiving","iInsurance","iEducation","iHousingPrinciple"]
rollups = [iTotalExp,iFoodAtHome,iFoodAway,iHousing,iUtilites,iClothingAndBeauty,iTransportation,iHealthcare,iEntertainment,iMiscellaneous,iCharitableAndFamilyGiving,iInsurance,iEducation,iHousingPrinciple]

mtbiRolledUp = mtbi

# looping through the different rollup columns
for x in range(len(rollupNames)):
	quarters = 4
	if(rollupNames[x] == "iHousingPrinciple"):
		quarters = -4
	mtbiRolledUp[rollupNames[x]] = np.where(mtbiRolledUp['UCC'].isin(rollups[x]), mtbiRolledUp['COST']*4, 0.0)


# ### Trimming the mtbi dataframe to be the columns we care about

# In[733]:

# renaming the dataframe to make partial runs easy
mtbiTrimmed = mtbiRolledUp

mtbiTrimmed = mtbiTrimmed.loc[: , ['NEWID','iTotalExp','iFoodAtHome','iFoodAway','iHousing','iUtilites','iClothingAndBeauty','iTransportation','iHealthcare','iEntertainment','iMiscellaneous','iCharitableAndFamilyGiving','iInsurance','iEducation','iHousingPrinciple']]


# ### Creating the Sum for all expenditure category columns for each NEWID
# Testing removing the rows that have 0 response for columns that we think are important

# In[734]:

# adding up all columns for each new id
iExpensesByNewID = mtbiTrimmed.groupby(['NEWID'],as_index=False).sum()
# removing rows with zero values in key categories
nonZeroColumns = ['iFoodAtHome','iFoodAway','iHousing','iUtilites']
for column in nonZeroColumns:
    iExpensesByNewID = iExpensesByNewID[iExpensesByNewID[column] != 0]
# iExpensesByNewID['iHousing'] = iExpensesByNewID['iHousing']-iExpensesByNewID['iHousingPrinciple']

iExpensesByNewID.head(10)


# ### Subestting FMLI for age and recoding the incomebrackets

# In[735]:

# subsetting for the age bracket
fmliAge = subsetDataframe(dataframe=fmli, columnName="AGE_REF", minValue=minAge, maxValue=maxAge)
fmliAge = fmliAge.reset_index()

# recoding the income brackets
fmliRecoded = binColumn(dataframe=fmliAge, toBinColumnName="FINCBTXM", binValues=incomeBrackets, binnedColumnName="INCLASS", labels=range(1,len(incomeBrackets)))


# ### Adding the Income class colum to the ExpensesByNewID dataframe

# In[736]:

# combining the fmli and iExpensesByNewID
inclassExpenses = pd.merge(left=fmliRecoded[['NEWID','INCLASS']],right=iExpensesByNewID, on=['NEWID'])
# inclassExpenses.head(10)
# nonZeroColumns = ['iFoodAtHome','iFoodAway','iHousing','iUtilites']
# for column in nonZeroColumns:
#     inclassExpenses = inclassExpenses[inclassExpenses[column] != 0]


# ### Averaging the expenditures based on incomebrackets

# In[737]:

# getting mean for all columns with the same income class besides newId and creating new dataframe
inclassAverages = round(inclassExpenses.ix[: ,inclassExpenses.columns != 'NEWID'].groupby(['INCLASS'],as_index=False).mean(),2)
# doing median instead of average
# inclassAverages = round(inclassExpenses.ix[: ,inclassExpenses.columns != 'NEWID'].groupby(['INCLASS'],as_index=False).median(),2)

inclassAverages


# ### Median of the expenditures based on income brackets

# In[738]:

inclassMedians = round(inclassExpenses.ix[:,inclassExpenses.columns != 'NEWID'].groupby(['INCLASS'],as_index=False).median(),2)
inclassMedians


# ### Converting the Average expenditures for income classes into percentages of expenditures

# In[739]:

# creating new dataframe for the percentages that only includes the plynty categories
percentages = inclassAverages.loc[:,rollupNames[1:]]
for column in rollupNames[1:]:
    percentages[column] = inclassAverages[column]/inclassAverages.iTotalExp
    
percentages


# ### Converting the Median expenditures for income classes into percentages of expenditures

# In[747]:

# creating new dataframe for the percentages that only includes the plynty categories
percentagesM = inclassMedians.loc[:,rollupNames[1:]]
for row in range(len(percentagesM)):
    # creating the row total for "row"
    rowTotal = percentagesM.loc[row,percentagesM.columns != 'iTotalExp'].sum()
    # replacing each element with the percent
    for column in rollupNames[1:]:
        percentagesM.loc[row,column] = percentagesM.loc[row,column]/rowTotal
    
# dataframe that contains the percentages for medians
percentagesM


# ### Creating Csv of percentages

# In[741]:

# percentages.to_csv(outputDir+"plyntyCsv.csv")


# # Exploratory in the data

# ### Graph of number of observations in the income brackets

# In[742]:

# ploting the number of people in each bracket
print(fmliRecoded['INCLASS'].value_counts().values)
print(fmliRecoded['INCLASS'].value_counts().values.sum())
plt.bar(list(fmliRecoded['INCLASS'].value_counts().index.tolist()), fmliRecoded['INCLASS'].value_counts().values, align='center')
plt.show()


# ### Checking the Standard Deviations
# 
# What I'm finding is that the higher income brackets (>150k) have high standard deviations for housing
# this might have to do with the non reporting

# In[743]:

inclassSD = inclassExpenses.groupby(['INCLASS'],as_index=False).std()
inclassSD.iloc[:,~inclassSD.columns.isin(['INCLASS','NEWID'])]


# ### Checking negative values for housing for incomeclasses

# In[744]:

for inclass in range(len(incomeBrackets)-1):
    print(len(inclassExpenses.loc[inclassExpenses.iHousing <= 0].loc[inclassExpenses.INCLASS == inclass]))
inclassExpenses.loc[inclassExpenses.iHousing <= 0]


# ### Looking deeper into housing and why its janky
# - What im finding is that the negative values in the housing column stay consistent while the max values go up
# - Negative values come from the housing principle
# - The large negatives could happen when the iHousing reporting is 0 and they report the housing principle
# - for some reason there is an issue with the 0 incomeclass

# In[745]:

# max and min of housing per income class
for inclass in range(1,len(incomeBrackets)-1):
    print(inclass)
    print(inclassExpenses.iHousing.loc[inclassExpenses.INCLASS == inclass].describe())


# ### Look into the stub files to see if there are changed abbreviations
