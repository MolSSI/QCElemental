from warnings import warn

import qcelemental

_nonapi_file = "common_models"
_shim_classes_removed_version = "0.40.0"

warn(
    f"qcelemental.models.{_nonapi_file} should be accessed through qcelemental.models (or qcelemental.models.v1 or .v2 for fixed QCSchema version). The 'models.{_nonapi_file}' route will be removed as soon as v{_shim_classes_removed_version}",
    DeprecationWarning,
)

# ComputeError = qcelemental.models.v1.ComputeError
# DriverEnum = qcelemental.models.v1.DriverEnum
# FailedOperation = qcelemental.models.v1.FailedOperation
Model = qcelemental.models.v1.Model
# Provenance = qcelemental.models.v1.Provenance
