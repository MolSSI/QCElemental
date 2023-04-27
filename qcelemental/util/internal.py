from typing import Dict

from qcelemental import __version__


def provenance_stamp(routine: str) -> Dict[str, str]:
    """Return dictionary satisfying QCSchema,
    https://github.com/MolSSI/QCSchema/blob/master/qcschema/dev/definitions.py#L23-L41
    with QCElemental's credentials for creator and version. The
    generating routine's name is passed in through `routine`.

    """
    return {"creator": "QCElemental", "version": __version__, "routine": routine}
