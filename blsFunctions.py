

###############################################################################################################################
# ### Read File Set Function
# Function that was built to easily read in and concatinate multiple files that start with the same abbreviation.

# #### Parameters:
# - fileabbreviation: The four letters associated with the files you wish to read in (ex. "fmli")
# - directory: path to the directory that holds files that should be read in.

# #### Returns:
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

# #### Returns:

# - subset pandas dataframe

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

        

###############################################################################################################################
# ### binColumn function
# This function is used in the plynty analysis to recode the income classes to specified incomeclasses
# #### Parameters:
# - dataframe: the pandas dataframe that you wish to bin a column of
# - toBinColumnName: name of column you wish use use as values to bin
# - binValues: array of values that are the ranges of the bins
# - binLabels: labels assocaiated with the bins you wish to create
# - binnedColumnName: name of the column that you wish to replace or create

# #### Returns:
# - dataframe with the binned column

def binColumn(dataframe, toBinColumnName, binValues, binnedColumnName, labels=None):
    if labels==None:
        dataframe[binnedColumnName] = pd.cut(dataframe.loc[:,toBinColumnName], bins=binValues)
    else:
        dataframe[binnedColumnName] = pd.cut(dataframe.loc[:,toBinColumnName], bins=binValues, labels=labels)
    return(dataframe)



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
# - stubfile: the stubfile you are using to create the roll up
# - abbreviations: an array of strings taht contain the abbreviations that you wish to roll up 
# - ignoreUCCs: an array that you wish to not add into your roll up

# #### Returns:
# - an array of the uccs associated with your abbreviations

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

import numpy as np
def rollUpDataframe(dataframe, rollUpNameArray, rollUpUCCArray, negativeColumns, multiple):
    for x in range(len(rollUpNameArray)):
        if(rollUpNameArray[x] in (negativeColumns)):
            multiple *= -1
            print("I found a negative "+str(multiple))
        dataframe[rollUpNameArray[x]] = np.where(dataframe['UCC'].isin(rollUpUCCArray[x]), dataframe['COST']*multiple, 0.0)
    return(dataframe)