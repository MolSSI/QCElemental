from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import Schema, constr, validator

from ..util import provenance_stamp
from .basemodels import ProtoModel
from .common_models import (ComputeError, DriverEnum, Model, Provenance, qcschema_input_default,
                            qcschema_optimization_input_default, qcschema_optimization_output_default)
from .molecule import Molecule
from .results import Result


class TrajectoryProtocolEnum(str, Enum):
    """
    Which gradient evaluations to keep in an optimization trajectory.
    """
    all = "all"
    initial_and_final = "initial_and_final"
    final = "final"
    none = "none"


class OptimizationProtocols(ProtoModel):
    """
    Protocols regarding the manipulation of a Optimization output data.
    """

    trajectory: TrajectoryProtocolEnum = Schema(TrajectoryProtocolEnum.all,
                                                description=str(TrajectoryProtocolEnum.__doc__))

    class Config:
        force_skip_defaults = True


class QCInputSpecification(ProtoModel):
    """
    A compute description for energy, gradient, and Hessian computations used in a geometry optimization.
    """
    schema_name: constr(strip_whitespace=True, regex=qcschema_input_default) = qcschema_input_default  # type: ignore
    schema_version: int = 1

    driver: DriverEnum = Schema(DriverEnum.gradient, description=str(DriverEnum.__doc__))
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
    protocols: OptimizationProtocols = Schema(OptimizationProtocols(), description=str(OptimizationProtocols.__doc__))

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
    trajectory: List[Result] = Schema(
        ..., description="A list of ordered Result objects for each step in the optimization.")
    energies: List[float] = Schema(..., description="A list of ordered energies for each step in the optimization.")

    stdout: Optional[str] = Schema(None, description="The standard output of the program.")
    stderr: Optional[str] = Schema(None, description="The standard error of the program.")

    success: bool = Schema(
        ..., description="The success of a given programs execution. If False, other fields may be blank.")
    error: Optional[ComputeError] = Schema(None, description=str(ComputeError.__doc__))
    provenance: Provenance = Schema(..., description=str(Provenance.__doc__))

    @validator('trajectory', whole=True)
    def _trajectory_protocol(cls, v, values):

        # Do not propogate validation errors
        if 'protocols' not in values:
            raise ValueError("Protocols was not properly formed.")

        keep_enum = values['protocols'].trajectory
        if keep_enum == 'all':
            pass
        elif keep_enum == "initial_and_final":
            if len(v) != 2:
                v = [v[0], v[-1]]
        elif keep_enum == "final":
            if len(v) != 1:
                v = [v[-1]]
        elif keep_enum == "none":
            v = []
        else:
            raise ValueError(f"Protocol `trajectory:{keep_enum}` is not understood.")

        return v
