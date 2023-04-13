#include <Python.h>
#include <stdint.h>


static PyObject *calculate_crc(PyObject *self, PyObject *data_bytes) {
    uint8_t *data;
    Py_ssize_t data_len;

    if (PyBytes_Check(data_bytes)) {
        Py_INCREF(data_bytes);
        data = (uint8_t *)PyBytes_AsString(data_bytes);
        data_len = PyBytes_Size(data_bytes);

    } else if (PyByteArray_Check(data_bytes)) {
        Py_INCREF(data_bytes);
        data = (uint8_t *)PyByteArray_AsString(data_bytes);
        data_len = PyByteArray_Size(data_bytes);

    } else {
        data_bytes = PyObject_Bytes(data_bytes);
        if (!data_bytes)
            return NULL;

        data = (uint8_t *)PyBytes_AsString(data_bytes);
        data_len = PyBytes_Size(data_bytes);
    }


    uint16_t crc = 0xFFFF;

    for (size_t i = 0; i < data_len; ++i) {
        crc ^= (uint16_t)data[i];
        for (size_t j = 0; j < 8; ++j) {
            if (crc & 1) {
                crc = (crc >> 1) ^ 0xA001;
            } else {
                crc >>= 1;
            }
        }
    }

    Py_DECREF(data_bytes);
    return PyLong_FromLong(crc);
}


PyMethodDef methods[] = {{.ml_name = "calculate_crc",
                          .ml_meth = (PyCFunction)calculate_crc,
                          .ml_flags = METH_O},
                         {NULL}};


PyModuleDef module_def = {.m_base = PyModuleDef_HEAD_INIT,
                          .m_name = "_encoder",
                          .m_methods = methods};


PyMODINIT_FUNC PyInit__encoder() { return PyModule_Create(&module_def); }
