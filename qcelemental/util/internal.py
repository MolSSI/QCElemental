from .._version import get_versions


def provenance_stamp(routine):
    """Return dictionary satisfying QCSchema,
    https://github.com/MolSSI/QCSchema/blob/master/qcschema/dev/definitions.py#L23-L41
    with QCElemental's credentials for creator and version. The
    generating routine's name is passed in through `routine`.

    """
    return {'creator': 'QCElemental', 'version': get_versions()['version'], 'routine': routine}
