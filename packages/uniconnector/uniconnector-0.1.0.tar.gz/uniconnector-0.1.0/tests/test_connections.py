# db_unify/connector.py

from .exceptions import UnsupportedDatabaseError, ConnectionError

# We use try/except blocks for imports because a user might only install the drivers they need.
try:
    import psycopg2
    from psycopg2 import OperationalError as PsycopgOpError
except ImportError:
    psycopg2 = None
    PsycopgOpError = None

try:
    import mysql.connector
    from mysql.connector import Error as MySqlError
except ImportError:
    mysql = None
    MySqlError = None
    
try:
    import sqlite3
except ImportError:
    sqlite3 = None # Should always be present in standard Python

SUPPORTED_DRIVERS = {
    'postgresql': psycopg2,
    'mysql': mysql,
    'sqlite': sqlite3
}

def connect(db_type: str, **kwargs):
    """
    A factory function that connects to a database and returns a connection object.

    :param db_type: The type of the database ('postgresql', 'mysql', 'sqlite').
    :param kwargs: The connection parameters (host, user, password, database, etc.).
    :return: A database connection object.
    :raises UnsupportedDatabaseError: if the db_type is not supported or driver not installed.
    :raises ConnectionError: if the connection fails.
    """
    db_type = db_type.lower()

    if db_type not in SUPPORTED_DRIVERS:
        raise UnsupportedDatabaseError(f"Database type '{db_type}' is not supported.")

    if SUPPORTED_DRIVERS[db_type] is None:
         raise UnsupportedDatabaseError(
            f"The driver for '{db_type}' is not installed. "
            f"Please install it (e.g., 'pip install psycopg2-binary' for postgresql)."
        )

    if db_type == 'postgresql':
        try:
            # psycopg2 uses 'dbname' instead of 'database'
            if 'database' in kwargs:
                kwargs['dbname'] = kwargs.pop('database')
            return psycopg2.connect(**kwargs)
        except PsycopgOpError as e:
            raise ConnectionError(f"PostgreSQL connection failed: {e}") from e

    elif db_type == 'mysql':
        try:
            return mysql.connector.connect(**kwargs)
        except MySqlError as e:
            raise ConnectionError(f"MySQL connection failed: {e}") from e
    
    elif db_type == 'sqlite':
        try:
            # SQLite connects to a file path, which we expect in the 'database' keyword.
            db_path = kwargs.get('database')
            if not db_path:
                raise ConnectionError("For SQLite, the 'database' parameter (file path) is required.")
            return sqlite3.connect(db_path)
        except sqlite3.Error as e:
            raise ConnectionError(f"SQLite connection failed: {e}") from e

    # This line should not be reachable due to the initial checks, but is good for safety.
    raise UnsupportedDatabaseError(f"Implementation missing for '{db_type}'.")