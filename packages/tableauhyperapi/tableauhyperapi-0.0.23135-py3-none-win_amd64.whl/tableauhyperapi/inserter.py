import datetime
import decimal
import warnings

from typing import Iterable, Union, Any, Optional

from .connection import Connection
from .date import Date
from .interval import Interval
from .sqltype import TypeTag
from .tablename import Name, TableName
from .tabledefinition import TableDefinition, Nullability
from .timestamp import Timestamp
from .warning import UnclosedObjectWarning
from .impl import hapi
from .impl.converter import Converter
from .impl.dll import ffi, lib
from .impl.dllutil import Error, InteropUtil
from .impl.schemaconverter import SchemaConverter
from .impl.util import check_precondition


class Inserter:
    """
    An object which is used to insert data into a table.

    :param connection: the connection to use.
    :param arg: either the table name or the definition of the table to insert data into.
    :param columns: The set of columns in which to insert. The columns have to exist in the table.
       When not None, Columns not present in columns will be set to their default value.
       columns is a Iterable of either string or Inserter.ColumnMapping
       A columnMapping can optionally contain a valid SQL expression.
       The SQL expression specified for the column is used to transform or compute values on the fly during insertion.
       The SQL expression can depend on columns that exist in the table.
       The SQL expression can also depend on values or columns that do not exist in the table,
       but must be specified in the inserter_dfinition.
    :param inserter_definition: The definition of columns to which values are provided.
       inserter_definition is a keyword-only parameter required only when columns is not None
       The column definition for all the columns without SQL expression must be specified in inserter_definition.
       For a column without SQL expression, the column definition provided in inserter_definition must match
       the actual definition of the column in the table.

    .. note:: SQL expression provided during insertion are used without any modification during insertion
         and hence vulnerable to SQL injection attacks.
         Applications should prevent end-users from providing expressions directly during insertion

    Sample usage:

    .. testsetup:: Inserter.__init__

        from tableauhyperapi import *
        def setup():
            hyper = HyperProcess(Telemetry.SEND_USAGE_DATA_TO_TABLEAU, 'myapp')
            connection = Connection(hyper.endpoint, 'mydb.hyper', CreateMode.CREATE_AND_REPLACE)
            table_def = TableDefinition('foo', [
                TableDefinition.Column('text', SqlType.text()),
                TableDefinition.Column('int', SqlType.int()),
            ])
            connection.catalog.create_table(table_def)
            return hyper, connection
        hyper, connection = setup()

    .. testcode:: Inserter.__init__

        with Inserter(connection, 'foo') as inserter:
            inserter.add_row(['a', 1])
            inserter.add_row(['b', 2])
            inserter.execute()

    .. testcleanup:: Inserter.__init__

        connection.close()
        hyper.close()
        import os
        os.remove('mydb.hyper')

    """

    class ColumnMapping:
        """
        An object which defines how a target column is mapped to inserter definition.

        :param column_name: the column name.
        :param expression: the SQL expression for computing the column
            If not set, the data for this column must be provided using add_row()/add_rows() calls during insertion

        """

        def __init__(self, column_name: Union[Name, str],
                     expression: Optional[str] = None):
            self.__column_name = Name(column_name)
            self.__expression = expression

        @property
        def column_name(self) -> Name:
            """ The name of the column. """
            return self.__column_name

        @property
        def expression(self) -> Optional[str]:
            """ The SQL expression used to compute the column. """
            return self.__expression

        def _as_select_list_expression(self):
            if self.__expression is None:
                return str(self.__column_name)
            else:
                return f'{self.__expression} AS {str(self.__column_name)}'

    def __init__(self, connection: Connection,
                 arg: Union[str, Name, TableName, TableDefinition],
                 columns: Iterable[Union[str, ColumnMapping]] = None,
                 *,
                 inserter_definition: Iterable[TableDefinition.Column] = None):
        self._cdata = None
        self._buffer = None
        self._native_stream_definition = None
        # Reference lib for correct gc order
        self.__lib_ref = lib

        check_precondition(isinstance(arg, TableDefinition) or isinstance(arg, str) or isinstance(arg, Name)
                           or isinstance(arg, TableName),
                           'Argument must be a table name or a table definition')

        check_precondition(inserter_definition is None or columns is not None,
                           'Inserter Defintion is required only when columns are provided')

        # table_def: Table Definition containing only the colums into which values are inserted
        # stream_def: Stream Definition used by the bulk inserter
        # self._select_str: comma separated list of column retrieved by the select statement during bulk insert
        #             Usage - `INSERT BULK INTO table (columns) SELECT self._select_str FROM EXTERNAL STREAM stream`
        # uses_expr: boolean to indicate if expressions are used in insertion
        table_def, stream_def, self._select_str, uses_expr = Inserter.__parse_from_arguments(connection,
                                                                                             arg,
                                                                                             columns,
                                                                                             inserter_definition)

        native_table_definition = SchemaConverter.table_definition_to_native(table_def)

        pp_inserter = ffi.new('hyper_inserter_t**')
        Error.check(hapi.hyper_create_inserter(connection._cdata, native_table_definition.cdata, pp_inserter))
        self._cdata = pp_inserter[0]

        self._native_table_definition = native_table_definition

        # Decimal context used for 128-bit numeric transformations
        traps = [decimal.Overflow, decimal.DivisionByZero, decimal.InvalidOperation, decimal.Inexact]
        self._big_numeric_decimal_context = decimal.Context(prec=38, traps=traps)

        # Stream definition is none, if all columns are computed by calculations
        if stream_def is not None:
            native_select_str = InteropUtil.string_to_char_p(self._select_str)
            native_stream_definition = SchemaConverter.table_definition_to_native(stream_def)
            # Initialize bulk insert/stream inserter when expressions are used
            if uses_expr is True:
                Error.check(hapi.hyper_init_bulk_insert(pp_inserter[0], native_stream_definition.cdata,
                                                        native_select_str))

            pp_buffer = ffi.new('hyper_inserter_buffer_t**')
            Error.check(hapi.hyper_create_inserter_buffer(pp_inserter[0],
                                                          native_stream_definition.cdata,
                                                          native_select_str,
                                                          pp_buffer))
            self._buffer = ffi.gc(pp_buffer[0], hapi.hyper_inserter_buffer_destroy)

        self.__inline_things(stream_def)

    @staticmethod
    def __parse_from_arguments(connection: Connection,
                               arg: Union[str, Name, TableName, TableDefinition],
                               columns: Iterable[Union[str, ColumnMapping]],
                               inserter_definition: Iterable[TableDefinition.Column]):
        if isinstance(arg, TableDefinition):
            table_definition = arg._clone()
        else:
            table_definition = connection.catalog.get_table_definition(arg)

        # We identify the usage of expressions by iterating through `columns` argument
        # The column in `columns` must be a target column and of type `str` or `ColumnMapping`

        # If expressions are used during Insertion:
        # The stream definition is different from the target table definition
        # The inserter definition is used to build the stream definition
        # For a column that doesn't use expression,
        # the column definition in the inserter definition and target table definition must be the same

        # If all columns use expressions the stream definition/inserter defintion is empty.
        # For ex.
        # Target_table: [Column("A", SqlType.int()), Column("B", SqlType.int())]
        # columns: [ColumnMapping["A", 1], ColumnMapping["B", 2]]
        #
        # The values are inserted when `execute()` method is called

        uses_expression = False
        # List of non-expression column names.
        # The non expression columns are tracked to ensure that it is specified in the inserter definition
        non_expression_columns = []
        select_list = []

        if columns is not None:
            # User is only inserting into a subset of columns
            target_columns_list = []
            for column in columns:
                if isinstance(column, str):
                    column = Inserter.ColumnMapping(column)
                elif not isinstance(column, Inserter.ColumnMapping):
                    raise TypeError("Values in 'columns' argument must be a 'ColumnMapping' or 'str'")

                target_column = table_definition.get_column_by_name(column.column_name)
                if target_column is None:
                    raise ValueError(f'Column {column.column_name} does not exist'
                                     f' in table {table_definition.table_name.name}')
                if column.expression is None:
                    non_expression_columns.append(target_column)
                else:
                    uses_expression = True
                select_list.append(column._as_select_list_expression())

                target_columns_list.append(target_column)

            table_definition = TableDefinition(table_definition.table_name,
                                               target_columns_list,
                                               table_definition.persistence)

        # If expressions are used, build a stream definition with the help of inserter_definition
        if uses_expression is True:
            # Verify non-expression columns are specified in the inserter definition only once
            # and the column defintion matches in the table definition
            if len(non_expression_columns) != 0 and inserter_definition is None:
                raise ValueError('Columns without expressions must be specified in inserter definition')
            for non_expression_col in non_expression_columns:
                matching_columns = list(filter(lambda inserter_column: inserter_column.name == non_expression_col.name,
                                               inserter_definition))
                if len(matching_columns) == 0:
                    raise ValueError(f'Column {str(non_expression_col.name)} must be specified '
                                     f'as a ColumnMapping in columns or in inserter definition')
                elif len(matching_columns) != 1:
                    raise ValueError(f'Column {str(non_expression_col.name)} specified more '
                                     f'than once in inserter definition')
                else:
                    inserter_column = matching_columns[0]
                    if (inserter_column.type != non_expression_col.type
                            or inserter_column.nullability != non_expression_col.nullability):
                        raise ValueError(f'Column definition for {str(non_expression_col.name)} '
                                         f'does not match definition provided in inserter definition')

            if inserter_definition is not None:
                stream_definition = TableDefinition(table_definition.table_name,
                                                    inserter_definition,
                                                    table_definition.persistence)
            else:
                stream_definition = None
        else:
            stream_definition = table_definition

        # Build the select list for C-API
        if len(select_list) != 0:
            select_list_string = ', '.join(select_list)
        else:
            select_list_string = ', '.join(str(column.name) for column in stream_definition.columns)

        return table_definition, stream_definition, select_list_string, uses_expression

    def __inline_things(self, table_definition: Optional[TableDefinition]):
        # noinspection DuplicatedCode
        insert_functions = {
            TypeTag.BOOL: self.__write_bool,
            TypeTag.BIG_INT: self.__write_big_int,
            TypeTag.SMALL_INT: self.__write_small_int,
            TypeTag.INT: self.__write_int,
            TypeTag.FLOAT: self.__write_float,
            TypeTag.DOUBLE: self.__write_double,
            TypeTag.OID: self.__write_uint,
            TypeTag.BYTES: self.__write_bytes,
            TypeTag.TEXT: self.__write_text,
            TypeTag.VARCHAR: self.__write_text,
            TypeTag.CHAR: self.__write_text,
            TypeTag.JSON: self.__write_text,
            TypeTag.DATE: self.__write_date,
            TypeTag.INTERVAL: self.__write_interval,
            TypeTag.TIME: self.__write_time,
            TypeTag.TIMESTAMP: self.__write_timestamp,
            TypeTag.TIMESTAMP_TZ: self.__write_timestamp_tz,
            TypeTag.TABGEOGRAPHY: self.__write_bytes,
            # Deprecated alias for TABGEOGRAPHY, will be removed as part of W-17701666.
            TypeTag.GEOGRAPHY: self.__write_bytes,
        }

        validation_functions = {
            TypeTag.BOOL: Inserter.__validate_bool,
            TypeTag.BIG_INT: Inserter.__validate_big_int,
            TypeTag.SMALL_INT: Inserter.__validate_small_int,
            TypeTag.INT: Inserter.__validate_int,
            TypeTag.FLOAT: Inserter.__validate_double,
            TypeTag.DOUBLE: Inserter.__validate_double,
            TypeTag.OID: Inserter.__validate_oid,
            TypeTag.BYTES: Inserter.__validate_bytes,
            TypeTag.TEXT: Inserter.__validate_text,
            TypeTag.VARCHAR: Inserter.__validate_varchar,
            TypeTag.CHAR: Inserter.__validate_char,
            TypeTag.JSON: Inserter.__validate_json,
            TypeTag.DATE: Inserter.__validate_date,
            TypeTag.INTERVAL: Inserter.__validate_interval,
            TypeTag.TIME: Inserter.__validate_time,
            TypeTag.TIMESTAMP: Inserter.__validate_timestamp,
            TypeTag.TIMESTAMP_TZ: Inserter.__validate_timestamp_tz,
            TypeTag.TABGEOGRAPHY: Inserter.__validate_tabgeography,
            # Deprecated alias for TABGEOGRAPHY, will be removed as part of W-17701666.
            TypeTag.GEOGRAPHY: Inserter.__validate_tabgeography,
            TypeTag.NUMERIC: Inserter.__validate_numeric,
        }

        self._column_count = len(table_definition.columns) if table_definition else 0
        self._range_column_count = range(self._column_count)
        self._columns = list(table_definition.columns) if table_definition else []

        self._insert_null_functions = []
        self._insert_value_functions = []
        self._validation_functions = []
        for col in self._columns:
            is_nullable = col.nullability == Nullability.NULLABLE

            if col.type.tag == TypeTag.NUMERIC:
                insert_value = self.__get_write_decimal_function(col)
            else:
                insert_value = insert_functions[col.type.tag]

            self._insert_value_functions.append(insert_value)
            self._validation_functions.append(validation_functions[col.type.tag])

            if is_nullable:
                self._insert_null_functions.append(self.__write_null)
            else:
                self._insert_null_functions.append(
                    lambda column_name=col.name.unescaped: self.__raise_value_is_null(column_name))

        self._hyper_add_null = hapi.hyper_inserter_buffer_add_null
        self._hyper_add_bool = hapi.hyper_inserter_buffer_add_bool
        self._hyper_add_int16 = hapi.hyper_inserter_buffer_add_int16
        self._hyper_add_int32 = hapi.hyper_inserter_buffer_add_int32
        self._hyper_add_int64 = hapi.hyper_inserter_buffer_add_int64
        self._hyper_add_float = hapi.hyper_inserter_buffer_add_float
        self._hyper_add_double = hapi.hyper_inserter_buffer_add_double
        self._hyper_add_binary = hapi.hyper_inserter_buffer_add_binary
        self._hyper_add_date = hapi.hyper_inserter_buffer_add_date
        self._hyper_add_raw = hapi.hyper_inserter_buffer_add_raw
        self._ffi_from_buffer = ffi.from_buffer
        self._py_interval = ffi.new('py_interval*')
        self._py_interval_buf = ffi.cast('const uint8_t*', self._py_interval)

    def __get_write_decimal_function(self, column: TableDefinition.Column):
        if column.type.precision <= 18:
            # 64-bit numerics
            write_func = self.__write_big_int
            scale = decimal.Decimal(10) ** column.type.scale

            def write_decimal(v: decimal.Decimal):
                return write_func((v * scale).to_integral_value())

            return write_decimal
        else:
            # 128-bit numerics
            def write_decimal(v: decimal.Decimal):
                i = int(v.scaleb(column.type.scale, context=self._big_numeric_decimal_context))
                num128 = i.to_bytes(16, byteorder='little', signed=True)
                return Error.check(self._hyper_add_raw(self._buffer, self._ffi_from_buffer(num128), len(num128)))

            return write_decimal

    def __raise_value_is_null(self, column_name):
        raise ValueError(f'Got NULL for a non-nullable column "{column_name}"')

    def add_row(self, row: Iterable[object]):
        """
        Inserts a row of data into the table. ``None`` corresponds to the database NULL, see :any:`TypeTag`
        for how Python types are mapped to Hyper data types.

        :param row: a row of data as a list of objects.
        """
        try:
            i = 0
            for v in row:
                if v is None:
                    self._insert_null_functions[i]()
                else:
                    self._insert_value_functions[i](v)
                i += 1
            if i != self._column_count:
                raise ValueError(f'Too few columns provided to `add_row()`. '
                                 f'Provided {i} column(s) but {self._column_count} are required.')
        except ValueError:
            # If a `ValueError` occurred, just re-raise it after closing the inserter and skip the `__validate_row()`
            # pass of the general `Exception` case. Otherwise, `__validate_row()` might raise a different exception
            # and confuse the user. (See Defect 1275968.)
            self.close()
            raise
        except Exception:
            self.close()
            # see if insertion failed because the values are invalid
            self.__validate_row(row)
            # nope, something else happened, re-raise the exception
            raise

    def add_rows(self, rows: Iterable[Iterable[object]]):
        """
        Inserts rows of data into the table. Each row is represented by a sequence of objects.  ``None`` corresponds to
        the database NULL, see :any:`TypeTag` for how Python types are mapped to Hyper data types.

        This is a convenience method equivalent to::

            for row in rows:
                inserter.add_row(row)

        :param rows: a sequence of rows of data.
        """
        for row in rows:
            self.add_row(row)

    def execute(self):
        """
        Flush remaining data and commit. If this method fails then the data is discarded and not inserted. The inserter
        is closed after this method returns, even in the case of a failure.
        If ``execute()`` is not called and the inserter is closed, then the inserted data is discarded.
        """
        if self._cdata is None:
            raise RuntimeError('Inserter is already closed')
        self.__close(True)

    def __close(self, insert_data):
        execute_exception = None

        if self._cdata is not None:
            if insert_data:
                if self._column_count == 0 and self._select_str is not ffi.NULL:
                    try:
                        native_select_str = InteropUtil.string_to_char_p(self._select_str)
                        Error.check(hapi.hyper_insert_computed_expressions(self._cdata,
                                                                           native_select_str))
                    except Exception as ex:
                        if execute_exception is None:
                            execute_exception = ex
                else:
                    try:
                        if self._buffer is not None:
                            Error.check(hapi.hyper_inserter_buffer_flush(self._buffer))
                    except Exception as ex:
                        execute_exception = ex

                try:
                    Error.check(hapi.hyper_close_inserter(self._cdata, execute_exception is None))
                except Exception as ex:
                    if execute_exception is None:
                        execute_exception = ex
            else:
                # do not check the error, it's not going to fail
                hapi.hyper_close_inserter(self._cdata, False)

        self._cdata = None

        if self._native_table_definition is not None:
            ffi.release(self._native_table_definition.cdata)
            self._native_table_definition = None

        if self._native_stream_definition is not None:
            ffi.release(self._native_stream_definition.cdata)
            self._native_stream_definition = None

        if self._buffer is not None:
            ffi.release(self._buffer)
            self._buffer = None

        self.add_row = self.__raise_inserter_is_closed

        if execute_exception is not None:
            raise execute_exception

    @property
    def is_open(self) -> bool:
        """ Returns ``True`` if the inserter has not been closed yet. """
        return self._cdata is not None

    def close(self):
        """
        If the inserter is not closed yet, discard all data and close it.
        """
        self.__close(False)

    @staticmethod
    def __raise_inserter_is_closed(*args, **kwargs):
        raise RuntimeError('The inserter is closed.')

    def __validate_row(self, row: Iterable[object]):
        i = 0
        for v in row:
            if i >= self._column_count:
                raise ValueError(
                    f'The table has {self._column_count} columns, but Inserter.add_row() was called for a row with '
                    f'more than {self._column_count} values.')

            # insert_null will raise an exception if NULL is not allowed
            if v is not None:
                self._validation_functions[i](v, self._columns[i])

            i += 1

        if i != self._column_count:
            raise ValueError(
                f'Inserter.add_row() was called for a row with {i} values, but the table has {self._column_count} '
                f'columns.')

    @staticmethod
    def __format_value(value):
        s = repr(value)
        if len(s) > 20:
            s = s[:20] + '...'
        return s

    @staticmethod
    def __validate_bytes_value(value: Any, column: TableDefinition.Column):
        if not isinstance(value, bytes) and not isinstance(value, bytearray):
            raise ValueError(f'Got an invalid value {Inserter.__format_value(value)} for column '
                             f'"{column.name.unescaped}", it '
                             f'must be a bytes or a bytearray instance')

    @staticmethod
    def __validate_int_value(value, column: TableDefinition.Column, min_value, max_value):
        if not isinstance(value, int):
            raise ValueError(f'Got an invalid value {Inserter.__format_value(value)} for column '
                             f'"{column.name.unescaped}", it '
                             f'must be an int instance')
        if value < min_value or value > max_value:
            raise ValueError(f'Got an invalid value {value} for column '
                             f'"{column.name.unescaped}", it must be in the range '
                             f'from {min_value} to {max_value}')

    @staticmethod
    def __validate_text_value(value, column: TableDefinition.Column):
        if not isinstance(value, str) and not isinstance(value, bytes) and not isinstance(value, bytearray):
            raise ValueError(f'Got an invalid value {Inserter.__format_value(value)} for column '
                             f'"{column.name.unescaped}", it '
                             f'must be an str, bytes, or bytearray instance')

    @staticmethod
    def __validate_bool(value: Any, column: TableDefinition.Column):
        if not isinstance(value, bool):
            raise ValueError(f'Got an invalid value {Inserter.__format_value(value)} for column '
                             f'"{column.name.unescaped}", it '
                             f'must be a bool instance')

    @staticmethod
    def __validate_big_int(value: Any, column: TableDefinition.Column):
        Inserter.__validate_int_value(value, column, Inserter._MIN_BIG_INT, Inserter._MAX_BIG_INT)

    @staticmethod
    def __validate_small_int(value: Any, column: TableDefinition.Column):
        Inserter.__validate_int_value(value, column, Inserter._MIN_SMALL_INT, Inserter._MAX_SMALL_INT)

    @staticmethod
    def __validate_int(value: Any, column: TableDefinition.Column):
        Inserter.__validate_int_value(value, column, Inserter._MIN_INT, Inserter._MAX_INT)

    @staticmethod
    def __validate_double(value: Any, column: TableDefinition.Column):
        if not isinstance(value, float):
            raise ValueError(f'Got an invalid value {Inserter.__format_value(value)} for column '
                             f'"{column.name.unescaped}", it '
                             f'must be a float instance')

    @staticmethod
    def __validate_oid(value: Any, column: TableDefinition.Column):
        Inserter.__validate_int_value(value, column, Inserter._MIN_OID, Inserter._MAX_OID)

    @staticmethod
    def __validate_bytes(value: Any, column: TableDefinition.Column):
        Inserter.__validate_bytes_value(value, column)

    @staticmethod
    def __validate_text(value: Any, column: TableDefinition.Column):
        Inserter.__validate_text_value(value, column)

    @staticmethod
    def __validate_varchar(value: Any, column: TableDefinition.Column):
        Inserter.__validate_text_value(value, column)

    @staticmethod
    def __validate_char(value: Any, column: TableDefinition.Column):
        Inserter.__validate_text_value(value, column)

    @staticmethod
    def __validate_json(value: Any, column: TableDefinition.Column):
        Inserter.__validate_text_value(value, column)

    @staticmethod
    def __validate_date(value: Any, column: TableDefinition.Column):
        if (not isinstance(value, datetime.datetime) and not isinstance(value, datetime.date) and
                not isinstance(value, Timestamp) and not isinstance(value, Date)):
            raise ValueError(f'Got an invalid value {Inserter.__format_value(value)} for column '
                             f'"{column.name.unescaped}", it '
                             f'must be a Date, Timestamp, datetime, or date instance')

    @staticmethod
    def __validate_interval(value: Any, column: TableDefinition.Column):
        if not isinstance(value, Interval):
            raise ValueError(f'Got an invalid value {Inserter.__format_value(value)} for column '
                             f'"{column.name.unescaped}", it '
                             f'must be a Interval instance')

    @staticmethod
    def __validate_time(value: Any, column: TableDefinition.Column):
        if not isinstance(value, datetime.datetime) and not isinstance(value, datetime.time):
            raise ValueError(f'Got an invalid value {Inserter.__format_value(value)} for column '
                             f'"{column.name.unescaped}", it '
                             f'must be a datetime or a time instance')

    @staticmethod
    def __validate_timestamp_value(value: Any, column: TableDefinition.Column):
        if not isinstance(value, datetime.datetime) and not isinstance(value, Timestamp):
            raise ValueError(f'Got an invalid value {Inserter.__format_value(value)} for column '
                             f'"{column.name.unescaped}", it '
                             f'must be a Timestamp or a datetime instance')

    @staticmethod
    def __validate_timestamp(value: Any, column: TableDefinition.Column):
        Inserter.__validate_timestamp_value(value, column)

    @staticmethod
    def __validate_timestamp_tz(value: Any, column: TableDefinition.Column):
        Inserter.__validate_timestamp_value(value, column)

    @staticmethod
    def __validate_tabgeography(value: Any, column: TableDefinition.Column):
        Inserter.__validate_bytes_value(value, column)

    @staticmethod
    def __validate_numeric(value: Any, column: TableDefinition.Column):
        if not isinstance(value, decimal.Decimal):
            raise ValueError(f'Got an invalid value {Inserter.__format_value(value)} for column '
                             f'"{column.name.unescaped}", it '
                             f'must be a Decimal instance')

    _MIN_BIG_INT = -2 ** 63
    _MAX_BIG_INT = 2 ** 63 - 1
    _TWO_TO_THIRTY_TWO = 2 ** 32
    _TWO_TO_SIXTY_FOUR = 2 ** 64
    _MIN_INT = -2 ** 31
    _MAX_INT = 2 ** 31 - 1
    _MIN_SMALL_INT = -2 ** 15
    _MAX_SMALL_INT = 2 ** 15 - 1
    _MIN_OID = 0
    _MAX_OID = 2 ** 32 - 1

    def __write_null(self):
        Error.check(self._hyper_add_null(self._buffer))

    def __write_bool(self, v: bool):
        Error.check(self._hyper_add_bool(self._buffer, v))

    def __write_small_int(self, v: int):
        Error.check(self._hyper_add_int16(self._buffer, v))

    def __write_int(self, v: int):
        Error.check(self._hyper_add_int32(self._buffer, v))

    def __write_uint(self, v: int):
        # cffi verifies that the value is in range for the target type, so we have to convert the unsigned
        # value to an int32_t here. E.g. 0xFFFFFFFF gets transformed into -1.
        v = v if v <= Inserter._MAX_INT else v - Inserter._TWO_TO_THIRTY_TWO
        Error.check(self._hyper_add_int32(self._buffer, v))

    def __write_big_int(self, v: int):
        Error.check(self._hyper_add_int64(self._buffer, v))

    def __write_float(self, v: float):
        Error.check(self._hyper_add_float(self._buffer, v))

    def __write_double(self, v: float):
        Error.check(self._hyper_add_double(self._buffer, v))

    def __write_bytes(self, v: Union[bytes, bytearray]):
        Error.check(self._hyper_add_binary(self._buffer, self._ffi_from_buffer(v), len(v)))

    def __write_text(self, v: Union[str, bytes, bytearray]):
        try:
            v = v.encode()
        except AttributeError:
            pass
        Error.check(self._hyper_add_binary(self._buffer, self._ffi_from_buffer(v), len(v)))

    def __write_date(self, v: Union[datetime.date, datetime.datetime, Date]):
        Error.check(self._hyper_add_date(self._buffer, v.year, v.month, v.day))

    def __write_time(self, v: Union[datetime.time, datetime.datetime]):
        Error.check(self._hyper_add_int64(self._buffer, Converter.time_to_hyper(v)))

    def __write_timestamp(self, v: Union[datetime.datetime, Timestamp]):
        v = Converter.to_hyper_timestamp(v)
        v = v if v <= Inserter._MAX_BIG_INT else v - Inserter._TWO_TO_SIXTY_FOUR
        Error.check(self._hyper_add_int64(self._buffer, v))

    def __write_timestamp_tz(self, v: Union[datetime.datetime, Timestamp]):
        v = Converter.to_hyper_timestamp_tz(v)
        v = v if v <= Inserter._MAX_BIG_INT else v - Inserter._TWO_TO_SIXTY_FOUR
        Error.check(self._hyper_add_int64(self._buffer, v))

    def __write_interval(self, v: Interval):
        p = self._py_interval
        p.microseconds = v.microseconds
        p.days = v.days
        p.months = v.months
        Error.check(self._hyper_add_raw(self._buffer, self._py_interval_buf, 16))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        if self._cdata is not None:
            warnings.warn('Inserter has not been closed. Use Inserter object in a with statement or call its close() '
                          'method when done.', UnclosedObjectWarning)
            hapi.hyper_close_inserter(self._cdata, False)
            self._cdata = None
