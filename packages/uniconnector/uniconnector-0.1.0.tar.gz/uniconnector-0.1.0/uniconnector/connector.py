# uniconnector/connector.py (Upgraded Version)

import sqlite3
from urllib.parse import urlparse # <-- ADD THIS IMPORT

try:
    import psycopg2
except ImportError:
    psycopg2 = None

try:
    import mysql.connector
except ImportError:
    mysql = None

def connect(db_type, **kwargs):
    """
    A factory function to connect to different types of databases.
    Can accept a 'uri' parameter for PostgreSQL and MySQL.
    """
    db_type = db_type.lower()

    # --- START OF NEW FEATURE ---
    # If a URI is provided, parse it and populate kwargs
    if 'uri' in kwargs:
        uri = kwargs.pop('uri') # Remove uri from kwargs to avoid conflicts
        parsed_uri = urlparse(uri)
        kwargs['user'] = parsed_uri.username
        kwargs['password'] = parsed_uri.password
        kwargs['host'] = parsed_uri.hostname
        kwargs['port'] = parsed_uri.port
        # The path includes a leading '/', so we strip it
        kwargs['database'] = parsed_uri.path.lstrip('/')
        # For postgres, the param is 'dbname', not 'database'
        if db_type == 'postgresql':
            kwargs['dbname'] = kwargs.pop('database')
    # --- END OF NEW FEATURE ---

    if db_type == 'sqlite':
        db_path = kwargs.get('database')
        if not db_path:
            raise ValueError("For SQLite, 'database' parameter is required.")
        return sqlite3.connect(db_path)

    elif db_type == 'postgresql':
        if not psycopg2:
            raise ImportError("psycopg2-binary is not installed. Please run 'pip install uniconnector[postgres]'")
        return psycopg2.connect(**kwargs)

    elif db_type == 'mysql':
        if not mysql:
            raise ImportError("mysql-connector-python is not installed. Please run 'pip install uniconnector[mysql]'")
        return mysql.connector.connect(**kwargs)

    else:
        raise ValueError(f"Unsupported database type: {db_type}")