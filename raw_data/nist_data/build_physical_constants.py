"""
This file will generate a JSON blob usable by QCElemental for physical constants
"""

import datetime
import json

import requests
from yapf.yapflib.yapf_api import FormatCode

metadata_file = "../../raw_data/srd121_nist-codata-fundamental-physical-constants-2014-metadata.json"
with open(metadata_file, "r") as handle:
    metadata = json.load(handle)

title = metadata["title"]
date_modified = metadata["modified"]
year = date_modified.split("-")[0]
doi = metadata["distribution"][-1]["accessURL"].strip("https://dx.doi.org/")
url = metadata["distribution"][0]["downloadURL"]
access_date = str(datetime.datetime.utcnow())

constants = requests.get(url).json()

output = '''
"""
This is a automatically generated file from the {0} NIST fundamental constants.
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

constants_json = {
    "title": title,
    "date": date_modified,
    "doi": doi,
    "url": url,
    "access_data": access_date,
    "constants": {},
}

for pc in constants["constant"]:
    value = pc["Value"].strip()
    uncertainty = pc["Uncertainty"]
    if uncertainty == "(exact)":
        value = value.replace("...", "")

    constants_json["constants"][pc["Quantity "].lower()] = {
        "quantity": pc["Quantity "],
        "unit": pc["Unit"],
        "value": value.replace(" ", ""),
        "uncertainty": uncertainty,
    }
output += "nist_{}_codata = {}".format(year, constants_json)

output = FormatCode(output)

fn = "nist_{}_codata.py".format(year)
with open(fn, "w") as handle:
    handle.write(output[0])
