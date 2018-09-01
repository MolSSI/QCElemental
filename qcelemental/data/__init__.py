import json
import pathlib

with open(pathlib.Path(__file__).parent /
          'srd144_Atomic_Weights_and_Isotopic_Compositions_for_All_Elements.json') as handle:
    atomic_weights_and_isotopic_compositions_for_all_elements = json.load(handle)

from .element_names import element_names
from .longest_lived_isotope_for_unstable_elements import longest_lived_isotope_for_unstable_elements
