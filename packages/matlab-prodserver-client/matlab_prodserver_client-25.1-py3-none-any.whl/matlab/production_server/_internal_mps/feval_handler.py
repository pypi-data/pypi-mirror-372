# Copyright 2014-2022, The MathWorks, Inc.
#

from .invocation_handler_utils import create_matlab_params, \
    process_matlab_response, check_matlab_result_for_errors
from matlab.production_server._proto_generated import MATLABResult_pb2
from matlab.production_server.mpsexceptions import IllegalStateError, \
    MATLABException, InvalidSchemeError
from urllib import parse
import http.client as httplib
import sys
from sys import platform
if sys.platform != 'darwin':
    import ssl



class FevalHandler(object):
    def __init__(self, client):
        parsed = parse.urlparse(client.url)
        self._scheme = parsed.scheme
        if not self._scheme == 'http' and not self._scheme == 'https':
            raise InvalidSchemeError('MWHttpClient only supports HTTP and HTTPS')
        self._hostname = parsed.hostname
        self._port = parsed.port
        self._client = client
        self._conn = None
        self._context = client.ssl_context
        self._reset_connection()

    def _reset_connection(self):
        if self._conn:
            self._conn.close()

        if self._scheme == 'http':
            self._conn = httplib.HTTPConnection(self._hostname, self._port, timeout=self._client.timeout)
        elif self._scheme == 'https':
            self._conn = httplib.HTTPSConnection(self._hostname, self._port, timeout=self._client.timeout,
                                                     context=self._context)
        self._is_close = False
        self._conn.connect()

        if self._client.timeout:
            self._conn.sock.settimeout(self._client.timeout)

    def process_request(self, ctf, ml_func, *args, **kwargs):
        if self._is_close:
            raise IllegalStateError(
                "This instance of MWHttpClient is in the closed state. " +
                "Once closed, an instance of MWHttpClient cannot be used "
                "to create a proxy instance. " +
                "You will have to create a new instance of MWHttpClient.")
        matlab_params = create_matlab_params(*args, **kwargs)
        serialized_data = matlab_params.SerializeToString()
        resource_id = parse.quote('/' + ctf.name + '/' + ml_func)
        headers = {"User-Agent": "MATLAB Production Server Python client",
                   "Content-Type": "application/x-google-protobuf"}

        self._conn.request('POST', resource_id, serialized_data,
                           headers=headers)
        try:
            response = self._conn.getresponse()
            data = response.read()
        except:
            # We've likely timed out on the connection; we must burn this one
            #  because we're unwilling to wait any longer for more data, which
            # renders this socket useless
            #
            self._reset_connection()
            raise
        if not response.status == 200:
            raise httplib.HTTPException(response.reason)
        matlab_result = MATLABResult_pb2.MATLAB_Result()
        matlab_result.ParseFromString(data)
        check_matlab_result_for_errors(ml_func, matlab_params, matlab_result)
        return process_matlab_response(matlab_params.nargout, matlab_result)
