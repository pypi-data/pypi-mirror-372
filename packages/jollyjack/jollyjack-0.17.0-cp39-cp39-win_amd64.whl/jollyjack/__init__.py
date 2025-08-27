# Importing pyarrow is necessary to load the runtime libraries


# start delvewheel patch
def _delvewheel_patch_1_11_1():
    import ctypes
    import os
    import platform
    import sys
    libs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'jollyjack.libs'))
    is_conda_cpython = platform.python_implementation() == 'CPython' and (hasattr(ctypes.pythonapi, 'Anaconda_GetVersion') or 'packaged by conda-forge' in sys.version)
    if sys.version_info[:2] >= (3, 8) and not is_conda_cpython or sys.version_info[:2] >= (3, 10):
        if os.path.isdir(libs_dir):
            os.add_dll_directory(libs_dir)
    else:
        load_order_filepath = os.path.join(libs_dir, '.load-order-jollyjack-0.17.0')
        if os.path.isfile(load_order_filepath):
            import ctypes.wintypes
            with open(os.path.join(libs_dir, '.load-order-jollyjack-0.17.0')) as file:
                load_order = file.read().split()
            kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
            kernel32.LoadLibraryExW.restype = ctypes.wintypes.HMODULE
            kernel32.LoadLibraryExW.argtypes = ctypes.wintypes.LPCWSTR, ctypes.wintypes.HANDLE, ctypes.wintypes.DWORD
            for lib in load_order:
                lib_path = os.path.join(os.path.join(libs_dir, lib))
                if os.path.isfile(lib_path) and not kernel32.LoadLibraryExW(lib_path, None, 8):
                    raise OSError('Error loading {}; {}'.format(lib, ctypes.FormatError(ctypes.get_last_error())))


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
