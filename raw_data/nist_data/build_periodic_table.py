"""
This file will generate a JSON blob usable by QCElemental for physical constants
"""

import datetime
import json
import re

import requests
from yapf.yapflib.yapf_api import FormatCode  # noqa

# from https://www.nist.gov/pml/periodic-table-elements on 30 Aug 2018
#   NIST SP 966 (July 2018)
element_names = [
    "Hydrogen",
    "Helium",
    "Lithium",
    "Beryllium",
    "Boron",
    "Carbon",
    "Nitrogen",
    "Oxygen",
    "Fluorine",
    "Neon",
    "Sodium",
    "Magnesium",
    "Aluminum",
    "Silicon",
    "Phosphorus",
    "Sulfur",
    "Chlorine",
    "Argon",
    "Potassium",
    "Calcium",
    "Scandium",
    "Titanium",
    "Vanadium",
    "Chromium",
    "Manganese",
    "Iron",
    "Cobalt",
    "Nickel",
    "Copper",
    "Zinc",
    "Gallium",
    "Germanium",
    "Arsenic",
    "Selenium",
    "Bromine",
    "Krypton",
    "Rubidium",
    "Strontium",
    "Yttrium",
    "Zirconium",
    "Niobium",
    "Molybdenum",
    "Technetium",
    "Ruthenium",
    "Rhodium",
    "Palladium",
    "Silver",
    "Cadmium",
    "Indium",
    "Tin",
    "Antimony",
    "Tellurium",
    "Iodine",
    "Xenon",
    "Cesium",
    "Barium",
    "Lanthanum",
    "Cerium",
    "Praseodymium",
    "Neodymium",
    "Promethium",
    "Samarium",
    "Europium",
    "Gadolinium",
    "Terbium",
    "Dysprosium",
    "Holmium",
    "Erbium",
    "Thulium",
    "Ytterbium",
    "Lutetium",
    "Hafnium",
    "Tantalum",
    "Tungsten",
    "Rhenium",
    "Osmium",
    "Iridium",
    "Platinum",
    "Gold",
    "Mercury",
    "Thallium",
    "Lead",
    "Bismuth",
    "Polonium",
    "Astatine",
    "Radon",
    "Francium",
    "Radium",
    "Actinium",
    "Thorium",
    "Protactinium",
    "Uranium",
    "Neptunium",
    "Plutonium",
    "Americium",
    "Curium",
    "Berkelium",
    "Californium",
    "Einsteinium",
    "Fermium",
    "Mendelevium",
    "Nobelium",
    "Lawrencium",
    "Rutherfordium",
    "Dubnium",
    "Seaborgium",
    "Bohrium",
    "Hassium",
    "Meitnerium",
    "Darmstadtium",
    "Roentgenium",
    "Copernicium",
    "Nihonium",
    "Flerovium",
    "Moscovium",
    "Livermorium",
    "Tennessine",
    "Oganesson",
]

# from https://www.nist.gov/pml/periodic-table-elements on 30 Aug 2018
#   NIST SP 966 (July 2018)

longest_lived_isotope_for_unstable_elements = {
    "Tc": 98,
    "Pm": 145,
    "Po": 209,
    "At": 210,
    "Rn": 222,
    "Fr": 223,
    "Ra": 226,
    "Ac": 227,
    "Np": 237,
    "Pu": 244,
    "Am": 243,
    "Cm": 247,
    "Bk": 247,
    "Cf": 251,
    "Es": 252,
    "Fm": 257,
    "Md": 258,
    "No": 259,
    "Lr": 266,
    "Rf": 267,
    "Db": 268,
    "Sg": 271,
    "Bh": 270,
    "Hs": 269,
    "Mt": 278,
    "Ds": 281,
    "Rg": 282,
    "Cn": 285,
    "Nh": 286,
    "Fl": 289,
    "Mc": 289,
    "Lv": 293,
    "Ts": 294,
    "Og": 294,
}

data_url = "https://nist.gov/srd/srd_data//srd144_Atomic_Weights_and_Isotopic_Compositions_for_All_Elements.json"

title = "Atomic Weights and Isotopic Compositions with Relative Atomic Masses - SRD144"
date_modified = "2011-01-14"
year = date_modified.split("-")[0]
doi = "10.1351/PAC-REP-10-06-02"
url = data_url
access_date = str(datetime.datetime.utcnow())

atomic_weights_data = requests.get(url).json()

output = '''
"""
This is a automatically generated file from the {0} NIST atomic weights.
Title: {1}
Date: {2}
DOI: {3}
URL: {4}
Access Date: {5} UTC

File Authors: QCElemental Authors
"""


'''.format(
    year, title, date_modified, doi, url, access_date
)

atomic_weights_json = {"title": title, "date": date_modified, "doi": doi, "url": url, "access_data": access_date}

# length number of elements
Z = [0]  # , 1, 2, ...
E = ["X"]  # , H, He, ...
name = ["Dummy"]  # , Hydrogen, Helium, ...

# length number of elements plus number of isotopes
_EE = ["X", "X"]  # , H, H, H, ..., He, He, He, ...
EA = ["X", "X0"]  # , H, H1, H2, ..., He, He3, He4, ...
A = [0, 0]  # , 1, 1, 2, ..., 4, 3, 4, ...
masses = ["0", "0"]  # , 1.0078, 1.0078, 2.014, ..., 4.0026, 3.016, 4.0026, ...V

uncertain_value = re.compile(r"""(?P<value>[\d.]+)(?P<uncertainty>\([\d#]+\))?""")
aliases = {"D": "H2", "T": "H3"}

newnames = {"Uut": "Nh", "Uup": "Mc", "Uus": "Ts"}
for delem in atomic_weights_data["data"]:
    symbol = delem["Atomic Symbol"]
    delem["Atomic Symbol"] = newnames.get(symbol, symbol)
    for diso in delem["isotopes"]:
        symbol = diso["Atomic Symbol"]
        diso["Atomic Symbol"] = newnames.get(symbol, symbol)

# element loop
for delem in atomic_weights_data["data"]:
    mass_of_most_common_isotope = None
    mass_number_of_most_common_isotope = None
    max_isotopic_contribution = 0.0

    # isotope loop
    for diso in delem["isotopes"]:
        mobj = re.match(uncertain_value, diso["Relative Atomic Mass"])

        if mobj:
            mass = mobj.group("value")
        else:
            raise ValueError(
                "Trouble parsing mass string ({}) for element ({})".format(
                    diso["Relative Atomic Mass"], diso["Atomic Symbol"]
                )
            )

        a = int(diso["Mass Number"])

        if diso["Atomic Symbol"] in aliases:
            _EE.append("H")
            EA.append(aliases[diso["Atomic Symbol"]])
            A.append(a)
            masses.append(mass)

            _EE.append("H")
            EA.append(diso["Atomic Symbol"])
            A.append(a)
            masses.append(mass)

        else:
            _EE.append(diso["Atomic Symbol"])
            EA.append(diso["Atomic Symbol"] + diso["Mass Number"])
            A.append(a)
            masses.append(mass)

        if "Isotopic Composition" in diso:
            mobj = re.match(uncertain_value, diso["Isotopic Composition"])

            if mobj:
                if float(mobj.group("value")) > max_isotopic_contribution:
                    mass_of_most_common_isotope = mass
                    mass_number_of_most_common_isotope = a
                    max_isotopic_contribution = float(mobj.group("value"))

    # Source atomic_weights_and_isotopic_compositions_for_all_elements deals with isotopic composition of
    #   stable elements. For unstable elements, need another source for the longest-lived isotope.
    if mass_of_most_common_isotope is None:
        mass_number_of_most_common_isotope = longest_lived_isotope_for_unstable_elements[diso["Atomic Symbol"]]
        eliso = delem["Atomic Symbol"] + str(mass_number_of_most_common_isotope)
        mass_of_most_common_isotope = masses[EA.index(eliso)]

    _EE.append(delem["Atomic Symbol"])
    EA.append(delem["Atomic Symbol"])
    A.append(mass_number_of_most_common_isotope)
    masses.append(mass_of_most_common_isotope)

    z = int(delem["Atomic Number"])

    Z.append(z)
    E.append(delem["Atomic Symbol"])
    name.append(element_names[z - 1].capitalize())

atomic_weights_json["Z"] = Z
atomic_weights_json["E"] = E
atomic_weights_json["name"] = name
atomic_weights_json["_EE"] = _EE
atomic_weights_json["EA"] = EA
atomic_weights_json["A"] = A
atomic_weights_json["mass"] = masses
output += "nist_{}_atomic_weights = {}".format(year, json.dumps(atomic_weights_json))

# output = FormatCode(output)[0]
fn = "nist_{}_atomic_weights.py".format(year)
with open(fn, "w") as handle:
    handle.write(output)
