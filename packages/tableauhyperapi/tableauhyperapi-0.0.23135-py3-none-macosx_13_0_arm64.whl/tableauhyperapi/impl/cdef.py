"""
This module defines the `ffi` object which is then used to load the native tableautableauhyperapi library or to generate
cdef_compiled.py with the precompiled cffi declarations.
"""

import cffi

try:
    # When inside tableautableauhyperapi package, relative path works. But when generating cdef_compiled.py, we import
    # cdef.py as a standalone module, in which case lib_h is also a standalone module next to it.
    from .lib_h import LIB_H
except ImportError:
    # noinspection PyUnresolvedReferences
    from lib_h import LIB_H

ffi = cffi.FFI()
ffi.cdef(LIB_H)
# ffi does not support unions, so we fake hyper_error_field_value
ffi.cdef("""
    typedef struct {
        int discriminator;
        void *value;
    } py_hyper_error_field_value;
    hyper_error_t* hyper_error_get_field(
        const hyper_error_t* error, hyper_error_field_key key, py_hyper_error_field_value* value);
    hyper_error_t* hyper_error_set_field(
        hyper_error_t* error, hyper_error_field_key field, py_hyper_error_field_value value);
""")
# define a struct with correct layout for INTERVAL
ffi.cdef("""
    typedef struct {
        int64_t microseconds;
        int32_t days;
        int32_t months;
    } py_interval;
""")
