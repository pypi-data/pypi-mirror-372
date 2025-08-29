from typing import Optional

from ..hyperexception import HyperException, ContextId

from .dll import ffi
from . import hapi


class InteropUtil:
    """ Convert between python str and native API's UTF8-encoded char* """

    @staticmethod
    def char_p_to_string(p):
        if p == ffi.NULL:
            return None
        else:
            return ffi.string(p).decode()

    @staticmethod
    def string_to_char_p(s: str):
        if s is None:
            return ffi.NULL
        else:
            return ffi.from_buffer('char[]', s.encode())

    @staticmethod
    def convert_and_free_string_list(pp):
        p = ffi.gc(pp[0], hapi.hyper_string_list_destroy)
        if p == ffi.NULL:
            return None

        return [InteropUtil.char_p_to_string(hapi.hyper_string_list_at(p, i))
                for i in range(hapi.hyper_string_list_size(p))]


class ConstError:
    """ Wrapper around native hyper_error_t*. This class works with any hyper_error_t* pointer and does not manage
    its lifetime. Error subclass is the one that owns hyper_error_t instances. """

    def __init__(self, cdata):
        self._cdata = cdata

    def get_string_field(self, field):
        return InteropUtil.char_p_to_string(ffi.cast('char*', self.get_pointer_field(field)))

    def get_int_field(self, field):
        p = self.get_pointer_field(field)
        if p == ffi.NULL:
            return 0
        # get lower four bytes
        pui = ffi.new('unsigned*', int(ffi.cast('uintptr_t', p)) & 0xFFFFFFFF)
        return ffi.cast('int*', pui)[0]

    def get_pointer_field(self, field):
        value = ffi.new('py_hyper_error_field_value*')
        if hapi.hyper_error_get_field(self._cdata, field, value) != ffi.NULL:
            raise RuntimeError('hyper_error_get_field returned an error')
        return value.value

    def to_exception(self) -> HyperException:
        # Construct the `HyperException`, mapping empty string fields to `None`.
        ex = HyperException(
            context_id=ContextId(self.get_int_field(hapi.HYPER_ERROR_FIELD_CONTEXT_ID)),
            main_message=self.get_string_field(hapi.HYPER_ERROR_FIELD_MESSAGE) or None,
            hint=self.get_string_field(hapi.HYPER_ERROR_FIELD_HINT_MESSAGE) or None)

        # Set the cause, if available.
        causep = self.get_pointer_field(hapi.HYPER_ERROR_FIELD_CAUSE)
        if causep != ffi.NULL:
            errp = ConstError(causep)
            ex.__cause__ = errp.to_exception()

        return ex


class Error(ConstError):
    """ Wrapper around hyper_error_t which takes ownership of it. Native object is destroyed with the Python object. """

    def __init__(self, cdata):
        """ Wrap a new hyper_error_t object. It takes ownership of it, use ConstError for hyper_error_t instances
        not owned by us. """
        cdata = ffi.gc(cdata, hapi.hyper_error_destroy)
        super(Error, self).__init__(cdata)

    @staticmethod
    def create(context_id):
        return Error(hapi.hyper_error_create(context_id.value))

    @staticmethod
    def check(p):
        """
        Check whether the error is non-NULL and raise the corresponding exception if so. It frees the error passed to
        it. This is to be used with C functions which return hyper_error_t*:

            Error.check(hapi.hyper_do_something(...))
        """
        if p != ffi.NULL:
            # this will free the error when it goes out of scope
            errp = Error(p)
            raise errp.to_exception()

    @staticmethod
    def set_string_field_static(p, field, value: str):
        Error.check(hapi.hyper_error_set_field(p, field,
                                               {'discriminator': 1,
                                                'value': ffi.from_buffer(value.encode())}))

    def set_string_field(self, field, value: str):
        Error.set_string_field_static(self._cdata, field, value)

    def set_cause(self, errp):
        Error.check(hapi.hyper_error_set_field(self._cdata, hapi.HYPER_ERROR_FIELD_CAUSE,
                                               {'discriminator': 2, 'value': errp}))


class Parameters:
    """ Wrapper for hyper_parameters_t. """

    def __init__(self, cdata):
        self.__cdata = ffi.gc(cdata, hapi.hyper_parameters_destroy)

    def set_value(self, key: str, value: str):
        Error.check(hapi.hyper_parameters_set(self.__cdata, key.encode(), value.encode()))

    @property
    def cdata(self):
        return self.__cdata

    @staticmethod
    def create_instance_parameters():
        pp = ffi.new('hyper_parameters_t**')
        Error.check(hapi.hyper_create_instance_parameters(pp, True))
        return Parameters(pp[0])

    @staticmethod
    def create_connection_parameters():
        pp = ffi.new('hyper_parameters_t**')
        Error.check(hapi.hyper_create_connection_parameters(ffi.NULL, pp))
        return Parameters(pp[0])


class ConstNativeTableDefinition:
    """ Wrapper for hyper_table_definition_t. This class does not manage lifetime of the native object.
    NativeTableDefinition subclass is the one which owns hyper_table_definition_t objects. """

    def __init__(self, cdata):
        self._cdata = cdata

    @property
    def cdata(self):
        return self._cdata

    @property
    def database_name(self):
        return InteropUtil.char_p_to_string(hapi.hyper_table_definition_database_name(self._cdata))

    @property
    def schema_name(self):
        return InteropUtil.char_p_to_string(hapi.hyper_table_definition_schema_name(self._cdata))

    @property
    def table_name(self):
        return InteropUtil.char_p_to_string(hapi.hyper_table_definition_table_name(self._cdata))

    @property
    def persistence(self):
        return hapi.hyper_table_definition_table_persistence(self._cdata)

    @property
    def column_count(self):
        return hapi.hyper_table_definition_column_count(self._cdata)

    def column_name(self, column_index):
        return InteropUtil.char_p_to_string(hapi.hyper_table_definition_column_name(self._cdata, column_index))

    def column_type_tag(self, column_index):
        return hapi.hyper_table_definition_column_type_tag(self._cdata, column_index)

    def column_type_oid(self, column_index):
        return hapi.hyper_table_definition_column_type_oid(self._cdata, column_index)

    def column_type_modifier(self, column_index):
        return hapi.hyper_table_definition_column_type_modifier(self._cdata, column_index)

    def column_is_nullable(self, column_index):
        return hapi.hyper_table_definition_column_is_nullable(self._cdata, column_index)

    def column_collation(self, column_index):
        return InteropUtil.char_p_to_string(hapi.hyper_table_definition_column_collation(self._cdata, column_index))


class NativeTableDefinition(ConstNativeTableDefinition):
    """ Wrapper for hyper_table_definition_t which takes ownership of the object passed to it.
    ConstNativeTableDefinition should be used for const hyper_table_definition_t* not owned by us. """

    def __init__(self, cdata):
        cdata = ffi.gc(cdata, hapi.hyper_destroy_table_definition)
        super(NativeTableDefinition, self).__init__(cdata)

    @staticmethod
    def create(database_name: Optional[str],
               schema_name: Optional[str],
               table_name: str,
               persistence: int) -> 'NativeTableDefinition':
        p = hapi.hyper_create_table_definition(
            InteropUtil.string_to_char_p(database_name),
            InteropUtil.string_to_char_p(schema_name),
            InteropUtil.string_to_char_p(table_name),
            persistence, False)

        if p == ffi.NULL:
            raise MemoryError()
        return NativeTableDefinition(p)

    def add_column(self, name: str, type_tag: int, modifier: int, collation: str, nullable: bool):
        Error.check(hapi.hyper_table_definition_add_column(self._cdata,
                                                           InteropUtil.string_to_char_p(name),
                                                           type_tag,
                                                           modifier,
                                                           InteropUtil.string_to_char_p(collation),
                                                           nullable))


def invoke_native_string_transform_function(func, string: str) -> str:
    utf8_string = string.encode()
    input_buf = ffi.from_buffer(utf8_string)
    required_size = func(ffi.NULL, 0, input_buf, len(utf8_string))
    assert required_size > 0
    output_buf = bytearray(required_size)
    func(ffi.from_buffer(output_buf, require_writable=True), len(output_buf), input_buf, len(utf8_string))
    return output_buf.decode('utf-8')
