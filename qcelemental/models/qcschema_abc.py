from abc import ABC
from typing import Any, Dict, Optional

from pydantic import Field, validator
from typing_extensions import Literal

from .basemodels import ProtoModel, Provenance
from ..util import provenance_stamp


class QCSchemaModelBase(ProtoModel, ABC):
    """Base class for all QCSchema objects."""

    schema_name: str = Field(..., description="The QCSchema name of the class")
    schema_version: Literal[2] = Field(
        2, description="The version number of ``schema_name`` to which this model conforms."
    )
    id: Optional[str] = Field(None, description="The optional ID for the object.")
    extras: Dict[str, Any] = Field(
        {},
        description="Additional information to bundle with the object. Use for schema development and scratch space.",
    )

    provenance: Provenance = Field(..., description=str(Provenance.__doc__))

    @validator("schema_name")
    def qcschema_name(cls, v):
        """Enforce all `schema_name` values conform to standard."""
        assert v == (
            f"qcschema_{cls.__name__.lower()}"
        ), "`schema_name` must be set to 'qcschema_' + f'{ClassName.lower()}'"
        return v


class AutoSetProvenance(QCSchemaModelBase):
    """Base class for QCSchema objects that auto-set their provenance value"""

    provenance: Provenance = Field(Provenance(**provenance_stamp(__name__)), description=Provenance.__doc__)
