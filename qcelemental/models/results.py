from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, Optional, Set, Union

import numpy as np
from pydantic import Field, constr, validator

from ..util import provenance_stamp
from .basemodels import ProtoModel
from .basis import BasisSet
from .common_models import ComputeError, DriverEnum, Model, Provenance, qcschema_input_default, qcschema_output_default
from .molecule import Molecule
from .types import Array

if TYPE_CHECKING:
    from pydantic.typing import ReprArgs


class AtomicResultProperties(ProtoModel):
    """
    Named properties of quantum chemistry computations following the MolSSI QCSchema.
    """

    # Calcinfo
    calcinfo_nbasis: Optional[int] = Field(None, description="The number of basis functions for the computation.")
    calcinfo_nmo: Optional[int] = Field(None, description="The number of molecular orbitals for the computation.")
    calcinfo_nalpha: Optional[int] = Field(None, description="The number of alpha electrons in the computation.")
    calcinfo_nbeta: Optional[int] = Field(None, description="The number of beta electrons in the computation.")
    calcinfo_natom: Optional[int] = Field(None, description="The number of atoms in the computation.")

    # Canonical
    nuclear_repulsion_energy: Optional[float] = Field(None, description="The nuclear repulsion energy energy.")
    return_energy: Optional[float] = Field(
        None, description="The energy of the requested method, identical to `return_value` for energy computations."
    )

    # SCF Keywords
    scf_one_electron_energy: Optional[float] = Field(
        None, description="The one-electron (core Hamiltonian) energy contribution to the total SCF energy."
    )
    scf_two_electron_energy: Optional[float] = Field(
        None, description="The two-electron energy contribution to the total SCF energy."
    )
    scf_vv10_energy: Optional[float] = Field(
        None, description="The VV10 functional energy contribution to the total SCF energy."
    )
    scf_xc_energy: Optional[float] = Field(
        None, description="The functional (XC) energy contribution to the total SCF energy."
    )
    scf_dispersion_correction_energy: Optional[float] = Field(
        None,
        description="The dispersion correction appended to an underlying functional when a DFT-D method is requested.",
    )
    scf_dipole_moment: Optional[Array[float]] = Field(None, description="The X, Y, and Z dipole components.")
    scf_quadrupole_moment: Optional[Array[float]] = Field(
        None, description="The (3, 3) quadrupole components (redundant; 6 unique)."
    )
    scf_total_energy: Optional[float] = Field(
        None, description="The total electronic energy of the SCF stage of the calculation."
    )
    scf_iterations: Optional[int] = Field(None, description="The number of SCF iterations taken before convergence.")

    # MP2 Keywords
    mp2_same_spin_correlation_energy: Optional[float] = Field(
        None, description="The portion of MP2 doubles correlation energy from same-spin (i.e. triplet) correlations."
    )
    mp2_opposite_spin_correlation_energy: Optional[float] = Field(
        None,
        description="The portion of MP2 doubles correlation energy from opposite-spin (i.e. singlet) correlations.",
    )
    mp2_singles_energy: Optional[float] = Field(
        None, description="The singles portion of the MP2 correlation energy. Zero except in ROHF."
    )
    mp2_doubles_energy: Optional[float] = Field(
        None,
        description="The doubles portion of the MP2 correlation energy including same-spin and opposite-spin correlations.",
    )
    mp2_total_correlation_energy: Optional[float] = Field(
        None, description="The MP2 correlation energy."
    )  # Old name, to be deprecated
    mp2_correlation_energy: Optional[float] = Field(None, description="The MP2 correlation energy.")
    mp2_total_energy: Optional[float] = Field(
        None, description="The total MP2 energy (MP2 correlation energy + HF energy)."
    )
    mp2_dipole_moment: Optional[Array[float]] = Field(None, description="The MP2 X, Y, and Z dipole components.")

    # CCSD Keywords
    ccsd_same_spin_correlation_energy: Optional[float] = Field(
        None, description="The portion of CCSD doubles correlation energy from same-spin (i.e. triplet) correlations."
    )
    ccsd_opposite_spin_correlation_energy: Optional[float] = Field(
        None,
        description="The portion of CCSD doubles correlation energy from opposite-spin (i.e. singlet) correlations",
    )
    ccsd_singles_energy: Optional[float] = Field(
        None, description="The singles portion of the CCSD correlation energy. Zero except in ROHF."
    )
    ccsd_doubles_energy: Optional[float] = Field(
        None,
        description="The doubles portion of the CCSD correlation energy including same-spin and opposite-spin correlations.",
    )
    ccsd_correlation_energy: Optional[float] = Field(None, description="The CCSD correlation energy.")
    ccsd_total_energy: Optional[float] = Field(
        None, description="The total CCSD energy (CCSD correlation energy + HF energy)."
    )
    ccsd_dipole_moment: Optional[Array[float]] = Field(None, description="The CCSD X, Y, and Z dipole components.")
    ccsd_iterations: Optional[int] = Field(None, description="The number of CCSD iterations taken before convergence.")

    # CCSD(T) keywords
    ccsd_prt_pr_correlation_energy: Optional[float] = Field(None, description="The CCSD(T) correlation energy.")
    ccsd_prt_pr_total_energy: Optional[float] = Field(
        None, description="The total CCSD(T) energy (CCSD(T) correlation energy + HF energy)."
    )
    ccsd_prt_pr_dipole_moment: Optional[Array[float]] = Field(
        None, description="The CCSD(T) X, Y, and Z dipole components."
    )

    class Config(ProtoModel.Config):
        force_skip_defaults = True

    def __repr_args__(self) -> "ReprArgs":
        return [(k, v) for k, v in self.dict().items()]

    @validator(
        "scf_dipole_moment",
        "mp2_dipole_moment",
        "ccsd_dipole_moment",
        "ccsd_prt_pr_dipole_moment",
        "scf_quadrupole_moment",
    )
    def _validate_poles(cls, v, values, field):
        if v is None:
            return v

        if field.name.endswith("_dipole_moment"):
            order = 1
        elif field.name.endswith("_quadrupole_moment"):
            order = 2

        shape = tuple([3] * order)
        return np.asarray(v).reshape(shape)

    def dict(self, *args, **kwargs):
        # pure-json dict repr for QCFractal compliance, see https://github.com/MolSSI/QCFractal/issues/579
        kwargs["encoding"] = "json"
        return super().dict(*args, **kwargs)


class WavefunctionProperties(ProtoModel):

    # Class properties
    _return_results_names: Set[str] = {
        "orbitals_a",
        "orbitals_b",
        "density_a",
        "density_b",
        "fock_a",
        "fock_b",
        "eigenvalues_a",
        "eigenvalues_b",
        "occupations_a",
        "occupations_b",
    }

    # The full basis set description of the quantities
    basis: BasisSet = Field(..., description=str(BasisSet.__doc__))
    restricted: bool = Field(
        ...,
        description=str(
            "If the computation was restricted or not (alpha == beta). If True, all beta quantities are skipped."
        ),
    )

    # Core Hamiltonian
    h_core_a: Optional[Array[float]] = Field(None, description="Alpha-spin core (one-electron) Hamiltonian.")
    h_core_b: Optional[Array[float]] = Field(None, description="Beta-spin core (one-electron) Hamiltonian.")
    h_effective_a: Optional[Array[float]] = Field(
        None, description="Alpha-spin effective core (one-electron) Hamiltonian."
    )
    h_effective_b: Optional[Array[float]] = Field(
        None, description="Beta-spin effective core (one-electron) Hamiltonian "
    )

    # SCF Results
    scf_orbitals_a: Optional[Array[float]] = Field(None, description="SCF alpha-spin orbitals.")
    scf_orbitals_b: Optional[Array[float]] = Field(None, description="SCF beta-spin orbitals.")
    scf_density_a: Optional[Array[float]] = Field(None, description="SCF alpha-spin density matrix.")
    scf_density_b: Optional[Array[float]] = Field(None, description="SCF beta-spin density matrix.")
    scf_fock_a: Optional[Array[float]] = Field(None, description="SCF alpha-spin Fock matrix.")
    scf_fock_b: Optional[Array[float]] = Field(None, description="SCF beta-spin Fock matrix.")
    scf_eigenvalues_a: Optional[Array[float]] = Field(None, description="SCF alpha-spin eigenvalues.")
    scf_eigenvalues_b: Optional[Array[float]] = Field(None, description="SCF beta-spin eigenvalues.")
    scf_occupations_a: Optional[Array[float]] = Field(None, description="SCF alpha-spin occupations.")
    scf_occupations_b: Optional[Array[float]] = Field(None, description="SCF beta-spin occupations.")

    # Return results, must be defined last
    orbitals_a: Optional[str] = Field(None, description="Index to the alpha-spin orbitals of the primary return.")
    orbitals_b: Optional[str] = Field(None, description="Index to the beta-spin orbitals of the primary return.")
    density_a: Optional[str] = Field(None, description="Index to the alpha-spin density of the primary return.")
    density_b: Optional[str] = Field(None, description="Index to the beta-spin density of the primary return.")
    fock_a: Optional[str] = Field(None, description="Index to the alpha-spin Fock matrix of the primary return.")
    fock_b: Optional[str] = Field(None, description="Index to the beta-spin Fock matrix of the primary return.")
    eigenvalues_a: Optional[str] = Field(None, description="Index to the alpha-spin eigenvalues of the primary return.")
    eigenvalues_b: Optional[str] = Field(None, description="Index to the beta-spin eigenvalues of the primary return.")
    occupations_a: Optional[str] = Field(
        None, description="Index to the alpha-spin orbital eigenvalues of the primary return."
    )
    occupations_b: Optional[str] = Field(
        None, description="Index to the beta-spin orbital eigenvalues of the primary return."
    )

    class Config(ProtoModel.Config):
        force_skip_defaults = True

    @validator("scf_eigenvalues_a", "scf_eigenvalues_b", "scf_occupations_a", "scf_occupations_b")
    def _assert1d(cls, v, values):

        try:
            v = v.reshape(-1)
        except (ValueError, AttributeError):
            raise ValueError("Vector must be castable to shape (-1, )!")
        return v

    @validator("scf_orbitals_a", "scf_orbitals_b")
    def _assert2d_nao_x(cls, v, values):
        bas = values.get("basis", None)

        # Do not raise multiple errors
        if bas is None:
            return v

        try:
            v = v.reshape(bas.nbf, -1)
        except (ValueError, AttributeError):
            raise ValueError("Matrix must be castable to shape (nbf, -1)!")
        return v

    @validator(
        "h_core_a",
        "h_core_b",
        "h_effective_a",
        "h_effective_b",
        # SCF
        "scf_density_a",
        "scf_density_b",
        "scf_fock_a",
        "scf_fock_b",
    )
    def _assert2d(cls, v, values):
        bas = values.get("basis", None)

        # Do not raise multiple errors
        if bas is None:
            return v

        try:
            v = v.reshape(bas.nbf, bas.nbf)
        except (ValueError, AttributeError):
            raise ValueError("Matrix must be castable to shape (nbf, nbf)!")
        return v

    @validator(
        "orbitals_a",
        "orbitals_b",
        "density_a",
        "density_b",
        "fock_a",
        "fock_b",
        "eigenvalues_a",
        "eigenvalues_b",
        "occupations_a",
        "occupations_b",
    )
    def _assert_exists(cls, v, values):

        if values.get(v, None) is None:
            raise ValueError(f"Return quantity {v} does not exist in the values.")
        return v


class WavefunctionProtocolEnum(str, Enum):
    """
    Wavefunction to keep from a Result computation.
    """

    all = "all"
    orbitals_and_eigenvalues = "orbitals_and_eigenvalues"
    return_results = "return_results"
    none = "none"


class ErrorCorrectionProtocol(ProtoModel):
    """Configuration for how QCEngine handles error correction
    
    WARNING: These protocols are currently experimental and only supported by NWChem tasks
    """

    default_policy: bool = Field(
        True, description="Whether to allow error corrections to be used " "if not directly specified in `policies`"
    )
    # TODO (wardlt): Consider support for common policies (e.g., 'only increase iterations') as strings (see #182)
    policies: Optional[Dict[str, bool]] = Field(
        None,
        description="Settings that define whether specific error corrections are allowed. "
        "Keys are the name of a known error and values are whether it is allowed to be used.",
    )

    def allows(self, policy: str):
        if self.policies is None:
            return self.default_policy
        return self.policies.get(policy, self.default_policy)


class AtomicResultProtocols(ProtoModel):
    """
    Protocols regarding the manipulation of a Result output data.
    """

    wavefunction: WavefunctionProtocolEnum = Field(
        WavefunctionProtocolEnum.none, description=str(WavefunctionProtocolEnum.__doc__)
    )
    stdout: bool = Field(True, description="Primary output file to keep from a Result computation")
    error_correction: ErrorCorrectionProtocol = Field(
        ErrorCorrectionProtocol(), description="Policies for error correction"
    )

    class Config:
        force_skip_defaults = True


### Primary models


class AtomicInput(ProtoModel):
    """The MolSSI Quantum Chemistry Schema"""

    id: Optional[str] = Field(None, description="An optional ID of the ResultInput object.")
    schema_name: constr(strip_whitespace=True, regex=qcschema_input_default) = qcschema_input_default  # type: ignore
    schema_version: int = 1

    molecule: Molecule = Field(..., description="The molecule to use in the computation.")
    driver: DriverEnum = Field(..., description=str(DriverEnum.__doc__))
    model: Model = Field(..., description=str(Model.__base_doc__))
    keywords: Dict[str, Any] = Field({}, description="The program specific keywords to be used.")
    protocols: AtomicResultProtocols = Field(
        AtomicResultProtocols(), description=str(AtomicResultProtocols.__base_doc__)
    )

    extras: Dict[str, Any] = Field({}, description="Extra fields that are not part of the schema.")

    provenance: Provenance = Field(Provenance(**provenance_stamp(__name__)), description=str(Provenance.__base_doc__))

    def __repr_args__(self) -> "ReprArgs":
        return [
            ("driver", self.driver.value),
            ("model", self.model.dict()),
            ("molecule_hash", self.molecule.get_hash()[:7]),
        ]


class AtomicResult(AtomicInput):
    schema_name: constr(strip_whitespace=True, regex=qcschema_output_default) = qcschema_output_default  # type: ignore

    properties: AtomicResultProperties = Field(..., description=str(AtomicResultProperties.__base_doc__))
    wavefunction: Optional[WavefunctionProperties] = Field(None, description=str(WavefunctionProperties.__base_doc__))

    return_result: Union[float, Array[float], Dict[str, Any]] = Field(
        ..., description="The value requested by the 'driver' attribute."
    )  # type: ignore

    stdout: Optional[str] = Field(None, description="The standard output of the program.")
    stderr: Optional[str] = Field(None, description="The standard error of the program.")

    success: bool = Field(
        ..., description="The success of a given programs execution. If False, other fields may be blank."
    )
    error: Optional[ComputeError] = Field(None, description=str(ComputeError.__base_doc__))
    provenance: Provenance = Field(..., description=str(Provenance.__base_doc__))

    @validator("schema_name", pre=True)
    def _input_to_output(cls, v):
        """If qcschema_input is passed in, cast it to output, otherwise no"""
        if v.lower().strip() in [qcschema_input_default, qcschema_output_default]:
            return qcschema_output_default
        raise ValueError(
            "Only {0} or {1} is allowed for schema_name, "
            "which will be converted to {0}".format(qcschema_output_default, qcschema_input_default)
        )

    @validator("return_result")
    def _validate_return_result(cls, v, values):
        if values["driver"] == "gradient":
            v = np.asarray(v).reshape(-1, 3)
        elif values["driver"] == "hessian":
            v = np.asarray(v)
            nsq = int(v.size ** 0.5)
            v.shape = (nsq, nsq)

        return v

    @validator("wavefunction", pre=True)
    def _wavefunction_protocol(cls, value, values):

        # We are pre, gotta do extra checks
        if value is None:
            return value
        elif isinstance(value, dict):
            wfn = value.copy()
        elif isinstance(value, WavefunctionProperties):
            wfn = value.dict()
        else:
            raise ValueError("wavefunction must be None, a dict, or a WavefunctionProperties object.")

        # Do not propagate validation errors
        if "protocols" not in values:
            raise ValueError("Protocols was not properly formed.")

        # Handle restricted
        restricted = wfn.get("restricted", None)
        if restricted is None:
            raise ValueError("`restricted` is required.")

        if restricted:
            for k in list(wfn.keys()):
                if k.endswith("_b"):
                    wfn.pop(k)

        # Handle protocols
        wfnp = values["protocols"].wavefunction
        return_keep = None
        if wfnp == "all":
            pass
        elif wfnp == "none":
            wfn = None
        elif wfnp == "return_results":
            return_keep = [
                "orbitals_a",
                "orbitals_b",
                "density_a",
                "density_b",
                "fock_a",
                "fock_b",
                "eigenvalues_a",
                "eigenvalues_b",
                "occupations_a",
                "occupations_b",
            ]
        elif wfnp == "orbitals_and_eigenvalues":
            return_keep = ["orbitals_a", "orbitals_b", "eigenvalues_a", "eigenvalues_b"]
        else:
            raise ValueError(f"Protocol `wavefunction:{wfnp}` is not understood.")

        if return_keep is not None:
            ret_wfn = {"restricted": restricted}
            if "basis" in wfn:
                ret_wfn["basis"] = wfn["basis"]

            for rk in return_keep:
                key = wfn.get(rk, None)
                if key is None:
                    continue

                ret_wfn[rk] = key
                ret_wfn[key] = wfn[key]

            return ret_wfn
        else:
            return wfn

    @validator("stdout")
    def _stdout_protocol(cls, value, values):

        # Do not propagate validation errors
        if "protocols" not in values:
            raise ValueError("Protocols was not properly formed.")

        outp = values["protocols"].stdout
        if outp is True:
            return value
        elif outp is False:
            return None
        else:
            raise ValueError(f"Protocol `stdout:{outp}` is not understood")


class ResultProperties(AtomicResultProperties):
    def __init__(self, *args, **kwargs):
        from warnings import warn

        warn(
            "ResultProperties has been renamed to AtomicResultProperties and will be removed in v0.13.0",
            DeprecationWarning,
        )
        super().__init__(*args, **kwargs)


class ResultProtocols(AtomicResultProtocols):
    def __init__(self, *args, **kwargs):
        from warnings import warn

        warn(
            "ResultProtocols has been renamed to AtomicResultProtocols and will be removed in v0.13.0",
            DeprecationWarning,
        )
        super().__init__(*args, **kwargs)


class ResultInput(AtomicInput):
    def __init__(self, *args, **kwargs):
        from warnings import warn

        warn("ResultInput has been renamed to AtomicInput and will be removed in v0.13.0", DeprecationWarning)
        super().__init__(*args, **kwargs)


class Result(AtomicResult):
    def __init__(self, *args, **kwargs):
        from warnings import warn

        warn("Result has been renamed to AtomicResult and will be removed in v0.13.0", DeprecationWarning)
        super().__init__(*args, **kwargs)
