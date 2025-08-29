from pathlib import Path
import warnings

from .util import find_hyper_api_library


try:
    # If the compiled version is available, use it. Otherwise use the slower source version.
    from .cdef_compiled import ffi
except ImportError as ex:
    # Presence of README-DEV.md indicates that we are running from the source directory in which
    # case cdef_compiled is not supposed to be there, don't warn in that case.
    if not (Path(__file__).parent.parent.parent / 'README-DEV.md').exists():
        warnings.warn(f'Failed to import cdef_compiled module, importing tableauhyperapi will be slow. Please report this to '
                      f'Tableau. Error message was: {ex}')
    from .cdef import ffi

lib = ffi.dlopen(str(find_hyper_api_library()))
