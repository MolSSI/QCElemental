from warnings import warn

import qcelemental

_nonapi_file = "procedures"
from .common_models import _qcsk_v2_default_v1_importpathschange

warn(
    f"qcelemental.models.{_nonapi_file} should be accessed through qcelemental.models (or qcelemental.models.v1 or .v2 for fixed QCSchema version). The 'models.{_nonapi_file}' route will be removed as soon as v{_qcsk_v2_default_v1_importpathschange}.",
    FutureWarning,
)

OptimizationInput = qcelemental.models.v1.OptimizationInput
OptimizationResult = qcelemental.models.v1.OptimizationResult
OptimizationProtocols = qcelemental.models.v1.OptimizationProtocols
QCInputSpecification = qcelemental.models.v1.QCInputSpecification

TDKeywords = qcelemental.models.v1.TDKeywords
TorsionDriveInput = qcelemental.models.v1.TorsionDriveInput
TorsionDriveResult = qcelemental.models.v1.TorsionDriveResult
OptimizationSpecification = qcelemental.models.v1.OptimizationSpecification
TrajectoryProtocolEnum = qcelemental.models.v1.TrajectoryProtocolEnum

# needed by QCFractal
Model = qcelemental.models.v1.Model
