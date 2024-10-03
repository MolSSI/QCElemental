from warnings import warn

import qcelemental

_nonapi_file = "results"
_shim_classes_removed_version = "0.40.0"

warn(
    f"qcelemental.models.{_nonapi_file} should be accessed through qcelemental.models (or qcelemental.models.v1 or .v2 for fixed QCSchema version). The 'models.{_nonapi_file}' route will be removed as soon as v{_shim_classes_removed_version}",
    DeprecationWarning,
)

AtomicInput = qcelemental.models.v1.AtomicInput
AtomicResult = qcelemental.models.v1.AtomicResult
AtomicResultProperties = qcelemental.models.v1.AtomicResultProperties
AtomicResultProtocols = qcelemental.models.v1.AtomicResultProtocols
