
#  Copyright (C) 2025 Y Hsu <yh202109@gmail.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public license as published by
#  the Free software Foundation, either version 3 of the License, or
#  any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details
#
#  You should have received a copy of the GNU General Public license
#  along with this program. If not, see <https://www.gnu.org/license/>


import os
import json
import pandas as pd
import time
import numpy as np

def pd_df_flag_to_category(df):
    flag_cols = [col for col in df.columns if col.lower().endswith('fl')]
    for col in flag_cols:
        if not pd.api.types.is_categorical_dtype(df[col]):
            values = set(df[col].dropna().unique())
            if {"Y","N"}.issubset(values):
                values2 = values - {"Y", "N"}
                df[col] = pd.Categorical(df[col].fillna(""), categories=["Y", "N"] + sorted(values2), ordered=True)
        else:
            cats = list(df[col].cat.categories)
            if "Y" in cats or "N" in cats:
                cats2 = ["Y", "N"] + [c for c in cats if c not in ("Y", "N")]
            else:
                cats2 = cats
            df[col] = df[col].cat.reorder_categories(cats2, ordered=True)
    return 

def crosstab_from_lists(df, rows, cols, perct_within_index):
    if not all(col in df.columns for col in rows):
        raise ValueError("All elements in 'rows' must be column names of df.")
    if not all(col in df.columns for col in cols):
        raise ValueError("All elements in 'cols' must be column names of df.")
    if perct_within_index is not None:
        if isinstance(perct_within_index, str):
            if perct_within_index not in df.columns:
                raise ValueError(f"'{perct_within_index}' is not a column name of df.")
            if perct_within_index not in rows and perct_within_index not in cols:
                raise ValueError(f"'{perct_within_index}' must be in either 'rows' or 'cols'.")

    ct1= pd.crosstab( [df[r] for r in rows], [df[c] for c in cols], margins=True)

    if perct_within_index is not None:
        # Calculate percentage within the specified index
        # Normalize only within the index specified by perct_within_index
        if perct_within_index in rows:
            normalize_axis = "index"
        elif perct_within_index in cols:
            normalize_axis = "columns"
        else:
            raise ValueError(f"'{perct_within_index}' must be in either 'rows' or 'cols'.")

        ct_perc = ct1.copy()
        # Remove the 'All' row/column for percentage calculation
        if normalize_axis == "index":
            idx_levels = ct1.index.names
            idx_pos = idx_levels.index(perct_within_index)
            for idx_val in ct1.index.get_level_values(perct_within_index).unique():
                mask = ct1.index.get_level_values(perct_within_index) == idx_val
                subtable = ct1[mask].drop("All", errors="ignore")
                total = subtable.sum(axis=0)
                ct_perc.loc[mask, :] = subtable.div(total, axis=1)
            # Set 'All' row to NaN for percent table
            if "All" in ct_perc.index.get_level_values(-1):
                ct_perc.loc[ct_perc.index.get_level_values(-1) == "All", :] = np.nan
        else:  # normalize_axis == "columns"
            col_levels = ct1.columns.names
            col_pos = col_levels.index(perct_within_index)
            for col_val in ct1.columns.get_level_values(perct_within_index).unique():
                mask = ct1.columns.get_level_values(perct_within_index) == col_val
                subtable = ct1.loc[:, mask].drop("All", axis=1, errors="ignore")
                total = subtable.sum(axis=1)
                ct_perc.loc[:, mask] = subtable.div(total, axis=0)
            # Set 'All' column to NaN for percent table
            if "All" in ct_perc.columns.get_level_values(-1):
                ct_perc.loc[:, ct_perc.columns.get_level_values(-1) == "All"] = np.nan

        ct_perc = (100*ct_perc).round(1)

        # Create a report table with count and percent formatted as "count (percent%)"
        report = ct1.astype(str) + " (" + ct_perc.astype(str) + "%)"
        report = report.replace(" (nan%)", "")

        ct = {"count": ct1, "percent_within_index": ct_perc, "report": report}
    else:
        ct = ct1

    return ct


def geo_mean_sd_by_group(df, group_by, var):

    def geo_stats(x):
        # Change output from pd.Series to list
        x = x.dropna()
        x = x[x > 0]
        if len(x) == 0:
            return [np.nan, np.nan, np.nan, np.nan]
        logs = np.log(x)
        gm = np.exp(logs.mean())
        gsd = np.exp(logs.std(ddof=1))
        n = len(x)
        se = logs.std(ddof=1) / np.sqrt(n)
        ci_lower = np.exp(logs.mean() - 1.96 * se)
        ci_upper = np.exp(logs.mean() + 1.96 * se)
        return [gm, gsd, ci_lower, ci_upper]

    result = df.groupby(group_by)[var].apply(geo_stats).apply(pd.Series)
    result.columns = ['geo_mean', 'geo_sd', 'ci_lower', 'ci_upper']
    result = result.reset_index()

    return result

if __name__ == "__main__":
    # Example usage of geometric_mean_sd_by_group
    data = {
        'group': ['A', 'A', 'A', 'B', 'B', 'B', 'C'],
        'value': [10, 20, 30, 5, 15, 25, np.nan]
    }
    df_example = pd.DataFrame(data)
    result = geo_mean_sd_by_group(df_example, group_by='group', var='value')
    print(result)
    pass