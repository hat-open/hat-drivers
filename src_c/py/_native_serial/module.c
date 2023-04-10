#include <Python.h>
#include <stdbool.h>
#include <hat/py_allocator.h>
#include <hat/serial.h>


// clang-format off
typedef struct {
    PyObject_HEAD
    hat_serial_t *serial;
    PyObject *empty_tuple;
    PyObject *close_cb;
    PyObject *in_cb;
    PyObject *out_cb;
} Serial;
// clang-format on


static void on_serial_close(hat_serial_t *s) {
    Serial *self = (Serial *)hat_serial_get_ctx(s);

    if (!self->close_cb || self->close_cb == Py_None)
        return;

    PyGILState_STATE gstate = PyGILState_Ensure();

    Py_XDECREF(PyObject_Call(self->close_cb, self->empty_tuple, NULL));

    PyGILState_Release(gstate);
}


static void on_serial_in(hat_serial_t *s) {
    Serial *self = (Serial *)hat_serial_get_ctx(s);

    if (!self->in_cb || self->in_cb == Py_None)
        return;

    PyGILState_STATE gstate = PyGILState_Ensure();

    Py_XDECREF(PyObject_Call(self->in_cb, self->empty_tuple, NULL));

    PyGILState_Release(gstate);
}


static void on_serial_out(hat_serial_t *s) {
    Serial *self = (Serial *)hat_serial_get_ctx(s);

    if (!self->out_cb || self->out_cb == Py_None)
        return;

    PyGILState_STATE gstate = PyGILState_Ensure();

    Py_XDECREF(PyObject_Call(self->out_cb, self->empty_tuple, NULL));

    PyGILState_Release(gstate);
}


static PyObject *Serial_new(PyTypeObject *type, PyObject *args,
                            PyObject *kwds) {
    Py_ssize_t in_buff_size;
    Py_ssize_t out_buff_size;
    if (!PyArg_ParseTupleAndKeywords(
            args, kwds, "nn", (char *[]){"in_buff_size", "out_buff_size", NULL},
            &in_buff_size, &out_buff_size))
        return NULL;

    Serial *self = (Serial *)PyType_GenericAlloc(type, 0);
    if (!self)
        return NULL;

    self->serial = NULL;
    self->empty_tuple = NULL;
    self->close_cb = NULL;
    self->in_cb = NULL;
    self->out_cb = NULL;

    self->empty_tuple = PyTuple_New(0);
    if (!self->empty_tuple) {
        Py_DECREF(self);
        return NULL;
    }

    self->serial =
        hat_serial_create(&hat_py_allocator, in_buff_size, out_buff_size,
                          on_serial_close, on_serial_in, on_serial_out, self);
    if (!self->serial) {
        Py_DECREF(self);
        PyErr_SetString(PyExc_RuntimeError, "error creating serial object");
        return NULL;
    }

    return (PyObject *)self;
}


static void Serial_dealloc(Serial *self) {
    if (self->serial)
        hat_serial_destroy(self->serial);

    Py_XDECREF(self->empty_tuple);
    Py_XDECREF(self->close_cb);
    Py_XDECREF(self->in_cb);
    Py_XDECREF(self->out_cb);

    PyObject_Free((PyObject *)self);
}


static PyObject *Serial_open(Serial *self, PyObject *args, PyObject *kwargs) {
    PyObject *port_str;
    unsigned long baudrate;
    unsigned char byte_size;
    int parity;
    unsigned char stop_bits;
    int xonxoff;
    int rtscts;
    int dsrdtr;
    if (!PyArg_ParseTupleAndKeywords(
            args, kwargs, "O!kbCbppp",
            (char *[]){"port", "baudrate", "byte_size", "parity", "stop_bits",
                       "xonxoff", "rtscts", "dsrdtr", NULL},
            &PyUnicode_Type, &port_str, &baudrate, &byte_size, &parity,
            &stop_bits, &xonxoff, &rtscts, &dsrdtr))
        return NULL;

    PyObject *port_bytes = PyUnicode_AsUTF8String(port_str);
    if (!port_bytes)
        return NULL;

    char *port = PyBytes_AsString(port_bytes);
    if (!port) {
        Py_DECREF(port_bytes);
        return NULL;
    }

    int result = hat_serial_open(self->serial, port, baudrate, byte_size,
                                 parity, stop_bits, xonxoff, rtscts, dsrdtr);

    Py_DECREF(port_bytes);

    if (result) {
        PyErr_SetString(PyExc_RuntimeError, "error opening serial port");
        return NULL;
    }

    Py_RETURN_NONE;
}


static PyObject *Serial_close(Serial *self, PyObject *args) {
    hat_serial_close(self->serial);

    Py_RETURN_NONE;
}


static PyObject *Serial_read(Serial *self, PyObject *args) {
    size_t data_len = hat_serial_get_in_buff_len(self->serial);

    if (!data_len)
        Py_RETURN_NONE;

    PyObject *data_bytes = PyBytes_FromStringAndSize(NULL, data_len);
    if (!data_bytes)
        return NULL;

    uint8_t *data = (uint8_t *)PyBytes_AsString(data_bytes);
    int result = hat_serial_read(self->serial, data, data_len);

    if (result) {
        Py_DECREF(data_bytes);
        PyErr_SetString(PyExc_RuntimeError, "read error");
    }

    return data_bytes;
}


static PyObject *Serial_write(Serial *self, PyObject *data_bytes) {
    if (!PyBytes_Check(data_bytes)) {
        PyErr_SetString(PyExc_ValueError, "invalid data");
        return NULL;
    }

    Py_ssize_t data_len = PyBytes_Size(data_bytes);
    if (data_len < 0)
        return NULL;

    size_t buff_size = hat_serial_get_out_buff_size(self->serial);
    size_t buff_len = hat_serial_get_out_buff_len(self->serial);

    if (data_len > buff_size - buff_len)
        data_len = buff_size - buff_len;

    if (data_len == 0)
        return PyLong_FromLong(0);

    uint8_t *data = (uint8_t *)PyBytes_AsString(data_bytes);
    int result = hat_serial_write(self->serial, data, data_len);

    if (result)
        return PyLong_FromLong(-1);

    return PyLong_FromLong(data_len);
}


static PyObject *Serial_clear_in_buf(Serial *self, PyObject *args) {
    return PyLong_FromLong(hat_serial_clear_in_buff(self->serial));
}


static PyObject *Serial_set_close_cb(Serial *self, PyObject *cb) {
    self->close_cb = cb;
    Py_RETURN_NONE;
}


static PyObject *Serial_set_in_cb(Serial *self, PyObject *cb) {
    self->in_cb = cb;
    Py_RETURN_NONE;
}


static PyObject *Serial_set_out_cb(Serial *self, PyObject *cb) {
    self->out_cb = cb;
    Py_RETURN_NONE;
}


PyMethodDef Serial_Methods[] = {{.ml_name = "open",
                                 .ml_meth = (PyCFunction)Serial_open,
                                 .ml_flags = METH_VARARGS | METH_KEYWORDS},
                                {.ml_name = "close",
                                 .ml_meth = (PyCFunction)Serial_close,
                                 .ml_flags = METH_NOARGS},
                                {.ml_name = "read",
                                 .ml_meth = (PyCFunction)Serial_read,
                                 .ml_flags = METH_NOARGS},
                                {.ml_name = "write",
                                 .ml_meth = (PyCFunction)Serial_write,
                                 .ml_flags = METH_O},
                                {.ml_name = "clear_in_buff",
                                 .ml_meth = (PyCFunction)Serial_clear_in_buf,
                                 .ml_flags = METH_NOARGS},
                                {.ml_name = "set_close_cb",
                                 .ml_meth = (PyCFunction)Serial_set_close_cb,
                                 .ml_flags = METH_O},
                                {.ml_name = "set_in_cb",
                                 .ml_meth = (PyCFunction)Serial_set_in_cb,
                                 .ml_flags = METH_O},
                                {.ml_name = "set_out_cb",
                                 .ml_meth = (PyCFunction)Serial_set_out_cb,
                                 .ml_flags = METH_O},
                                {NULL}};

PyType_Slot serial_type_slots[] = {
    {Py_tp_new, Serial_new},
    {Py_tp_dealloc, (destructor)Serial_dealloc},
    {Py_tp_methods, Serial_Methods},
    {0, NULL},
};

PyType_Spec serial_type_spec = {.name =
                                    "hat.drivers.serial._native_serial.Serial",
                                .basicsize = sizeof(Serial),
                                .flags = Py_TPFLAGS_HEAPTYPE,
                                .slots = serial_type_slots};

PyModuleDef module_def = {.m_base = PyModuleDef_HEAD_INIT,
                          .m_name = "_native_serial"};


PyMODINIT_FUNC PyInit__native_serial() {
    PyObject *module = PyModule_Create(&module_def);
    if (!module)
        return NULL;

    PyObject *serial_type = PyType_FromSpec(&serial_type_spec);
    if (!serial_type) {
        Py_DECREF(module);
        return NULL;
    }

    int result = PyModule_AddObject(module, "Serial", serial_type);
    Py_DECREF(serial_type);
    if (result) {
        Py_DECREF(module);
        return NULL;
    }

    return module;
}
