import json
import os
import pathlib

#py36 with open(pathlib.Path(__file__).parent /
#py36           'srd144_Atomic_Weights_and_Isotopic_Compositions_for_All_Elements.json') as handle:
with open(os.path.join(str(pathlib.Path(__file__).parent),
          'srd144_Atomic_Weights_and_Isotopic_Compositions_for_All_Elements.json')) as handle:
    atomic_weights_and_isotopic_compositions_for_all_elements = json.load(handle)

from .element_names import element_names

from .longest_lived_isotope_for_unstable_elements import longest_lived_isotope_for_unstable_elements

#py36 with open(pathlib.Path(__file__).parent / 'srd121_nist-codata-fundamental-physical-constants-2014.json') as handle:
#py36     nist_codata_2014 = json.load(handle)
with open(os.path.join(str(pathlib.Path(__file__).parent), 'srd121_nist-codata-fundamental-physical-constants-2014.json')) as handle:
    nist_codata_2014 = json.load(handle)

#py36 with open(pathlib.Path(__file__).parent /
#py36           'srd121_nist-codata-fundamental-physical-constants-2014-metadata.json') as handle:
with open(os.path.join(str(pathlib.Path(__file__).parent),
          'srd121_nist-codata-fundamental-physical-constants-2014-metadata.json')) as handle:
    nist_codata_2014_metadata = json.load(handle)
