import copy
import pprint
import re

import numpy as np

from ..exceptions import ValidationError
from ..physical_constants import constants
from ..util import distance_matrix, provenance_stamp, unnp, update_with_error
from .chgmult import validate_and_fill_chgmult
from .nucleus import reconcile_nucleus
from .regex import VERSION_PATTERN


def from_input_arrays(
        *,
        enable_qm=True,
        enable_efp=True,
        missing_enabled_return_qm='error',
        missing_enabled_return_efp='error',
        # qm
        geom=None,
        elea=None,
        elez=None,
        elem=None,
        mass=None,
        real=None,
        elbl=None,
        name=None,
        units='Angstrom',
        input_units_to_au=None,
        fix_com=None,
        fix_orientation=None,
        fix_symmetry=None,
        fragment_separators=None,
        fragment_charges=None,
        fragment_multiplicities=None,
        molecular_charge=None,
        molecular_multiplicity=None,
        # efp
        fragment_files=None,
        hint_types=None,
        geom_hints=None,
        # qm-vz
        geom_unsettled=None,
        variables=None,
        # processing details
        speclabel=True,
        tooclose=0.1,
        zero_ghost_fragments=False,
        nonphysical=False,
        mtol=1.e-3,
        verbose=1):
    """Compose a Molecule dict from unvalidated arrays and variables
    in multiple domains.

    Drives :py:func:`qcelemental.molparse.from_arrays` for sucessive
    domains and hooks them together (e.g., impose `fix_com` on "qm"
    when "efp" present.

    """
    molinit = {}
    if enable_qm:
        molinit['qm'] = {}
    if enable_efp:
        molinit['efp'] = {}

    if enable_efp:
        processed = from_arrays(
            domain='efp',
            missing_enabled_return=missing_enabled_return_efp,
            units=units,
            input_units_to_au=input_units_to_au,
            fix_com=fix_com,
            fix_orientation=fix_orientation,
            fix_symmetry=fix_symmetry,
            fragment_files=fragment_files,
            hint_types=hint_types,
            geom_hints=geom_hints,
            # which other processing details needed?
            verbose=verbose)
        update_with_error(molinit, {'efp': processed})
        if molinit['efp'] == {}:
            del molinit['efp']

    efp_present = enable_efp and 'efp' in molinit and bool(len(molinit['efp']['geom_hints']))
    if efp_present:
        fix_com = True
        fix_orientation = True
        fix_symmetry = 'c1'

    if enable_qm:
        dm = 'qmvz' if geom_unsettled else 'qm'
        processed = from_arrays(
            domain=dm,
            missing_enabled_return=missing_enabled_return_qm,
            geom=geom,
            elea=elea,
            elez=elez,
            elem=elem,
            mass=mass,
            real=real,
            elbl=elbl,
            name=name,
            units=units,
            input_units_to_au=input_units_to_au,
            fix_com=fix_com,
            fix_orientation=fix_orientation,
            fix_symmetry=fix_symmetry,
            fragment_separators=fragment_separators,
            fragment_charges=fragment_charges,
            fragment_multiplicities=fragment_multiplicities,
            molecular_charge=molecular_charge,
            molecular_multiplicity=molecular_multiplicity,
            geom_unsettled=geom_unsettled,
            variables=variables,
            # processing details
            speclabel=speclabel,
            tooclose=tooclose,
            zero_ghost_fragments=zero_ghost_fragments,
            nonphysical=nonphysical,
            mtol=mtol,
            verbose=1)
        update_with_error(molinit, {'qm': processed})
        if molinit['qm'] == {}:
            del molinit['qm']

    return molinit


def from_arrays(*,
                geom=None,
                elea=None,
                elez=None,
                elem=None,
                mass=None,
                real=None,
                elbl=None,
                name=None,
                units='Angstrom',
                input_units_to_au=None,
                fix_com=None,
                fix_orientation=None,
                fix_symmetry=None,
                fragment_separators=None,
                fragment_charges=None,
                fragment_multiplicities=None,
                molecular_charge=None,
                molecular_multiplicity=None,
                comment=None,
                provenance=None,
                connectivity=None,
                fragment_files=None,
                hint_types=None,
                geom_hints=None,
                geom_unsettled=None,
                variables=None,
                domain='qm',
                missing_enabled_return='error',
                np_out=True,
                speclabel=True,
                tooclose=0.1,
                zero_ghost_fragments=False,
                nonphysical=False,
                mtol=1.e-3,
                verbose=1):
    """Compose a Molecule dict from unvalidated arrays and variables, returning dict.

    See fields of Return molrec below. Required parameters (for QM XYZ)
    are `geom` and one of `elem`, `elez`, `elbl` (`speclabel=True`)

    Parameters
    ----------
    geom : array-like
        (nat, 3) or (3 * nat, ) ndarray or list o'lists of Cartesian coordinates.
    fragment_separators : array-like of int, optional
        (nfr - 1, ) list of atom indices at which to split `geom` into fragments.
    elbl : ndarray of str
        (nat, ) Label extending `elem` symbol, possibly conveying ghosting, isotope, mass, tagging information.
    tooclose : float, optional
        Interatom distance (native `geom` units) nearer than which atoms not allowed.
    nonphysical : bool, optional
    speclabel : bool, optional
        If `True`, interpret `elbl` as potentially full nucleus spec including
        ghosting, isotope, mass, tagging information, e.g., `@13C_mine` or
        `He4@4.01`. If `False`, interpret `elbl` as only the user/tagging
        extension to nucleus label, e.g. `_mine` or `4` in the previous examples.
    missing_enabled_return : {'minimal', 'none', 'error'}
        What to do when an enabled domain is of zero-length? Respectively, return
        a fully valid but empty molrec, return empty dictionary, or throw error.
    np_out : bool, optional
        When `True`, fields geom, elea, elez, elem, mass, real, elbl will be ndarray.
        Use `False` to get a json-able version.

    Returns
    -------
    molrec : dict
        Molecule dictionary spec follows. Its principles are

        (1) contents are fully validated and defaulted - no error
        checking necessary,

        (2) contents may be mildly redundant - atomic numbers and
        element symbols present,

        (3) big system, nat-length single-type arrays, not small system,
        nat-number heterogeneous objects,

        (4) some fields are optional (e.g., fix_symmetry) but largely
        self-describing so units or fix_com must be present.

        (5) apart from some mild optional fields, _all_ fields will
        be present (corollary of "fully validated and defaulted") - no
        need to check for every key. in some cases like efp, keys will
        appear in blocks, so pre-handshake there will be a few hint keys
        and post-handshake they will be joined by full qm-like molrec.

        (6) molrec should be idempotent through this function (equiv to
        schema validator) but are not idempotent throughout its life. if
        fields permit, frame may be changed. Future? if fields permit,
        mol may be symmetrized. Coordinates and angles may change units
        or range if program returns them in only one form.

    name : str, optional
        Label for molecule; should be valid Python identifier.
    units : {'Angstrom', 'Bohr'}
        Units for `geom`.
    input_units_to_au : float, optional
        If `units='Angstrom'`, overrides consumer's value for [A]-->[a0] conversion.
    fix_com : bool
        Whether translation of `geom` is allowed or disallowed.
    fix_orientation : bool
        Whether rotation of `geom` is allowed or disallowed.
    fix_symmetry : str, optional
        Maximal point group symmetry which `geom` should be treated. Lowercase.
    geom : ndarray of float
        (3 * nat, ) Cartesian coordinates in `units`.
    elea : ndarray of int
        (nat, ) Mass number for atoms, if known isotope, else -1.
    elez : ndarray of int
        (nat, ) Number of protons, nuclear charge for atoms.
    elem : ndarray of str
        (nat, ) Element symbol for atoms.
    mass : ndarray of float
        (nat, ) Atomic mass [u] for atoms.
    real : ndarray of bool
        (nat, ) Real/ghostedness for atoms.
    elbl : ndarray of str
        (nat, ) Label with any tagging information from element spec.
    fragment_separators : list of int
        (nfr - 1, ) list of atom indices at which to split `geom` into fragments.
    fragment_charges : list of float
        (nfr, ) list of charge allocated to each fragment.
    fragment_multiplicities : list of int
        (nfr, ) list of multiplicity allocated to each fragment.
    molecular_charge : float
        total charge on system.
    molecular_multiplicity : int
        total multiplicity on system.
    comment : str, optional
        Additional comment for molecule.
    provenance : dict of str
        Accumulated history of molecule, with fields "creator", "version", "routine".
    connectivity : list of tuples of int, optional
        (nbond, 3) list of (0-indexed) (atomA, atomB, bond_order) (int, int, double) tuples

    EFP extension (this + units is minimal)

    fragment_files : list of str
        (nfr, ) lowercased names of efp meat fragment files.
    hint_types : {'xyzabc', 'points'}
        (nfr, ) type of fragment orientation hint.
    geom_hints : list of lists of float
        (nfr, ) inner lists have length 6 (xyzabc; to orient the center) or
        9 (points; to orient the first three atoms) of the EFP fragment.

    QMVZ extension (geom_unsettled replaces geom)

    geom_unsettled : list of lists of str
        (nat, ) all-string Cartesian and/or zmat anchor and value contents
        mixing anchors, values, and variables.
    variables : list of pairs
        (nvar, 2) pairs of variables (str) and values (float). May be incomplete.

    Raises
    ------
    qcelemental.ValidationError
        For most anything wrong.

    """
    # <<  domain sorting  >>
    available_domains = ['qm', 'efp', 'qmvz']
    if domain not in available_domains:
        raise ValidationError('Topology domain {} not available for processing. Choose among {}'.format(
            domain, available_domains))

    if domain == 'qm' and (geom is None or np.array(geom).size == 0):
        if missing_enabled_return == 'none':
            return {}
        elif missing_enabled_return == 'minimal':
            geom = []
        else:
            raise ValidationError("""For domain 'qm', `geom` must be provided.""")
    if domain == 'efp' and (geom_hints is None or np.array(geom_hints).size == 0):
        if missing_enabled_return == 'none':
            return {}
        elif missing_enabled_return == 'minimal':
            geom_hints = []
            fragment_files = []
            hint_types = []
        else:
            raise ValidationError("""For domain 'efp', `geom_hints` must be provided.""")

    molinit = {}
    extern = False

    processed = validate_and_fill_units(
        name=name,
        units=units,
        input_units_to_au=input_units_to_au,
        comment=comment,
        provenance=provenance,
        connectivity=connectivity,
        always_return_iutau=False)  # yapf: disable
    processed['provenance'] = provenance_stamp(__name__)
    update_with_error(molinit, processed)

    if domain == 'efp':
        processed = validate_and_fill_efp(
            fragment_files=fragment_files,
            hint_types=hint_types,
            geom_hints=geom_hints)  # yapf: disable
        update_with_error(molinit, processed)
        extern = bool(len(molinit['geom_hints']))

    if domain == 'qm' or (domain == 'efp' and geom is not None) or domain == 'qmvz':
        if domain == 'qmvz':
            processed = validate_and_fill_unsettled_geometry(
                geom_unsettled=geom_unsettled,
                variables=variables)  # yapf: disable
            update_with_error(molinit, processed)
            nat = len(molinit['geom_unsettled'])

        else:
            processed = validate_and_fill_geometry(
                geom=geom,
                tooclose=tooclose)  # yapf: disable
            update_with_error(molinit, processed)
            nat = molinit['geom'].shape[0] // 3

        processed = validate_and_fill_nuclei(
            nat,
            elea=elea,
            elez=elez,
            elem=elem,
            mass=mass,
            real=real,
            elbl=elbl,
            speclabel=speclabel,
            nonphysical=nonphysical,
            mtol=mtol,
            verbose=verbose)
        update_with_error(molinit, processed)

        processed = validate_and_fill_fragments(
            nat,
            fragment_separators=fragment_separators,
            fragment_charges=fragment_charges,
            fragment_multiplicities=fragment_multiplicities)
        update_with_error(molinit, processed)

        Z_available = molinit['elez'] * molinit['real'] * 1.
        processed = validate_and_fill_chgmult(
            zeff=Z_available,
            fragment_separators=molinit['fragment_separators'],
            molecular_charge=molecular_charge,
            fragment_charges=molinit['fragment_charges'],
            molecular_multiplicity=molecular_multiplicity,
            fragment_multiplicities=molinit['fragment_multiplicities'],
            zero_ghost_fragments=zero_ghost_fragments,
            verbose=verbose)
        del molinit['fragment_charges']  # sometimes safe update is too picky about overwriting v_a_f_fragments values
        del molinit['fragment_multiplicities']
        update_with_error(molinit, processed)

    extern = (domain == 'efp')

    processed = validate_and_fill_frame(
        extern=extern,
        fix_com=fix_com,
        fix_orientation=fix_orientation,
        fix_symmetry=fix_symmetry)  # yapf: disable
    update_with_error(molinit, processed)

    if verbose >= 2:
        print('RETURN FROM qcel.molparse.from_arrays(domain={})'.format(domain.upper()))
        pprint.pprint(molinit)

    if not np_out:
        molinit = unnp(molinit)

    return molinit


def validate_and_fill_units(name=None,
                            units='Angstrom',
                            input_units_to_au=None,
                            comment=None,
                            provenance=None,
                            connectivity=None,
                            always_return_iutau=False):
    molinit = {}

    if name is not None:
        molinit['name'] = name

    if comment is not None:
        molinit['comment'] = comment

    def validate_provenance(dicary):
        expected_prov_keys = ['creator', 'routine', 'version']
        try:
            prov_keys = sorted(dicary.keys())
        except AttributeError:
            raise ValidationError("Provenance entry is not dictionary: {}".format(dicary))

        if prov_keys == expected_prov_keys:
            if not isinstance(dicary['creator'], str):
                raise ValidationError(
                    """Provenance key 'creator' should be string of creating program's name: {}""".format(
                        dicary['creator']))
            if not re.fullmatch(VERSION_PATTERN, dicary['version'], re.VERBOSE):
                raise ValidationError("""Provenance key 'version' should be a valid PEP 440 string: {}""".format(
                    dicary['version']))
            if not isinstance(dicary['routine'], str):
                raise ValidationError(
                    """Provenance key 'routine' should be string of creating function's name: {}""".format(
                        dicary['routine']))
            return True
        else:
            raise ValidationError('Provenance keys ({}) incorrect: {}'.format(expected_prov_keys, prov_keys))

    if provenance is None:
        molinit['provenance'] = {}
    else:
        if validate_provenance(provenance):
            molinit['provenance'] = copy.deepcopy(provenance)

    if connectivity is not None:
        conn = []
        try:
            for (at1, at2, bondorder) in connectivity:
                if not (float(at1)).is_integer() or at1 < 0:  # or at1 >= nat:
                    raise ValidationError("""Connectivity first atom should be int [0, nat): {}""".format(at1))
                if not (float(at2)).is_integer() or at2 < 0:  # or at2 >= nat:
                    raise ValidationError("""Connectivity second atom should be int [0, nat): {}""".format(at2))
                if bondorder < 0 or bondorder > 5:
                    raise ValidationError("""Connectivity bond order should be float [0, 5]: {}""".format(bondorder))
                conn.append((int(min(at1, at2)), int(max(at1, at2)), float(bondorder)))
            conn.sort(key=lambda tup: tup[0])
            molinit['connectivity'] = conn
        except ValueError:
            raise ValidationError(
                "Connectivity entry is not of form [(at1, at2, bondorder), ...]: {}".format(connectivity))

    if units.capitalize() in ['Angstrom', 'Bohr']:
        molinit['units'] = units.capitalize()
    else:
        raise ValidationError('Invalid molecule geometry units: {}'.format(units))

    if molinit['units'] == 'Bohr':
        iutau = 1.
    elif molinit['units'] == 'Angstrom':
        iutau = 1. / constants.bohr2angstroms

    if input_units_to_au is not None:
        if abs(input_units_to_au - iutau) < 0.05:
            iutau = input_units_to_au
        else:
            raise ValidationError("""No big perturbations to physical constants! {} !~= {}""".format(
                iutau, input_units_to_au))

    if always_return_iutau or input_units_to_au is not None:
        molinit['input_units_to_au'] = iutau

    return molinit


def validate_and_fill_frame(extern, fix_com=None, fix_orientation=None, fix_symmetry=None):

    if fix_com is True:
        com = True
    elif fix_com is False:
        if extern:
            raise ValidationError('Invalid fix_com ({}) with extern ({})'.format(fix_com, extern))
        else:
            com = False
    elif fix_com is None:
        com = extern
    else:
        raise ValidationError('Invalid fix_com: {}'.format(fix_com))

    if fix_orientation is True:
        orient = True
    elif fix_orientation is False:
        if extern:
            raise ValidationError('Invalid fix_orientation ({}) with extern ({})'.format(fix_orientation, extern))
        else:
            orient = False
    elif fix_orientation is None:
        orient = extern
    else:
        raise ValidationError('Invalid fix_orientation: {}'.format(fix_orientation))

    symm = None
    if extern:
        if fix_symmetry is None:
            symm = 'c1'
        elif fix_symmetry.lower() == 'c1':
            symm = 'c1'
        else:
            raise ValidationError('Invalid (non-C1) fix_symmetry ({}) with extern ({})'.format(fix_symmetry, extern))
    else:
        if fix_symmetry is not None:
            symm = fix_symmetry.lower()

    molinit = {}
    molinit['fix_com'] = com
    molinit['fix_orientation'] = orient
    if symm:
        molinit['fix_symmetry'] = symm

    return molinit


def validate_and_fill_efp(fragment_files=None, hint_types=None, geom_hints=None):

    if (fragment_files is None or hint_types is None or geom_hints is None or fragment_files == [None]
            or hint_types == [None] or geom_hints == [None]
            or not (len(fragment_files) == len(hint_types) == len(geom_hints))):

        raise ValidationError(
            """Missing or inconsistent length among efp quantities: fragment_files ({}), hint_types ({}), and geom_hints ({})"""
            .format(fragment_files, hint_types, geom_hints))

    # NOTE: imposing case on file
    try:
        files = [f.lower() for f in fragment_files]
    except AttributeError:
        raise ValidationError("""fragment_files not strings: {}""".format(fragment_files))

    if all(f in ['xyzabc', 'points', 'rotmat'] for f in hint_types):
        types = hint_types
    else:
        raise ValidationError("""hint_types not among 'xyzabc', 'points', 'rotmat': {}""".format(hint_types))

    hints = []
    hlen = {'xyzabc': 6, 'points': 9, 'rotmat': 12}
    for ifr, fr in enumerate(geom_hints):
        try:
            hint = [float(f) for f in fr]
        except (ValueError, TypeError):
            raise ValidationError("""Un float-able elements in geom_hints[{}]: {}""".format(ifr, fr))

        htype = hint_types[ifr]
        if len(hint) == hlen[htype]:
            hints.append(hint)
        else:
            raise ValidationError("""EFP hint type {} not {} elements: {}""".format(htype, hlen[htype], hint))

    return {'fragment_files': files, 'hint_types': types, 'geom_hints': hints}


def validate_and_fill_geometry(geom=None, tooclose=0.1):
    """Check `geom` for overlapping atoms. Return flattened"""

    npgeom = np.array(geom, dtype=np.float).reshape((-1, 3))
    dm = distance_matrix(npgeom, npgeom)

    iu = np.triu_indices(dm.shape[0])
    dm[iu] = 10.
    tooclosem = np.where(dm < tooclose)

    if tooclosem[0].shape[0]:
        raise ValidationError("""Following atoms are too close: {}""".format(
            [(i, j, dm[i, j]) for i, j in zip(*tooclosem)]))

    return {'geom': npgeom.reshape((-1))}


def validate_and_fill_nuclei(
        nat,
        elea=None,
        elez=None,
        elem=None,
        mass=None,
        real=None,
        elbl=None,
        # processing details
        speclabel=True,
        nonphysical=False,
        mtol=1.e-3,
        verbose=1):
    """Check the nuclear identity arrays for consistency and fill in knowable values."""

    if elea is None:
        elea = np.asarray([None] * nat)
    else:
        # -1 equivalent to None
        elea = np.array([(None if at == -1 else at) for at in elea])

    if elez is None:
        elez = np.asarray([None] * nat)
    else:
        elez = np.array(elez)

    if elem is None:
        elem = np.asarray([None] * nat)
    else:
        elem = np.array(elem)

    if mass is None:
        mass = np.asarray([None] * nat)
    else:
        mass = np.array(mass)

    if real is None:
        real = np.asarray([None] * nat)
    else:
        real = np.array(real)

    if elbl is None:
        elbl = np.asarray([None] * nat)
    else:
        elbl = np.array(elbl)

    if not ((nat, ) == elea.shape == elez.shape == elem.shape == mass.shape == real.shape == elbl.shape):
        raise ValidationError(
            """Dimension mismatch natom ({}) among A ({}), Z ({}), E ({}), mass ({}), real ({}), and elbl({})""".
            format((nat, ), elea.shape, elez.shape, elem.shape, mass.shape, real.shape, elbl.shape))

    if nat:
        A, Z, E, mass, real, label = zip(*[
            reconcile_nucleus(
                A=elea[at],
                Z=elez[at],
                E=elem[at],
                mass=mass[at],
                real=real[at],
                label=elbl[at],
                speclabel=speclabel,
                nonphysical=nonphysical,
                mtol=mtol,
                verbose=verbose) for at in range(nat)
        ])
    else:
        A = Z = E = mass = real = label = []
    return {
        'elea': np.array(A, dtype=np.int),
        'elez': np.array(Z, dtype=np.int),
        'elem': np.array(E),
        'mass': np.array(mass, dtype=np.float),
        'real': np.array(real, dtype=np.bool),
        'elbl': np.array(label)
    }


def validate_and_fill_fragments(nat, fragment_separators=None, fragment_charges=None, fragment_multiplicities=None):
    """Check consistency of fragment specifiers wrt type and length. For
    charge & multiplicity, scientific defaults are not computed or applied;
    rather, missing slots are filled with `None` for later processing.

    """
    if fragment_separators is None:
        if fragment_charges is None and fragment_multiplicities is None:
            frs = []  #np.array([], dtype=np.int)  # if empty, needs to be both ndarray and int
            frc = [None]
            frm = [None]
        else:
            raise ValidationError(
                """Fragment quantities given without separation info: sep ({}), chg ({}), and mult ({})""".format(
                    fragment_separators, fragment_charges, fragment_multiplicities))
    else:
        trial_geom = np.zeros((nat, 3))
        try:
            split_geom = np.split(trial_geom, fragment_separators, axis=0)
        except TypeError:
            raise ValidationError("""fragment_separators ({}) unable to perform trial np.split on geometry.""".format(
                fragment_separators))
        if any(len(f) == 0 for f in split_geom):
            if nat != 0:
                raise ValidationError(
                    """fragment_separators ({}) yields zero-length fragment(s) after trial np.split on geometry.""".
                    format(split_geom))
        if sum(len(f) for f in split_geom) != nat:
            raise ValidationError(
                """fragment_separators ({}) yields overlapping fragment(s) after trial np.split on geometry, possibly unsorted."""
                .format(split_geom))
        frs = fragment_separators
        nfr = len(split_geom)

        if fragment_charges is None:
            frc = [None] * nfr
        else:
            try:
                frc = [(f if f is None else float(f)) for f in fragment_charges]
            except TypeError:
                raise ValidationError("""fragment_charges not among None or float: {}""".format(fragment_charges))

        if fragment_multiplicities is None:
            frm = [None] * nfr
        elif all(f is None or (isinstance(f, (int, np.int64)) and f >= 1) for f in fragment_multiplicities):
            frm = fragment_multiplicities
        else:
            raise ValidationError(
                """fragment_multiplicities not among None or positive integer: {}""".format(fragment_multiplicities))

    if not (len(frc) == len(frm) == len(frs) + 1):
        raise ValidationError(
            """Dimension mismatch among fragment quantities: sep + 1 ({}), chg ({}), and mult({})""".format(
                len(frs) + 1, len(frc), len(frm)))

    return {'fragment_separators': list(frs), 'fragment_charges': frc, 'fragment_multiplicities': frm}


def validate_and_fill_unsettled_geometry(geom_unsettled, variables):
    lgeom = [len(g) for g in geom_unsettled]

    if lgeom[0] not in [0, 3]:
        raise ValidationError("""First line must be Cartesian or single atom.""")

    if any(l == 3 for l in lgeom) and not all((l in [3, 6]) for l in lgeom):
        raise ValidationError(
            """Mixing Cartesian and Zmat formats must occur in just that order once absolute frame established.""")

    allowed_to_follow = {0: [2], 2: [4], 3: [3, 6], 4: [6], 6: [3, 6]}

    for il in range(len(lgeom) - 1):
        if lgeom[il + 1] not in allowed_to_follow[lgeom[il]]:
            raise ValidationError(
                """This is not how a Zmat works - aim for lower triangular. Line len ({}) may be followed by line len ({}), not ({})."""
                .format(lgeom[il], allowed_to_follow[lgeom[il]], lgeom[il + 1]))

    if not all(len(v) == 2 for v in variables):
        raise ValidationError("""Variables should come in pairs: {}""".format(variables))

    vvars = [[str(v[0]), float(v[1])] for v in variables]

    return {'geom_unsettled': geom_unsettled, 'variables': vvars}
