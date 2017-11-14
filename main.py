"""
=====================================
Boiler Plat Visualization Application
=====================================

:Author:
    Tyler Biggs

.. todo::

    [x] Have this application auto-generate the datapaths correctly
    [ ] try to swap to get_model_by_name to avoid unlabeled index use
    [ ] structure the display of selected metadata
    [ ] add a nested color structure (by dataframe then by column)?
    [ ] add an interative marker structure?
    [ ] Move legend to margins

"""

# General imports
import os
import sys
import collections
import itertools
import json
# Bokeh imports
from bokeh import events
from bokeh.plotting import figure
from bokeh.layouts import layout, widgetbox, row, column
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.models.widgets import MultiSelect, Div, Paragraph, Button
from bokeh.palettes import linear_palette, viridis
from bokeh.io import curdoc
# Local, relative module imports
sys.path.append(os.getcwd())
from utils import read_metadata, md_reader, create_pandas_dataframe,\
    get_sample_names, retr_termSource_values
from generateISA import create_metadata, main


# Build the metadata with system appropriate filepaths
# os.path.abspath('data')
METADATA = json.loads(create_metadata(os.path.abspath('albokeh/data')))

# Create the title HTML Div.
title_div = Div(
    text=open(os.path.join(
        os.path.dirname(__file__),
        "templates",
        "rdf_title.html")).read(), width=800
)

# Source the metadata
# METADATA = read_metadata("albokeh/metadata.json")
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

    fig = figure(
        name="primary_figure",
        width=800,
        tools="pan,wheel_zoom,box_zoom,reset,tap"
    )

    sel_dataframes = [ALL_LOADED_DATAFRAMES[x]["dataframe"]
                      for x in DATAFRAME_SEL.value]

    metadata_list = [ALL_LOADED_DATAFRAMES[x]["assay_md"]
                     for x in DATAFRAME_SEL.value]

    sel_bonds = BOND_SEL.value

    # enumerate through the data frames to be used and the index value.
    # enumerate() is used as zip() failes when there is only one item.
    for idx, df in enumerate(sel_dataframes):

        # Declare the source for the current frame:
        fig_source = ColumnDataSource(df)

        # Add the callback event. In this case I call a function that takess
        # the associated metadata as an argument, and returns a callback
        # function. This is to workaroudn callback functions only allowing
        # one argument.
        # fig.on_event(events.SelectionGeometry,
                     # generate_selection_callback(metadata=metadata_list[idx]))
        fig_source.callback = generate_selection_callback(metadata=metadata_list[idx])

        # Iterate over the bonds selected.
        for idxx, bond in enumerate(sel_bonds):

            active_bond = 'RDF_' + bond

            fig.line(  # Draw a line plot
                source=fig_source,
                x='r',
                y=active_bond,
                legend='sample',
                # color=bond_color,
                line_width=1.5,
            )

            fig.circle(  # Draw a circle/dot plot
                source=fig_source,
                x='r',
                y=active_bond,
                legend='sample',
                # color=bond_color,
            )

    return fig


def build_fig_callback():
    """This is the callback function that will update the figure curdoc
    model."""
    mainLayout.children[1].children[1] = create_figure()


def generate_selection_callback(metadata):
    """Generates and returns a callback function that updates a div element."""
    def generated_callback(event):
        """The new callback function to be assigned."""
        print(event)
        mainLayout.children[2] = Paragraph(text=str(metadata))

    return generated_callback


DATAFRAME_SEL.on_change('value', update_dataframe_selector)

MAKE_PLOT_BUTTON = Button(label="Build Plot")
MAKE_PLOT_BUTTON.on_click(build_fig_callback)

p = Paragraph(text="""The dataframe selector represents the selection
    of one *.csv file.""")

controls = widgetbox(DATAFRAME_SEL, BOND_SEL, MAKE_PLOT_BUTTON, p)

mainLayout = layout(
    children=[
        [title_div],
        [controls, create_figure()],
        Paragraph()
    ],
    sizing_mode='fixed'
)

curdoc().add_root(mainLayout)
