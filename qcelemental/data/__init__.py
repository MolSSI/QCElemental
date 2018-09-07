import json
import pathlib

with open(pathlib.Path(__file__).parent /
          'srd144_Atomic_Weights_and_Isotopic_Compositions_for_All_Elements.json') as handle:
    atomic_weights_and_isotopic_compositions_for_all_elements = json.load(handle)

from .element_names import element_names

from .longest_lived_isotope_for_unstable_elements import longest_lived_isotope_for_unstable_elements

with open(pathlib.Path(__file__).parent / 'srd121_nist-codata-fundamental-physical-constants-2014.json') as handle:
    nist_codata_2014 = json.load(handle)

with open(pathlib.Path(__file__).parent /
          'srd121_nist-codata-fundamental-physical-constants-2014-metadata.json') as handle:
    nist_codata_2014_metadata = json.load(handle)
