"""
Contains metadata about density functionals
"""

from typing import Dict

from pydantic import Field

from ..models import ProtoModel


class DFTFunctionalInfo(ProtoModel):
    name: str = Field(..., description="The name of the functional.")
    ansatz: int = Field(
        ...,
        description="Maximum functional derivative with respect to the density. This is 2 for meta-GGAs, 1 for GGAs, and 0 otherwise.)",
    )
    deriv: int = Field(..., description="Maximum derivative to compute.")
    c_hybrid: bool = Field(..., description="Requires wavefunction correlation?")
    x_hybrid: bool = Field(..., description="Requires exact exchange?")
    c_lrc: bool = Field(..., description="Contains range-separated correlation?")
    x_lrc: bool = Field(..., description="Contains range-separated exchange?")
    nlc: bool = Field(..., description="Does this functional need non-local correlation?")


class DFTFunctionalContext:
    """Information about DFT functionals.

    Parameters
    ----------
    context : {'default'}
        Origin of loaded data.

    Attributes
    ----------
    functionals : Dict[str, DFTFunctionalInfo]
        dictionary of (lower-case) functional name to info

    name : str
        The name of the context ('default')
    """

    def __init__(self, context: str = "defualt"):
        if context != "default":
            raise KeyError(f"Context set as '{context}'," + " only contexts {'default'} are currently supported")

        from .data import dft_data_blob

        self.suffixes = dft_data_blob.data_blob["empirical_dispersion_suffixes"]
        self.functionals: Dict[str, DFTFunctionalInfo] = {
            name: DFTFunctionalInfo(name=name, **data) for name, data in dft_data_blob.data_blob["functionals"].items()
        }

        self.name = context

    def __str__(self) -> str:
        return "DFTFunctionalContext(context='{}')".format(self.name)


# singleton
dftfunctionalinfo = DFTFunctionalContext("default")


def get(name: str) -> DFTFunctionalInfo:

    name = name.lower()
    for x in dftfunctionalinfo.suffixes:
        if name.endswith(x):
            name = name.replace(x, "")
            break

    return dftfunctionalinfo.functionals[name].copy()
