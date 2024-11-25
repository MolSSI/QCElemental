from warnings import warn

import qcelemental

_nonapi_file = "types"
from .common_models import _qcsk_v2_default_v1_importpathschange

warn(
    f"qcelemental.models.{_nonapi_file} should be accessed through qcelemental.models (or qcelemental.models.v1 or .v2 for fixed QCSchema version). The 'models.{_nonapi_file}' route will be removed as soon as v{_qcsk_v2_default_v1_importpathschange}.",
    DeprecationWarning,
)

Array = qcelemental.models.v1.Array
# ArrayMeta = qcelemental.models.v1.ArrayMeta
# TypedArray = qcelemental.models.v1.TypedArray
