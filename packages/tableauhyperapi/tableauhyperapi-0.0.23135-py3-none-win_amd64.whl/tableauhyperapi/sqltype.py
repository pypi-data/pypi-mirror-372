import datetime
import decimal
import enum
import functools

from typing import Optional, Union

from .date import Date
from .impl import hapi
from .impl.util import check_precondition
from .interval import Interval
from .timestamp import Timestamp


ScalarValue = Union[bool, bytearray, bytes, datetime.time, Date, decimal.Decimal, float, int, Interval, str, Timestamp]
NullableValue = Optional[ScalarValue]
"""
Return type used for single SQL values.

This lists all the possible types in :any:`TypeTag`.
Note that the SQL NULL value maps to None, and thus it is covered by the `Optional`.
"""


# Mark as unique again as part of W-17701666.
# @enum.unique
class TypeTag(enum.Enum):
    """
    Constants which represent Hyper data types. These are used as values of the :any:`SqlType.tag` attribute.
    """

    UNSUPPORTED = hapi.HYPER_UNSUPPORTED
    """ Unsupported type. Queries and tables may have columns of this type if the database was created by
    a newer version of the library. Values are represented by Python's ``bytes``. """

    BOOL = hapi.HYPER_BOOL
    """ Boolean values. Represented by Python's ``bool``. """

    BIG_INT = hapi.HYPER_BIG_INT
    """ Eight-byte integer values. Represented by Python's ``int``. """

    SMALL_INT = hapi.HYPER_SMALL_INT
    """ Two-byte integer values. Represented by Python's ``int``. """

    INT = hapi.HYPER_INT
    """ Four-byte integer values. Represented by Python's ``int``. """

    NUMERIC = hapi.HYPER_NUMERIC
    """ Exact decimal numbers with user-specified precision. Represented by ``decimal.Decimal``. """

    FLOAT = hapi.HYPER_FLOAT
    """ Single precision floating point values. Represented by Python's ``float``. """

    DOUBLE = hapi.HYPER_DOUBLE
    """ Double precision floating point values. Represented by Python's ``float``. """

    OID = hapi.HYPER_OID
    """ OID values. Represented by Python's ``int``. """

    BYTES = hapi.HYPER_BYTE_A
    """ Byte array. These are returned as ``bytes`` objects from queries. When writing data, ``bytearray`` and
    ``bytes`` objects are accepted. """

    TEXT = hapi.HYPER_TEXT
    """ Unicode text.
    These are returned as ``str`` or UTF8-encoded ``bytes`` objects, depending on the ``str_as_bytes`` parameter of
    :any:`execute_query`/:any:`execute_list_query`/:any:`execute_scalar_query` methods. When writing data,
    ``str``, ``bytearray``, and ``bytes`` objects are accepted. Bytes are assumed to be UTF8-encoded.
    """

    VARCHAR = hapi.HYPER_VARCHAR
    """ Unicode text with maximum length.
    These are returned as ``str`` or UTF8-encoded ``bytes`` objects, depending on the ``str_as_bytes`` parameter of
    :any:`execute_query`/:any:`execute_list_query`/:any:`execute_scalar_query` methods. When writing data,
    ``str``, ``bytearray``, and ``bytes`` objects are accepted. Bytes are assumed to be UTF8-encoded.
    """

    CHAR = hapi.HYPER_CHAR
    """ Space-padded unicode text.
    These are returned as ``str`` or UTF8-encoded ``bytes`` objects, depending on the ``str_as_bytes`` parameter of
    :any:`execute_query`/:any:`execute_list_query`/:any:`execute_scalar_query` methods. When writing data,
    ``str``, ``bytearray``, and ``bytes`` objects are accepted. Bytes are assumed to be UTF8-encoded.
    """

    JSON = hapi.HYPER_JSON
    """ Unicode text. These are returned as ``str`` or UTF8-encoded ``bytes`` objects, depending on the ``str_as_bytes``
    parameter of :any:`execute_query`/:any:`execute_list_query`/:any:`execute_scalar_query` methods. When writing data,
    ``str``, ``bytearray``, and ``bytes`` objects are accepted. Bytes are assumed to be UTF8-encoded.
    """

    DATE = hapi.HYPER_DATE
    """ Date values. These are returned as :any:`Date` objects from queries. When writing data, ``datetime.date``,
    ``datetime.datetime`` are also accepted; time part in ``datetime.datetime`` is ignored. """

    INTERVAL = hapi.HYPER_INTERVAL
    """ Time interval - union of logically independent months, days, and microseconds components. Represented by
    :any:`Interval` objects. """

    TIME = hapi.HYPER_TIME
    """ Time of the day, from 00:00:00 to 23:59:59:999999. These are returned as ``datetime.time`` objects from queries.
    When writing data, ``datetime.time`` and ``datetime.datetime`` objects are accepted; date part in
    ``datetime.datetime`` is ignored. """

    TIMESTAMP = hapi.HYPER_TIMESTAMP
    """ Timestamp - date and time of day. These are returned as :any:`Timestamp` objects from queries. When writing
    data, ``datetime.datetime`` objects are also accepted. """

    TIMESTAMP_TZ = hapi.HYPER_TIMESTAMP_TZ
    """ UTC Timestamp - date and time of day. These are returned as :any:`Timestamp` objects from queries. When writing
    data, ``datetime.datetime`` objects are also accepted. """

    TABGEOGRAPHY = hapi.HYPER_TABGEOGRAPHY
    """ Tableau Geography. These are returned as ``bytes`` objects from queries. When writing data, ``bytes`` and ``bytearray``
    objects are accepted. """

    GEOGRAPHY = hapi.HYPER_GEOGRAPHY
    """ Deprecated alias for `TABGEOGRAPHY`. Will be removed as part of W-17701666. """

    @staticmethod
    def _from_value(value: int):
        for e in TypeTag:
            if e.value == value:
                return e
        raise ValueError('Invalid type tag value {}'.format(value))


# SqlType.int() shadows builtin int when 'int' is used as a type annotation
_int_type = int


# noinspection DuplicatedCode
@functools.total_ordering
class SqlType:
    """
    An object which represents a column type - type tag and optional type-specific modifiers.

    Do not use the constructor directly, instead use one of the factory methods.
    """

    _UNUSED_MODIFIER = 0xFFFFFFFF

    __OID_MAP = {
        TypeTag.BOOL: hapi.HYPER_OID_BOOL,
        TypeTag.BIG_INT: hapi.HYPER_OID_BIG_INT,
        TypeTag.SMALL_INT: hapi.HYPER_OID_SMALL_INT,
        TypeTag.INT: hapi.HYPER_OID_INT,
        TypeTag.NUMERIC: hapi.HYPER_OID_NUMERIC,
        TypeTag.FLOAT: hapi.HYPER_OID_FLOAT,
        TypeTag.DOUBLE: hapi.HYPER_OID_DOUBLE,
        TypeTag.OID: hapi.HYPER_OID_OID,
        TypeTag.BYTES: hapi.HYPER_OID_BYTE_A,
        TypeTag.TEXT: hapi.HYPER_OID_TEXT,
        TypeTag.VARCHAR: hapi.HYPER_OID_VARCHAR,
        TypeTag.CHAR: hapi.HYPER_OID_CHAR,
        TypeTag.JSON: hapi.HYPER_OID_JSON,
        TypeTag.DATE: hapi.HYPER_OID_DATE,
        TypeTag.INTERVAL: hapi.HYPER_OID_INTERVAL,
        TypeTag.TIME: hapi.HYPER_OID_TIME,
        TypeTag.TIMESTAMP: hapi.HYPER_OID_TIMESTAMP,
        TypeTag.TIMESTAMP_TZ: hapi.HYPER_OID_TIMESTAMP_TZ,
        TypeTag.TABGEOGRAPHY: hapi.HYPER_OID_TABGEOGRAPHY,
        # Deprecated alias for TABGEOGRAPHY, will be removed as part of W-17701666.
        TypeTag.GEOGRAPHY: hapi.HYPER_OID_GEOGRAPHY,
    }

    def __init__(self, tag: TypeTag, modifier: int = _UNUSED_MODIFIER, oid: int = None):
        self.__tag = tag
        if oid is None:
            if tag == TypeTag.CHAR and modifier == hapi.hyper_encode_string_modifier(1):
                oid = hapi.HYPER_OID_CHAR1
            else:
                oid = SqlType.__OID_MAP[tag]
        self.__oid = oid
        self.__modifier = modifier

    @property
    def tag(self) -> TypeTag:
        """ The underlying type tag, one of the :any:`TypeTag` constants. """
        return self.__tag

    @property
    def internal_oid(self) -> int:
        """ The underlying type OID. This property is internal and may change or go away in the future versions. """
        return self.__oid

    @property
    def internal_type_modifier(self) -> int:
        """
        The underlying type modifier.
        This property is internal and may change or go away in the future versions.
        """
        return self.__modifier

    @property
    def precision(self) -> Optional[int]:
        """ The precision, i.e., maximum number of digits, of a :any:`NUMERIC` value. """
        if self.__tag == TypeTag.NUMERIC:
            return hapi.hyper_get_precision_from_modifier(self.__modifier)
        else:
            return None

    @property
    def scale(self) -> Optional[int]:
        """ The scale, i.e., number of fractional digits, of a :any:`NUMERIC` value. """
        if self.__tag == TypeTag.NUMERIC:
            return hapi.hyper_get_scale_from_modifier(self.__modifier)
        else:
            return None

    @property
    def max_length(self) -> Optional[int]:
        """ The max length of this type if it is :any:`CHAR` or :any:`VARCHAR`, otherwise ``None``. """
        if self.__tag in (TypeTag.CHAR, TypeTag.VARCHAR):
            return hapi.hyper_get_max_length_from_modifier(self.__modifier)
        else:
            return None

    @staticmethod
    def bool() -> 'SqlType':
        """ Creates an instance of a :any:`BOOL` type. """
        return SqlType(TypeTag.BOOL)

    @staticmethod
    def small_int() -> 'SqlType':
        """ Creates an instance of a :any:`SMALL_INT` type. """
        return SqlType(TypeTag.SMALL_INT)

    @staticmethod
    def int() -> 'SqlType':
        """ Creates an instance of an :any:`INT` type. """
        return SqlType(TypeTag.INT)

    @staticmethod
    def big_int() -> 'SqlType':
        """ Creates an instance of a :any:`BIG_INT` type. """
        return SqlType(TypeTag.BIG_INT)

    @staticmethod
    def float() -> 'SqlType':
        """ Creates an instance of a :any:`FLOAT` type. """
        return SqlType(TypeTag.FLOAT)

    @staticmethod
    def double() -> 'SqlType':
        """ Creates an instance of a :any:`DOUBLE` type. """
        return SqlType(TypeTag.DOUBLE)

    @staticmethod
    def oid() -> 'SqlType':
        """ Creates an instance of an :any:`OID` type. """
        return SqlType(TypeTag.OID)

    @staticmethod
    def date() -> 'SqlType':
        """ Creates an instance of a :any:`DATE` type. """
        return SqlType(TypeTag.DATE)

    @staticmethod
    def time() -> 'SqlType':
        """ Creates an instance of a :any:`TIME` type. """
        return SqlType(TypeTag.TIME)

    @staticmethod
    def timestamp() -> 'SqlType':
        """ Creates an instance of a :any:`TIMESTAMP` type. """
        return SqlType(TypeTag.TIMESTAMP)

    @staticmethod
    def timestamp_tz() -> 'SqlType':
        """ Creates an instance of a :any:`TIMESTAMP_TZ` type. """
        return SqlType(TypeTag.TIMESTAMP_TZ)

    @staticmethod
    def interval() -> 'SqlType':
        """ Creates an instance of an :any:`INTERVAL` type. """
        return SqlType(TypeTag.INTERVAL)

    @staticmethod
    def text() -> 'SqlType':
        """ Creates an instance of a :any:`TEXT` type. """
        return SqlType(TypeTag.TEXT)

    @staticmethod
    def json() -> 'SqlType':
        """ Creates an instance of a :any:`JSON` type. """
        return SqlType(TypeTag.JSON)

    @staticmethod
    def tabgeography() -> 'SqlType':
        """ Creates an instance of a :any:`TABGEOGRAPHY` type. """
        return SqlType(TypeTag.TABGEOGRAPHY)

    # Deprecated: Will be removed as part of W-17701666.
    @staticmethod
    def geography() -> 'SqlType':
        """ Creates an instance of a :any:`GEOGRAPHY` type. """
        return SqlType(TypeTag.GEOGRAPHY)

    @staticmethod
    def bytes() -> 'SqlType':
        """ Creates an instance of a :any:`BYTES` type. """
        return SqlType(TypeTag.BYTES)

    @staticmethod
    def char(max_length: _int_type) -> 'SqlType':
        """ Creates an instance of a :any:`CHAR` type. """
        check_precondition(max_length >= 1, "'max_length' must be positive")
        return SqlType(TypeTag.CHAR, hapi.hyper_encode_string_modifier(max_length))

    @staticmethod
    def varchar(max_length: _int_type) -> 'SqlType':
        """ Creates an instance of a :any:`VARCHAR` type. """
        check_precondition(max_length >= 1, "'max_length' must be positive")
        return SqlType(TypeTag.VARCHAR, hapi.hyper_encode_string_modifier(max_length))

    @staticmethod
    def numeric(precision: _int_type, scale: _int_type) -> 'SqlType':
        """ Creates an instance of a :any:`NUMERIC` type. """
        check_precondition(1 <= precision <= 38, "'precision' must be between 1 and 38")
        check_precondition(0 <= scale <= precision, "'scale' must be between 0 and 'precision'")
        return SqlType(TypeTag.NUMERIC, hapi.hyper_encode_numeric_modifier(precision, scale))

    def __as_int_tuple(self):
        return self.__tag.value, self.__modifier, self.__oid

    def __eq__(self, other):
        if not isinstance(other, SqlType):
            return NotImplemented

        return self.__as_int_tuple() == other.__as_int_tuple()

    def __lt__(self, other):
        if not isinstance(other, SqlType):
            return NotImplemented

        return self.__as_int_tuple() < other.__as_int_tuple()

    def __hash__(self):
        return hash(self.__as_int_tuple())

    def __str__(self):
        if self.__tag in (TypeTag.CHAR, TypeTag.VARCHAR):
            return f'{self.__tag.name}({self.max_length})'

        if self.__tag == TypeTag.NUMERIC:
            return f'NUMERIC({self.precision}, {self.scale})'

        # Deprecated alias for TABGEOGRAPHY, will be removed as part of W-17701666.
        if self.__tag == TypeTag.TABGEOGRAPHY or self.__tag == TypeTag.GEOGRAPHY:
            return 'TABLEAU.TABGEOGRAPHY'

        return self.__tag.name

    def __repr__(self):
        cls_name = self.__class__.__name__
        if self.__tag in (TypeTag.CHAR, TypeTag.VARCHAR):
            return f'{cls_name}.{self.__tag.name.lower()}({self.max_length})'

        if self.__tag == TypeTag.NUMERIC:
            return f'{cls_name}.numeric({self.precision}, {self.scale})'

        # Represent both as `geography()` to keep backwards compatibility during the migration phase (W-17701666)
        if self.__tag == TypeTag.TABGEOGRAPHY:
            return f'{cls_name}.geography()'

        return f'{cls_name}.{self.__tag.name.lower()}()'
