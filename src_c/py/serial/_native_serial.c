#include <Python.h>
#include <stdatomic.h>
#include <stdbool.h>
#include <hat/py_allocator.h>
#include <hat/serial.h>


typedef struct {
    PyObject ob_base;
    hat_serial_t *serial;
    _Atomic(PyObject *) close_cb;
    _Atomic(PyObject *) in_change_cb;
    _Atomic(PyObject *) out_change_cb;
    _Atomic(PyObject *) drain_cb;
} Serial;


#define atomic_py_clear(op)                                                    \
    do {                                                                       \
        PyObject *_py_tmp = _PyObject_CAST(atomic_load(&(op)));                \
        if (_py_tmp != NULL) {                                                 \
            atomic_store(&(op), NULL);                                         \
            Py_DECREF(_py_tmp);                                                \
        }                                                                      \
    } while (0)


// ensure that self is not dealloced during this call
// (callback should reference self)
static void on_serial_close(hat_serial_t *s) {
    Serial *self = (Serial *)hat_serial_get_ctx(s);
    PyObject *close_cb = atomic_load(&(self->close_cb));
    if (!close_cb || close_cb == Py_None)
        return;

    PyGILState_STATE gstate = PyGILState_Ensure();

    close_cb = atomic_load(&(self->close_cb));
    if (close_cb && close_cb != Py_None)
        Py_XDECREF(PyObject_CallNoArgs(close_cb));

    PyGILState_Release(gstate);
}


// ensure that self is not dealloced during this call
// (callback should reference self)
static void on_serial_in_change(hat_serial_t *s) {
    Serial *self = (Serial *)hat_serial_get_ctx(s);
    PyObject *in_change_cb = atomic_load(&(self->in_change_cb));
    if (!in_change_cb || in_change_cb == Py_None)
        return;

    PyGILState_STATE gstate = PyGILState_Ensure();

    in_change_cb = atomic_load(&(self->in_change_cb));
    if (in_change_cb && in_change_cb != Py_None)
        Py_XDECREF(PyObject_CallNoArgs(in_change_cb));

    PyGILState_Release(gstate);
}


// ensure that self is not dealloced during this call
// (callback should reference self)
static void on_serial_out_change(hat_serial_t *s) {
    Serial *self = (Serial *)hat_serial_get_ctx(s);
    PyObject *out_change_cb = atomic_load(&(self->out_change_cb));
    if (!out_change_cb || out_change_cb == Py_None)
        return;

    PyGILState_STATE gstate = PyGILState_Ensure();

    out_change_cb = atomic_load(&(self->out_change_cb));
    if (out_change_cb && out_change_cb != Py_None)
        Py_XDECREF(PyObject_CallNoArgs(out_change_cb));

    PyGILState_Release(gstate);
}


// ensure that self is not dealloced during this call
// (callback should reference self)
static void on_serial_drain(hat_serial_t *s) {
    Serial *self = (Serial *)hat_serial_get_ctx(s);
    PyObject *drain_cb = atomic_load(&(self->drain_cb));
    if (!drain_cb || drain_cb == Py_None)
        return;

    PyGILState_STATE gstate = PyGILState_Ensure();

    drain_cb = atomic_load(&(self->drain_cb));
    if (drain_cb && drain_cb != Py_None)
        Py_XDECREF(PyObject_CallNoArgs(drain_cb));

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

    atomic_init(&(self->close_cb), NULL);
    atomic_init(&(self->in_change_cb), NULL);
    atomic_init(&(self->out_change_cb), NULL);
    atomic_init(&(self->drain_cb), NULL);

    self->serial =
        hat_serial_create(&hat_py_allocator, in_buff_size, out_buff_size,
                          on_serial_close, on_serial_in_change, NULL,
                          on_serial_out_change, NULL, on_serial_drain, self);
    if (!self->serial) {
        Py_DECREF(self);
        PyErr_SetString(PyExc_MemoryError, "error creating serial object");
        return NULL;
    }

    return (PyObject *)self;
}


// ensure that object will not be deallocated from serial background thread
static void Serial_dealloc(Serial *self) {
    atomic_py_clear(self->close_cb);
    atomic_py_clear(self->in_change_cb);
    atomic_py_clear(self->out_change_cb);
    atomic_py_clear(self->drain_cb);

    if (self->serial)
        hat_serial_destroy(self->serial);

    PyObject_Free((PyObject *)self);
}


static PyObject *Serial_open(Serial *self, PyObject *args, PyObject *kwargs) {
    PyObject *port_str;
    unsigned long baudrate;
    unsigned char bytesize;
    int parity;
    unsigned char stopbits;
    int xonxoff;
    int rtscts;
    int dsrdtr;
    if (!PyArg_ParseTupleAndKeywords(
            args, kwargs, "O!kbCbppp",
            (char *[]){"port", "baudrate", "bytesize", "parity", "stopbits",
                       "xonxoff", "rtscts", "dsrdtr", NULL},
            &PyUnicode_Type, &port_str, &baudrate, &bytesize, &parity,
            &stopbits, &xonxoff, &rtscts, &dsrdtr))
        return NULL;

    PyObject *port_bytes = PyUnicode_AsUTF8String(port_str);
    if (!port_bytes)
        return NULL;

    char *port = PyBytes_AsString(port_bytes);
    if (!port) {
        Py_DECREF(port_bytes);
        return NULL;
    }

    hat_serial_error_t result =
        hat_serial_open(self->serial, port, baudrate, bytesize, parity,
                        stopbits, xonxoff, rtscts, dsrdtr);
    Py_DECREF(port_bytes);
    if (result) {
        PyErr_SetString(PyExc_RuntimeError, hat_serial_error_msg(result));
        return NULL;
    }

    return Py_NewRef(Py_None);
}


static PyObject *Serial_close(Serial *self, PyObject *args) {
    hat_serial_close(self->serial);

    return Py_NewRef(Py_None);
}


static PyObject *Serial_read(Serial *self, PyObject *args) {
    size_t data_len = hat_serial_get_available(self->serial);

    if (!data_len)
        return Py_NewRef(Py_None);

    PyObject *data_bytes = PyBytes_FromStringAndSize(NULL, data_len);
    if (!data_bytes)
        return NULL;

    uint8_t *data = (uint8_t *)PyBytes_AsString(data_bytes);
    size_t result = hat_serial_read(self->serial, data, data_len);

    if (result != data_len) {
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

    if (data_len == 0)
        return PyLong_FromLong(0);

    uint8_t *data = (uint8_t *)PyBytes_AsString(data_bytes);
    size_t result = hat_serial_write(self->serial, data, data_len);

    return PyLong_FromLong(result);
}


static PyObject *Serial_drain(Serial *self, PyObject *args) {
    hat_serial_drain(self->serial);

    return Py_NewRef(Py_None);
}


static PyObject *Serial_set_close_cb(Serial *self, PyObject *cb) {
    atomic_py_clear(self->close_cb);
    atomic_store(&(self->close_cb), Py_XNewRef(cb));
    return Py_NewRef(Py_None);
}


static PyObject *Serial_set_in_change_cb(Serial *self, PyObject *cb) {
    atomic_py_clear(self->in_change_cb);
    atomic_store(&(self->in_change_cb), Py_XNewRef(cb));
    return Py_NewRef(Py_None);
}


static PyObject *Serial_set_out_change_cb(Serial *self, PyObject *cb) {
    atomic_py_clear(self->out_change_cb);
    atomic_store(&(self->out_change_cb), Py_XNewRef(cb));
    return Py_NewRef(Py_None);
}


static PyObject *Serial_set_drain_cb(Serial *self, PyObject *cb) {
    atomic_py_clear(self->drain_cb);
    atomic_store(&(self->drain_cb), Py_XNewRef(cb));
    return Py_NewRef(Py_None);
}


PyMethodDef Serial_Methods[] = {
    {.ml_name = "open",
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
    {.ml_name = "drain",
     .ml_meth = (PyCFunction)Serial_drain,
     .ml_flags = METH_NOARGS},
    {.ml_name = "set_close_cb",
     .ml_meth = (PyCFunction)Serial_set_close_cb,
     .ml_flags = METH_O},
    {.ml_name = "set_in_change_cb",
     .ml_meth = (PyCFunction)Serial_set_in_change_cb,
     .ml_flags = METH_O},
    {.ml_name = "set_out_change_cb",
     .ml_meth = (PyCFunction)Serial_set_out_change_cb,
     .ml_flags = METH_O},
    {.ml_name = "set_drain_cb",
     .ml_meth = (PyCFunction)Serial_set_drain_cb,
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
