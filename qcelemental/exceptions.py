"""
Exceptions for QCElemental
"""


class NotAnElementError(Exception):
    """Error when element or nuclide can't be identified."""

    def __init__(self, atom):
        self.message = 'Atom identifier ({}) uninterpretable as atomic number, element symbol, or nuclide symbol'.format(
            atom)


class MoleculeFormatError(Exception):
    """Error called when a molparse.from_string contains unparsable lines."""

    def __init__(self, msg):
        self.message = 'Molecule line uninterpretable: {}'.format(msg)


class ValidationError(Exception):
    """Error called for problems with syntax input file. Prints
    error message *msg* to standard output stream.

    """

    def __init__(self, msg):
        self.message = 'Input Error: {}'.format(msg)


class FeatureNotImplemented(Exception):
    """Error called for functions defined but not yet implemented.
    Also for functions defined that will never be implemented.

    """

    def __init__(self, msg):
        self.message = 'Feature not implemented: {}'.format(msg)
