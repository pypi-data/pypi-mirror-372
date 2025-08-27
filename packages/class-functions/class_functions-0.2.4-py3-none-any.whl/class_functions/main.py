# %% Required modules
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import numpy as np
import math


# %% parallelCoordinatesPlot function
def parallelCoordinatesPlot(
    filePath,
    numAssignments,
    startColIndex,
    normalize=True,
    replaceMissingWithZero=True,
    ydIndex=None,
):
    """This functions creates a parallel coordinates plot of student scores to
    visualize the point at which students start struggling.

    Parameters
    ----------
    filePath : Str
        Full path to the location of the Canvas gradebook file.
    numAssignments : Int
        The number of assignments for which you want to create box plots.
    startColIndex : Int
        The column index where the assignments start. This assumes that all
        of the assignment columns are adjacent.
    normalize : Bool
        Whether to convert the scores to a 0-1 scale so that assignments
        of differnt point values can be compared. The default is True.
    replaceMissingWithZero : Bool
        Whether to replace missing assignment scores with 0. The default is True.
    ydIndex : Int
        The column index for the yellowdig assignment, if there is one.

    Returns
    -------
    An interactive parallel coordinates plot of student scores.
    """
    df = pd.read_csv(filePath)

    # Extract only student name and homework columns
    colNums = [0]
    if ydIndex is not None:
        colNums.append(ydIndex)
    colNums.extend(list(range(startColIndex, startColIndex + numAssignments)))

    # Create new column names for homework assignments
    colNames = ["Student"]
    hwCols = ["h" + str(i) for i in range(1, numAssignments + 1)]
    if ydIndex is not None:
        hwCols.insert(0, "yd")
    colNames.extend(hwCols)
    df = df.iloc[:, colNums]
    df.columns = colNames

    # Calculate divisors, including a divisor for the total score
    divisors = df.iloc[
        0, 1:
    ]  # Get the first row, which contains the value of the assignments
    divisors = divisors.tolist()
    divisors.append(sum(divisors))

    # Create a total column that sums the scores for each student
    df["total"] = df.iloc[:, 1:].apply("sum", axis=1)

    # Remove the first row, which contains the assignment values
    df = df.iloc[1:, :]

    # Convert hw columns to numeric just in case they are not
    df[hwCols] = df[hwCols].apply(pd.to_numeric)

    # Loop through each row to calculate the percentage for each assignment
    if normalize:
        for c in range(1, df.shape[1]):
            df.iloc[:, c] = df.iloc[:, c] / divisors[c - 1]
    if replaceMissingWithZero:
        df = df.astype(float).fillna(0)  # Fill in missing values with 0

    # Remove test student
    df = df.query('Student.str.contains("Test") == False')

    fig = px.parallel_coordinates(
        df, color="total", title="Parallel Coordinates Plot of Scores"
    )
    fig.show()


# %% tidyUpCols Function
def tidyUpCols(myList, keepNums=False):
    """
    Parameters
    ----------
    myList : List
        List of column names, like df.columns
    keepNums : Bool
        Whether we want to keep numbers in column names. The default is False.

    Returns
    -------
    ml2 : List
        List of tidy column names.
    """
    ml2 = []
    for i in range(len(myList)):
        if myList[i] != None:
            ti = (
                myList[i]
                .strip()
                .lower()
                .replace(".", "")
                .replace("/", "_")
                .replace(" ", "_")
                .replace("$", "")
            )
        else:
            continue  # Goes to the next iteration in the for loop

        if "--" in ti:
            ti2 = ti.split("--")
            [ml2.append(x) for x in ti2]
        elif keepNums == True:
            ti = re.sub("[^a-zA-Z_0-9]", "", ti)
            ml2.append(ti)
        else:
            ti = re.sub("[^a-zA-Z_]", "", ti)
            ml2.append(ti)
    return ml2

#%% Abbreviate column names function
def abbreviate_col_names(col_name):
    # If Yellowdig is in the name, then return YD
    if col_name.find('Yellowdig') >= 0:
        return "YD"
    elif col_name == 'Student':
        return 'Student'
    else:
        # Remove the stuff in parentheses at the end
        tname = col_name.split(' (')[0]
        # Create a list of whole words or digits
        parts = re.findall(r'[A-Za-z]+|\d+', tname)
        # Create an empty string
        abbreviation = ''
        for part in parts:
            if part.isdigit():
                # If it's a digit, then add it
                abbreviation += part 
            elif part[0].isupper():
                # If the first letter is uppercase, then add it
                abbreviation += part[0]
        return abbreviation
    
# %% assignmentPlots function
def assignmentPlots(
    filePath,
    numAssignments,
    startColIndex,
    normalize=True,
    replaceMissingWithZero=True,
    ydIndex=None,
):
    """
    This function uses an export from canvas to create boxplots and stripplots
    of assignments.

    Parameters
    ----------
    filePath : Str
        Full path to the location of the Canvas gradebook file.
    numAssignments : Int
        The number of assignments for which you want to create box plots.
    startColIndex : Int
        The column index where the assignments start. This assumes that all
        of the assignment columns are adjacent.
    normalize : Bool
        Whether to convert the scores to a 0-1 scale so that assignments
        of differnt point values can be compared. The default is True.
    replaceMissingWithZero : Bool
        Whether to replace missing assignment scores with 0. The default is True.
    ydIndex : Int
        The column index for the yellowdig assignment, if there is one.

    Returns
    -------
    A box and whisker plot on the left and a stripplot on the right.

    """
    df = pd.read_csv(filePath)
    
    # Extract only student name and homework columns
    colNums = [0]
    if ydIndex is not None:
        colNums.append(ydIndex)
    colNums.extend(list(range(startColIndex, startColIndex + numAssignments)))
    
    # Create new column names for homework assignments
    colNames = ["Student"]
    hwCols = ["h" + str(i) for i in range(1, numAssignments + 1)]
    if ydIndex is not None:
        hwCols.insert(0, "yd")
    colNames.extend(hwCols)
    df = df.iloc[:, colNums]
    df.columns = colNames
    
    # Find the row that contains Points Possible
    points_row = df.iloc[:,0].str.contains('Points')
    points_row = points_row[points_row == True]
    points_row = points_row.index[0]
    
    # Calculate divisors, including a divisor for the total score
    divisors = df.iloc[points_row, 1:]  # Get the first row, which contains the value of the assignments
    divisors = pd.to_numeric(divisors.tolist())
    divisors = np.append(divisors, np.sum(divisors))
    
    # Remove the rows up to the points_row
    df = df.iloc[points_row+1:,:]
    
    # Convert all but first column to numeric values
    df.iloc[:,1:] = df.iloc[:,1:].apply(pd.to_numeric, errors='coerce')
    
    # Create a total column that sums the scores for each student
    df["total"] = df.iloc[:, 1:].apply("sum", axis=1)
    
    # Loop through each row to calculate the percentage for each assignment
    if normalize:
        for c in range(1, df.shape[1]):
            df.iloc[:, c] = df.iloc[:, c] / divisors[c - 1]
    if replaceMissingWithZero:
        df.iloc[:,1:] = df.iloc[:,1:].astype(float).fillna(0)  # Fill in missing values with 0
    
    # Remove test student
    df = df.query('Student.str.contains("Test") == False')
    
    # Convert from wide to long
    hw = df.melt(value_vars=hwCols, var_name="Homework", value_name="Score")
    
    # Create canvas with two columns
    fig, axs = plt.subplots(figsize=(15, 5), ncols=2)
    fig.tight_layout(pad=2)
    
    # Boxplot on left side
    sns.boxplot(
        data=hw,
        x="Homework",
        y="Score",
        hue="Homework",
        ax=axs[0],
        showmeans=True,
        meanprops={"markeredgecolor": "black"},
    )
    axs[0].set_title("Boxplot of Homework Scores")
    
    # Stripplot on right side
    sns.stripplot(data=hw, x="Homework", y="Score", hue="Homework", ax=axs[1])
    axs[1].set_title("Stripplot of Homework Scores")


# Test out the function
# assignmentPlots('/Users/rnguymon/Downloads/htdy2.csv', 5, 9)


def assignmentPlots2(
    filePath,
    cols_to_exclude = [],
    normalize=True,
    replaceMissingWithZero=True
):
    """
    This function uses an export from canvas to create boxplots and stripplots
    of assignments.

    Parameters
    ----------
    filePath : Str
        Full path to the location of the Canvas gradebook file.
    cols_to_exclude: List
        List of abbreviated column names that you don't want to include. You may have to run the function once to see what the column names are.
    normalize : Bool
        Whether to convert the scores to a 0-1 scale so that assignments
        of differnt point values can be compared. The default is True.
    replaceMissingWithZero : Bool
        Whether to replace missing assignment scores with 0. The default is True.

    Returns
    -------
    A box and whisker plot on the left and a stripplot on the right.

    """
    df = pd.read_csv(filePath)

    # Find the row that contains Points Possible
    points_row = df.iloc[:,0].str.contains('Points')
    points_row = points_row[points_row == True]
    points_row = points_row.index[0]
    points_row
    
    # Find the student column 
    cols_to_keep = [c for c in df.columns if c.find('Student') >= 0]
    
    # Find the columns that contains the points possible values
    points_cols = pd.to_numeric(df.iloc[points_row,:], errors='coerce')
    points_cols = points_cols.index[points_cols.notna()]
    cols_to_keep.extend(points_cols)
    
    # Keep only the student and points columns 
    df = df.loc[:,cols_to_keep]
    
    # Abbreviate column names
    df.columns = [abbreviate_col_names(c) for c in df.columns]
    
    # Get numbers to use as the divisors
    divisors = df.iloc[points_row, 1:]  # Get the first row, which contains the value of the assignments
    divisors = pd.to_numeric(divisors)
    
    # Remove the rows up to the points_row
    df = df.iloc[points_row+1:,:]
    
    # Remove test student 
    df = df.query('Student.str.contains("Test") == False')
    
    # Set student name as index 
    df = df.set_index('Student')
    
    # Keep only columns that have submissions
    pct_complete = df.count(axis=0)/df.shape[0]
    asgn_with_submissions = pct_complete[pct_complete > 0].index
    df = df.loc[:, asgn_with_submissions]
    
    # Remove columns that the user doesn't want 
    df = df.drop(columns=cols_to_exclude)
    
    # Put Yellowdig as the first column
    col_names = list(df.columns)
    for i, c in enumerate(col_names):
        if c == 'YD':
            my_col = col_names.pop(i)
    col_names.insert(0,my_col)
    df = df.loc[:, col_names]
    
    # Keep only the matching divisors
    divisors = divisors[df.columns]
    
    # Convert all columns to numeric values
    df = df.apply(pd.to_numeric, errors='coerce')
    
    # Create a total column that sums the scores for each student
    df["Total"] = df.apply("sum", axis=1)
    divisors['Total'] = sum(divisors)
    
    # Loop through each row to calculate the percentage for each assignment
    if normalize:
        for c in range(df.shape[1]):
            df.iloc[:, c] = df.iloc[:, c] / divisors.iloc[c]
    if replaceMissingWithZero:
        df = df.astype(float).fillna(0)  # Fill in missing values with 0
    
    # Convert from wide to long
    hw = df.melt(var_name="Homework", value_name="Score")
    
    # Create canvas with two columns
    fig, axs = plt.subplots(figsize=(15, 5), ncols=2, sharey=True)
    
    # Boxplot on left side
    sns.boxplot(
        data=hw,
        x="Homework",
        y="Score",
        hue="Homework",
        ax=axs[0],
        showmeans=True,
        meanprops={"markeredgecolor": "black"},
    )
    axs[0].set_title("Boxplot of Homework Scores")
    
    # Stripplot on right side
    sns.stripplot(data=hw, x="Homework", y="Score", hue="Homework", ax=axs[1])
    axs[1].set_title("Stripplot of Homework Scores")
    fig.tight_layout(pad=2);

# %% relocate function
def relocate(df, old_index, new_index):
    """
    This function relocates one column of a dataframe based on index number.

    Parameters
    ----------
    df : Pandas dataframe
        This is the dataframe object that has a column you would like to
        relocate.
    old_index : INT
        This is th eindex number of the column that you want to relocate.
    new_index : INT
        This is the destination index number of the relocated column.

    Returns
    -------
    df : Pandas dataframe
        The same dataframe with the relocated column.

    """
    # Convert column names to a list, col_names
    col_names = df.columns.tolist()
    # Remove the column and insert it into a new location
    col_names.insert(new_index, col_names.pop(old_index))
    # Slice the dataframe using the col_names list
    df = df.loc[:, col_names]
    # Return the dataframe
    return df

# %% relocate by name function
def relocate_by_name(df, col_name, new_index):
    """
    This function relocates one column of a dataframe based on the new column's name and the new index number.

    Parameters
    ----------
    df : Pandas dataframe
        This is the dataframe object that has a column you would like to
        relocate.
    col_name : STR
        This is the name of the column that you want to relocate.
    new_index : INT
        This is the destination index number of the relocated column.

    Returns
    -------
    df : Pandas dataframe
        The same dataframe with the relocated column.

    """
    # Convert column names to a list, col_names
    col_names = list(df.columns)

    # Loop through the column names and remove the specified column
    for i, c in enumerate(col_names):
        if c == col_name:
            my_col = col_names.pop(i)

    # Insert the column into the new location
    col_names.insert(new_index,my_col)

    # Slice the dataframe using the col_names list
    df = df.loc[:, col_names]

    # Return the dataframe
    return df
