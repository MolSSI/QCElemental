"""
This file will generate a JSON blob usable by QCElemental for physical constants
"""

import datetime
import os

import black
import pandas as pd
import requests

table_url = "https://physics.nist.gov/cuu/Constants/Table/allascii.txt"

title = "NIST-CODATA Internationally Recommended 2018 Values of the Fundamental Physical Constants - SRD 121"  # edited year from https://catalog.data.gov/dataset/nist-codata-fundamental-physical-constants-srd-121
date_modified = "2019-05-20"  # https://pml.nist.gov/cuu/Constants/bibliography.html
data_through = "2018-12-31"  # https://pml.nist.gov/cuu/Constants/bibliography.html
year = data_through.split("-")[0]
doi = ""  # LAB: I can't find a thing
url = table_url
access_date = str(datetime.datetime.utcnow())

constants = requests.get(url).text
with open("localtable", "w") as fp:
    fp.write(constants)
    # Warning: colspecs="infer" or infer_nrows=400 still misses some ends of names
    data_also = pd.read_fwf("localtable", widths=[60, 25, 24, 20], skiprows=[0, 1, 2, 3, 4, 5, 6, 7, 8, 10])
os.unlink("localtable")

constants = data_also.to_dict("index")

output = f'''
"""
This is a automatically generated file from the {year} NIST fundamental constants.
Title: {title}
Date: {date_modified}
DOI: {doi}
URL: {url}
Access Date: {access_date} UTC

File Authors: QCElemental Authors
"""


'''

constants_json = {
    "title": title,
    "date": date_modified,
    "doi": doi,
    "url": url,
    "access_data": access_date,
    "constants": {},
}

for pc in constants.values():
    value = pc["Value"].strip()
    uncertainty = pc["Uncertainty"]
    if uncertainty == "(exact)":
        value = value.replace("...", "")

    constants_json["constants"][pc["Quantity"].lower()] = {
        "quantity": pc["Quantity"],
        "unit": str(pc["Unit"])
        .replace("nan", "")
        .replace("^-1", "^{-1}")
        .replace("^-2", "^{-2}")
        .replace("^-3", "^{-3}")
        .replace("^-4", "^{-4}")
        .replace("_90", "_{90}"),
        "value": value.replace(" ", ""),
        "uncertainty": uncertainty,
    }
output += "nist_{}_codata = {}".format(year, constants_json)

output = black.format_str(output, mode=black.FileMode())

fn = f"nist_{year}_codata.py"
with open(fn, "w") as handle:
    handle.write(output)
