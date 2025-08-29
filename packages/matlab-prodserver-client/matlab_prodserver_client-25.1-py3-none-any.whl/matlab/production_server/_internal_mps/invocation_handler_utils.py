# Copyright 2014-2022, The MathWorks, Inc.
#

from .matlab_array_builder import create_matlab_array
from .matlab_response_builder import create_matlab_result
from matlab.production_server.mpsexceptions \
    import MATLABException, NargoutMismatchError
from matlab.production_server._proto_generated import MATLABParams_pb2

def create_matlab_params(*args, **kwargs):
    """
    creates serializable message for input arguments
    """
    matlab_params = MATLABParams_pb2.MATLAB_Params()
    matlab_params.nargout = 1
    for key, value in kwargs.items():
        if key == 'nargout':
            if not isinstance(value, int):
                raise TypeError(
                    'number of output arguments should be a non-negative int')
            if value < 0:
                raise ValueError('nargout value out of range')
            matlab_params.nargout = value
        else:
            raise TypeError('unexpected keyword argument : ' + str(key))
    ml_ref = [(create_matlab_array(arg)).__get_ml_ref__() for arg in args]
    matlab_params.rhs.extend(ml_ref)
    return matlab_params


def process_matlab_response(nargout, matlab_result):
    """
    returns MATLAB result to Python
    """
    response = matlab_result.lhs
    result = [create_matlab_result(ml_output) for ml_output in response]
    if nargout == 1:
        return result[0]
    return result


def check_matlab_result_for_errors(function_name,
                                   matlab_params, matlab_result):
    """
    check MATLAB response for errors
    """
    matlab_error = matlab_result.error
    if matlab_error.message:
        raise MATLABException(matlab_result.error)

    if not (matlab_params.nargout == len(matlab_result.lhs)):
        raise NargoutMismatchError(function_name, matlab_params, matlab_result)
