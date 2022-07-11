from typing import Any, Dict, Optional

from pydantic import Field
from typing_extensions import Literal


from .qcschema_abc import AutoSetProvenance, QCSchemaModelBase
from .molecule import Molecule


class SpecificationBase(AutoSetProvenance):
    """Specification objects contain the keywords and other configurable parameters directed at a particular QC program"""

    keywords: Dict[str, Any] = Field({}, description="The program specific keywords to be used.")
    program: str = Field(..., description="The program for which the Specification is intended.")


class InputBase(AutoSetProvenance):
    """An Input is composed of a .specification and a .molecule which together fully specify a computation"""

    specification: SpecificationBase = Field(..., description=SpecificationBase.__doc__)
    molecule: Molecule = Field(..., description=Molecule.__doc__)


class ResultBase(QCSchemaModelBase):
    """Base class for all result classes"""

    input_data: InputBase = Field(..., description=InputBase.__doc__)
    success: bool = Field(
        ...,
        description="A boolean indicator that the operation succeeded or failed. Allows programmatic assessment of "
        "all results regardless of if they failed or succeeded by checking `result.success`.",
    )

    stdout: Optional[str] = Field(
        None,
        description="The primary logging output of the program, whether natively standard output or a file. Presence vs. absence (or null-ness?) configurable by protocol.",
    )
    stderr: Optional[str] = Field(None, description="The standard error of the program execution.")


class SuccessfulResultBase(ResultBase):
    """Base object for any successful result"""

    success: Literal[True] = Field(True, description="Always `True` for a successful result")
