import abc
import json
from pathlib import Path
from typing import Any, Dict, Optional, Set, Union

import numpy as np
from pydantic import BaseModel, BaseSettings, Field
from typing_extensions import Literal

from qcelemental.testing import compare_recursive
from qcelemental.util import deserialize, serialize
from qcelemental.util.autodocs import AutoPydanticDocGenerator

from ..util import provenance_stamp
from .basemodels import ProtoModel, Provenance
from .molecule import Molecule


class InputResultBase(ProtoModel, abc.ABC):
    """Base class from which input and result models are derived


    NOTE: Abstract implementation coming from Samuel Colvin's suggestion:
        https://github.com/samuelcolvin/pydantic/discussions/2410#discussioncomment-408613
    """

    @property
    @abc.abstractmethod
    def schema_name(self) -> str:
        """The QCSchema specification this model conforms to"""

    schema_version: Literal[2] = Field(
        2, description="The version number of ``schema_name`` to which this model conforms."
    )
    id: Optional[str] = Field(None, description="The optional ID for the computation.")
    extras: Dict[str, Any] = Field(
        {},
        description="Additional information to bundle with the computation. Use for schema development and scratch space.",
    )

    provenance: Provenance = Field(..., description=str(Provenance.__doc__))


class InputBase(InputResultBase):
    """Base Class for all input objects"""

    provenance: Provenance = Field(Provenance(**provenance_stamp(__name__)), description=str(Provenance.__doc__))


class ResultBase(InputResultBase):
    """Base class for all result classes"""

    input_data: Any = Field(..., description="The input data supplied to generate the computation")
    success: bool = Field(..., description="The success of program execution")

    stdout: Optional[str] = Field(
        None,
        description="The primary logging output of the program, whether natively standard output or a file. Presence vs. absence (or null-ness?) configurable by protocol.",
    )
    stderr: Optional[str] = Field(None, description="The standard error of the program execution.")


class SuccessfulResultBase(ResultBase):
    """Base object for any successfully returned result"""

    success: Literal[True] = Field(
        True,
        description="A boolean indicator that the operation succeeded consistent with the model of successful operations. "
        "Should always be True. Allows programmatic assessment of all operations regardless of if they failed or "
        "succeeded",
    )


class InputSpecificationBase(InputBase):
    """Input specification base"""

    keywords: Dict[str, Any] = Field({}, description="The program specific keywords to be used.")
    protocols: Any = Field(..., description="Protocols associated with the input")


class InputComputationBase(InputBase):
    """Base input directed at any computational chemistry program"""

    input_spec: InputSpecificationBase = Field(..., description="The input specification for the computation")
    molecule: Molecule = Field(..., description="The molecule to use in the computation.")

    @property
    def initial_molecule(self) -> Molecule:
        """To maintain backwards compatibility to access the 'initial_molecule' attribute"""
        # NOTE: Useful? Still have to use 'molecule' for instantiating the object...
        return self.molecule
