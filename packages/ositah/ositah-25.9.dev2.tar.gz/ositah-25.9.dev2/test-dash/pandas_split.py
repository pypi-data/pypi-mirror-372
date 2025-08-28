#!/bin/env python
#
# Script to test/demonstrate a problem with Pandas split(expand=True) with Pandas 1.3.4.
import numpy as np
import pandas as pd

# Create a dataframe with 2 columns
df = pd.DataFrame(
    data=[
        ["A", "B / Z"],
        ["C", "D"],
        ["E", "F"],
    ],
    columns=["master", "project"],
)

# Create a third column initialized to np.Nan
# If the "master" column equals "A", split the project column value into 2 new columns.
# Works as expected : one of the row has "project_saved" not np.NaN
df["project_saved"] = np.NaN
df.project_saved = df.project_saved.astype("object")
df.loc[
    df["master"] == "A",
    "project_saved",
] = df["project"]
df[["newmaster", "newproject"]] = df.project_saved.str.split(" / ", 1, expand=True)
print(
    "Step 1 : create 2 new columns and split project_saved if not np.Nan (1+ matching row)"
)
print(df)
print()

# Attempt to update the initial "master" and "project" columns when "project_saved" is not np.Nan
# Unfortunately doesn't work: the columns are set to np.NaN. Works properly if expand=False (and
# only one column is updated)
df.loc[
    df.project_saved.notna(),
    ["master", "project"],
] = df.project_saved.str.split(" / ", 1, expand=True)
print(
    "Step 2 : update master and project columns by splitting project_saved if not np.Nan"
)
print(df)
print()

# Do the same but with a column to split that contains only np.NaN values.
# An excepion is raised: "ValueError: Columns must be same length as key"
# Remark: using None rather than np.NaN doesn't help
df["project_saved_2"] = np.NaN
df.project_saved_2 = df.project_saved_2.astype("object")
df.loc[
    df["master"] == "Z",
    "project_saved_2",
] = df["project"]
# df[
#     ["newmaster2", "newproject2"]
# ] = df.project_saved_2.str.split(" / ", 1, expand=True)
# Workaround from https://github.com/pandas-dev/pandas/issues/35807#issuecomment-676912441
names = ["newmaster2", "newproject2"]
exploded = (
    df["project_saved_2"]
    .str.split("/", expand=True, n=len(names) - 1)
    .rename(columns={k: name for k, name in enumerate(names)})
)
for column in names:
    if column not in exploded.columns:
        exploded[column] = np.NaN
df = df.join(exploded)
print(
    "Step 3 : create 2 new columns and split project_saved if not np.Nan (no matching row)"
)
print(df)
