import os
import sys

from pathlib import Path

MICROSECONDS_PER_SECOND = 1_000_000
MICROSECONDS_PER_DAY = 24 * 60 * 60 * MICROSECONDS_PER_SECOND

PLAT_WINDOWS = 'win32'
PLAT_LINUX = 'linux'
PLAT_OSX = 'osx'

if sys.platform.startswith(PLAT_WINDOWS):
    PLATFORM = PLAT_WINDOWS
elif sys.platform.startswith(PLAT_LINUX):
    PLATFORM = PLAT_LINUX
elif sys.platform.startswith('darwin'):
    PLATFORM = PLAT_OSX
else:
    raise RuntimeError('Unknown platform {}'.format(sys.platform))


def _get_packaged_native_bin_dir() -> Path:
    return Path(os.path.dirname(__file__)).parent / 'bin'


def _get_tableauhyperapi_lib_filename():
    if PLATFORM == PLAT_WINDOWS:
        return 'tableauhyperapi.dll'
    elif PLATFORM == PLAT_LINUX:
        return 'libtableauhyperapi.so'
    elif PLATFORM == PLAT_OSX:
        return 'libtableauhyperapi.dylib'
    else:
        raise RuntimeError('Unknown platform {}'.format(PLATFORM))


def find_hyper_api_library() -> Path:
    def get_directories():
        # We expect hyper-api binary to be inside tableauhyperapi/bin, but that can be overridden, so for instance
        # one may run code directly from the source folder.
        env_var_value = os.environ.get('HYPER_API_PATH')
        if env_var_value:
            yield Path(env_var_value)

        yield _get_packaged_native_bin_dir()

    lib_name = _get_tableauhyperapi_lib_filename()
    for dir in get_directories():
        lib = dir / lib_name
        if lib.exists():
            return lib

    # noinspection PyUnboundLocalVariable
    raise RuntimeError(f'{lib_name} library not found. Could not find the Hyper API binary directory, '
                       f'tried {dir}.')


def check_precondition(condition, error_message, error_class=None):
    if not condition:
        if not error_class:
            error_class = ValueError
        raise error_class(error_message)


def less_than_for_pairs_first_optional(pair1, pair2):
    # name with fewer components compares less
    if not pair1[0]:
        if pair2[0]:
            return True
        else:
            return pair1[1] < pair2[1]
    elif not pair2[0]:
        return False

    return pair1 < pair2


def c_modulus(x, y):
    """ C-style modulus operation (different treatment of negative numbers) """
    return x % y if x >= 0 else x % (-y)


def c_divide(x, y):
    """ C-style division operation (different treatment of negative numbers) """
    return x // y if x >= 0 else -(-x // y)
