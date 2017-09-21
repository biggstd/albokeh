"""
=============
ISA Utilities
=============

This module consists of helpers to pull desired meta-data from an ISA-generated
`.json` file. It has the following main functions.

A function that takes a meta-data key:value pair, and examines the `.json` for
the pair, and returns a list of data frames associated with that pair.

A function that takes a data frame id value, and a desired key and returns the
key:value pair in some format to be used in Bokeh plotting.
"""

# import os
# import sys
import json
# import pandas
from pdcsvref import maxime_rdf_csv


def read_metadata(metadata_path="metadata.json"):
    """
    Reads a json file from metadata_path and returns it as a python dictionary.

    :param metadata_path: The relative path of the metadata json file.

    :returns: Returns a python dictionary of the metadata file.
    """
    with open(metadata_path, "r") as md_file:
        metadata = json.load(md_file)
    return metadata


def fetch_dataframe_field_vals(dict_to_search, field):
    """
    A recursive function to crawl through a provided ISA dictionary.
    This function crawls through both lists and dictionaries. Sourced
    from: https://stackoverflow.com/a/20254842

    :param dict_to_search: An individual assay dictionary.
    :param field: The field to be matched.

    :returns: A list of values that are contained in `field`.
    """
    fields_found = list()
    for key, value in dict_to_search.items():

        if key == field:
            fields_found.append(value)

        elif isinstance(value, dict):
            results = fetch_dataframe_field_vals(value, field)
            for result in results:
                fields_found.append(result)

        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    more_results = fetch_dataframe_field_vals(item, field)
                    for another_result in more_results:
                        fields_found.append(another_result)

    return fields_found


def md_reader(metadata_dict, search_dict):
    """
    Reads a meta-data dictionary and returns a list of pandas data frames that
    match a key:value pair. This is to be used in collecting all datasets
    that have a desired measurement or other attribute. This is a recursive
    function.

    :param metadata_dict: A python dictionary of the metadata to be searched.

    :param search_dict: A dictionary of terms to be matched.

    :returns: A list of dictionaries with the datafile path and the assay
    metadata.

    It accomplishes this by iterating over the assays and checking the entries
    therein. Possible entries in each assay and their nesting include:

    - characteristicCategories
        - @id
        - annotationValue
        - termAccession
        - termSource
    - comments
    - dataFiles
        - comments
        - type
        - name (filename or path)
    - filename
    - materials
        - otherMaterials
        - samples
    - measurementType
        - annotationValue
        - termAccession
        - termSource
    - processSequence
    - technologyPlatform
    - technologyType
        - annotationValue
        - termAccession
        - termSource
    - unitCategories
        - annotationValue
        - termAccession
        - termSource

    """
    found_dict_l = list()

    # Iterate through the metadata dictionary. This is done so the assay being
    # searched can be tracked.
    for study in metadata_dict['studies']:
        for assay in study['assays']:
            for attr, val in search_dict.items():
                retr_vals = fetch_dataframe_field_vals(assay, attr)
                if val in retr_vals:
                    for datafile in assay['dataFiles']:
                        id_path_pair = dict(
                            dataFile=datafile,
                            assay_md=assay)
                        found_dict_l.append(id_path_pair)
    return found_dict_l


def create_pandas_dataframe(data_dict):
    """
    Takes a dataFile entry dictionary and returns a ready to use pandas
    dataframe. The function examines the 'type' attribute of the dictionary,
    and matches it to a dictionary to get the appropriate keyword arguments
    that must be passed to pandas read_csv().
    """

    func_ref = {
        "Maxime-RDF": maxime_rdf_csv
    }

    file_isa_type = data_dict.get("type")
    df_path = data_dict.get("name")

    df_creation_func = func_ref.get(file_isa_type)
    pd_dataframe = df_creation_func(path=df_path)

    return pd_dataframe


def attach_metadata_as_attr(pandas_df, assay_dict, attr):
    """
    Attaches a metadata value to a pandas dataframe as an attribute. This
    is best used for values that are static and do not need to be stored
    as a column. Attributes do not survive many pandas manipulation functions.

    :param pandas_df: A pandas dataframe.
    :param assay_dict: The ISA assay metadata dictionary.
    :param attr: The new attribute to attach to the pandas_df. This must be a
    key that is present in the assay_dict.

    :returns: The input pandas dataframe with a new Python attribute attached.
    """
    pass


def attach_metadata_as_col(pandas_df, assay_dict):
    pass
