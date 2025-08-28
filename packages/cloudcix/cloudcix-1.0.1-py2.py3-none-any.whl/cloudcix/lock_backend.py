"""
Functions for interacting with a the backend of the lock for cirtical sections.

"""
# stdlib
import logging
from contextlib import contextmanager
# lib
from psycopg2 import connect, sql
# local
import cloudcix.conf


__all__ = [
    'lock_backend_connection',
    'create',
    'exclusive_lock',
    'read',
    'update',
    'verify',
]


def lock_backend_connection():
    """
    Creates a database connect session
    """
    db_params = {
        'database': 'lock',
        'user': cloudcix.conf.settings.CLOUDCIX_LOCK_USER,
        'password': cloudcix.conf.settings.CLOUDCIX_LOCK_CREDENTIALS,
        'host': cloudcix.conf.settings.CLOUDCIX_LOCK_HOST,
        'port': cloudcix.conf.settings.CLOUDCIX_LOCK_PORT,
    }
    return connect(**db_params)


def create(
    connection: connect,
    columns: str,
    values: str,
):
    """
    creates a new db record with columns for given values
    connection: connect, Locks db connection session
    columns: str, key fields of record, e.g. columns = f'target, requestor, request'
    values: str, value fields of record, e.g. values = f'"KVM #10", "Build-Bridge-Build-VM #123", "TRUE"'
    """

    logger = logging.getLogger('cloudcix.locks_backend.create')
    query = f'INSERT INTO request ({columns}) VALUES ({values});'
    logger.debug(f'Executing DB query: {query}')
    with connection.cursor() as cursor:
        cursor.execute(query)
        connection.commit()


@contextmanager
def exclusive_lock(
    connection: connect,
):
    """
    Lock a database table from modification for the duration of the context manager.
    connection: connect, Locks db connection session
    """
    logger = logging.getLogger('cloudcix.locks_backend.exclusive_lock')
    query = 'LOCK TABLE request IN EXCLUSIVE MODE'
    logger.debug(f'Executing DB query: {query}')
    with connection.cursor() as cursor:
        cursor.execute(sql.SQL(query))
        try:
            # Context manager needs one yield statement
            yield
        finally:
            if cursor and not cursor.closed:
                cursor.close()


def read(
    connection: connect,
    select: str,
    where: str,
):
    """
    reads the db record with columns for given where
    connection: connect, Locks db connection session
    columns: list, load the required fields, eg columns=['turn']
    where: string, identifier of db record
    """
    logger = logging.getLogger('cloudcix.locks_backend.read')
    query = f'SELECT {select} FROM request WHERE {where} ;'
    logger.debug(f'Executing DB query: {query}')
    with connection.cursor() as cursor:
        cursor.execute(query)
        record = cursor.fetchone()
    return record


def update(
    connection: connect,
    update_statement: str,
    where: str,
):
    """
    updates the `request` record with columns for given where
    connection: connect, Locks db connection session
    columns: string, changes to apply, eg columns='request=FALSE'
    where: string, identifier of db record
    """
    logger = logging.getLogger('cloudcix.locks_backend.update')
    query = f'UPDATE request SET {update_statement} WHERE {where};'
    logger.debug(f'Executing DB query: {query}')
    with connection.cursor() as cursor:
        cursor.execute(query)
        connection.commit()


def verify(
    connection: connect,
    where: str,
):
    """
    Verifies a record exists in the request` table for the given where
    connection: connect, establishes db connection session
    where: string, identifier of db record
    returns: True or False
    """
    logger = logging.getLogger('cloudcix.locks_backend.verify')
    query = f'SELECT CASE WHEN EXISTS (SELECT 1 FROM request WHERE {where}) '
    query += 'THEN CAST (1 AS BIT) ELSE CAST (0 AS BIT) END;'
    logger.debug(f'Executing DB query: {query}')
    with connection.cursor() as cursor:
        cursor.execute(query)
        result = bool(int(cursor.fetchone()[0]))
    return result
