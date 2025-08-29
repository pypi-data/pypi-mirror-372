# Copyright 2014 MathWorks, Inc.
"""
Manage the connection to a MATLAB Production Server instance and evaluates
MATLAB functions.

This module creates and manages that connection to a MATLAB Production Server
instance. The connection object is used to evaluate MATLAB functions hosted on
the server instance. To evaluate
a MATLAB function, you must know:
    * the name of the function
    * the number of input arguments
    * the number of output arguments
    * the name of the archive hosting the function

Classes
-------
    MWHttpClient : Encapsulates the connection to a
    MATLAB Production Server instance

Example
-------
    >>> import matlab
    >>> from production_server import client
    >>> myClient = client.MHHttpClient(...)
    >>> result = myClient.archive.func(...)
    >>> myClient.close()
"""

__all__ = ['MWHttpClient']

import sys

from production_server._internal_mps.feval_handler import FevalHandler
from sys import platform
from matlab.production_server.mpsexceptions import InvalidSchemeError

class MWHttpClient(object):
    """
    Encapsulate the connection to a server instance and provide a way to
    evaluate hosted functions

    This class creates a connection object encapsulating the connection
    between the client and a server instance. Once created the connection
    gains methods that represent all of the MATLAB functions hosted on the
    server instance. The signature for the methods are:
        client.<archivename>.<functionname>(args...,nargout=<numArgs>)

    Methods
    -------
    close : Close the connection to the server instance.
    """

    def __init__(self, url, timeout_ms=120 * 1000, ssl_context=None):
        """
        Create and initialize a connection to a
        MATLAB Production Server instance.

        :param url : string
          URL of a MATLAB Production Server instance.
        :param timeout_ms : int
          Number of milliseconds the client waits for a response before timing
          out. Default 2 minutes.
        :param ssl_context : SSL
          ssl context that is needed when the protocol in url is https.
        """
        self.url = url

        if url.startswith('https:'):
            if sys.platform == 'darwin':
                raise InvalidSchemeError('HTTPS is not supported on macOS')
            if ssl_context is None:
                raise ValueError(
                    'ssl context is needed')
            else:
                self.ssl_context = ssl_context

        if timeout_ms is not None:
            if not isinstance(timeout_ms, int):
                raise TypeError(
                    'can only assign a non-negative int type to timeout_ms')
            if timeout_ms < 0:
                raise ValueError('timeout value out of range')
            self.timeout = float(timeout_ms / 1000.0)
        else:
            self.timeout = timeout_ms
        self._feval_handler = FevalHandler(self)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __getattr__(self, item):
        if item not in self.__dict__:
            return _CTFProxy(self, item)
        else:
            self.__getitem__(item)

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    def close(self):
        """
        Close the connection to a MATLAB Production Server instance.
        """
        self._feval_handler._is_close = True
        self._feval_handler._conn.close()


class _CTFProxy(object):
    def __init__(self, client, ctf_name):
        self.client = client
        self.name = ctf_name

    def __getattr__(self, item):
        if item not in self.__dict__:
            return _matlab_function(self, item)
        else:
            self.__getitem__(item)

    def __setattr__(self, key, value):
        self.__dict__[key] = value


def _matlab_function(ctf, ml_func):
    def func(*args, **kwargs):
        try:
            matlab_result = ctf.client._feval_handler.process_request(
                ctf, ml_func, *args, **kwargs)
            ml_func_pointer = lambda *args, **kwargs: \
                ctf.client._feval_handler.process_request(
                    ctf, ml_func, *args, **kwargs)
            setattr(ctf, ml_func, ml_func_pointer)
            setattr(ctf.client, ctf.name, ctf)
            return matlab_result
        except Exception as ex:
            raise ex

    return func
