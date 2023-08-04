"""
Datum Object Model
"""

from decimal import Decimal
from typing import Any, Dict, Optional, Union
from typing_extensions import Annotated

import numpy as np

from pydantic import BaseModel, field_validator, ConfigDict, WrapSerializer, SerializerFunctionWrapHandler


def cast_ndarray(v: Any, nxt: SerializerFunctionWrapHandler) -> str:
    """Special helper to list NumPy arrays before serializing"""
    if isinstance(v, np.ndarray):
        return f'{nxt(v.flatten().tolist())}'
    return f'{nxt(v)}'


def cast_complex(v: Any, nxt: SerializerFunctionWrapHandler) -> str:
    """Special helper to serialize NumPy arrays before serializing"""
    if isinstance(v, complex):
        return f'{nxt((v.real, v.imag))}'
    return nxt(v)


def preserve_decimal(v: Any, nxt: SerializerFunctionWrapHandler) -> Union[str, Decimal]:
    """
    Ensure Decimal types are preserved on the way out

    This arose because Decimal was serialized to string and "dump" is equal to "serialize" in v2 pydantic
    https://docs.pydantic.dev/latest/migration/#changes-to-json-schema-generation
    """
    if isinstance(v, Decimal):
        return v
    return nxt(v)


# Serializers are pop'd out of the list in FILO (right to left)
AnyArrayComplex = Annotated[
    Any,
    WrapSerializer(cast_ndarray, when_used="json"),
    WrapSerializer(cast_complex, when_used="json"),
    WrapSerializer(preserve_decimal)
]


class Datum(BaseModel):
    r"""Facilitates the storage of quantum chemical results by labeling them with basic metadata.

    Attributes
    ----------
    label : str
        Official label for `data`, often qcvar. May contain spaces.
    units : str
        ASCII, LaTeX-like representation of units, without square brackets.
    data : float or decimal.Decimal or numpy.ndarray
        Value for `label`.
    comment : str
        Additional notes.
    doi : str
        Literature citation or definition DOI link.
    glossary : str
        Extended description or definition.
    numeric : bool
        Whether `data` is numeric. Pass `True` to disable validating `data` as float/Decimal/np.ndarray.

    """

    numeric: bool
    label: str
    units: str
    data: AnyArrayComplex
    comment: str = ""
    doi: Optional[str] = None
    glossary: str = ""

    model_config = ConfigDict(extra="forbid",
                              frozen=True,
                              )

    def __init__(self, label, units, data, *, comment=None, doi=None, glossary=None, numeric=True):
        kwargs = {"label": label, "units": units, "data": data, "numeric": numeric}
        if comment is not None:
            kwargs["comment"] = comment
        if doi is not None:
            kwargs["doi"] = doi
        if glossary is not None:
            kwargs["glossary"] = glossary

        super().__init__(**kwargs)

    @field_validator("data")
    @classmethod
    def must_be_numerical(cls, v, info):
        try:
            1.0 * v
        except TypeError:
            try:
                Decimal("1.0") * v
            except TypeError:
                if info.data["numeric"]:
                    raise ValueError(f"Datum data should be float, Decimal, or np.ndarray, not {type(v)}.")
            else:
                info.data["numeric"] = True
        else:
            info.data["numeric"] = True

        return v

    def __str__(self, label=""):
        width = 40
        text = ["-" * width, "{:^{width}}".format("Datum " + self.label, width=width)]
        if label:
            text.append("{:^{width}}".format(label, width=width))
        text.append("-" * width)
        text.append("Data:     {}".format(self.data))
        text.append("Units:    [{}]".format(self.units))
        text.append("doi:      {}".format(self.doi))
        text.append("Comment:  {}".format(self.comment))
        text.append("Glossary: {}".format(self.glossary))
        text.append("-" * width)
        return "\n".join(text)

    def dict(self, *args, **kwargs):
        return super().model_dump(*args, **{**kwargs, **{"exclude_unset": True}})

    def to_units(self, units=None):
        from .physical_constants import constants

        to_unit = self.units if units is None else units
        factor = constants.conversion_factor(self.units, to_unit)

        if isinstance(self.data, Decimal):
            return factor * float(self.data)
        else:
            return factor * self.data


def print_variables(qcvars: Dict[str, "Datum"]) -> str:
    r"""Form a printable representation of qcvariables.

    Parameters
    ----------
    qcvars
        Group of Datum objects to print.

    Returns
    -------
    str
        Printable string representation of label, data, and unit in Datum-s.

    """
    text = ["\n  Variable Map:", "  ----------------------------------------------------------------------------"]

    if len(qcvars) == 0:
        text.append("  (none)")
        return "\n".join(text)

    largest_key = max(len(k) for k in qcvars) + 2  # for quotation marks
    largest_characteristic = 8
    for k, v in qcvars.items():
        try:
            exp = int(str(v.data).split("E")[1])
        except IndexError:
            pass
        else:
            largest_characteristic = max(exp, largest_characteristic)

    for k, qca in sorted(qcvars.items()):
        # if k != qca.lbl:
        #    raise ValidationError('Huh? {} != {}'.format(k, qca.label))

        if isinstance(qca.data, np.ndarray):
            data = np.array_str(qca.data, max_line_width=120, precision=8, suppress_small=True)
            data = "\n".join("        " + ln for ln in data.splitlines())
            text.append(
                """  {:{keywidth}} => {:{width}} [{}]""".format(
                    '"' + k + '"', "", qca.units, keywidth=largest_key, width=largest_characteristic + 14
                )
            )
            text.append(data)
        elif isinstance(qca.data, Decimal):
            text.append(
                """  {:{keywidth}} => {:{width}} [{}]""".format(
                    '"' + k + '"', qca.data, qca.units, keywidth=largest_key, width=largest_characteristic + 14
                )
            )
        elif not qca.numeric:
            text.append(
                """  {:{keywidth}} => {:>{width}} [{}]""".format(
                    '"' + k + '"', str(qca.data), qca.units, keywidth=largest_key, width=largest_characteristic + 14
                )
            )
        else:
            text.append(
                """  {:{keywidth}} => {:{width}.{prec}f} [{}]""".format(
                    '"' + k + '"', qca.data, qca.units, keywidth=largest_key, width=largest_characteristic + 14, prec=12
                )
            )

    text.append("")
    return "\n".join(text)
