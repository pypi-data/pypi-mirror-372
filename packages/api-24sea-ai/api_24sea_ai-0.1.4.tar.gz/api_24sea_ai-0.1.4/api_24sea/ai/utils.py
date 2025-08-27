# -*- coding: utf-8 -*-
"""Utility functions for the `api_24sea.ai` package."""
from typing import Dict, List, Optional, Union

import pandas as pd

from api_24sea import exceptions as E


def process_models_overview(
    m_list: List[Dict[str, Optional[Union[str, int]]]]
) -> pd.DataFrame:
    """Process the models overview list into a DataFrame with additional
    columns. Renames some columns for clarity.

    List of operations:
    - Rename `project_id` to `site`
    - Rename `location_id` to `location`
    - Rename `model_group_id` to `model_group`
    - Rename `name` to `model`
    - Add `statistic`, `site_id`, `location_id`, and `short_hand` columns by
      splitting the `model` name.
    - Rename `units` to `unit_str`
    - Expand rows where `location` is a list/tuple into multiple rows.
    - For rows where `location_id` is 'FLT', derive `location_id` from
      `location` by removing the `site_id` prefix.

    Parameters
    ----------
    m_list : list of dict
        List of models overview dictionaries.

    Returns
    -------
    pd.DataFrame
        Processed DataFrame with additional columns.

    Raises
    ------
    E.ProfileError
        If the model names do not match the expected format.
    """
    df = pd.DataFrame(m_list)
    if df.empty:
        return df
    # Rename project_id to site
    if "project_id" in df.columns:
        df.rename(columns={"project_id": "site"}, inplace=True)
    if "location_id" in df.columns:
        df.rename(columns={"location_id": "location"}, inplace=True)
    if "model_group_id" in df.columns:
        df.rename(columns={"model_group_id": "model_group"}, inplace=True)
    if "name" in df.columns:
        df.rename(columns={"name": "model"}, inplace=True)
    # Add statistic, site_id, location_id, and short_hand columns by
    # splitting the model name.
    # short_hand is the final part, it can contain underscores
    if "model" in df.columns:
        split_model = df["model"].str.split("_", expand=True)
        if split_model.shape[1] >= 5:
            df["statistic"] = split_model.iloc[:, 0]
            df["short_hand"] = (
                split_model.iloc[:, 3:]
                .fillna("")
                .agg("_".join, axis=1)
                .str.rstrip("_")
                .values
            )
            df["location_id"] = split_model.iloc[:, 2]
            df["site_id"] = split_model.iloc[:, 1]
        elif split_model.shape[1] == 4:
            df["statistic"] = split_model.iloc[:, 0]
            df["short_hand"] = split_model.iloc[:, 3]
            df["location_id"] = split_model.iloc[:, 2]
            df["site_id"] = split_model.iloc[:, 1]
        else:
            raise E.ProfileError(
                "\033[31;1mThere was an issue processing the "
                "models overview. The model names do not "
                "match the expected format. Please check your "
                f"input data.\n{m_list}\033[0m"
            )
    if "units" in df.columns:
        df.rename(columns={"units": "unit_str"}, inplace=True)
    is_list = df["location"].apply(lambda x: isinstance(x, (list, tuple)))
    df_expanded = pd.concat(
        [df.loc[~is_list], df.loc[is_list].explode("location")],
        ignore_index=True,
    )
    df_expanded["location"] = df_expanded["location"].str.upper()
    # For floating locations (FLT), derive location_id from location by removing the site_id prefix
    if "location_id" in df_expanded.columns:
        is_flt = df_expanded["location_id"].astype(str).str.upper() == "FLT"
        if is_flt.any():

            def _derive_loc_id(row):
                site_id = str(row.get("site_id", "")).upper()
                loc = str(row.get("location", "")).upper()
                return (
                    loc.replace(site_id, "", 1)
                    if site_id and loc.startswith(site_id)
                    else loc
                )

            df_expanded.loc[is_flt, "location_id"] = df_expanded.loc[
                is_flt
            ].apply(_derive_loc_id, axis=1)

    return df_expanded
