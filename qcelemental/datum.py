"""
Datum Object Model
"""

from decimal import Decimal
from typing import Any, Dict, Optional, Union

import numpy as np
from pydantic import (
    BaseModel,
    ConfigDict,
    SerializationInfo,
    SerializerFunctionWrapHandler,
    WrapSerializer,
    field_validator,
    model_serializer,
)
from typing_extensions import Annotated


def reduce_complex(data):
    # Reduce Complex
    if isinstance(data, complex):
        return [data.real, data.imag]
    # Fallback
    return data

def keep_decimal_cast_ndarray_complex(
    v: Any, nxt: SerializerFunctionWrapHandler, info: SerializationInfo
) -> Union[list, Decimal]:
    """
    Ensure Decimal types are preserved on the way out

    This arose because Decimal was serialized to string and "dump" is equal to "serialize" in v2 pydantic
    https://docs.pydantic.dev/latest/migration/#changes-to-json-schema-generation

    This also checks against NumPy Arrays and complex numbers in the instance of being in JSON mode
    """
    if isinstance(v, Decimal):
        return v
    if info.mode == "json":
        if isinstance(v, complex):
            return nxt(reduce_complex(v))
        if isinstance(v, np.ndarray):
            # Handle NDArray and complex NDArray
            flat_list = v.flatten().tolist()
            reduced_list = list(map(reduce_complex, flat_list))
            return nxt(reduced_list)
    return nxt(v)


# Only 1 serializer is allowed. You can't chain wrap serializers.
AnyArrayComplex = Annotated[Any, WrapSerializer(keep_decimal_cast_ndarray_complex)]


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

    model_config = ConfigDict(
        extra="forbid",
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

    @model_serializer(mode="wrap")
    def _serialize_model(self, handler) -> Dict[str, Any]:
        """
        Customize the serialization output. Does duplicate with some code in model_dump, but handles the case of nested
        models and any model config options.

        Encoding is handled at the `model_dump` level and not here as that should happen only after EVERYTHING has been
        dumped/de-pydantic-ized.
        """

        # Get the default return, let the model_dump handle kwarg
        default_result = handler(self)
        # Exclude unset always
        output_dict = {key: value for key, value in default_result.items() if key in self.model_fields_set}
        return output_dict

    def dict(self, *args, **kwargs):
        """
        Passthrough to model_dump without deprecation warning
        exclude_unset is forced through the model_serializer
        """
        return super().model_dump(*args, **kwargs)

    def json(self, *args, **kwargs):
        """
        Passthrough to model_dump_sjon without deprecation warning
        exclude_unset is forced through the model_serializer
        """
        return super().model_dump_json(*args, **kwargs)

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
