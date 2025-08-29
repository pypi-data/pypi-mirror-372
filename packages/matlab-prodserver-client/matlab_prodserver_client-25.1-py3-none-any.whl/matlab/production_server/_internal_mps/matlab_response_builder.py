# Copyright 2014-2023, The MathWorks, Inc.
#

from matlab.production_server._proto_generated \
    import MATLABArray_pb2 as MATLABArray
from .matlab_array_builder import _int_mw_type
import matlab
import itertools
import os
import sys

def create_matlab_result(ml_output):
    if ml_output.type == MATLABArray.MATLAB_Array.CHAR:
        if not len(ml_output.dimension) == 2 or \
                not ml_output.dimension[0] == 1:
            raise ValueError('Only 1xN char array is supported')
        return ''.join([chr(c) for c in
                        ml_output.mwchar.elements])

    if ml_output.type == MATLABArray.MATLAB_Array.STRUCT:
        if not ml_output.dimension == [1, 1]:
            raise ValueError('Only STRUCT scalar is supported')

        fields = ml_output.struct_.field_names
        values = [create_matlab_result(val)
                  for val in ml_output.struct_.elements]
        output_struct = {}
        for field, value in itertools.zip_longest(fields, values):
            output_struct[field] = value
        return output_struct

    if ml_output.type == MATLABArray.MATLAB_Array.CELL:
        if not len(ml_output.dimension) == 2 or not \
                (ml_output.dimension[0] == 1 or ml_output.dimension[1] == 1):
            raise ValueError('Only 1xN and Nx1 CELL array is supported')
        return [create_matlab_result(val)
                for val in ml_output.cell.elements]

    try:
        message_info = _MATLABResponseBuilder[ml_output.type]
    except KeyError:
        raise TypeError('unsupported matlab type')

    extension_type = message_info['Extension']
    matlab_array = ml_output.__getattribute__(extension_type)
    if ml_output.dimension == [1, 1]:
        if extension_type == 'int8' or extension_type == 'uint8':
            # In Python3 the output has been already converted into integer
            converter = ord if isinstance(matlab_array.elements[0], bytes) else lambda x: x
            if len(matlab_array.imag_elements) == 1:
                return complex(
                    converter(matlab_array.elements[0]),
                    converter(matlab_array.imag_elements[0]))

            return converter(matlab_array.elements[0])

        try:
            if len(matlab_array.imag_elements) == 1:
                return complex(
                    matlab_array.elements[0],
                    matlab_array.imag_elements[0])

            # coerce Long back to Int here if _int_mw_type == INT64
            # and extension_type is '(u)int64'
            if (_int_mw_type == MATLABArray.MATLAB_Array.INT64
                and extension_type == 'int64') or (extension_type == 'int16') \
                    or (extension_type == 'uint16'):
                return int(matlab_array.elements[0])

            return matlab_array.elements[0]
        except AttributeError:
            assert extension_type == 'logical'
            return matlab_array.elements[0]

    else:
        if extension_type == 'int8' or extension_type == 'uint8':
            import array
            ext_to_array_type = {'int8': 'b', 'uint8': 'B'}
            real = array.array(ext_to_array_type[extension_type])
            imag = array.array(ext_to_array_type[extension_type])
            if len(matlab_array.imag_elements) != 0:
                real.frombytes(matlab_array.elements)
                imag.frombytes(matlab_array.imag_elements)
                
                zipped = [(ir + ii*1j) for (ir, ii) in zip(real, imag)]
                mlarr = message_info['MLArray_Constructor'](
                    zipped, size=ml_output.dimension, is_complex=True)
                return mlarr
            real.frombytes(matlab_array.elements)
            
            mlarr = message_info['MLArray_Constructor'](real, size=ml_output.dimension)
            return mlarr

        # elements is a repeatedscalarfieldcontainer type
        # and not a sequence type
        try:
            if len(matlab_array.imag_elements) != 0:
                initializer = [complex(x, y) for x, y in zip(
                    matlab_array.elements,
                    matlab_array.imag_elements)]
                return message_info['MLArray_Constructor'](
                    initializer, ml_output.dimension, is_complex=True)
        except AttributeError:
            assert extension_type == 'logical'

        return message_info['MLArray_Constructor'](
            matlab_array.elements._values,
            ml_output.dimension)


_MATLABResponseBuilder = {
    MATLABArray.MATLAB_Array.UINT8: {'Extension': 'uint8',
                                     'MLArray_Constructor': matlab.uint8},
    MATLABArray.MATLAB_Array.INT8: {'Extension': 'int8',
                                    'MLArray_Constructor': matlab.int8},
    MATLABArray.MATLAB_Array.UINT16: {'Extension': 'uint16',
                                      'MLArray_Constructor': matlab.uint16},
    MATLABArray.MATLAB_Array.INT16: {'Extension': 'int16',
                                     'MLArray_Constructor': matlab.int16},
    MATLABArray.MATLAB_Array.UINT32: {'Extension': 'uint32',
                                      'MLArray_Constructor': matlab.uint32},
    MATLABArray.MATLAB_Array.INT32: {'Extension': 'int32',
                                     'MLArray_Constructor': matlab.int32},
    MATLABArray.MATLAB_Array.UINT64: {'Extension': 'uint64',
                                      'MLArray_Constructor': matlab.uint64},
    MATLABArray.MATLAB_Array.INT64: {'Extension': 'int64',
                                     'MLArray_Constructor': matlab.int64},
    MATLABArray.MATLAB_Array.SINGLE: {'Extension': 'single',
                                      'MLArray_Constructor': matlab.single},
    MATLABArray.MATLAB_Array.DOUBLE: {'Extension': 'mwdouble',
                                      'MLArray_Constructor': matlab.double},
    MATLABArray.MATLAB_Array.LOGICAL: {'Extension': 'logical',
                                       'MLArray_Constructor': matlab.logical},
}
