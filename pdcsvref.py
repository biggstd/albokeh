"""
===========================
Pandas CSV Reader Reference
===========================

A reference of needed keyword arguments to ensure that different types of
`.csv` files are appropriately loaded as pandas dataframes.
"""

import pandas as pd


def maxime_rdf_csv(path):
    """
    Creates pandas dataframes from Maxime's RDF files.
    Maxime-RDF
    """
    df = pd.read_csv(
        filepath_or_buffer=path,
        index_col=False,
        sep='\s+'  # Split by whitespace
    )
    # Move the columns to deal with the leading hash-tag
    df_mod = df[df.columns[:-1]]
    df_mod.columns = df.columns[1:]

    return df_mod
