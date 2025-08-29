import datetime
import decimal
import warnings

from typing import Optional, List

from . import connection  # noqa F401
from .date import Date
from .interval import Interval
from .resultschema import ResultSchema
from .sqltype import NullableValue
from .sqltype import TypeTag
from .timestamp import Timestamp
from .warning import UnclosedObjectWarning
from .impl import hapi
from .impl.converter import Converter
from .impl.dll import ffi, lib
from .impl.dllutil import ConstNativeTableDefinition, Error
from .impl.schemaconverter import SchemaConverter


class Result:
    """
    An object which is used to read query results.

    A ``Result`` implements the iterator protocol, so it can be used as follows:

    .. testsetup:: Result.__init__

        from tableauhyperapi import *
        def setup():
            hyper = HyperProcess(Telemetry.SEND_USAGE_DATA_TO_TABLEAU, 'myapp')
            connection = Connection(hyper.endpoint, 'mydb.hyper', CreateMode.CREATE_AND_REPLACE)
            table_def = TableDefinition('foo', [
                TableDefinition.Column('text', SqlType.text()),
                TableDefinition.Column('int', SqlType.int()),
            ])
            connection.catalog.create_table(table_def)
            with Inserter(connection, 'foo') as inserter:
                inserter.add_row(['a', 1])
                inserter.add_row(['b', 2])
                inserter.execute()
            return hyper, connection
        hyper, connection = setup()

    .. testcode:: Result.__init__

        with connection.execute_query('SELECT * FROM foo') as result:
            for row in result:
                print(row)

    .. testoutput:: Result.__init__

        ['a', 1]
        ['b', 2]

    This is equivalent to the following:

    .. testcode:: Result.__init__

        with connection.execute_query('SELECT * FROM foo') as result:
            while result.next_row():
                row = result.get_values()
                print(row)

    .. testoutput:: Result.__init__

        ['a', 1]
        ['b', 2]

    Alternatively, one can use get_value() to retrieve individual row values:

    .. testcode:: Result.__init__

        with connection.execute_query('SELECT * FROM foo') as result:
            while result.next_row():
                value = result.get_value(0)
                print(value)

    .. testoutput:: Result.__init__

        a
        b

    .. testcleanup:: Result.__init__

        connection.close()
        hyper.close()
        import os
        os.remove('mydb.hyper')

    NULL database values are represented by ``None``. See :any:`TypeTag` documentation for how Hyper data
    types map to Python types.

    The ``Result`` constructor may not be used directly, use :any:`Connection.execute_query`.
    """

    # There is a ton of repetition here, for performance. Do not refactor without profiling.

    # noinspection PyShadowingNames
    def __init__(self, text_as_bytes: bool, connection: 'connection.Connection', result_cdata):
        # Private method, do not use directly. See the documentation above.

        self.__cdata = ffi.gc(result_cdata, hapi.hyper_close_rowset)
        self.__connection = connection
        # Reference lib for correct gc order
        self.__lib_ref = lib

        self.__inline_things()

        self.__current_chunk = None
        self.__read_value_functions = None

        tdp = ConstNativeTableDefinition(hapi.hyper_rowset_get_table_definition(self.__cdata))
        self.__schema = SchemaConverter.result_schema_from_native(tdp)

        self.__column_count = len(self.__schema.columns)
        self.__range_column_count = range(self.__column_count)

        self.__numeric_multipliers = [decimal.Decimal(10) ** col.type.scale
                                      if (col.type.tag == TypeTag.NUMERIC and col.type.scale <= 18)
                                      else 0 for col in self.__schema.columns]

        # total number of values in the chunk = number of rows * number of columns
        self.__current_chunk_cells = 0
        self.__current_chunk_rows = 0
        # cell offset of the current row, index in __current_chunk_values, __current_chunk_sizes,
        self.__current_row_cell = 0
        self.__current_row = 0
        # array of pointers to values
        self.__current_chunk_values = None
        # array of value sizes
        self.__current_chunk_sizes = None

        self.next_row = self.__next_row1

        read_text = self.__read_bytes if text_as_bytes else self.__read_text

        # (self, column_index) -> value
        read_value_functions = {
            TypeTag.UNSUPPORTED: self.__read_bytes,
            TypeTag.BOOL: self.__read_bool,
            TypeTag.BIG_INT: self.__read_big_int,
            TypeTag.SMALL_INT: self.__read_small_int,
            TypeTag.INT: self.__read_int,
            TypeTag.NUMERIC: self.__read_numeric,
            TypeTag.FLOAT: self.__read_float,
            TypeTag.DOUBLE: self.__read_double,
            TypeTag.OID: self.__read_uint32,
            TypeTag.BYTES: self.__read_bytes,
            TypeTag.TEXT: read_text,
            TypeTag.VARCHAR: read_text,
            TypeTag.CHAR: read_text,
            TypeTag.JSON: read_text,
            TypeTag.DATE: self.__read_date,
            TypeTag.INTERVAL: self.__read_interval,
            TypeTag.TIME: self.__read_time,
            TypeTag.TIMESTAMP: self.__read_timestamp,
            TypeTag.TIMESTAMP_TZ: self.__read_timestamp_tz,
            TypeTag.TABGEOGRAPHY: self.__read_bytes,
            # Deprecated alias for TABGEOGRAPHY, will be removed as part of W-17701666.
            TypeTag.GEOGRAPHY: self.__read_bytes,
        }

        def get_read_value_function(col: ResultSchema.Column):
            if (col.type.tag == TypeTag.NUMERIC) and (col.type.precision > 18):
                return self.__read_big_numeric
            else:
                return read_value_functions[col.type.tag]

        self.__read_value_functions = [get_read_value_function(col) for col in self.__schema.columns]

        self.__row_template = [None] * self.__column_count

        # Decimal context used for 128-bit numeric transformations
        traps = [decimal.Overflow, decimal.DivisionByZero, decimal.InvalidOperation, decimal.Inexact]
        self._big_numeric_decimal_context = decimal.Context(prec=38, traps=traps)

    # We call a ton of methods when reading values, so inlining them speeds up things significantly
    # (like tens of percents significantly)
    def __inline_things(self):
        self.__ffi = ffi

        self.__uint32_ptr_t = self.__ffi.typeof('uint32_t*')
        self.__uint64_ptr_t = self.__ffi.typeof('uint64_t*')
        self.__float_ptr_t = self.__ffi.typeof('float*')
        self.__double_ptr_t = self.__ffi.typeof('double*')
        self.__py_interval_ptr_t = self.__ffi.typeof('py_interval*')
        self.__ffi_null = self.__ffi.NULL
        self.__ffi_cast = self.__ffi.cast
        self.__ffi_buffer = self.__ffi.buffer

        self.__hyper_read_int8 = hapi.hyper_read_int8
        self.__hyper_read_int16 = hapi.hyper_read_int16
        self.__hyper_read_int32 = hapi.hyper_read_int32
        self.__hyper_read_int64 = hapi.hyper_read_int64

    # need to get the chunk first
    def __next_row1(self):
        self.__destroy_chunk()

        while True:
            chunk_cdata = self.__ffi.new('hyper_rowset_chunk_t**')
            Error.check(hapi.hyper_rowset_get_next_chunk(self.__cdata, chunk_cdata))
            if chunk_cdata[0] == self.__ffi_null:
                # no more chunks
                self.close()
                return False
            chunk = self.__ffi.gc(chunk_cdata[0], hapi.hyper_destroy_rowset_chunk)

            p_num_cols = self.__ffi.new('size_t*')
            p_num_rows = self.__ffi.new('size_t*')
            p_values = self.__ffi.new('uint8_t***')
            p_sizes = self.__ffi.new('size_t**')
            hapi.hyper_rowset_chunk_field_values(chunk, p_num_cols, p_num_rows, p_values, p_sizes)

            row_count = p_num_rows[0]
            assert p_num_cols[0] == self.__column_count
            if row_count:
                self.__current_chunk = chunk
                self.__current_chunk_rows = row_count
                self.__current_chunk_cells = p_num_cols[0] * row_count
                self.__current_chunk_values = p_values[0]
                self.__current_chunk_sizes = p_sizes[0]
                break

        self.next_row = self.__next_row2
        return True

    # got a chunk, read rows from it
    def __next_row2(self):
        self.__current_row_cell += self.__column_count
        self.__current_row += 1
        if self.__current_row >= self.__current_chunk_rows:
            return self.__next_row1()
        return True

    def __destroy_chunk(self):
        if self.__current_chunk is not None:
            self.__ffi.release(self.__current_chunk)
            self.__current_chunk = None

        self.__current_chunk_cells = 0
        self.__current_row_cell = 0
        self.__current_row = 0
        self.__current_chunk_values = None
        self.__current_chunk_sizes = None

    @staticmethod
    def __raise_result_is_closed(*args, **kwargs):
        raise RuntimeError('Result has been closed')

    @property
    def is_open(self) -> bool:
        """
        Returns ``True`` if the result has not been closed yet. Note that reading all rows of data automatically
        closes the result object.
        """
        return self.__cdata is not None

    def close(self):
        """
        Closes the result. Normally this is called automatically by ``with`` statement. Also, result is automatically
        closed when all rows have been read from it.
        """
        self.__destroy_chunk()
        if self.__cdata is not None:
            ffi.release(self.__cdata)
            self.__cdata = None
        self.__connection = None
        # leave self.__schema be, this is important when the query returned zero columns
        # make get_value() raise an exception
        if self.__read_value_functions is not None:
            self.__read_value_functions = [self.__raise_result_is_closed for _ in self.__read_value_functions]
        # next_row() returns False after closing
        self.next_row = lambda: False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __iter__(self):
        while self.next_row():
            yield self.get_values()

    @property
    def schema(self) -> ResultSchema:
        """ Gets the result schema. """
        return self.__schema

    @property
    def affected_row_count(self) -> Optional[int]:
        """
        Gets the affected row count, if the statement had any.
        """
        # TFSID 931205: what about SELECT?
        count = hapi.hyper_rowset_get_affected_row_count(self.__cdata)
        return count if count >= 0 else None

    @property
    def connection(self) -> 'connection.Connection':
        """ Gets the underlying connection. """
        return self.__connection

    def next_row(self) -> bool:
        """
        Fetches the next row.

        :return: ``True`` if there is data to read, ``False`` otherwise.

        Note: if this method returns ``False``, then the result is closed.
        """
        # actual implementation is set by init, close, and the real iteration methods
        raise RuntimeError()

    def get_value(self, column_index: int) -> object:
        """
        Gets the value at the given column index in the current row. This MUST only be called if :any:`next_row()`
        returned ``True``.

        :param column_index: the column index.
        :return: the value as the corresponding python object if it is non-NULL, or ``None`` otherwise. See
            :any:`TypeTag` for how Hyper data types map to Python types.
        """
        return self.__read_value_functions[column_index](column_index)

    def get_values(self) -> List[NullableValue]:
        """
        Gets the values in the current row. This MUST only be called if :any:`next_row()` returned ``True``.

        :return: the row values as a list of objects. NULL is represented by ``None``, see :any:`TypeTag`
            for how Hyper data types map to Python types.
        """
        row = list(self.__row_template)
        for i in self.__range_column_count:
            row[i] = self.get_value(i)
        return row

    def __read_bool(self, column_index: int) -> Optional[bool]:
        cell = self.__current_row_cell + column_index
        if not self.__current_chunk_values[cell]:
            return None
        value = self.__current_chunk_values[cell]
        return self.__hyper_read_int8(value) != 0

    def __read_small_int(self, column_index: int) -> Optional[int]:
        cell = self.__current_row_cell + column_index
        if not self.__current_chunk_values[cell]:
            return None
        value = self.__current_chunk_values[cell]
        return self.__hyper_read_int16(value)

    def __read_int(self, column_index: int) -> Optional[int]:
        cell = self.__current_row_cell + column_index
        if not self.__current_chunk_values[cell]:
            return None
        value = self.__current_chunk_values[cell]
        return self.__hyper_read_int32(value)

    def __read_uint32(self, column_index: int) -> Optional[int]:
        cell = self.__current_row_cell + column_index
        if not self.__current_chunk_values[cell]:
            return None
        value = self.__current_chunk_values[cell]
        return self.__ffi_cast(self.__uint32_ptr_t, value)[0]

    def __read_big_int(self, column_index: int) -> Optional[int]:
        cell = self.__current_row_cell + column_index
        if not self.__current_chunk_values[cell]:
            return None
        value = self.__current_chunk_values[cell]
        return self.__hyper_read_int64(value)

    def __read_uint64(self, column_index: int) -> Optional[int]:
        cell = self.__current_row_cell + column_index
        if not self.__current_chunk_values[cell]:
            return None
        value = self.__current_chunk_values[cell]
        return self.__ffi_cast(self.__uint64_ptr_t, value)[0]

    def __read_float(self, column_index: int) -> Optional[float]:
        cell = self.__current_row_cell + column_index
        if not self.__current_chunk_values[cell]:
            return None
        value = self.__current_chunk_values[cell]
        return self.__ffi_cast(self.__float_ptr_t, value)[0]

    def __read_double(self, column_index: int) -> Optional[float]:
        cell = self.__current_row_cell + column_index
        if not self.__current_chunk_values[cell]:
            return None
        value = self.__current_chunk_values[cell]
        return self.__ffi_cast(self.__double_ptr_t, value)[0]

    def __read_bytes(self, column_index: int) -> Optional[bytes]:
        cell = self.__current_row_cell + column_index
        if not self.__current_chunk_values[cell]:
            return None
        value = self.__current_chunk_values[cell]
        size = self.__current_chunk_sizes[cell]
        return bytes(self.__ffi_buffer(value, size))

    def __read_text(self, column_index: int) -> Optional[str]:
        cell = self.__current_row_cell + column_index
        if not self.__current_chunk_values[cell]:
            return None
        value = self.__current_chunk_values[cell]
        size = self.__current_chunk_sizes[cell]
        return str(self.__ffi_buffer(value, size), 'utf-8')

    def __read_date(self, column_index: int) -> Optional[Date]:
        v = self.__read_uint32(column_index)
        if v is None:
            return None
        return Date._from_hyper(v)

    def __read_time(self, column_index: int) -> Optional[datetime.time]:
        v = self.__read_uint64(column_index)
        if v is None:
            return None
        return Converter.time_from_hyper(v)

    def __read_timestamp(self, column_index: int) -> Optional[Timestamp]:
        v = self.__read_uint64(column_index)
        if v is None:
            return None
        return Timestamp(v)

    def __read_timestamp_tz(self, column_index: int) -> Optional[Timestamp]:
        v = self.__read_uint64(column_index)
        if v is None:
            return None
        return Timestamp(v, tzinfo=datetime.timezone.utc)

    def __read_interval(self, column_index: int) -> Optional[Interval]:
        cell = self.__current_row_cell + column_index
        if not self.__current_chunk_values[cell]:
            return None
        value = self.__current_chunk_values[cell]
        p = self.__ffi_cast(self.__py_interval_ptr_t, value)
        return Interval(p.months, p.days, p.microseconds)

    def __read_numeric(self, column_index: int) -> Optional[decimal.Decimal]:
        v = self.__read_big_int(column_index)
        if v is None:
            return None
        return decimal.Decimal(v) / self.__numeric_multipliers[column_index]

    def __read_big_numeric(self, column_index: int) -> Optional[decimal.Decimal]:
        v = self.__read_bytes(column_index)
        if v is None:
            return None
        scale = self.__schema.columns[column_index].type.scale
        d = decimal.Decimal(int.from_bytes(v, 'little', signed=True))
        return d.scaleb(-scale, self._big_numeric_decimal_context)

    def __read_char1_as_text(self, column_index: int) -> Optional[str]:
        v = self.__read_int(column_index)
        if v is None:
            return None
        return chr(v)

    def __read_char1_as_bytes(self, column_index: int) -> Optional[bytes]:
        v = self.__read_int(column_index)
        if v is None:
            return None
        return chr(v).encode()

    def __del__(self):
        if self.__cdata is not None:
            warnings.warn('Result has not been closed. Use Result object in a with statement or call its close() '
                          'method when done.', UnclosedObjectWarning)
            # do nothing, self.__cdata is a gc'ed pointer

    def __repr__(self):
        parts = []

        if self.is_open:
            parts = ['state: open']
            affected = self.affected_row_count
            if affected is not None:
                parts.append(f'affected_row_count: {affected}')
        else:
            parts = ['state: closed']

        cols = self.schema.columns
        if cols:
            if len(cols) > 6:
                colnames = [str(x.name) for x in cols[:3]] + ['...'] + [str(x.name) for x in cols[-2:]]
            else:
                colnames = [str(x.name) for x in self.schema.columns]

            colnames = ', '.join(colnames)
            parts.append(f'columns: [{colnames}]')

        details = '; '.join(parts)

        return f'<{self.__class__.__name__} instance at {id(self):#x}; {details}>'
