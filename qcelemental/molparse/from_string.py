import pprint
import re
from typing import Dict, Tuple, Union

from ..exceptions import ChoicesError, MoleculeFormatError, ValidationError
from ..util import filter_comments, provenance_stamp
from . import pubchem
from .from_arrays import from_input_arrays
from .regex import CARTXYZ, CHGMULT, ENDL, NUCLEUS, NUMBER, SEP

__all__ = ["from_string"]


def from_string(
    molstr: str,
    dtype: str = None,
    *,
    name: str = None,
    fix_com: bool = None,
    fix_orientation: bool = None,
    fix_symmetry: str = None,
    return_processed: bool = False,
    enable_qm: bool = True,
    enable_efp: bool = True,
    missing_enabled_return_qm: str = "none",
    missing_enabled_return_efp: str = "none",
    verbose=1,
) -> Union[Dict, Tuple[Dict, Dict]]:
    r"""Construct a molecule dictionary from any recognized string format.

    Parameters
    ----------
    molstr
        Multiline string specification of molecule in a recognized format.
    dtype
        {'xyz', 'xyz+', 'psi4', 'psi4+'}
        Molecule format name; see below for details.
    return_processed
        Additionally return intermediate dictionary.
    enable_qm
        Consider quantum mechanical domain in processing the string constants
        into the returned molrec.
    enable_efp
        Consider effective fragment potential domain in processing the string
        contents into the returned molrec. Only relevant if `dtype` supports EFP.
    missing_enabled_return_qm
        {'minimal', 'none', 'error'}
        If `enable_qm=True`, what to do if it has no atoms/fragments?
        Respectively, return a fully valid but empty molrec, return empty
        dictionary, or throw error.
    missing_enabled_return_efp
        {'minimal', 'none', 'error'}
        If `enable_efp=True`, what to do if it has no atoms/fragments?
        Respectively, return a fully valid but empty molrec, return empty
        dictionary, or throw error.
    name
        Override `molstr` information for label for molecule; should
        be valid Python identifier. One of a very limited number of
        fields (three others follow) for trumping `molstr`. Provided
        for convenience, since the alternative would be collect the
        resulting molrec (discarding the Mol if called from class),
        editing it, then remaking the Mol.
    fix_com
        Override `molstr` information for whether translation of `geom`
        is allowed or disallowed.
    fix_orientation
        Override `molstr` information for whether rotation of `geom`
        is allowed or disallowed.
    fix_symmetry
        Override `molstr` information for maximal point group symmetry
        which geometry should be treated.

    Returns
    -------
    molrec : dict
        Molecule dictionary spec. See :py:func:`from_arrays`.
    molinit : dict, optional
        Intermediate "molrec"-like dictionary containing `molstr` info after
        parsing by this function but before the validation and defaulting of
        `from_arrays` that returns the proper `molrec`.
        Only provided if `return_processed` is True.

    Raises
    ------
    qcelemental.MoleculeFormatError
        After processing of `molstr`, only an empty string should remain.
        Anything left is a syntax error.

    Notes
    -----
    Several formats are interpretable:

    .. code-block:: none

        xyz - Strict XYZ format
        -----------------------

            String Layout
            -------------
            <number of atoms>
            comment line
            <element_symbol or atomic_number> <x> <y> <z>
            ...
            <element_symbol or atomic_number> <x> <y> <z>

            QM Domain
            ---------
            Specifiable: geom, elem/elez (element identity)
            Inaccessible: mass, real (vs. ghost), elbl (user label), name, units (assumed [A]),
                          input_units_to_au, fix_com/orientation/symmetry, fragmentation,
                          molecular_charge, molecular_multiplicity

            Notes
            -----
            <number of atoms> is pattern-matched but ignored.

        xyz+ - Enhanced XYZ format
        --------------------------

            String Layout
            -------------
            <number of atoms> [<bohr|au|ang>]
            [<molecular_charge> <molecular_multiplicity>] comment line
            <psi4_nucleus_spec> <x> <y> <z>
            ...
            <psi4_nucleus_spec> <x> <y> <z>

            QM Domain
            ---------
            Specifiable: geom, elem/elez (element identity), mass, real (vs. ghost), elbl (user label),
                         units (defaults [A]), molecular_charge, molecular_multiplicity
            Inaccessible: name, input_units_to_au, fix_com/orientation/symmetry, fragmentation

            Notes
            -----
            <number of atoms> is pattern-matched but ignored.

        psi4 - Psi4 molecule {...} format
        ---------------------------------

            QM Domain
            ---------
            Specifiable: geom, elem/elez (element identity), mass, real (vs. ghost), elbl (user label),
                         units (defaults [A]), fix_com/orientation/symmetry, fragment_separators,
                         fragment_charges, fragment_multiplicities, molecular_charge, molecular_multiplicity
            Inaccessible: name, input_units_to_au

                PubChem
                -------
                pubchem : <cid|name|formula> [*]

                A string like the above searches the PubChem database and substitutes the below. Adding the wildcard
                searches for multiple matches and raises ChoicesError with matches for further consideration attached.

                Specifiable: geom, elem/elez (element identity), units (fixed [A]), molecular_charge,
                             molecular_multiplicity (fixed singlet), name

            EFP Domain
            ----------
            Specifiable: units, fix_com/orientation/symmetry, fragment_files, hint_types, geom_hints
            Inaccessible: anything atomic or fragment details -- geom, elem/elez (element identity),
                          mass, real (vs. ghost), elbl (user label), fragment_separators, fragment_charges,
                          fragment_multiplicities, molecular_charge, molecular_multiplicity

        psi4+ - Psi4 non-Cartesian molecule {...} format
        ------------------------------------------------
        Like `dtype=psi4` (although combination with EFP not tested) except
        that instead of pure-Cartesian geometry, allow variables, zmatrix,
        and un-fully-specified geometries. *Not* MolSSI standard, but we're
        not dropping zmatrix yet. Note that in Psi4 internal coordinates
        defined through a zmatrix have no bearing on geometry
        optimization internals or constraints.

    """
    if verbose >= 2:
        print("<<< FROM_STRING\n", molstr, "\n>>>")

    # << 1 >>  str-->str -- discard comments
    molstr = filter_comments(molstr.strip())

    def parse_as_xyz_ish(molstr, strict):
        molinit = {}

        # << 2 >>  str-->dict -- process atoms, units[, chg, mult]
        molstr, processed = _filter_xyz(molstr, strict=strict)
        molinit.update(processed)

        if molstr:
            raise MoleculeFormatError(f"""Unprocessable Molecule remnants under {dtype}:\n{molstr}""")

        return molstr, molinit

    def parse_as_psi4_ish(molstr, unsettled):
        molinit = {}

        # Notes
        # * *_filter functions must fill non-overlapping fields
        # * not recc but can add to downstream by appending to str

        # << 2.1 >>  str-->str -- process pubchem into str for downfunction
        molstr, processed = _filter_pubchem(molstr)
        molinit.update(processed)

        # << 2.2 >>  str-->dict -- process units, com, orient, symm
        molstr, processed = _filter_universals(molstr)
        molinit.update(processed)

        # << 2.3 >>  str-->dict -- process efp frags
        molstr, processed = _filter_libefp(molstr)
        molinit.update(processed)

        # << 2.4 >>  str-->dict -- process atoms, chg, mult, frags
        molstr, processed = _filter_mints(molstr, unsettled=unsettled)
        molinit.update(processed)

        if molstr:
            raise MoleculeFormatError(f"""Unprocessable Molecule remnants under {dtype}:\n{molstr}""")

        return molstr, molinit

    if dtype == "xyz":
        molstr, molinit = parse_as_xyz_ish(molstr, strict=True)

    elif dtype == "xyz+":
        molstr, molinit = parse_as_xyz_ish(molstr, strict=False)

    elif dtype == "psi4":
        molstr, molinit = parse_as_psi4_ish(molstr, unsettled=False)

    elif dtype == "psi4+":
        molstr, molinit = parse_as_psi4_ish(molstr, unsettled=True)

    elif dtype is None:
        dtype = "[psi4, xyz, xyz+, psi4+]"  # for error message
        try:
            molstr, molinit = parse_as_psi4_ish(molstr, unsettled=False)
            dtype = "psi4"
        except MoleculeFormatError as e:
            min_error_length = len(str(e))
            min_error = e
            try:
                molstr, molinit = parse_as_xyz_ish(molstr, strict=True)
                dtype = "xyz"
            except MoleculeFormatError as e:
                if len(str(e)) < min_error_length:
                    min_error_length = len(str(e))
                    min_error = e
                try:
                    molstr, molinit = parse_as_xyz_ish(molstr, strict=False)
                    dtype = "xyz+"
                except MoleculeFormatError as e:
                    if len(str(e)) < min_error_length:
                        min_error_length = len(str(e))
                        min_error = e
                    try:
                        molstr, molinit = parse_as_psi4_ish(molstr, unsettled=True)
                        dtype = "psi4+"
                    except MoleculeFormatError as e:
                        if len(str(e)) < min_error_length:
                            min_error_length = len(str(e))
                            min_error = e
                        raise min_error
    else:
        raise KeyError(f"Molecule: dtype of `{dtype}` not recognized.")

    # << 3 >>  args-->dict -- process name, com, orient, symm from arguments
    processed = _filter_kwargs(name, fix_com, fix_orientation, fix_symmetry)
    molinit.update(processed)

    if verbose >= 2:
        print("\nFROM_STRING (", dtype, ") --> FROM_INPUT_ARRAYS <<<")
        pprint.pprint(molinit)
        print(">>>\n")

    # << 4 >>  dict-->molspec
    molrec = from_input_arrays(
        speclabel=True,
        enable_qm=enable_qm,
        enable_efp=enable_efp,
        missing_enabled_return_qm=missing_enabled_return_qm,
        missing_enabled_return_efp=missing_enabled_return_efp,
        **molinit,
    )

    # replace from_arrays stamp with from_string stamp
    if "qm" in molrec and molrec["qm"]:
        molrec["qm"]["provenance"] = provenance_stamp(__name__)
    if "efp" in molrec and molrec["efp"]:
        molrec["efp"]["provenance"] = provenance_stamp(__name__)

    if verbose >= 2:
        print("\nFROM_STRING MOLREC <<<", molrec, ">>>\n")

    if return_processed:
        return molrec, molinit
    else:
        return molrec


# TODO maybe molrec needs a "fix_loose" flag to signal the reciever can symmetrize
#    pubchemerror = re.compile(r'^\s*PubchemError\s*$', re.IGNORECASE)
#    pubcheminput = re.compile(r'^\s*PubchemInput\s*$', re.IGNORECASE)
#        # N.B. Anything starting with PubchemError will be handled correctly by the molecule parser
#        # in libmints, which will just print the rest of the string and exit gracefully.

pubchemre = re.compile(r"\Apubchem" + r"\s*:\s*" + r"(?P<pubsearch>(([\S ]+)))\Z", re.IGNORECASE)


def _filter_pubchem(string):
    """Find any "pubchem:" lines in `string`, make call to the pubchem database
    and return the XYZ results back to `string`.

    Author: @andysim

    """

    def process_pubchem(matchobj):
        pubsearch = matchobj.group("pubsearch")

        # search pubchem for the provided string
        try:
            results = pubchem.get_pubchem_results(pubsearch)
        except Exception as e:
            raise ValidationError(e.message)

        if pubsearch.endswith("*"):
            pubsearch = pubsearch[:-1]
        if len(results) == 1:
            # There's only 1 result - use it
            xyz = results[0].get_molecule_string()
            processed["name"] = "IUPAC {}".format(results[0].name())
            processed["molecular_charge"] = float(results[0].molecular_charge)
            if "Input Error" in xyz:
                raise ValidationError(xyz)
        else:
            # There are multiple results -- print and exit
            # * formerly, this checked for (then used) any exact match, but now (LAB; Sep 2018), disabling that
            #   since user explicitly added '*' char & "best match" (not available formerly) returned w/o '*'
            msg = "\tPubchemError\n"
            msg += "\tMultiple pubchem results were found. Replace\n\n\t\tpubchem:%s\n\n" % (pubsearch)
            msg += "\twith the Chemical ID number or exact name from one of the following and re-run.\n\n"
            msg += "\t Chemical ID     IUPAC Name\n\n"
            ematches = {}
            for result in results:
                msg += "%s" % (result)
                ematches[result.cid] = result.iupac
            raise ChoicesError(msg, ematches)

        # remove PubchemInput first line and assert [A]
        xyz = xyz.replace("PubchemInput", "units ang")
        return xyz

    reconstitute = []
    processed = {}

    for line in string.split("\n"):
        line = re.sub(pubchemre, process_pubchem, line.strip())
        if line:
            reconstitute.append(line)

    return "\n".join(reconstitute), processed


def _filter_kwargs(name, fix_com, fix_orientation, fix_symmetry):
    processed = {}
    if name is not None:
        processed["name"] = name
    if fix_com is not None:
        processed["fix_com"] = fix_com
    if fix_orientation is not None:
        processed["fix_orientation"] = fix_orientation
    if fix_symmetry is not None:
        processed["fix_symmetry"] = fix_symmetry

    return processed


com = re.compile(r"\A(no_com|nocom)\Z", re.IGNORECASE)
orient = re.compile(r"\A(no_reorient|noreorient)\Z", re.IGNORECASE)
bohrang = re.compile(r"\Aunits?[\s=]+((?P<ubohr>(bohr|au|a.u.))|(?P<uang>(ang|angstrom)))\Z", re.IGNORECASE)
symmetry = re.compile(r"\Asymmetry[\s=]+(?P<pg>\w+)\Z", re.IGNORECASE)


def _filter_universals(string):
    """Process multiline `string` for fix_ and unit markers,
    returning a string of unprocessed `string` and a dictionary of
    processed fields.

    fix_com
    fix_orientation
    fix_symmetry
    #input_units_to_au (not settable)
    units

    """

    def process_com(matchobj):
        processed["fix_com"] = True
        return ""

    def process_orient(matchobj):
        processed["fix_orientation"] = True
        return ""

    def process_bohrang(matchobj):
        if matchobj.group("uang"):
            processed["units"] = "Angstrom"
        elif matchobj.group("ubohr"):
            processed["units"] = "Bohr"
        return ""

    def process_symmetry(matchobj):
        processed["fix_symmetry"] = matchobj.group("pg").lower()
        return ""

    reconstitute = []
    processed = {}
    com_found = False
    orient_found = False
    bohrang_found = False
    symmetry_found = False

    for line in string.split("\n"):
        line = line.strip()
        if not com_found:
            line, com_found = re.subn(com, process_com, line)
        if not orient_found:
            line, orient_found = re.subn(orient, process_orient, line)
        if not bohrang_found:
            line, bohrang_found = re.subn(bohrang, process_bohrang, line)
        if not symmetry_found:
            line, symmetry_found = re.subn(symmetry, process_symmetry, line)
        if line:
            reconstitute.append(line)

    return "\n".join(reconstitute), processed


# fmt: off
fragment_marker = re.compile(r'^\s*--\s*$', re.MULTILINE)
efpxyzabc = re.compile(
    r'\A' + r'efp' + SEP + r'(?P<efpfile>(\w+))' + SEP +
    r'(?P<x>' + NUMBER + r')' + SEP + r'(?P<y>' + NUMBER + r')' + SEP + r'(?P<z>' + NUMBER + r')' + SEP +
    r'(?P<a>' + NUMBER + r')' + SEP + r'(?P<b>' + NUMBER + r')' + SEP + r'(?P<c>' + NUMBER + r')' + ENDL + r'\Z',
    re.IGNORECASE | re.VERBOSE)

efppoints = re.compile(
    r'\A' + r'efp' + SEP + r'(?P<efpfile>(\w+))' + ENDL +
    r'[\s,]*' + r'(?P<x1>' + NUMBER + r')' + SEP + r'(?P<y1>' + NUMBER + r')' + SEP + r'(?P<z1>' + NUMBER + r')' + ENDL +
    r'[\s,]*' + r'(?P<x2>' + NUMBER + r')' + SEP + r'(?P<y2>' + NUMBER + r')' + SEP + r'(?P<z2>' + NUMBER + r')' + ENDL +
    r'[\s,]*' + r'(?P<x3>' + NUMBER + r')' + SEP + r'(?P<y3>' + NUMBER + r')' + SEP + r'(?P<z3>' + NUMBER + r')' + ENDL + r'\Z',
    re.IGNORECASE | re.MULTILINE | re.VERBOSE)
# fmt: on


def _filter_libefp(string):
    def process_efpxyzabc(matchobj):
        processed["fragment_files"].append(matchobj.group("efpfile"))
        processed["hint_types"].append("xyzabc")
        processed["geom_hints"].append(
            [
                float(matchobj.group("x")),
                float(matchobj.group("y")),
                float(matchobj.group("z")),
                float(matchobj.group("a")),
                float(matchobj.group("b")),
                float(matchobj.group("c")),
            ]
        )
        return ""

    def process_efppoints(matchobj):
        processed["fragment_files"].append(matchobj.group("efpfile"))
        processed["hint_types"].append("points")
        processed["geom_hints"].append(
            [
                float(matchobj.group("x1")),
                float(matchobj.group("y1")),
                float(matchobj.group("z1")),
                float(matchobj.group("x2")),
                float(matchobj.group("y2")),
                float(matchobj.group("z2")),
                float(matchobj.group("x3")),
                float(matchobj.group("y3")),
                float(matchobj.group("z3")),
            ]
        )
        return ""

    reconstitute = []
    processed = {}
    processed["fragment_files"] = []
    processed["hint_types"] = []
    processed["geom_hints"] = []

    # handle `--`-demarcated blocks
    for frag in re.split(fragment_marker, string):
        frag = re.sub(efpxyzabc, process_efpxyzabc, frag.strip())
        frag = re.sub(efppoints, process_efppoints, frag)
        if frag:
            reconstitute.append(frag)

    return "\n--\n".join(reconstitute), processed


fragment_marker = re.compile(r"^\s*--\s*$", re.MULTILINE)
cgmp = re.compile(r"\A" + CHGMULT + r"\Z", re.VERBOSE)

VAR = r"(-?[a-z][a-z0-9_]*)"  # slight cheat to allow neg in `variable`
NUCLABEL = r"([A-Z]{1,3}((_\w+)|(\d+))?)"
ANCHORTO = r"((\d+)|" + NUCLABEL + r")"
ANCHORVAL = r"(" + NUMBER + r"|" + VAR + ")"

# fmt: off
atom_cartesian = re.compile(r'\A' + r'(?P<nucleus>' + NUCLEUS + r')' + SEP + CARTXYZ + r'\Z',
                            re.IGNORECASE | re.VERBOSE)
atom_vcart = re.compile(r'\A' + r'(?P<nucleus>' + NUCLEUS + r')' + SEP +
                        r'(?P<Xval>' + ANCHORVAL + r')' + SEP +
                        r'(?P<Yval>' + ANCHORVAL + r')' + SEP +
                        r'(?P<Zval>' + ANCHORVAL + r')' + r'\Z',
                        re.IGNORECASE | re.VERBOSE)
atom_zmat1 = re.compile(r'\A' + r'(?P<nucleus>' + NUCLEUS + r')' + r'\Z',
                        re.IGNORECASE | re.VERBOSE)
atom_zmat2 = re.compile(r'\A' + r'(?P<nucleus>' + NUCLEUS + r')' + SEP +
                        r'(?P<Ridx>' + ANCHORTO + r')' + SEP + r'(?P<Rval>' + ANCHORVAL + r')' + r'\Z',
                        re.IGNORECASE | re.VERBOSE)
atom_zmat3 = re.compile(r'\A' + r'(?P<nucleus>' + NUCLEUS + r')' + SEP +
                        r'(?P<Ridx>' + ANCHORTO + r')' + SEP + r'(?P<Rval>' + ANCHORVAL + r')' + SEP +
                        r'(?P<Aidx>' + ANCHORTO + r')' + SEP + r'(?P<Aval>' + ANCHORVAL + r')' + r'\Z',
                        re.IGNORECASE | re.VERBOSE)
atom_zmat4 = re.compile(r'\A' + r'(?P<nucleus>' + NUCLEUS + r')' + SEP +
                        r'(?P<Ridx>' + ANCHORTO + r')' + SEP + r'(?P<Rval>' + ANCHORVAL + r')' + SEP +
                        r'(?P<Aidx>' + ANCHORTO + r')' + SEP + r'(?P<Aval>' + ANCHORVAL + r')' + SEP +
                        r'(?P<Didx>' + ANCHORTO + r')' + SEP + r'(?P<Dval>' + ANCHORVAL + r')' + r'\Z',
                        re.IGNORECASE | re.VERBOSE)
variable = re.compile(
    r'\A' + r'(?P<varname>' + VAR + r')' + r'\s*=\s*' + r'(?P<varvalue>((tda)|(' + NUMBER + r')))' + r'\Z',
    re.IGNORECASE | re.VERBOSE,
)
# fmt: on


def _filter_mints(string, unsettled=False):
    r"""Handle extracting fragment, atom, and chg/mult lines from `string`.

    Returns
    -------
    str, dict
        Returns first a subset (plus some fragment separation guidance) of
            `string` containing the unmatched contents. These are generally input
            violations unless handled by a subsequent processing function.
        Returns second a dictionary with processed extractions. Contains (some
            optional) the following keys.

            molecular_charge : float, optional
            molecular_multiplicity : int, optional
            geom
            elbl
            fragment_separators
            fragment_charges
            fragment_multiplicities

    unsettled : bool, optional
        Whether to allow variable entries and zmat structure, accumulating into
        geom_unsettled, rather than pure numerical Cartesian entries,
        accumulating into geom.

    """

    def process_system_cgmp(matchobj):
        """Handles optional special first fragment with sole contents overall chg/mult."""

        processed["molecular_charge"] = float(matchobj.group("chg"))
        processed["molecular_multiplicity"] = int(matchobj.group("mult"))
        return ""

    def filter_fragment(fstring):
        """Handles extraction from everything within a fragment marker "--" of a
        single chg/mult (or None/None) and multiple atom lines.

        """

        def process_fragment_cgmp(matchobj):
            processed["fragment_charges"].append(float(matchobj.group("chg")))
            processed["fragment_multiplicities"].append(int(matchobj.group("mult")))
            return ""

        def process_atom_cartesian(matchobj):
            processed["elbl"].append(matchobj.group("nucleus"))
            processed["geom"].append(float(matchobj.group("x")))
            processed["geom"].append(float(matchobj.group("y")))
            processed["geom"].append(float(matchobj.group("z")))
            return ""

        def process_atom_unsettled(matchobj):
            processed["elbl"].append(matchobj.group("nucleus"))
            geo = []
            if "Xval" in matchobj.groupdict():
                geo.append(matchobj.group("Xval"))
                geo.append(matchobj.group("Yval"))
                geo.append(matchobj.group("Zval"))
            if "Rval" in matchobj.groupdict():
                geo.append(matchobj.group("Ridx"))
                geo.append(matchobj.group("Rval"))
            if "Aval" in matchobj.groupdict():
                geo.append(matchobj.group("Aidx"))
                geo.append(matchobj.group("Aval"))
            if "Dval" in matchobj.groupdict():
                geo.append(matchobj.group("Didx"))
                geo.append(matchobj.group("Dval"))
            processed["geom_unsettled"].append(geo)
            return ""

        def process_variable(matchobj):
            processed["variables"].append((matchobj.group("varname"), matchobj.group("varvalue")))
            return ""

        freconstitute = []
        start_atom = len(processed["elbl"])
        if start_atom > 0:
            processed["fragment_separators"].append(start_atom)

        fcgmp_found = False
        for iln, line in enumerate(fstring.split("\n")):
            line = line.strip()
            if not fcgmp_found:
                line, fcgmp_found = re.subn(cgmp, process_fragment_cgmp, line)
            if unsettled:
                line = re.sub(atom_vcart, process_atom_unsettled, line)
                line = re.sub(atom_zmat1, process_atom_unsettled, line)
                line = re.sub(atom_zmat2, process_atom_unsettled, line)
                line = re.sub(atom_zmat3, process_atom_unsettled, line)
                line = re.sub(atom_zmat4, process_atom_unsettled, line)
                line = re.sub(variable, process_variable, line)
            else:
                line = re.sub(atom_cartesian, process_atom_cartesian, line)
            if line:
                freconstitute.append(line)

        if not fcgmp_found:
            processed["fragment_charges"].append(None)
            processed["fragment_multiplicities"].append(None)

        return "\n".join(freconstitute), processed

    reconstitute = []
    processed = {}
    processed["elbl"] = []
    processed["fragment_separators"] = []
    processed["fragment_charges"] = []
    processed["fragment_multiplicities"] = []
    if unsettled:
        processed["geom_unsettled"] = []
        processed["variables"] = []
    else:
        processed["geom"] = []

    # handle `--`-demarcated blocks
    for ifr, frag in enumerate(re.split(fragment_marker, string)):
        frag = frag.strip()
        if ifr == 0 and cgmp.match(frag):
            frag, ntotch = re.subn(cgmp, process_system_cgmp, frag)
        else:
            frag, processed = filter_fragment(frag)
        if frag:
            reconstitute.append(frag)

    return "\n--\n".join(reconstitute), processed


xyz1strict = re.compile(r"\A" + r"(?P<nat>\d+)" + r"\Z")
SIMPLENUCLEUS = r"""((?P<E>[A-Z]{1,3})|(?P<Z>\d{1,3}))"""
atom_cartesian_strict = re.compile(
    r"\A" + r"(?P<nucleus>" + SIMPLENUCLEUS + r")" + SEP + CARTXYZ + r"\Z", re.IGNORECASE | re.VERBOSE
)

xyz1 = re.compile(r"\A" + r"(?P<nat>\d+)" + r"[\s,]*" + r"((?P<ubohr>(bohr|au))|(?P<uang>ang))?" + r"\Z", re.IGNORECASE)
xyz2 = re.compile(r"\A" + CHGMULT, re.VERBOSE)
atom_cartesian = re.compile(
    r"\A" + r"(?P<nucleus>" + NUCLEUS + r")" + SEP + CARTXYZ + r"\Z", re.IGNORECASE | re.VERBOSE
)


def _filter_xyz(string, strict):
    r"""Handle extracting atom, units, and chg/mult lines from `string`.

    Parameters
    ----------
    strict : bool
        Whether to enforce a strict XYZ file format or to allow units, chg/mult,
        and add'l atom info.

    Returns
    -------
    str, dict
        Returns first a subset of `string` containing the unmatched contents.
        These are generally input violations unless handled by a subsequent
        processing function.
        Returns second a dictionary with processed extractions. Contains (some
            optional) the following keys.

            molecular_charge : float, optional (`strict=False` only)
            molecular_multiplicity : int, optional (`strict=False` only)
            geom
            elbl
            units : {'Angstrom', 'Bohr'} (`Bohr` `strict=False` only)

    """

    def process_bohrang(matchobj):
        nat = matchobj.group("nat")  # lgtm[py/unused-local-variable]
        if matchobj.group("uang"):
            processed["units"] = "Angstrom"
        elif matchobj.group("ubohr"):
            processed["units"] = "Bohr"
        return ""

    def process_system_cgmp(matchobj):
        processed["molecular_charge"] = float(matchobj.group("chg"))
        processed["molecular_multiplicity"] = int(matchobj.group("mult"))
        return ""

    def process_atom_cartesian(matchobj):
        processed["elbl"].append(matchobj.group("nucleus"))
        processed["geom"].append(float(matchobj.group("x")))
        processed["geom"].append(float(matchobj.group("y")))
        processed["geom"].append(float(matchobj.group("z")))
        return ""

    # nat = 0
    reconstitute = []
    processed = {}
    processed["geom"] = []
    processed["elbl"] = []

    if strict:
        for iln, line in enumerate(string.split("\n")):
            line = line.strip()
            if iln == 0:
                line = re.sub(xyz1strict, "", line)
            elif iln == 1:
                continue
            else:
                line = re.sub(atom_cartesian_strict, process_atom_cartesian, line)
            if line:
                reconstitute.append(line)
    else:
        for iln, line in enumerate(string.split("\n")):
            line = line.strip()
            if iln == 0:
                line = re.sub(xyz1, process_bohrang, line)
            elif iln == 1:
                line = re.sub(xyz2, process_system_cgmp, line)
            else:
                line = re.sub(atom_cartesian, process_atom_cartesian, line)
            if line and iln != 1:
                reconstitute.append(line)

    if "units" not in processed:
        processed["units"] = "Angstrom"

    # if len(processed['geom']) != nat:
    #    raise ValidationError
    processed["geom_hints"] = []  # no EFP

    return "\n".join(reconstitute), processed
