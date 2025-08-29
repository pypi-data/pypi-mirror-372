# Copyright 2014-2023 The MathWorks, Inc.
#
import os
import sys
import matlab
import struct
from matlab.production_server._proto_generated \
    import MATLABArray_pb2 as MATLABArray

# Since integers have unlimited precision in Python 3, it makes sense to map them to the largest
# specific size available, namely int64.
_int_mw_type = MATLABArray.MATLAB_Array.INT64
_int_ext = 'int64'

long_type = int
unicode_type = str

def getBytes(arr):
    return arr.tobytes()
    
class MATLABArrayBuilder(object):
    def get_mw_type(self):
        return self.ml_ref.type

    def __init__(self, mw_type):
        self.ml_ref = MATLABArray.MATLAB_Array()
        self.ml_ref.type = mw_type

    def __get_ml_ref__(self):
        return self.ml_ref


class MATLABByteArray(MATLABArrayBuilder):
    def __init__(self, ml_input=[]):
        message_info = _TypeExtensions[type(ml_input)]
        super(MATLABByteArray, self).__init__(message_info['MWType'])

        extension_type = message_info['Extension']
        try:
            self.ml_ref.dimension.extend(ml_input.size)
            if ml_input._is_complex:
                # array.array.tobytes() is called to convert the array to an array of machine values
                # and return the bytes representation.
                self.ml_ref.__getattribute__(extension_type).elements = \
                    getBytes(ml_input._real.toarray())
                self.ml_ref.__getattribute__(extension_type).imag_elements = \
                    getBytes(ml_input._imag.toarray())
            else:
                self.ml_ref.__getattribute__(extension_type).elements = \
                    getBytes(ml_input._data.toarray())
                
        except AttributeError:
            self.ml_ref.dimension.extend([1, len(ml_input)])
            if bytearray == type(ml_input):
                self.ml_ref.__getattribute__(extension_type).elements = \
                    bytes(ml_input)
            elif isinstance(ml_input, bytes):
                self.ml_ref.__getattribute__(extension_type).elements = \
                    ml_input
            else:
                self.ml_ref.__getattribute__(extension_type).elements = \
                   ''.join(chr(x) for x in ml_input).encode()

class MATLABNumericArray(MATLABArrayBuilder):
    def __init__(self, ml_input=[]):
        message_info = _TypeExtensions[type(ml_input)]
        super(MATLABNumericArray, self).__init__(message_info['MWType'])

        extension_type = message_info['Extension']
        try:
            self.ml_ref.dimension.extend(ml_input.size)
            if ml_input._is_complex:
                self.ml_ref.__getattribute__(
                    extension_type).elements.extend(ml_input._real)
                self.ml_ref.__getattribute__(
                    extension_type).imag_elements.extend(ml_input._imag)
            else:
                self.ml_ref.__getattribute__(
                    extension_type).elements.extend(ml_input._data)
        except AttributeError:
            self.ml_ref.dimension.extend([1, 1])
            if isinstance(ml_input, complex):
                self.ml_ref.__getattribute__(
                    extension_type).elements.extend([ml_input.real])
                self.ml_ref.__getattribute__(
                    extension_type).imag_elements.extend([ml_input.imag])
            else:
                self.ml_ref.__getattribute__(
                    extension_type).elements.extend([ml_input])


class MATLABCharArray(MATLABArrayBuilder):
    def __init__(self, ml_input=''):
        super(MATLABCharArray, self).__init__(MATLABArray.MATLAB_Array.CHAR)
        if len(ml_input) == 0:
            self.ml_ref.dimension.extend([0, 0])
        else:
            self.ml_ref.dimension.extend([1, len(ml_input)])
            self.ml_ref.mwchar.elements.extend(
                [ord(x) for x in ml_input])


class MATLABStruct(MATLABArrayBuilder):
    def __init__(self, ml_input={}):
        super(MATLABStruct, self).__init__(MATLABArray.MATLAB_Array.STRUCT)
        self.ml_ref.dimension.extend([1, 1])
        self._fields = ml_input.keys()
        try:
            self.ml_ref.struct_.field_names.extend(
                self._fields)
        except TypeError:
            raise TypeError("field names must be strings")
        self._values = ml_input.values()
        struct_values = [create_matlab_array(val).__get_ml_ref__()
                         for val in self._values]
        self.ml_ref.struct_.elements.extend(
            struct_values)


class MATLABCellArray(MATLABArrayBuilder):
    def __init__(self, ml_input=[]):
        super(MATLABCellArray, self).__init__(MATLABArray.MATLAB_Array.CELL)
        self.ml_ref.dimension.extend([1, len(ml_input)])
        self.ml_ref.cell.elements.extend(
            [(create_matlab_array(val)).__get_ml_ref__() for val in ml_input])


_MATLABArrayBuilderClass = {
    matlab.uint8: MATLABByteArray,
    matlab.int8: MATLABByteArray,
    matlab.uint16: MATLABNumericArray,
    matlab.int16: MATLABNumericArray,
    matlab.uint32: MATLABNumericArray,
    matlab.int32: MATLABNumericArray,
    matlab.uint64: MATLABNumericArray,
    matlab.int64: MATLABNumericArray,
    matlab.single: MATLABNumericArray,
    matlab.double: MATLABNumericArray,
    matlab.logical: MATLABNumericArray,
    bool: MATLABNumericArray,
    int: MATLABNumericArray,
    long_type: MATLABNumericArray,
    float: MATLABNumericArray,
    complex: MATLABNumericArray,
    bytes: MATLABByteArray,
    bytearray: MATLABByteArray,
    list: MATLABCellArray,
    tuple: MATLABCellArray,
    dict: MATLABStruct,
    set: MATLABCellArray,
    frozenset: MATLABCellArray,
    str: MATLABCharArray,
    unicode_type: MATLABCharArray
}

_TypeExtensions = {
    matlab.uint8: {'MWType': MATLABArray.MATLAB_Array.UINT8,
                   'Extension': 'uint8'},
    matlab.int8: {'MWType': MATLABArray.MATLAB_Array.INT8,
                  'Extension': 'int8'},
    matlab.uint16: {'MWType': MATLABArray.MATLAB_Array.UINT16,
                    'Extension': 'uint16'},
    matlab.int16: {'MWType': MATLABArray.MATLAB_Array.INT16,
                   'Extension': 'int16'},
    matlab.uint32: {'MWType': MATLABArray.MATLAB_Array.UINT32,
                    'Extension': 'uint32'},
    matlab.int32: {'MWType': MATLABArray.MATLAB_Array.INT32,
                   'Extension': 'int32'},
    matlab.uint64: {'MWType': MATLABArray.MATLAB_Array.UINT64,
                    'Extension': 'uint64'},
    matlab.int64: {'MWType': MATLABArray.MATLAB_Array.INT64,
                   'Extension': 'int64'},
    matlab.single: {'MWType': MATLABArray.MATLAB_Array.SINGLE,
                    'Extension': 'single'},
    matlab.double: {'MWType': MATLABArray.MATLAB_Array.DOUBLE,
                    'Extension': 'mwdouble'},
    matlab.logical: {'MWType': MATLABArray.MATLAB_Array.LOGICAL,
                     'Extension': 'logical'},
    # build-in python types
    bool: {'MWType': MATLABArray.MATLAB_Array.LOGICAL,
           'Extension': 'logical'},
    int: {'MWType': _int_mw_type,
          'Extension': _int_ext},
    long_type: {'MWType': MATLABArray.MATLAB_Array.INT64,
           'Extension': 'int64'},
    float: {'MWType': MATLABArray.MATLAB_Array.DOUBLE,
            'Extension': 'mwdouble'},
    complex: {'MWType': MATLABArray.MATLAB_Array.DOUBLE,
              'Extension': 'mwdouble'},
    bytes: {'MWType': MATLABArray.MATLAB_Array.UINT8,
            'Extension': 'uint8'},
    bytearray: {'MWType': MATLABArray.MATLAB_Array.UINT8,
                'Extension': 'uint8'},
}


def create_matlab_array(input):
    try:
        return _MATLABArrayBuilderClass[type(input)](input)
    except KeyError:
        raise TypeError("unsupported python type : " + str(type(input)))
