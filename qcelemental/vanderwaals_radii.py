"""
Contains van der Waals radii
"""

import collections
from decimal import Decimal
from typing import Dict, Union

from .datum import Datum, print_variables
from .exceptions import DataUnavailableError
from .periodic_table import periodictable


class VanderWaalsRadii:
    """Van der Waals radii sets.

    Parameters
    ----------
    context : {'MANTINA2009'}
        Origin of loaded data.

    Attributes
    ----------
    vdwr : dict of Datum
        Each van der Waals radius is an entry in `vdwr`, where key is the
        "Fe"-cased element symbol if generic or symbol-prefixed label
        if specialized within element. The value is a Datum object with
        `lbl` the same as key, `units` and `data` value as Decimal object.
    doi : str
        The DOI of the current context.
    name : str
        The name of the context ('MANTINA2009')
    native_units : str
        The units the original data was provided in.
    year : int
        The year the context was created.

    """

    def __init__(self, context: str = "MANTINA2009"):
        self.vdwr: Dict[str, Datum] = collections.OrderedDict()

        from .data import mantina_2009_vanderwaals_radii

        if context == "MANTINA2009":
            self.doi = mantina_2009_vanderwaals_radii["doi"]
            self.native_units = mantina_2009_vanderwaals_radii["units"]

            # TypedDict wont be in until 3.8, have to ignore heterogeneous dicts for now
            for vdwr in mantina_2009_vanderwaals_radii["vanderwaals_radii"]:  # type: ignore
                self.vdwr[vdwr[0]] = Datum(vdwr[0], self.native_units, Decimal(vdwr[1]), doi=self.doi)
        else:
            raise KeyError("Context set as '{}', only contexts {'MANTINA2009', } are currently supported")

        self.name = context
        self.year = int(mantina_2009_vanderwaals_radii["date"][:4])  # type: ignore

    def __str__(self) -> str:
        return "VanderWaalsRadii(context='{}')".format(self.name)

    def get(
        self, atom: Union[int, str], *, return_tuple: bool = False, units: str = "bohr", missing: float = None
    ) -> Union[float, "Datum"]:  # lgtm [py/similar-function]
        """
        Access a van der Waals radius for species ``atom``.

        Parameters
        ----------
        atom : int or str
            Identifier for element or nuclide, e.g., ``H``, ``C``, ``Al``.
        units : str, optional
            Units of returned value. To return in native unit (MANTINA2009: angstrom), pass it explicitly.
            Only relevant for ``return_tuple=False`` since ``True`` returns underlying data structure with native units.
        missing : float or None, optional
            How to handle when ``atom`` is valid but outside the available data range. When ``None``, raises DataUnavailableError.
            When a float, returns that float, so supply in ``units`` units. Supplying a float is a more compact assurance
            that a call will work over all the periodic table than the equivalent

            .. code-block:: python

                try:
                    rad = qcel.vdwradii.get(atom)
                except qcel.DataUnavailableError:
                    rad = 4.0

            Only relevant for ``return_tuple=False``.
        return_tuple : bool, optional
            See below.

        Returns
        -------
        float
            When ``return_tuple=False``, value of Van der Waals radius. If multiple defined for element, returns largest.
        qcelemental.Datum
            When ``return_tuple=True``, Datum with units, description, uncertainty, and value of van der Waals radius as Decimal (preserving significant figures).
            If multiple defined for element, returns largest.

        Raises
        ------
        NotAnElementError
            If `atom` cannot be resolved into an element or nuclide or label.
        DataUnavailableError
            If `atom` is a valid element or nuclide but not one for which a van der Waals radius is available and `missing=None`.

        """
        if atom in self.vdwr.keys():
            # catch extra labels like 'C_sp3'
            identifier = atom
        else:
            identifier = periodictable.to_E(atom)

        try:
            assert isinstance(identifier, str)  # Should be string by now
            qca = self.vdwr[identifier]
        except KeyError as e:
            if missing is not None and return_tuple is False:
                return missing
            else:
                raise DataUnavailableError("vanderwaals radius", identifier) from e

        if return_tuple:
            return qca
        else:
            return qca.to_units(units)

    def string_representation(self) -> str:
        """Print name, value, and units of all van der Waals radii."""

        return print_variables(self.vdwr)

    def write_c_header(self, filename: str = "vdwrad.h", missing: float = 2.0) -> None:  # lgtm [py/similar-function]
        """Write C header file defining Van der Waals radii array.

        Parameters
        ----------
        filename : str, optional
            File name for header. Note that changing this won't change the header guard.
        missing : float, optional
            In order that the C array be atomic-number indexable and that it span the
            periodic table, this value is used anywhere data is missing.

        """
        text = [
            "#ifndef _qcelemental_vdwrad_h_",
            "#define _qcelemental_vdwrad_h_",
            "",
            "/* This file is autogenerated from the QCElemental python module */",
            "",
            "const double vanderwaals_radii[] = {",
        ]

        for el in periodictable.E:
            try:
                qca = self.vdwr[el]
                text.append("{},  /*- [{}] {} {} -*/".format(qca.data, qca.units, qca.label, qca.comment))
            except KeyError:
                text.append(
                    "{:.2f},  /*- [{}] {} {} -*/".format(
                        missing, self.native_units, el, "Default value for missing data"
                    )
                )

        text.append("};")
        text.append("#endif /* header guard */")
        text.append("")

        with open(filename, "w") as handle:
            handle.write("\n".join(text))
        print("File written ({}). Remember to add license and clang-format it.".format(filename))


# singleton
vdwradii = VanderWaalsRadii("MANTINA2009")
