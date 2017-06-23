import pandas as pd
import numpy as np
import os
import subprocess
import math
import matplotlib.pyplot as plt
from scipy.interpolate import *
from blsFunctions import *

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
minNumOfCUsArray = [150]
# minNumOfCUsArray = [50,75,100,125,150,175,200,225,250]
significanceLevelArray = [0.005]
# significanceLevelArray = [0,0.0025,0.005,0.0075,0.01, 0.0125, 0.015]

year = "15"
filesToRead = ["fmli", "mtbi"]

# minAge = 55
# maxAge = 64

minAge = 60
maxAge = 75

# minAge = 65
# maxAge = 130

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

if os.path.isfile(pathToStubFileDir+"DStub.csv") and os.path.isfile(pathToStubFileDir+"IStub.csv") and os.path.isfile(pathToStubFileDir+"IntStub.csv"):
    print()
else:
    # converting the stub files via R 
    subprocess.call("Rscript "+rScriptStubfilePathAndName+" "+pathToStubFileDir+" "+IStubFileName+" "+DStubFileName+" "+IntStubFileName, shell=True)
    print("Stubfile Csvs created in "+pathToStubFileDir)
    print()

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

everyIncomeBracket= []

# subsetting the fmli file for single vs multiple people
fmli = fmli.loc[fmli.FAM_SIZE > 1]

for minNumOfCUs in minNumOfCUsArray:
	for significanceLevel in significanceLevelArray:
		print("Min Number of CUs in each Bracket: " + str(minNumOfCUs))
		print("Significance level:"+str(significanceLevel))

		incomeBrackets = list(range(-10000000, 10000000, 5000))
		numberIncomeBrackets = len(incomeBrackets)-1


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

		createSizedIncomeBrackets(incomeBrackets, fmliAge, minNumOfCUs)
		# recoding the income brackets

		while numberIncomeBrackets > perferedNumIncomeBrackets:
			fmliRecoded = binColumn(dataframe=fmliAge, toBinColumnName="FINCBTXM", binValues=incomeBrackets, binnedColumnName="INCLASS", labels=range(1,len(incomeBrackets)))
			# combining the fmli and iExpensesByNewID
			inclassExpenses = pd.merge(left=fmliRecoded[['NEWID','INCLASS','FINCBTXM']],right=iExpensesByNewID, on=['NEWID'])
			# cleaning the inclassExpenses dataframe of outliers
			outliers1 = inclassExpenses.copy()


			outliers1
			innerFence = []
			outerFence = []
			for inclass in range(1,len(incomeBrackets)):
			    outliers1InClass = outliers1.where(outliers1['INCLASS']==inclass)
			    Q1 = outliers1InClass['iHousing'].quantile(0.25)
			    Q3 = outliers1InClass['iHousing'].quantile(0.75)
			    IQR = Q3 - Q1
			    outerFence.extend(outliers1InClass[outliers1InClass['iHousing'] < (Q1 - (3 * IQR))].index.tolist())
			    outerFence.extend(outliers1InClass[outliers1InClass['iHousing'] > (Q3 + (3 * IQR))].index.tolist())

			clean2 = outliers1.drop(outliers1.index[outerFence])
			# creating percentage outputs for cleaned dataframe
			inclassCleanAverages2 = round(clean2.ix[: ,clean2.columns != 'NEWID'].groupby(['INCLASS'],as_index=False).mean(),2)
			# creating new dataframe for the percentages that only includes the plynty categories
			cleanPercentages2 = inclassCleanAverages2.loc[:,rollupNames[1:]]
			for column in rollupNames[1:]:
			    cleanPercentages2[column] = inclassCleanAverages2[column]/inclassCleanAverages2.iTotalExp
			# truncate the max ExpInc
			cleanPercentages2nonTruncated = cleanPercentages2.copy()
			differences = []
			significance = significanceLevel
			for row in range(len(cleanPercentages2)-1):
			    difference = 0
			    for column in range(len(cleanPercentages2.columns)-1):
			    	if (cleanPercentages2.ix[:,column].mean() * abs(cleanPercentages2.ix[row,column] - cleanPercentages2.ix[row+1,column])) > significance:
			    		difference += (cleanPercentages2.ix[:,column].mean() * abs(cleanPercentages2.ix[row,column] - cleanPercentages2.ix[row+1,column]))

			    differences.append(difference)
			# print()
			# print(differences)
			# print()
			incomeBrackets.remove(incomeBrackets[differences.index(min(differences))+1])
			cleanPercentages2.reset_index
			# print(differences)
			numberIncomeBrackets = len(incomeBrackets)-1

		# fmliTotalRecoded = binColumn(dataframe=fmli, toBinColumnName="FINCBTXM", binValues=incomeBrackets, binnedColumnName="INCLASS", labels=range(0,len(incomeBrackets)-1))

		print("Income Brackets: "+str(incomeBrackets))
		everyIncomeBracket.extend(incomeBrackets)
		print()

allbrackets = pd.Series(everyIncomeBracket)
if((len(minNumOfCUsArray) > 1) | (len(significanceLevelArray) > 1)):
	print("Count of Bracket values for all observations")
	print(allbrackets.value_counts())

# numberIncomeBrackets = len(incomeBrackets)-1
