from warnings import warn

import qcelemental

_qcsk_v2_available_v1_nochange = "0.50.0"
_qcsk_v2_default_v1_importpathschange = "0.70.0"
_qcsk_v2_nochange_v1_dropped = "1.0.0"

_nonapi_file = "common_models"

warn(
    f"qcelemental.models.{_nonapi_file} should be accessed through qcelemental.models (or qcelemental.models.v1 or .v2 for fixed QCSchema version). The 'models.{_nonapi_file}' route will be removed as soon as v{_qcsk_v2_default_v1_importpathschange}.",
    DeprecationWarning,
)

ComputeError = qcelemental.models.v1.ComputeError
DriverEnum = qcelemental.models.v1.DriverEnum
FailedOperation = qcelemental.models.v1.FailedOperation
Model = qcelemental.models.v1.Model
Provenance = qcelemental.models.v1.Provenance
