from warnings import warn

import qcelemental

from .common_models import _qcsk_v2_default_v1_importpathschange

_nonapi_file = "basis"

warn(
    f"qcelemental.models.{_nonapi_file} should be accessed through qcelemental.models (or qcelemental.models.v1 or .v2 for fixed QCSchema version). The 'models.{_nonapi_file}' route will be removed as soon as v{_qcsk_v2_default_v1_importpathschange}.",
    DeprecationWarning,
)

BasisSet = qcelemental.models.v1.BasisSet
