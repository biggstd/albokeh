"""
===================
Simple ISA Document
===================

Author: Tyler Biggs

A simple, but complete ISA document for testing purposes.
"""

from isatools.model import *
from isatools.isajson import ISAJSONEncoder
import json
import os


def create_ISA_json():
    """
    Creates a simple ISA json and saves it to the local directory.
    """

    def join_path(filename):
        file_path = os.path.join(data_path, filename)
        return file_path

    # INVESTIGATION
    inv = Investigation()
    inv.identifier = "Investigation identifier"
    inv.title = "Ttitle of the Investigation"
    inv.description = (
        "A longer description that describes the ISA "
        "document in question. It could go on for quite "
        "some time, and cover several lines.")

    # STUDY
    stu = Study()
    stu.identifier = "studyID"
    stu.title = "My ISA Study"
    stu.description = "My ISA study description."

    inv.studies.append(stu)

    # ONTOLOGIES
    obi = OntologySource(
        name='OBI',
        description="Ontology for Investigations")

    inv.ontology_source_references.append(obi)
    intervention_design = OntologyAnnotation(term_source=obi)
    intervention_design.term = "intervention design"
    stu.design_descriptors.append(intervention_design)
    source = Source(name='source_material')
    stu.sources.append(source)
    assay = Assay()

    assay.samples.append(Sample(
        name='temperature',
        factor_values=[FactorValue(value=25, unit='celsius')]))

    metadata_json = json.dumps(
        inv,
        cls=ISAJSONEncoder,
        sort_keys=True,
        indent=4,
        separators=(',', ':')
    )

    return metadata_json


def main():
    """Writes the aluminate json entry to a specified folder."""
    metadata = create_ISA_json()

    with open('simple_ISA_doc.json', 'w') as f:
        f.write(metadata)


if __name__ == '__main__':
    main()
