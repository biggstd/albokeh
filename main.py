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
# Bokeh imports
from bokeh.plotting import figure
from bokeh.layouts import layout, widgetbox
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.models.widgets import MultiSelect, CheckboxGroup, Div
from bokeh.palettes import linear_palette, viridis
from bokeh.io import curdoc
# Local, relative module imports
sys.path.append(os.getcwd())
from utils import read_metadata, md_reader, create_pandas_dataframe,\
	get_sample_names

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
ALL_LOADED_DATAFRAMES = list()
ALL_LOADED_SAMPLES = list()

for data_dict in DFMD:
	# Construct a dataframe:
    new_df = create_pandas_dataframe(data_dict.get("dataFile"))
    # Find the sample that this dataframe represents:
    new_sample = get_sample_names(data_dict.get("assay_md"))[0]
    ALL_LOADED_SAMPLES.extend(new_sample)
    # Add a new column that contains the compound
    new_df['sample'] = new_compound
    ALL_LOADED_DATAFRAMES.extend(new_df)

# Create SOURCES that will dynamically update themselves.
ACTIVE_DATAFRAMES = ColumnDataSource(data=dict(active=[]))

# Define active dataframes/compounds/aluminum dimers
DATAFRAME_SEL = MultiSelect(
	title="Dataframe Selection",
	options=ALL_LOADED_SAMPLES
)

mainLayout = layout([DATAFRAME_SEL])

curdoc().add_root(mainLayout)

