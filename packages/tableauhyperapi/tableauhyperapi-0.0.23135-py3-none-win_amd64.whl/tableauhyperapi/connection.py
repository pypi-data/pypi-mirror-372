import enum
import threading
import warnings

from pathlib import PurePath
from typing import Optional, Union, List, Mapping

from .endpoint import Endpoint
from .hyperexception import HyperException, ContextId
from .result import Result
from .sqltype import NullableValue
from .warning import UnclosedObjectWarning
from .impl import hapi
from .impl.dll import ffi, lib
from .impl.dllutil import Error, Parameters, InteropUtil
from .impl.util import check_precondition
from . import catalog


class CreateMode(enum.Enum):
    """ Constants which define what happens when connecting to a database depending on whether it already exists. """

    NONE = hapi.HYPER_DO_NOT_CREATE
    """ Do not create the database. Method will fail if database does not exist. """

    CREATE = hapi.HYPER_CREATE
    """ Create the database. Method will fail if the database already exists. """

    CREATE_IF_NOT_EXISTS = hapi.HYPER_CREATE_IF_NOT_EXISTS
    """ Create the database if it does not exist. """

    CREATE_AND_REPLACE = hapi.HYPER_CREATE_AND_REPLACE
    """ Create the database. If it already exists, drop the old one first. """


class Connection:
    """
    Connects to a Hyper server.

    :param endpoint: :any:`Endpoint` which specifies the Hyper instance to connect to.
    :param database: Optional path to the database file.
    :param create_mode: If database path is specified, defines what happens if the database already exists. By default
        it is :any:`CreateMode.NONE`.
    :param parameters: Optional dictionary of connection parameters to pass to Hyper.
        The available parameters are documented
        `in the Tableau Hyper documentation, chapter "Connection Settings"
        <https://tableau.github.io/hyper-db/docs/hyper-api/connection#connection-settings>`__.

    If the database is not specified, then it connects to the main database. This is useful to create and delete
    databases. Note that the main database gets deleted once the :any:`HyperProcess` gets closed.

    No methods of this class are thread-safe, except :any:`cancel()`, which can be called from a different thread.

    .. testsetup:: connection.__init__

        import os
        from tableauhyperapi import *
        hyper = HyperProcess(Telemetry.SEND_USAGE_DATA_TO_TABLEAU, 'myapp')

    .. testcode:: connection.__init__

        # Connect and create the database. If it already exists, replace it.
        with Connection(hyper.endpoint, 'mydb.hyper', CreateMode.CREATE_AND_REPLACE) as connection:
            schema = TableDefinition('table', [
                TableDefinition.Column('text', SqlType.text()),
                TableDefinition.Column('int', SqlType.int()),
            ])
            connection.catalog.create_table(schema)

    .. testcleanup:: connection.__init__

        hyper.close()
        if os.path.exists('mydb.hyper'):
            os.remove('mydb.hyper')

    """

    def __init__(self, endpoint: Endpoint,
                 database: Optional[Union[str, PurePath]] = None,
                 create_mode: Optional[CreateMode] = CreateMode.NONE,
                 parameters: Optional[Mapping[str, str]] = None):
        self.__cdata = None
        # Reference lib for correct gc order
        self.__lib_ref = lib

        check_precondition(isinstance(endpoint, Endpoint), "'endpoint' must be an Endpoint instance")

        if isinstance(database, PurePath):
            database = str(database)

        if parameters and 'dbname' in parameters:
            if database:
                raise ValueError("Database name cannot be provided as a 'database' parameter in addition to setting "
                                 "'dbname' in the parameters dictionary")
            database = parameters['dbname']
            del parameters['dbname']

        self.__cdata = self.__create_connection(endpoint, database, create_mode, parameters)
        self.__endpoint = endpoint

        # Lock to serialize cancel() and close() calls.
        self.__cancel_lock = threading.Lock()

    @staticmethod
    def __create_connection(endpoint: Endpoint,
                            database: Optional[str],
                            create_mode: CreateMode,
                            parameters: Optional[Mapping[str, str]]):
        native_params = Parameters.create_connection_parameters()
        native_params.set_value('endpoint', endpoint.connection_descriptor)

        if endpoint.user_agent:
            native_params.set_value('user_agent', endpoint.user_agent)

        native_params.set_value('api_language', 'Python')

        if database:
            native_params.set_value('dbname', database)

        if parameters:
            for key, value in parameters.items():
                native_params.set_value(key, value)

        pp = ffi.new('hyper_connection_t**')
        Error.check(hapi.hyper_connect(native_params.cdata, pp, create_mode.value))
        return ffi.gc(pp[0], hapi.hyper_disconnect)

    @property
    def _cdata(self):
        if self.__cdata is None:
            raise RuntimeError('Connection is closed')
        return self.__cdata

    @property
    def _endpoint(self) -> Endpoint:
        return self.__endpoint

    @property
    def is_open(self) -> bool:
        """ Returns ``True`` if the connection has not been closed yet. """
        return self.__cdata is not None

    @property
    def is_ready(self) -> bool:
        """ Checks whether the connection is ready, i.e., it is not processing a query. An open :any:`Inserter` or
        :any:`Result` keeps the connection busy. """
        return self.__cdata is not None and hapi.hyper_connection_is_ready(self.__cdata)

    def close(self):
        """ Closes the connection. Note that this has no effect if there is an active result or data inserter.
         These need to be closed before the connection to the server will be actually dropped."""

        with self.__cancel_lock:
            if self.__cdata is not None:
                ffi.release(self.__cdata)
                self.__cdata = None

    def cancel(self):
        """
        Cancels the current SQL command or query of this connection (if any). This method may be safely called from
        any thread. After this method was called, the current SQL command or query may fail with a cancellation error
        at any point during its execution. However, there are no guarantees if and when it will fail.
        """

        with self.__cancel_lock:
            if self.__cdata is not None:
                try:
                    Error.check(hapi.hyper_cancel(self.__cdata))
                except HyperException:
                    # TODO TFSID 921655: log it
                    pass

    @property
    def catalog(self) -> 'catalog.Catalog':
        """ Gets the :any:`Catalog` for this connection. """
        return catalog.Catalog(self)

    def execute_query(self, query, text_as_bytes=False) -> Result:
        """
        Executes a SQL query and returns the result as a :any:`Result` object.

        :param query: SQL query to execute.
        :param text_as_bytes: optional, if ``True`` then string values read from the database will be returned as
            UTF-8-encoded ``bytearray`` objects. By default string values are returned as ``str`` objects.
        :return: A :any:`Result` instance. Use this method in a ``with`` statement to automatically close the result
            when done reading from it, or call its :any:`close()<Result.close>` method. No queries can be executed or
            tables created/opened while the result is open.
        """
        pp_result = ffi.new('hyper_rowset_t**')
        Error.check(hapi.hyper_execute_query(self._cdata,
                                             InteropUtil.string_to_char_p(query),
                                             pp_result))
        return Result(text_as_bytes, self, pp_result[0])

    def execute_list_query(self, query, text_as_bytes=False) -> List[List[NullableValue]]:
        """
        Executes a SQL query and returns the result as list of rows of data, each represented by a list of objects.

        :param query: SQL query to execute.
        :param text_as_bytes: optional, if ``True`` then string values read from the database will be returned as
            UTF-8-encoded ``bytearray`` objects. By default string values are returned as ``str`` objects.
        :return: A list of rows, each represented by a list of objects. See :any:`TypeTag` documentation for how
            database values are represented by Python objects.
        """
        with self.execute_query(query, text_as_bytes) as result:
            # Note, it is tempting to return an iterable with yield, but that would make it easy to leak the
            # result object until it's garbage-collected (if the iteration stops in the middle).
            return list(result)

    def execute_command(self, command) -> Optional[int]:
        """
        Executes a SQL statement and returns the affected row count if the statement has one.

        :param command: SQL statement to execute.
        :return: Count of affected rows if available, ``None`` otherwise.
        """
        row_count_cdata = ffi.new('int*')
        Error.check(hapi.hyper_execute_command(self._cdata,
                                               InteropUtil.string_to_char_p(command),
                                               row_count_cdata))
        row_count = row_count_cdata[0]
        if row_count < 0:
            row_count = None
        return row_count

    def execute_scalar_query(self, query, text_as_bytes=False) -> NullableValue:
        """
        Executes a scalar query, i.e. a query that returns exactly one row with one column, and returns the value
        from the result.

        :param query: SQL query to execute.
        :param text_as_bytes: optional, if ``True`` then a string value read from the database will be returned as
            UTF-8-encoded ``bytearray`` objects. By default string values are returned as ``str`` objects.
        :return: the value from the result. A NULL database value is returned as ``None``. See :any:`TypeTag`
            documentation for how database values are represented by Python objects.
        """
        with self.execute_query(query, text_as_bytes) as result:
            if len(result.schema.columns) != 1:
                raise HyperException(ContextId(0xA1B8BBEC6D), 'Query result must have exactly one column')
            if not result.next_row():
                raise HyperException(ContextId(0xB8BBEC6DA1), 'Query returned zero rows')
            value = result.get_value(0)
            if result.next_row():
                raise HyperException(ContextId(0xBEC6DA1B8B), 'Query returned more than one row')
            return value

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        if self.__cdata is not None:
            warnings.warn('Connection has not been closed. Use Connection object in a with statement or call its '
                          'close() method when done.', UnclosedObjectWarning)
        # it is closed by cffi, self.__cdata is a gc'ed pointer

    def __repr__(self):
        status = 'open' if self.is_ready else ('busy' if self.is_open else 'closed')
        return f"<Connection object at {id(self):#x}; status: {status}; endpoint: {self._endpoint!r}>"
