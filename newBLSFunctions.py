###############################################################################################################################
# ### Read File Set Function
# Function that was built to easily read in and concatinate multiple files that start with the same abbreviation.

# #### Parameters:
# - fileabbreviation: The four letters associated with the files you wish to read in (ex. "fmli")
# - directory: path to the directory that holds files that should be read in.

# ### Returns:
# - pandas dataframe of all the files that start with the fileabbreviation
import glob
import pandas as pd
def readFileSet(fileabbreviation, directory):
	# finding all the files with names that start with the fileabbreviation
	filenames = glob.glob(directory+fileabbreviation+"*.csv")
	dfs = []
	for filename in filenames:
		dfs.append(pd.read_csv(filename, na_values=["."]))
	largeDataframe = pd.concat(dfs,ignore_index=True)
	return largeDataframe

###############################################################################################################################
# ### getSubsetNEWIDs Function
# Function that returns a list of NEWIDs that correspond to the 

# ### Parameters:
# - dataframe: the pandas dataframe to subset
# - columnName: name of the column in the pandas dataframe to subset by
# - minValue: this has 3 different uses
#   1. the single value you wish to subset by
#   2. the array of values that you wish to subset by
#   3. the minimum value (inclusive) in a range of values you wish to subset by
# - secondColumnName: the name of the second column if you wish to subest the dataframe
# - maxValue: the highest value in a range of values you wish to subset by

# ### Returns:
# - list of NEWIDs that are within the subset parameters 
def getSubsetNEWIDs(dataframe, columnName,  minValue, secondColumnName = None, maxValue = None):
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
        return(dataframe.NEWID)
    else:
        print("Could not a column named "+columnName+" in the dataframe")

###############################################################################################################################
# ### Subset Dictionary function

# #### Parameters:
# - subsetNEWIDsDict: dictionary that contains lists and/or dictionaries containing NEWIDs based on characteristics
# - subsetKeysList: a list of strings that correspond to the keys in the subsetNEWIDsDict to subset by

# ### Returns:
# - Set containing NEWIDs corresponding to the subsetKeysList
# or
# - Dictionary containing NEWIDs corresponding to the subsetKeysList
# # - Keys: tuple of values associated with subsetKeysList
# # - Values: Set of NEWIDs assocaited with Keys
import itertools
def subsetDictionary(subsetNEWIDsDict, subsetKeysList):
    singleSubsets = []
    nonDictSubset = set()
    removeSubsets = []
    # Dealing with non-dictionary entries in the subsetNEWIDsDict
    for checkKey in subsetKeysList:
        if not isinstance(subsetNEWIDsDict[checkKey],dict):
            singleSubsets.append(subsetNEWIDsDict[checkKey])
            removeSubsets.append(checkKey)
    if len(removeSubsets) > 0:
        nonDictSubset = set.intersection(*map(set,singleSubsets))

    # re-creating the subsetKeysList containing only Dictionary entries 
    subsetKeysList = [x for x in subsetKeysList if x not in removeSubsets]

    # if there are no dictionary entries
    if(len(subsetKeysList) == 0):
        return(nonDictSubset)
    
    # creating tuples that become keys of subset dictionary
    keys = []
    for subsetKey in subsetKeysList:
        keyList = []
        for key in subsetNEWIDsDict[subsetKey].keys():
            keyList.append(key)
        keys.append(keyList)
    keyCombos = list(itertools.product(*keys))
    
    subset = {}
    for keys in keyCombos:
        keyNEWIDs = []
        for i in range(0,len(subsetKeysList)):
            keyNEWIDs.append(subsetNEWIDsDict[subsetKeysList[i]][keys[i]])
        intersectionNEWIDs = set.intersection(*map(set,keyNEWIDs))
        intersectionNEWIDs = intersectionNEWIDs.intersection(nonDictSubset)
        subset[keys] = intersectionNEWIDs
    return(subset)

###############################################################################################################################
# ### RepresentInts function
# function that determines if a string can be repesented as an integer

# Created by stackoverflow user [Triptych](https://stackoverflow.com/users/43089/triptych) and posted in [this](https://stackoverflow.com/questions/1265665/python-check-if-a-string-represents-an-int-without-using-try-except) stackoverflow question

# #### Parameters:
# - s: the string that you wish to check

# #### Returns:
# - boolean: retruns true if the string can be represented as an integer

def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

###############################################################################################################################
# ### Categorical UCC Roll Up function

# #### Parameters:
# - stubfile: the stubfile to create the roll up
# - abbreviations: a list of strings that contain the abbreviations or UCCs associated with the roll up 
# - ignoreUCCs: a list to exclude from the roll up

# ### Returns:
# - a list of uccs associated with the abbreviations

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

###############################################################################################################################
# ### Expenses Sum By NEWID function

# ### Parameters:
# - subsetDictionary: two options
# 	1. Set containing NEWIDs corresponding to the subsetKeysList
#	2. Dictionary containing NEWIDs corresponding to the subsetKeysList
#		- Keys: tuple of values associated with subsetKeysList
#		- Values: Set of NEWIDs assocaited with Keys
# - dataDict:

# ### Returns:
# - dictionary
# # - Keys: tuple of subset associated with the subset key list
# # - Values: Dataframe of expenses sums by NEWID
def expensesSumByNEWID(subsetDictionary, dataDict):
	mtbiKeys = [key for key in dataDict.keys() if 'mtbi' in key.lower()]
	if isinstance(subsetDictionary,dict):
		expensesByNEWID = {}
		for key,value in subsetDictionary.items():
			subsetDataframe = pd.DataFrame()
			for mtbiKey in mtbiKeys:
				subsetDataframe = subsetDataframe.append(dataDict[mtbiKey][dataDict[mtbiKey].NEWID.isin(value)], ignore_index=True)
			expensesByNEWID[key] = subsetDataframe
		return(expensesByNEWID)
	else:
		subsetDataframe = pd.DataFrame()
		for mtbiKey in mtbiKeys:
			subsetDataframe = subsetDataframe.append(dataDict[mtbiKey][dataDict[mtbiKey].NEWID.isin(subsetDictionary)], ignore_index=True)
		return(subsetDataframe)

###############################################################################################################################
# ### Dictionary Sum function

# ### Parameters:
# incomeClassesDict: Dictionary
# - Keys: Income Classes
# - Values: Dataframes subset for the Income Class

# ### Returns:
# - dictionary
# # - Keys: Income classes
# # - Values: dictionaries
# # # - Keys: plynty categories
# # # - Values: sum of income for category
def dictionarySum(incomeClassesDict):
    for key,value in incomeClassesDict.items():
        value = value.drop("NEWID", 1)
        classDictionary = {}
        for column in value.columns:
                classDictionary[column] = value[column].sum()
        incomeClassesDict[key] = classDictionary
    return(incomeClassesDict)

###############################################################################################################################
# ### Dictionary Sum function

# ### Parameters:
# incomeClassDict
# - Keys: Income Class
# - Values: dictionary of plynty categories mapped to total sum
# # - Keys: plynty categories
# # - Values: total spent on the plynty category
# totalCategory: string of plynty category in sub dictionary that contains the total expenditure

# ### Returns:
# - Dictionary
# # - Keys: Income brackets
# # - Values: dictionaries
# # # - Keys: plynty categories
# # # - Values: percent of total expenditure spent on the plynty category
import copy
def incomeSumToPercent(incomeClassDict, totalCategory):
	# copying the incomeClassDict
    returnDict = copy.deepcopy(incomeClassDict)
    for key,value in incomeClassDict.items():
        totalExpenditrue = incomeClassDict[key][totalCategory]
        for k,v in value.items():
            returnDict[key][k] = v/totalExpenditrue
    return(returnDict)

###############################################################################################################################
# ### Weight Expenses by NEWID function

# ### Parameters:
# expensesByNEWID (dictionary)
# - Keys: tuple of subset
# - Values: Dataframe of plynty expenses (nonWeighted)
# weightSeries
# - index: NEWID
# - value: Weight multiple

# ### Returns:
# - Dictionary
# # - Keys: tuple of subset
# # - Values: Dataframe of plynty expenses (weighted)
import numpy as np
def weightExpensesByNEWID(expensesByNEWID, weightSeries):
	for key,value in expensesByNEWID.items():
	    for index, row in value.iterrows():
	        weight = weightSeries[row["NEWID"]]
	        if not isinstance(weight, np.float64):
	            weight = weight.values.mean()
	        for column in value.columns[value.columns != 'NEWID']:
	            row[column] = row[column] * weight
	        value.iloc[index] = row
	    expensesByNEWID[key] = value
	return(expensesByNEWID)