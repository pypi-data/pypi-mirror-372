"""
File containing some utility functions that wrap around various repeatedly used logic
"""
# stdlib
import logging
import time
# lib
import opentracing
# local
from cloudcix.lock_backend import (
    lock_backend_connection,
    create,
    exclusive_lock,
    update,
    verify,
)


__all__ = [
    'ResourceLock',
]


class ResourceLock:

    def __init__(self, target, requestor, span=None):
        self._target = target
        self._requestor = requestor
        self._span = span

    def __enter__(self):
        # Request sole access of the target
        self._request_turn()
        self._wait_for_turn()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._release_turn()

    def _request_turn(self):
        """
        Creates a request record in `lock` database for given target and requestor
        """
        logger = logging.getLogger('cloudcix.locks._request_turn')
        logger.debug(f'Requesting to lock target: {self._target} by Requestor: {self._requestor}')

        if self._span is not None:
            child_span = opentracing.tracer.start_span('critical_section_lock_request', child_of=self._span)

        with lock_backend_connection() as connection:
            with exclusive_lock(connection):
                logger.debug(f'Database locked for Target: {self._target}, Requestor: {self._requestor}')
                columns = 'target, requestor, is_requested'
                values = f"'{self._target}', '{self._requestor}', TRUE"
                create(connection, columns, values)

        logger.debug(f'Request transaction created for Target: {self._target} and Requestor: {self._requestor}')
        if self._span is not None:
            child_span.finish()

    def _wait_for_turn(self):
        """
        Waits for a request record in `lock` database for given target and requestor to get authorised
        ie if `turn` field is True.
        """
        if self._span is not None:
            child_span = opentracing.tracer.start_span('critical_section_wait_for_authorisation', child_of=self._span)

        authorised = False
        while not authorised:
            # Add a delay between reads
            time.sleep(1)
            with lock_backend_connection() as connection:
                # verify record exists
                where = f"target='{self._target}' and requestor='{self._requestor}' and is_requested=TRUE and turn=TRUE"
                authorised = verify(connection, where)
        logger = logging.getLogger('cloudcix.locks._wait_turn')
        logger.debug(f'Request Authorised for Target: {self._target} and Requestor: {self._requestor}')

        if self._span is not None:
            child_span.finish()

    def _release_turn(self):
        """
        Deletes a request record in `lock` database for given target and requestor by setting `is_requested` to False
        """
        logger = logging.getLogger('cloudcix.locks._release_turn')
        logger.debug(f'Releasing the lock target: {self._target} by Requestor: {self._requestor}')

        if self._span is not None:
            child_span = opentracing.tracer.start_span('critical_section_lock_release', child_of=self._span)

        with lock_backend_connection() as connection:
            with exclusive_lock(connection):
                logger.debug(f'Database locked for Target: {self._target}, Requestor: {self._requestor}')
                update_statement = 'is_requested = FALSE'
                where = f"target='{self._target}' and requestor='{self._requestor}' and is_requested=TRUE and turn=TRUE"
                update(connection, update_statement, where)

        if self._span is not None:
            child_span.finish()
