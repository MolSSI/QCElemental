from enum import Enum
from typing import Dict, List, Optional

from pydantic import Field, constr, validator

from ..exceptions import ValidationError
from .basemodels import ProtoModel


class HarmonicType(str, Enum):
    """
    The angular momentum representation of a shell.
    """

    spherical = "spherical"
    cartesian = "cartesian"


class ElectronShell(ProtoModel):
    """
    Information for a single electronic shell
    """

    angular_momentum: List[int] = Field(..., description="Angular momentum for this shell.")
    harmonic_type: HarmonicType = Field(..., description=str(HarmonicType.__doc__))
    exponents: List[float] = Field(..., description="Exponents for this contracted shell.")
    coefficients: List[List[float]] = Field(
        ...,
        description="General contraction coefficients for this shell, individual list components will be the individual segment contraction coefficients.",
    )

    @validator("coefficients")
    def _check_coefficient_length(cls, v, values):
        len_exp = len(values["exponents"])
        for row in v:
            if len(row) != len_exp:
                raise ValueError("The length of coefficients does not match the length of exponents.")

        return v

    @validator("coefficients")
    def _check_general_contraction_or_fused(cls, v, values):
        if len(values["angular_momentum"]) > 1:
            if len(values["angular_momentum"]) != len(v):
                raise ValueError("The length for a fused shell must equal the length of coefficients.")

        return v

    def nfunctions(self) -> int:
        """
        Computes the number of basis functions on this shell.

        Returns
        -------
        int
            The number of basis functions on this shell.
        """

        if self.harmonic_type == "spherical":
            return sum((2 * L + 1) for L in self.angular_momentum)
        else:
            return sum(((L + 1) * (L + 2) // 2) for L in self.angular_momentum)

    def is_contracted(self) -> bool:
        """
        Checks if the shell represents a contracted Gaussian or not.

        Returns
        -------
        bool
            True if the shell is contracted.
        """

        return (len(self.coefficients) != 1) and (len(self.angular_momentum) == 1)


class ECPType(str, Enum):
    """
    The type of the ECP potential.
    """

    scalar = "scalar"
    spinorbit = "spinorbit"


class ECPPotential(ProtoModel):
    """
    Information for a single ECP potential.
    """

    ecp_type: ECPType = Field(..., description=str(ECPType.__doc__))
    angular_momentum: List[int] = Field(..., description="Angular momentum for the ECPs.")
    r_exponents: List[int] = Field(..., description="Exponents of the 'r' term.")
    gaussian_exponents: List[float] = Field(..., description="Exponents of the 'gaussian' term.")
    coefficients: List[List[float]] = Field(
        ...,
        description="General contraction coefficients for this shell, individual list components will be the individual segment contraction coefficients.",
    )

    @validator("gaussian_exponents")
    def _check_gaussian_exponents_length(cls, v, values):
        len_exp = len(values["r_exponents"])
        if len(v) != len_exp:
            raise ValueError("The length of gaussian_exponents does not match the length of `r` exponents.")

        return v

    @validator("coefficients")
    def _check_coefficient_length(cls, v, values):
        len_exp = len(values["r_exponents"])
        for row in v:
            if len(row) != len_exp:
                raise ValueError("The length of coefficients does not match the length of `r` exponents.")

        return v


class BasisCenter(ProtoModel):
    """
    Data for a single atom/center in a basis set.
    """

    electron_shells: List[ElectronShell] = Field(..., description="Electronic shells for this center.")
    ecp_electrons: int = Field(0, description="Number of electrons replace by ECP potentials.")
    ecp_potentials: Optional[List[ECPPotential]] = Field(None, description="ECPs for this center.")


class BasisSet(ProtoModel):
    """
    A quantum chemistry basis description.
    """

    schema_name: constr(strip_whitespace=True, regex="qcschema_basis") = "qcschema_basis"
    schema_version: int = 1

    name: str = Field(..., description="A standard basis name if available (e.g., 'cc-pVDZ').")
    description: Optional[str] = Field(None, description="A brief description of the basis set.")
    center_data: Dict[str, BasisCenter] = Field(..., description="A mapping of all types of centers available.")
    atom_map: List[str] = Field(
        ..., description="Mapping of all centers in the parent molecule to centers in `center_data`."
    )

    nbf: Optional[int] = Field(None, description="The number of basis functions.")

    @validator("atom_map")
    def _check_atom_map(cls, v, values):
        sv = set(v)
        missing = sv - values["center_data"].keys()

        if missing:
            raise ValueError(f"'atom_map' contains unknown keys to 'center_data': {missing}.")

        return v

    @validator("nbf", always=True)
    def _check_nbf(cls, v, values):

        # Bad construction, pass on errors
        try:
            nbf = cls._calculate_nbf(values["atom_map"], values["center_data"])
        except KeyError:
            return v

        if v is None:
            v = nbf
        else:
            if v != nbf:
                raise ValidationError("Calculated nbf does not match supplied nbf.")

        return v

    @classmethod
    def _calculate_nbf(cls, atom_map, center_data) -> int:
        """
        Number of basis functions in the basis set.

        Returns
        -------
        int
            The number of basis functions.
        """

        center_count = {}
        for k, center in center_data.items():
            center_count[k] = sum(x.nfunctions() for x in center.electron_shells)

        ret = 0
        for center in atom_map:
            ret += center_count[center]

        return ret
