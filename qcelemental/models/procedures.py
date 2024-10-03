from warnings import warn

import qcelemental

_nonapi_file = "procedures"
_shim_classes_removed_version = "0.40.0"

warn(
    f"qcelemental.models.{_nonapi_file} should be accessed through qcelemental.models (or qcelemental.models.v1 or .v2 for fixed QCSchema version). The 'models.{_nonapi_file}' route will be removed as soon as v{_shim_classes_removed_version}",
    DeprecationWarning,
)

OptimizationInput = qcelemental.models.v1.OptimizationInput
OptimizationResult = qcelemental.models.v1.OptimizationResult
QCInputSpecification = qcelemental.models.v1.QCInputSpecification

TDKeywords = qcelemental.models.v1.TDKeywords
TorsionDriveInput = qcelemental.models.v1.TorsionDriveInput
TorsionDriveResult = qcelemental.models.v1.TorsionDriveResult
OptimizationSpecification = qcelemental.models.v1.OptimizationSpecification
