import ctypes
import ctypes.util

from hat import util


def des_encrypt(des_key: util.Bytes,
                data: util.Bytes,
                iv: util.Bytes
                ) -> util.Bytes:
    return _DES_ncbc_encrypt(des_key, data, iv, True)


def des_decrypt(des_key: util.Bytes,
                data: util.Bytes,
                iv: util.Bytes
                ) -> util.Bytes:
    return _DES_ncbc_encrypt(des_key, data, iv, False)


def _DES_ncbc_encrypt(des_key, data, iv, encrypt):
    if _lib is None:
        raise Exception('not initialized')

    if len(des_key) != 8:
        raise Exception('invalid key length')

    if len(iv) != 8:
        raise Exception('invalid iv length')

    c_des_key = ctypes.create_string_buffer(bytes(des_key), 8)
    c_iv = ctypes.create_string_buffer(bytes(iv), 8)

    c_schedule = ctypes.create_string_buffer(16 * 16)
    _lib.DES_set_key_unchecked(c_des_key, c_schedule)

    data_len = len(data)
    if data_len % 8:
        data_len += (8 - (data_len % 8))

    c_input = ctypes.create_string_buffer(bytes(data), data_len)
    c_ouput = ctypes.create_string_buffer(data_len)

    _lib.DES_ncbc_encrypt(c_input, c_ouput, data_len, c_schedule, c_iv,
                          int(encrypt))

    return bytes(c_ouput)


class _Lib:

    def __init__(self):
        path = ctypes.util.find_library('ssl')
        self._lib = ctypes.cdll.LoadLibrary(path)

        self._lib.DES_set_key_unchecked.argtypes = [ctypes.c_void_p,
                                                    ctypes.c_void_p]
        self._lib.DES_set_key_unchecked.restype = None

        self._lib.DES_ncbc_encrypt.argtypes = [ctypes.c_void_p,
                                               ctypes.c_void_p,
                                               ctypes.c_long,
                                               ctypes.c_void_p,
                                               ctypes.c_void_p,
                                               ctypes.c_int]
        self._lib.DES_ncbc_encrypt.restype = None

        self.DES_set_key_unchecked = self._lib.DES_set_key_unchecked
        self.DES_ncbc_encrypt = self._lib.DES_ncbc_encrypt


try:
    _lib = _Lib()

except Exception:
    _lib = None
