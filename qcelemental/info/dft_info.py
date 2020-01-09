"""
Contains metadata about density functionals
"""

from typing import Dict

from pydantic import Field

from ..models import ProtoModel


class DFTFunctional(ProtoModel):
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


class DFTFunctionalInfo:
    """Information about DFT functionals.

    Parameters
    ----------
    context : {'PSI4'}
        Origin of loaded data.

    Attributes
    ----------
    functionals : Dict[str, DftFunctional]
        dictionary of (lower-case) functional name to info

    name : str
        The name of the context ('PSI4')
    """

    def __init__(self, context: str = "defualt"):
        if context != "default":
            raise KeyError(f"Context set as '{context}'," + " only contexts {'default'} are currently supported")

        from .data import dft_data_blob

        self.functionals: Dict[str, DFTFunctional] = {
            name: DFTFunctional(**data) for name, data in dft_data_blob.data_blob["functionals"].items()
        }

        self.name = context

    def __str__(self) -> str:
        return "DFTFunctionalInfo(context='{}')".format(self.name)


# singleton
dftfunctionalinfo = DFTFunctionalInfo("default")


def get(name):

    name = name.lower().split("-d")[0].split("-nlc")[0]

    return dftfunctionalinfo.functionals[name].copy()
