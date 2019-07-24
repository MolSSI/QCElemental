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
    def __getitem__(self, dtype):
        return type('Array', (TypedArray, ), {'_dtype': dtype})


class Array(np.ndarray, metaclass=ArrayMeta):
    pass
