# -*- coding: utf-8 -*-

"""
This module implements the CloudCIX API JSON Encodes and Decoders, along with other utilities to improve the quality of
life for anyone using the CloudCIX library.
"""

import datetime
import decimal
import json
import re
import uuid
from dateutil import parser

DATETIME_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2})?(\.\d+)?(Z|[+-]\d{2}:?\d{2})?$')
DATE_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}$')
IP_PATTERN = re.compile(r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}')
TIME_PATTERN = re.compile(r'^\d{2}:\d{2}(:\d{2})(\.\d+)?$')


class JSONEncoder(json.JSONEncoder):
    """
    JSONEncoder that can encode date/time/timedelta, decimal and other python objects into JSON.

    Inspired by Django Rest Framework
    """

    def default(self, obj):
        """
        Converts the passed object into its JSON representation, usually by converting them into a string.

        :param obj: The object to be converted into JSON
        :type obj: object
        """
        if isinstance(obj, datetime.datetime):
            rep = obj.isoformat()
            if rep.endswith('+00:00'):
                rep = rep[:-6] + 'Z'
            return rep
        elif isinstance(obj, datetime.date):
            return obj.isoformat()
        elif isinstance(obj, datetime.time):
            # Check to ensure the time isn't timezone aware
            if obj.utcoffset() is not None:
                raise ValueError('JSON cannot represent timezone-aware times')
            rep = obj.isoformat()
            if obj.microsecond:
                rep = rep[:12]
            return rep
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        elif isinstance(obj, uuid.UUID):
            return str(obj)
        elif hasattr(obj, '__getitem__'):
            try:
                return dict(obj)
            except (KeyError, ValueError):
                pass
        elif hasattr(obj, '__iter__'):
            return tuple(item for item in obj)
        return super(JSONEncoder, self).default(obj)


class JSONDecoder(json.JSONDecoder):
    """
    JSONDecoder that can decode date/time/timedelta, decimal and other strings into python objects.

    Inspired by Django Rest Framework.
    """

    def __init__(self, *args, **kwargs):
        """
        Create an instance of the Decoder.

        See :py:class:`json.JSONDecoder` for the constructor parameters.
        """
        kwargs.pop('encoding', None)
        super(JSONDecoder, self).__init__(
            *args,
            object_hook=self.parse,
            parse_float=decimal.Decimal,
            **kwargs,
        )

    def parse(self, obj):
        """
        Parse a JSON value into its python equivalent.

        If the value is an iterable, this method will be called recursively on every item contained within the value.

        :param obj: The JSON object to be decoded into Python.
        :type obj: Any
        """
        if hasattr(obj, 'items'):
            for k, v in obj.items():
                obj[k] = self.parse(v)
        elif isinstance(obj, str):
            if IP_PATTERN.match(obj):
                return obj  # Skip IP addresses
            try:
                num = float(obj)
                return int(num) if num.is_integer() else num
            except ValueError:
                pass
            # Check for specific time format
            if TIME_PATTERN.match(obj):
                try:
                    return datetime.datetime.strptime(obj, '%H:%M:%S.%f').time()
                except ValueError:
                    try:
                        return datetime.datetime.strptime(obj, '%H:%M:%S').time()
                    except ValueError:
                        pass
            # Check for specific date format
            if DATE_PATTERN.match(obj):
                try:
                    return datetime.datetime.strptime(obj, '%Y-%m-%d').date()
                except ValueError:
                    pass
            # Check for ISO-like datetime only if pattern matches
            if DATETIME_PATTERN.match(obj):
                try:
                    return parser.parse(obj)
                except Exception:
                    pass
        return obj
