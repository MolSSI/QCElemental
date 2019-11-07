from .autodocs import auto_gen_docs_on_demand, get_base_docs
from .gph_uno_bipartite import uno
from .importing import parse_version, safe_version, which, which_import
from .internal import provenance_stamp
from .itertools import unique_everseen

# from .mpl import plot_coord
from .misc import (
    compute_angle,
    compute_dihedral,
    compute_distance,
    distance_matrix,
    filter_comments,
    measure_coordinates,
    standardize_efp_angles_units,
    unnp,
    update_with_error,
)
from .np_blockwise import blockwise_contract, blockwise_expand
from .np_rand3drot import random_rotation_matrix
from .scipy_hungarian import linear_sum_assignment
from .serialization import (
    deserialize,
    json_dumps,
    json_loads,
    jsonext_dumps,
    jsonext_loads,
    msgpackext_dumps,
    msgpackext_loads,
    serialize,
)
