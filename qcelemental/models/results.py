from typing import Any, Dict, List, Optional, Union

import numpy as np
from pydantic import Schema, constr, validator

from ..util import provenance_stamp
from .basemodels import ProtoModel
from .basis import BasisSet
from .common_models import ComputeError, DriverEnum, Model, Provenance, qcschema_input_default, qcschema_output_default
from .molecule import Molecule
from .types import Array


class ResultProperties(ProtoModel):
    """
    Named properties of quantum chemistry computations following the MolSSI QCSchema.
    """

    # Calcinfo
    calcinfo_nbasis: Optional[int] = Schema(None, description="The number of basis functions for the computation.")
    calcinfo_nmo: Optional[int] = Schema(None, description="The number of molecular orbitals for the computation.")
    calcinfo_nalpha: Optional[int] = Schema(None, description="The number of alpha electrons in the computation.")
    calcinfo_nbeta: Optional[int] = Schema(None, description="The number of beta electrons in the computation.")
    calcinfo_natom: Optional[int] = Schema(None, description="The number of atoms in the computation.")

    # Canonical
    nuclear_repulsion_energy: Optional[float] = Schema(None, description="The nuclear repulsion energy energy.")
    return_energy: Optional[float] = Schema(
        None, description="The energy of the requested method, identical to `return_value` for energy computations.")

    # SCF Keywords
    scf_one_electron_energy: Optional[float] = Schema(
        None, description="The one-electron (core Hamiltonian) energy contribution to the total SCF energy.")
    scf_two_electron_energy: Optional[float] = Schema(
        None, description="The two-electron energy contribution to the total SCF energy.")
    scf_vv10_energy: Optional[float] = Schema(
        None, description="The VV10 functional energy contribution to the total SCF energy.")
    scf_xc_energy: Optional[float] = Schema(
        None, description="The functional (XC) energy contribution to the total SCF energy.")
    scf_dispersion_correction_energy: Optional[float] = Schema(
        None,
        description="The dispersion correction appended to an underlying functional when a DFT-D method is requested.")
    scf_dipole_moment: Optional[List[float]] = Schema(None, description="The X, Y, and Z dipole components.")
    scf_total_energy: Optional[float] = Schema(
        None, description="The total electronic energy of the SCF stage of the calculation.")
    scf_iterations: Optional[int] = Schema(None, description="The number of SCF iterations taken before convergence.")

    # MP2 Keywords
    mp2_same_spin_correlation_energy: Optional[float] = Schema(
        None, description="The portion of MP2 doubles correlation energy from same-spin (i.e. triplet) correlations.")
    mp2_opposite_spin_correlation_energy: Optional[float] = Schema(
        None,
        description="The portion of MP2 doubles correlation energy from opposite-spin (i.e. singlet) correlations.")
    mp2_singles_energy: Optional[float] = Schema(
        None, description="The singles portion of the MP2 correlation energy. Zero except in ROHF.")
    mp2_doubles_energy: Optional[float] = Schema(
        None,
        description=
        "The doubles portion of the MP2 correlation energy including same-spin and opposite-spin correlations.")
    mp2_total_correlation_energy: Optional[float] = Schema(
        None, description="The MP2 correlation energy.")  # Old name, to be deprecated
    mp2_correlation_energy: Optional[float] = Schema(None, description="The MP2 correlation energy.")
    mp2_total_energy: Optional[float] = Schema(
        None, description="The total MP2 energy (MP2 correlation energy + HF energy).")
    mp2_dipole_moment: Optional[List[float]] = Schema(None, description="The MP2 X, Y, and Z dipole components.")

    # CCSD Keywords
    ccsd_same_spin_correlation_energy: Optional[float] = Schema(
        None, description="The portion of CCSD doubles correlation energy from same-spin (i.e. triplet) correlations.")
    ccsd_opposite_spin_correlation_energy: Optional[float] = Schema(
        None,
        description="The portion of CCSD doubles correlation energy from opposite-spin (i.e. singlet) correlations")
    ccsd_singles_energy: Optional[float] = Schema(
        None, description="The singles portion of the CCSD correlation energy. Zero except in ROHF.")
    ccsd_doubles_energy: Optional[float] = Schema(
        None,
        description=
        "The doubles portion of the CCSD correlation energy including same-spin and opposite-spin correlations.")
    ccsd_correlation_energy: Optional[float] = Schema(None, description="The CCSD correlation energy.")
    ccsd_total_energy: Optional[float] = Schema(
        None, description="The total CCSD energy (CCSD correlation energy + HF energy).")
    ccsd_dipole_moment: Optional[List[float]] = Schema(None, description="The CCSD X, Y, and Z dipole components.")
    ccsd_iterations: Optional[int] = Schema(None,
                                            description="The number of CCSD iterations taken before convergence.")

    # CCSD(T) keywords
    ccsd_prt_pr_correlation_energy: Optional[float] = Schema(None, description="The CCSD(T) correlation energy.")
    ccsd_prt_pr_total_energy: Optional[float] = Schema(
        None, description="The total CCSD(T) energy (CCSD(T) correlation energy + HF energy).")
    ccsd_prt_pr_dipole_moment: Optional[List[float]] = Schema(None,
                                                              description="The CCSD(T) X, Y, and Z dipole components.")

    class Config(ProtoModel.Config):
        force_skip_defaults = True

    def __str__(self):
        data_str = ', '.join(f'{k}={v}' for k, v in self.dict().items())
        return f"{self.__class__.__name__}({data_str})"


### Primary models


class ResultInput(ProtoModel):
    """The MolSSI Quantum Chemistry Schema"""
    id: Optional[str] = Schema(None, description="An optional ID of the ResultInput object.")
    schema_name: constr(strip_whitespace=True, regex=qcschema_input_default) = qcschema_input_default  # type: ignore
    schema_version: int = 1

    molecule: Molecule = Schema(..., description="The molecule to use in the computation.")
    driver: DriverEnum = Schema(..., description=str(DriverEnum.__doc__))
    model: Model = Schema(..., description=str(Model.__doc__))
    keywords: Dict[str, Any] = Schema({}, description="The program specific keywords to be used.")

    extras: Dict[str, Any] = Schema({}, description="Extra fields that are not part of the schema.")

    provenance: Provenance = Schema(Provenance(**provenance_stamp(__name__)), description=str(Provenance.__doc__))

    def __str__(self):
        return (f"{self.__class__.__name__}"
                f"(driver='{self.driver}' "
                f"model='{self.model.dict()}' "
                f"molecule_hash='{self.molecule.get_hash()[:7]}')")


class Result(ResultInput):
    schema_name: constr(strip_whitespace=True, regex=qcschema_output_default) = qcschema_output_default  # type: ignore

    properties: ResultProperties = Schema(..., description=str(ResultProperties.__doc__))
    return_result: Union[float, Array[float], Dict[str, Any]] = Schema(
        ..., description="The value requested by the 'driver' attribute.")  # type: ignore

    stdout: Optional[str] = Schema(None, description="The standard output of the program.")
    stderr: Optional[str] = Schema(None, description="The standard error of the program.")

    success: bool = Schema(
        ..., description="The success of a given programs execution. If False, other fields may be blank.")
    error: Optional[ComputeError] = Schema(None, description=str(ComputeError.__doc__))
    provenance: Provenance = Schema(..., description=str(Provenance.__doc__))

    @validator("schema_name", pre=True)
    def _input_to_output(cls, v):
        """If qcschema_input is passed in, cast it to output, otherwise no"""
        if v.lower().strip() in [qcschema_input_default, qcschema_output_default]:
            return qcschema_output_default
        raise ValueError("Only {0} or {1} is allowed for schema_name, "
                         "which will be converted to {0}".format(qcschema_output_default, qcschema_input_default))

    @validator("return_result", whole=True)
    def _validate_return_result(cls, v, values):
        if values["driver"] == "gradient":
            v = np.asarray(v).reshape(-1, 3)
        elif values["driver"] == "hessian":
            v = np.asarray(v)
            nsq = int(v.size**0.5)
            v.shape = (nsq, nsq)

        return v


class WavefunctionProperties(ProtoModel):

    # The full basis set description of the quantities
    basis: BasisSet = Schema(..., description=str(BasisSet.__doc__))

    # Core Hamiltonian
    h_core_a: Array[float] = Schema(None, description="Alpha-spin core (one-electron) Hamiltonian in the AO basis.")
    h_core_b: Array[float] = Schema(None, description="Beta-spin core (one-electron) Hamiltonian in the AO basis.")
    h_effective_a: Array[float] = Schema(
        None, description="Alpha-spin effective core (one-electron) Hamiltonian in the AO basis.")
    h_effective_b: Array[float] = Schema(
        None, description="Beta-spin effective core (one-electron) Hamiltonian in the AO basis.")

    # Return results
    orbitals_a: Array[float] = Schema(None,
                                      description="The alpha-spin orbitals in the AO basis of the primary return.")
    orbitals_b: Array[float] = Schema(None, description="")
    density_a: Array[float] = Schema(None, description="")
    density_b: Array[float] = Schema(None, description="")
    fock_a: Array[float] = Schema(None, description="")
    fock_b: Array[float] = Schema(None, description="")
    eigenvalues_a: Array[float] = Schema(None, description="")
    eigenvalues_b: Array[float] = Schema(None, description="")
    occupations_a: Array[float] = Schema(None, description="")
    occupations_b: Array[float] = Schema(None, description="")

    # SCF Results
    scf_orbitals_a: Array[float] = Schema(None, description="")
    scf_orbitals_b: Array[float] = Schema(None, description="")
    scf_density_a: Array[float] = Schema(None, description="")
    scf_density_b: Array[float] = Schema(None, description="")
    scf_fock_a: Array[float] = Schema(None, description="")
    scf_fock_b: Array[float] = Schema(None, description="")
    scf_eigenvalues_a: Array[float] = Schema(None, description="")
    scf_eigenvalues_b: Array[float] = Schema(None, description="")
    scf_occupations_a: Array[float] = Schema(None, description="")
    scf_occupations_b: Array[float] = Schema(None, description="")


class Wavefunction(Result):
    schema_name: constr(strip_whitespace=True, regex="qcschema_wavefunction") = "qcschema_wavefunction"  # type: ignore

    wavefunction: WavefunctionProperties = Schema(..., description=str(WavefunctionProperties.__doc__))
