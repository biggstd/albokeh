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
from utils import read_metadata, md_reader, create_pandas_dataframe

# Create the title HTML Div.
title_div = Div(
    text=open(os.path.join(
        os.path.dirname(__file__),
        "templates",
        "rdf_title.html")).read(), width=800
)

# Source the metadata
METADATA = read_metadata()
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
for data_dict in DFMD:
    new_df = create_pandas_dataframe(data_dict.get("dataFile"))