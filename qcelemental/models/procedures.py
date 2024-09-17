import qcelemental as qcel

_nonapi_file = "procedures"
_shim_classes_removed_version = "0.40.0"


class OptimizationInput(qcel.models.v1.OptimizationInput):
    """QC Geometry Optimization Input Schema.

    .. deprecated:: 0.32
       Use :py:func:`qcelemental.models.OptimizationInput` instead.

    """

    _model = __qualname__

    def __init__(self, *args, **kwargs):
        from warnings import warn

        warn(
            f"qcelemental.models.{_nonapi_file}.{self._model} should be accessed through qcelemental.models.{self._model} (or qcelemental.models.v1.{self._model} or v2 for QCSchema-version-fixed). The 'models.{_nonapi_file}' route will be removed as soon as v{_shim_classes_removed_version}",
            DeprecationWarning,
        )
        super().__init__(*args, **kwargs)


class OptimizationResult(qcel.models.v1.OptimizationResult):
    """QC Geometry Optimization Output Schema.

    .. deprecated:: 0.32
       Use :py:func:`qcelemental.models.OptimizationResult` instead.

    """

    _model = __qualname__

    def __init__(self, *args, **kwargs):
        from warnings import warn

        warn(
            f"qcelemental.models.{_nonapi_file}.{self._model} should be accessed through qcelemental.models.{self._model} (or qcelemental.models.v1.{self._model} or v2 for QCSchema-version-fixed). The 'models.{_nonapi_file}' route will be removed as soon as v{_shim_classes_removed_version}",
            DeprecationWarning,
        )
        super().__init__(*args, **kwargs)


class QCInputSpecification(qcel.models.v1.QCInputSpecification):
    """QC Single-Point Input for Geometry Optimization Schema.

    .. deprecated:: 0.32
       Use :py:func:`qcelemental.models.QCInputSpecification` instead.

    """

    _model = __qualname__

    def __init__(self, *args, **kwargs):
        from warnings import warn

        warn(
            f"qcelemental.models.{_nonapi_file}.{self._model} should be accessed through qcelemental.models.{self._model} (or qcelemental.models.v1.{self._model} or v2 for QCSchema-version-fixed). The 'models.{_nonapi_file}' route will be removed as soon as v{_shim_classes_removed_version}",
            DeprecationWarning,
        )
        super().__init__(*args, **kwargs)


class TDKeywords(qcel.models.v1.TDKeywords):
    """QC Torsion Drive Options Schema.

    .. deprecated:: 0.32
       Use :py:func:`qcelemental.models.TDKeywords` instead.

    """

    _model = __qualname__

    def __init__(self, *args, **kwargs):
        from warnings import warn

        warn(
            f"qcelemental.models.{_nonapi_file}.{self._model} should be accessed through qcelemental.models.{self._model} (or qcelemental.models.v1.{self._model} or v2 for QCSchema-version-fixed). The 'models.{_nonapi_file}' route will be removed as soon as v{_shim_classes_removed_version}",
            DeprecationWarning,
        )
        super().__init__(*args, **kwargs)


class TorsionDriveInput(qcel.models.v1.TorsionDriveInput):
    """QC Torsion Drive Input Schema.

    .. deprecated:: 0.32
       Use :py:func:`qcelemental.models.TorsionDriveInput` instead.

    """

    _model = __qualname__

    def __init__(self, *args, **kwargs):
        from warnings import warn

        warn(
            f"qcelemental.models.{_nonapi_file}.{self._model} should be accessed through qcelemental.models.{self._model} (or qcelemental.models.v1.{self._model} or v2 for QCSchema-version-fixed). The 'models.{_nonapi_file}' route will be removed as soon as v{_shim_classes_removed_version}",
            DeprecationWarning,
        )
        super().__init__(*args, **kwargs)


class TorsionDriveResult(qcel.models.v1.TorsionDriveResult):
    """QC Torsion Drive Output Schema.

    .. deprecated:: 0.32
       Use :py:func:`qcelemental.models.TorsionDriveResult` instead.

    """

    _model = __qualname__

    def __init__(self, *args, **kwargs):
        from warnings import warn

        warn(
            f"qcelemental.models.{_nonapi_file}.{self._model} should be accessed through qcelemental.models.{self._model} (or qcelemental.models.v1.{self._model} or v2 for QCSchema-version-fixed). The 'models.{_nonapi_file}' route will be removed as soon as v{_shim_classes_removed_version}",
            DeprecationWarning,
        )
        super().__init__(*args, **kwargs)


class OptimizationSpecification(qcel.models.v1.OptimizationSpecification):
    """QC Geometry Optimization Specification for Torsion Drive Schema.

    .. deprecated:: 0.32
       Use :py:func:`qcelemental.models.OptimizationSpecification` instead.

    """

    _model = __qualname__

    def __init__(self, *args, **kwargs):
        from warnings import warn

        warn(
            f"qcelemental.models.{_nonapi_file}.{self._model} should be accessed through qcelemental.models.{self._model} (or qcelemental.models.v1.{self._model} or v2 for QCSchema-version-fixed). The 'models.{_nonapi_file}' route will be removed as soon as v{_shim_classes_removed_version}",
            DeprecationWarning,
        )
        super().__init__(*args, **kwargs)
