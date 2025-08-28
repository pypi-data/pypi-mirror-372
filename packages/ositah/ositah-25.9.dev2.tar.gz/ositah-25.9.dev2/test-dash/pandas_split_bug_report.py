#!/bin/env python
#
# Script to test/demonstrate a problem with Pandas split(expand=True) with Pandas 1.3.4
# when trying to assign values to existing columns

import numpy as np
import pandas as pd

# pd.show_versions()
# print()

# Create a dataframe with 2 columns
df = pd.DataFrame(
    data=[
        ["A", "B", "B / Z"],
        #        ["A", "B", np.NaN],
        ["C", "D", "Y"],
        ["E", "F", np.NaN],
    ],
    columns=["master", "project", "project_saved"],
)
print("Initial dataframe")
print(df)
print()

# Attempt to update the initial "master" and "project" columns by splitting "project_saved" on /.
# Works but unfortunately set these columns to np.NaN when project_saved is np.Nan, as expected.
df.project_saved = df.project_saved.astype("object")
df[["master", "project"]] = df.project_saved.str.split(" / ", 1, expand=True)
print("Updated master and project columns by splitting project_saved")
print(df)
print()

# Reset dataframe to original values
df = pd.DataFrame(
    data=[
        ["A", "B", "B / Z"],
        #        ["A", "B", np.NaN],
        ["C", "D", "Y"],
        ["E", "F", np.NaN],
    ],
    columns=["master", "project", "project_saved"],
)
print("Reset dataframe to initial values")
print(df)
print()


# Attempt to update the initial "master" and "project" columns when "project_saved" is not np.Nan
# by splitting "project_saved" value into 2 parts (separator=/).
# Unfortunately doesn't work: the columns are set to np.NaN if the condition project_saved.notna()
# is true (and preserved when false as expected).
df.project_saved = df.project_saved.astype("object")
df.loc[
    df.project_saved.notna(),
    ["master", "project"],
] = df.project_saved.str.split(" / ", 1, expand=True)
print("Updated master and project columns by splitting project_saved if not np.Nan")
print(df)
