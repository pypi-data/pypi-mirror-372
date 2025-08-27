# Importing pyarrow is necessary to load the runtime libraries


# start delvewheel patch
def _delvewheel_patch_1_11_1():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'jollyjack.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_11_1()
del _delvewheel_patch_1_11_1
# end delvewheel patch

import pyarrow
import pyarrow.parquet

from .package_metadata import (
    __version__,
    __dependencies__
)

try:
    from .jollyjack_cython import *
except ImportError as e:
    if any(x in str(e) for x in ['arrow', 'parquet']):
        pyarrow_req = next((r for r in __dependencies__ if r.startswith('pyarrow')), '')
        raise ImportError(f"This version of {__package__}={__version__} is built against {pyarrow_req}, please ensure you have it installed. Current pyarrow version is {pyarrow.__version__}. ({str(e)})") from None
    else:
        raise
