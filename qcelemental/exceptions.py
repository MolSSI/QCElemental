"""
Exceptions for QCElemental
"""


class NotAnElementError(Exception):
    """Error when element or nuclide can't be identified."""

    def __init__(self, atom):
        self.message = 'Atom identifier ({}) uninterpretable as atomic number, element symbol, or nuclide symbol'.format(
            atom)
