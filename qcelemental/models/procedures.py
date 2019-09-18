from typing import Any, Dict, List, Optional

from pydantic import Schema, constr

from ..util import provenance_stamp
from .basemodels import ProtoModel
from .common_models import (ComputeError, DriverEnum, Model, Provenance, qcschema_input_default,
                            qcschema_optimization_input_default, qcschema_optimization_output_default)
from .molecule import Molecule
from .results import Result


class QCInputSpecification(ProtoModel):
    """
    A compute description for energy, gradient, and Hessian computations used in a geometry optimization.
    """
    schema_name: constr(strip_whitespace=True, regex=qcschema_input_default) = qcschema_input_default  # type: ignore
    schema_version: int = 1

    driver: DriverEnum = Schema(..., description=str(DriverEnum.__doc__))
    model: Model = Schema(..., description=str(Model.__doc__))
    keywords: Dict[str, Any] = Schema({}, description="The program specific keywords to be used.")

    extras: Dict[str, Any] = Schema({}, description="Extra fields that are not part of the schema.")


class OptimizationInput(ProtoModel):
    id: Optional[str] = None
    hash_index: Optional[str] = None
    schema_name: constr(  # type: ignore
        strip_whitespace=True, regex=qcschema_optimization_input_default) = qcschema_optimization_input_default
    schema_version: int = 1

    keywords: Dict[str, Any] = Schema({}, description="The optimization specific keywords to be used.")
    extras: Dict[str, Any] = Schema({}, description="Extra fields that are not part of the schema.")

    input_specification: QCInputSpecification = Schema(..., description=str(QCInputSpecification.__doc__))
    initial_molecule: Molecule = Schema(..., description="The starting molecule for the geometry optimization.")

    provenance: Provenance = Schema(Provenance(**provenance_stamp(__name__)), description=str(Provenance.__doc__))

    def __str__(self) -> str:
        return (f"{self.__class__.__name__}"
                f"(model='{self.input_specification.model.dict()}' "
                f"molecule_hash='{self.initial_molecule.get_hash()[:7]}')")


class Optimization(OptimizationInput):
    schema_name: constr(  # type: ignore
        strip_whitespace=True, regex=qcschema_optimization_output_default) = qcschema_optimization_output_default

    final_molecule: Optional[Molecule] = Schema(..., description="The final molecule of the geometry optimization.")
    trajectory: List[Result] = Schema(..., description="A list of order Result objects for each step in the optimization.")
    energies: List[float] = Schema(..., description="A list of ordered energies for each step in the optimization.")

    stdout: Optional[str] = Schema(None, description="The standard output of the program.")
    stderr: Optional[str] = Schema(None, description="The standard error of the program.")

    success: bool = Schema(
        ..., description="The success of a given programs execution. If False, other fields may be blank.")
    error: Optional[ComputeError] = Schema(None, description=str(ComputeError.__doc__))
    provenance: Provenance = Schema(..., description=str(Provenance.__doc__))
