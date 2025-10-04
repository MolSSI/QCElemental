def check_convertible_version(ver: int, error: str):
    """Standardize version/error handling for v1 QCSchema."""

    if ver in [1, 2]:
        return True
    elif ver == -12:
        return "self"
    else:
        raise ValueError(f"QCSchema {error} version={ver} does not exist for conversion.")


qcschema_draft = "http://json-schema.org/draft-04/schema#"
