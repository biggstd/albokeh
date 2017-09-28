"""
=====================================
Boiler Plat Visualization Application
=====================================

:Author:
    Tyler Biggs

"""

import os
import sys
import collections
import itertools
# Bokeh imports
from bokeh.plotting import figure
from bokeh.layouts import layout, widgetbox
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.models.widgets import MultiSelect, CheckboxGroup, Div, Paragraph
from bokeh.palettes import linear_palette, viridis
from bokeh.io import curdoc
# Local, relative module imports
sys.path.append(os.getcwd())
from utils import read_metadata, md_reader, create_pandas_dataframe,\
    get_sample_names, retr_termSource_values
from generateISA import create_metadata, main


# Create the title HTML Div.
title_div = Div(
    text=open(os.path.join(
        os.path.dirname(__file__),
        "templates",
        "rdf_title.html")).read(), width=800
)

# Source the metadata
METADATA = read_metadata("albokeh/metadata.json")
# Create the search dictionary for retr_dataframe
SEARCH_DICT = {'annotationValue': 'Simulated RDF'}

# Source the desired dataframes.
# This returns a list of dictionaries with the following fields:
#   dataFile - the datafile dictionary
#   assay_md - the assay metadata dictionary
DFMD = md_reader(METADATA, SEARCH_DICT)

# Placeholder for available compounds found in the retrieved data.
AVAIL_CMPDS = collections.defaultdict(list)

# Create dataframes with the desired metadata attached as either
# objects of as columns.
# For now just create a list of the desired dataframes
ALL_LOADED_DATAFRAMES = dict()
ALL_LOADED_SAMPLES = list()

for data_dict in DFMD:
    # Construct a dataframe:
    new_df = create_pandas_dataframe(data_dict.get("dataFile"))
    # Find the sample that this dataframe represents:
    # TODO: Fix list parsing hack
    new_sample = get_sample_names(data_dict.get("assay_md"))[0]
    ALL_LOADED_SAMPLES.append(new_sample)
    # Add a new column that contains the compound
    new_df['sample'] = new_sample
    # Build the dict
    ALL_LOADED_DATAFRAMES[new_sample] = dict(
        dataframe=new_df,
        assay_md=data_dict.get("assay_md"),
        assay_bonds=[retr_termSource_values(
            data_dict.get("assay_md"), "Inter-atom distances")]
    )

# Create SOURCES that will dynamically update themselves.
ACTIVE_DATAFRAMES = ColumnDataSource()
AVAIL_BONDS = ColumnDataSource()

# Define active dataframes/compounds/aluminum dimers
DATAFRAME_SEL = MultiSelect(
    title="Dataframe Selection",
    options=ALL_LOADED_SAMPLES)

BOND_SEL = MultiSelect(
    title="Bond Selector")


def update_dataframe_selector(attr, old, new):
    """The updater function for the dataframe selector."""
    sel_datasets = [ALL_LOADED_DATAFRAMES[x] for x in DATAFRAME_SEL.value]
    avail_bonds = list()

    for x in DATAFRAME_SEL.value:
        avail_bonds.extend(
            [y for y in ALL_LOADED_DATAFRAMES[x]["assay_bonds"]])

    avail_bonds_set = set([x for x in itertools.chain(*avail_bonds)])

    ACTIVE_DATAFRAMES.data = dict(user_sel_df=sel_datasets)
    AVAIL_BONDS.data = dict(avail_bonds=list(avail_bonds_set))
    BOND_SEL.options = AVAIL_BONDS.data['avail_bonds']
    # DEBUGGING PRINT CALLS:
    # print(ACTIVE_DATAFRAMES.data)
    # print(AVAIL_BONDS.data)


def create_figure():
    """Create the figure."""
    fig = figure(width=800)
    
    ACTIVE_DATAFRAMES.data


DATAFRAME_SEL.on_change('value', update_dataframe_selector)


# Create a source for the active bonds from within the loaded dataframes
# ACTIVE_BONDS = ColumnDataSource(data=dict(user_sel=[], available=[]))

# ACTIVE_BONDS_SEL = MultiSelect(
#     title="Bond Selection",
#     options=FIXME)

p = Paragraph(text="""The dataframe selector represents the selection
    of one *.csv file.""", width=200, height=100)

mainLayout = layout([widgetbox(DATAFRAME_SEL, BOND_SEL)], [widgetbox(p)])

curdoc().add_root(mainLayout)
