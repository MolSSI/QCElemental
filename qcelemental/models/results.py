import qcelemental as qcel

_nonapi_file = "results"
_shim_classes_removed_version = "0.40.0"


class AtomicResultProtocols(qcel.models.v1.AtomicResultProtocols):
    f"""QC Result Formatting Schema.

    .. deprecated:: 0.32
       Use :py:func:`qcelemental.models.AtomicResultProtocols` instead.

    """
    _model = __qualname__

    def __init__(self, *args, **kwargs):
        from warnings import warn

        warn(
            f"qcelemental.models.{_nonapi_file}.{self._model} should be accessed through qcelemental.models.{self._model} (or qcelemental.models.v1.{self._model} or v2 for QCSchema-version-fixed). The 'models.{_nonapi_file}' route will be removed as soon as v{_shim_classes_removed_version}",
            DeprecationWarning,
        )
        super().__init__(*args, **kwargs)
