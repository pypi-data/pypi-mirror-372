"""
A small package to aid in the use of the chaining techniques taught by Structural Python
"""

__version__ = "0.4.1"


from .io import (load_json, dump_json)
from .envelope import (
    envelope_tree,
    max,
    min,
    absmax,
    absmin
)
from .tree import (
    compare_tree_values,
    extract_keys,
    trim_branches,
    retrieve_leaves,
    filter_keys,
    merge_trees
)
from . import tables