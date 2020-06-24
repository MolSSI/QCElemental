"""
Exceptions for QCElemental
"""


class NotAnElementError(Exception):
    """Error when element or nuclide can't be identified."""

    def __init__(self, atom, strict=False):
        if strict:
            msg = "atomic number or element"
        else:
            msg = "atomic number, element symbol, or nuclide symbol"
        self.message = f"Atom identifier ({atom}) uninterpretable as {msg}"


class DataUnavailableError(Exception):
    """Error when dataset incomplete and otherwise valid query can't be fulfilled."""

    def __init__(self, dataset, atom):
        self.message = "Dataset ({}) missing value for key ({})".format(dataset, atom)


class MoleculeFormatError(Exception):
    """Error called when a molparse.from_string contains unparsable lines."""

    def __init__(self, msg):
        self.message = "Molecule line uninterpretable: {}".format(msg)


class ValidationError(Exception):
    """Error called for problems with syntax input file. Prints
    error message *msg* to standard output stream.

    """

    def __init__(self, msg):
        self.message = "Input Error: {}".format(msg)


class ChoicesError(Exception):
    """Error called for problems with syntax input file. Prints
    error message *msg* to standard output stream. Also attaches
    `choices` dictionary with options to proceed.

    """

    def __init__(self, msg, choices=None):
        self.message = "Input Error: {}".format(msg)
        self.choices = {} if choices is None else choices
