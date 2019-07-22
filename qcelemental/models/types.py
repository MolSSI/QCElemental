import numpy as np

class TypedArray(np.ndarray):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        try:
            v = np.asarray(v, dtype=cls._dtype)
        except ValueError:
            raise ValueError("Could not cast {} to NumPy Array!".format(v))

        return v


class ArrayMeta(type):
    def __getitem__(self, t):
        return type('Array', (TypedArray, ), {'_dtype': t})


class Array(np.ndarray, metaclass=ArrayMeta):
    def __init__(self, **kwargs):
        super().__init__()
