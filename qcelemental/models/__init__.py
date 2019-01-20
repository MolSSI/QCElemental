try:
    import pydantic
except ImportError:
    raise ImportError("""Python module pydantic not found. Solve by installing it: `conda install pydantic -c conda-forge` or `pip install pydantic`""")

from .objects import Molecule
