import enum
import iris
import datetime

class Cursor(iris.irissdk.dbapiCursor): pass

class DataRow(iris.irissdk.dbapiDataRow): pass

class SQLType(enum.IntEnum):
    BIGINT = -5
    BINARY = -2
    BIT = -7
    CHAR = 1
    DECIMAL = 3
    DOUBLE = 8
    FLOAT = 6
    GUID = -11
    INTEGER = 4
    LONGVARBINARY = -4
    LONGVARCHAR = -1
    NUMERIC = 2
    REAL = 7
    ROWID = -12
    SMALLINT = 5
    DATE = 9
    TIME = 10
    TIMESTAMP = 11
    TINYINT = -6
    TYPE_DATE = 91
    TYPE_TIME = 92
    TYPE_TIMESTAMP = 93
    VARBINARY = -3
    VARCHAR = 12
    WCHAR = -8
    WLONGVARCHAR = -10
    WVARCHAR = -9
    DATE_HOROLOG = 1091
    TIME_HOROLOG = 1092
    TIMESTAMP_POSIX = 1093


# exceptions

class Warning(Exception):
    """Exception raised for important warnings."""


class Error(Exception):
    """Exception that is the base class of all other error exceptions."""


class InterfaceError(Error):
    """Exception raised for errors that are related to the database interface
    rather than the database itself."""


class DatabaseError(Error):
    """Exception raised for errors that are related to the database."""


class DataError(DatabaseError):
    """Exception raised for errors that are due to problems with the processed
    data."""


class OperationalError(DatabaseError):
    """Exception raised for errors that are related to the database's operation
    and not necessarily under the control of the programmer."""


class IntegrityError(DatabaseError):
    """Exception raised when the relational integrity of the database is
    affected."""


class InternalError(DatabaseError):
    """Exception raised when the database encounters an internal error."""


class ProgrammingError(DatabaseError):
    """Exception raised for programming errors under the user's control."""


class NotSupportedError(DatabaseError):
    """Exception raised in case a method or database API was used which is not
    supported by the database."""


# globals
apilevel = "2.0"
threadsafety = 1
paramstyle = "qmark"

# Type Objects and Constructors

_EPOCH = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)

def Date(year: int, month: int, day: int):
    return datetime.date(year, month, day)

def Time(hour: int, minute: int, second: int):
    return datetime.time(hour, minute, second)

def Timestamp(year: int, month: int, day: int, hour: int, minute: int, second: int):
    return datetime.datetime(year, month, day, hour, minute, second)

def DateFromTicks(ticks: int):
    return TimestampFromTicks(ticks).date()

def TimeFromTicks(ticks: int):
    return TimestampFromTicks(ticks).time()

def TimestampFromTicks(ticks: int):
    return (_EPOCH + datetime.timedelta(seconds=ticks)).replace(tzinfo=None)

def Binary(string):
    if isinstance(string, bytes):
        return string
    elif isinstance(string, str):
        return string.encode()
    else:
        raise TypeError("string or bytes object expected")

class _DBAPITypeObject:
    def __init__(self, *values):
        self._values = values
    def __eq__(self, other):
        return other in self._values

STRING = _DBAPITypeObject(
    SQLType.CHAR,
    SQLType.GUID,
    SQLType.LONGVARCHAR,
    SQLType.VARCHAR,
    SQLType.WCHAR,
    SQLType.WLONGVARCHAR,
    SQLType.WVARCHAR
)
BINARY = _DBAPITypeObject(
    SQLType.BINARY,
    SQLType.LONGVARBINARY,
    SQLType.VARBINARY
)
NUMBER = _DBAPITypeObject(
    SQLType.BIGINT,
    SQLType.BIT,
    SQLType.DECIMAL,
    SQLType.DOUBLE,
    SQLType.FLOAT,
    SQLType.INTEGER,
    SQLType.NUMERIC,
    SQLType.REAL,
    SQLType.SMALLINT,
    SQLType.TINYINT
)
DATETIME = _DBAPITypeObject(
    SQLType.DATE,
    SQLType.TIME,
    SQLType.TIMESTAMP,
    SQLType.TYPE_DATE,
    SQLType.TYPE_TIME,
    SQLType.TYPE_TIMESTAMP,
    SQLType.DATE_HOROLOG,
    SQLType.TIME_HOROLOG,
    SQLType.TIMESTAMP_POSIX
)
ROWID = _DBAPITypeObject(
    SQLType.ROWID
)

def connect(*args, **kwargs):
    # same as iris.connect, except DB-API exceptions may be raised
    connection = iris.IRISConnection()
    connection._connect_dbapi(*args, **kwargs)
    return connection


connect.__doc__ = iris.connect.__doc__
