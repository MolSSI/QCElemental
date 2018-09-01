class NotAnElementError(Exception):
    def __init__(self, atom):
        self.message = 'Atom identifier ({}) uninterpretable as atomic number, element symbol, or nuclide symbol'.format(
            atom)
