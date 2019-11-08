"""Queries the PubChem database using a compound name (i.e. 1,3,5-hexatriene)
   to obtain a molecule string that can be passed to Molecule. ::

      results = getPubChemObj("1,3,5-hexatriene")

      Results is an array of results from PubChem matches to your query.
        for entry in results:
           entry["CID"]         => PubChem compound identifer
           entry["IUPAC"]       => IUPAC name for the resulting compound
           entry["PubChemObj"]  => instance of PubChemObj for this compound

           entry["PubChemObj"].get_molecule_string()   => returns a string compatible
                                                        with Psi4's Molecule creation

"""

import json
import re

from ..exceptions import ValidationError
from .regex import DECIMAL


class PubChemObj:
    def __init__(self, cid, mf, iupac, charge):
        self.url = "http://pubchem.ncbi.nlm.nih.gov/summary/summary.cgi"
        self.cid = cid
        self.mf = mf
        self.iupac = iupac
        self.molecular_charge = charge
        self.natom = 0
        self.dataSDF = ""

    def __str__(self):
        return "%17d   %s\n" % (self.cid, self.iupac)

    def get_sdf(self):
        """Function to return the SDF (structure-data file) of the PubChem object."""
        from urllib.request import urlopen, Request
        from urllib.parse import quote
        from urllib.error import URLError

        if len(self.dataSDF) == 0:
            url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{}/SDF?record_type=3d".format(
                quote(str(self.cid))
            )
            req = Request(url, headers={"Accept": "chemical/x-mdl-sdfile"})
            try:
                self.dataSDF = urlopen(req).read().decode("utf-8")
            except URLError as e:
                msg = "Unable to open\n\n%s\n\ndue to the error\n\n%s\n\n" % (url, e)
                msg += "It is possible that 3D information does not exist for this molecule in the PubChem database\n"
                print(msg)
                raise ValidationError(msg)
        return self.dataSDF

    def name(self):
        """Function to return the IUPAC name of the PubChem object."""
        return self.iupac

    def get_cartesian(self):
        """Function to return a string of the atom symbol and XYZ
        coordinates of the PubChem object.

        """
        try:
            sdf_text = self.get_sdf()
        except Exception as e:
            raise ValidationError(e.message)

        # Find
        # NA NB                        CONSTANT
        # 14 13  0     0  0  0  0  0  0999 V2000
        m = re.search(r"^\s*(\d+)\s+(?:\d+\s+){8}V2000$", sdf_text, re.MULTILINE)
        self.natom = 0
        if m:
            self.natom = int(m.group(1))

        if self.natom == 0:
            raise ValidationError(
                "PubChem: Cannot find the number of atoms.  3D data doesn't appear\n"
                + "to be available for %s.\n" % self.iupac
            )

        lines = re.split("\n", sdf_text)

        #  3.7320   -0.2500    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
        atom_re = re.compile(
            r"^\s*" + DECIMAL + r"\s+" + DECIMAL + r"\s+" + DECIMAL + r"\s*(\w+)(?:\s+\d+){12}", re.VERBOSE
        )

        molecule_string = "PubchemInput\n"

        atom_count = 0
        for line in lines:

            atom_match = atom_re.match(line)
            if atom_match:
                x = float(atom_match.group(1))
                y = float(atom_match.group(2))
                z = float(atom_match.group(3))
                sym = atom_match.group(4)

                atom_count = atom_count + 1

                molecule_string += "%s %10.6f %10.6f %10.6f\n" % (sym, x, y, z)

                if atom_count == self.natom:
                    break

        return molecule_string

    def get_molecule_string(self):
        """Function to obtain a molecule string through
        get_cartesian() or fail.
        """
        try:
            return self.get_cartesian()
        except Exception as e:
            return e.message


def get_pubchem_results(name):
    """Function to query the PubChem database for molecules matching the
    input string. Builds a PubChemObj object if found.

    """
    from urllib.request import urlopen
    from urllib.parse import quote
    from urllib.error import URLError

    if name.isdigit():
        print("\tSearching PubChem database for CID {}".format(name))
        url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{}/property/IUPACName,MolecularFormula,Charge/JSON".format(
            quote(name)
        )

    else:
        if name.endswith("*"):
            name = name[:-1]
            loose = True
        else:
            loose = False
        print(
            "\tSearching PubChem database for {} ({} returned)".format(
                name, "all matches" if loose else "single best match"
            )
        )
        url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{}/property/IUPACName,MolecularFormula,Charge/JSON?name_type={}".format(
            quote(name), "word" if loose else "complete"
        )

    try:
        response = urlopen(url)
    except URLError as e:
        # travis urllib.error.HTTPError: HTTP Error 503: Service Unavailable
        raise ValidationError(
            """\tPubchemError\n%s\n\treceived when trying to open\n\t%s\n\tCheck your internet connection, and the above URL, and try again.\n"""
            % (str(e), url)
        ) from e
    data = json.loads(response.read().decode("utf-8"))
    results = []
    for d in data["PropertyTable"]["Properties"]:
        if "IUPACName" not in d:
            continue
        pubobj = PubChemObj(d["CID"], d["IUPACName"], d["IUPACName"], d["Charge"])
        results.append(pubobj)

    print("\tFound {} result(s)".format(len(results)))
    return results


if __name__ == "__main__":
    # * comment "..exceptions" line above
    # * sulfonate below has no 3D structure available
    # * XYZ printing for tropolone* suppressed b/c too many and some have no 3D

    for inp in [
        "1-methoxy-4-[(E)-prop-1-enyl]benzene",
        "4-[bis(4-hydroxyphenyl)methyl]phenol",
        "tropolone",
        "tropolone*",
        "sodium benzenesulfonate",
    ]:  # pragma: no cover
        obj = get_pubchem_results(inp)

        for r in obj:
            print(r, end="")
            if inp != "tropolone*":
                print(r.get_molecule_string())
