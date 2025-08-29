# Copyright 2014, The MathWorks, Inc.
#

import os


class MATLABException(Exception):
    def __init__(self, matlab_error):
        self.ml_error_message = matlab_error.message
        self.ml_error_identifier = matlab_error.identifier
        self.ml_error_stack = matlab_error.stack

    def __repr__(self):
        return self.ml_error_message + os.linesep + self.ml_error_identifier

    def __str__(self):
        stack = ''
        for s in self.ml_error_stack:
            stack += 'Error in => file: ' + s.file + ',function name: ' + \
                     s.name + ',at line: ' + str(s.line) + os.linesep
        return self.ml_error_message + os.linesep + stack


class NargoutMismatchError(Exception):
    def __init__(self, function_name, matlab_params, matlab_result):
        self.ml_params = matlab_params
        self.ml_result = matlab_result
        self.ml_func = function_name

    def __str__(self):
        return "Incorrect number of outputs returned from MATLAB. " \
               "MATLAB Returned " + len(self.ml_result.lhs) + \
               " number of outputs. " + "Method ," + self.ml_func + \
               ", expected " + self.ml_params.nargout + " number of outputs."


class IllegalStateError(Exception):
    def __init__(self, value):
        self._value = value

    def __str__(self):
        return self._value

    def __repr__(self):
        return self._value


class InvalidSchemeError(Exception):
    def __init__(self, value):
        self._value = value

    def __str__(self):
        return self._value

    def __repr__(self):
        return self._value
