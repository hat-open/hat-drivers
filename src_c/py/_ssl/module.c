#include <Python.h>
#include <openssl/ssl.h>


// clang-format off
typedef struct {
    PyObject_HEAD
    PyObject *socket;
    SSL *ssl;
} PartialPySSLSocket;
// clang-format on


static PyObject *key_update(PyObject *self, PyObject *args) {
    PartialPySSLSocket *sslobj;
    int updatetype;
    if (!PyArg_ParseTuple(args, "OI", &sslobj, &updatetype))
        return NULL;

    // clang-format off
    int result;
    Py_BEGIN_ALLOW_THREADS
    result = SSL_key_update(sslobj->ssl, updatetype);
    Py_END_ALLOW_THREADS

    return PyLong_FromLong(result);
    // clang-format on
}


static PyObject *renegotiate(PyObject *self, PyObject *args) {
    PartialPySSLSocket *sslobj;
    if (!PyArg_ParseTuple(args, "O", &sslobj))
        return NULL;

    // clang-format off
    int result;
    Py_BEGIN_ALLOW_THREADS
    result = SSL_renegotiate(sslobj->ssl);
    Py_END_ALLOW_THREADS

    return PyLong_FromLong(result);
    // clang-format on
}


PyMethodDef methods[] = {{.ml_name = "key_update",
                          .ml_meth = (PyCFunction)key_update,
                          .ml_flags = METH_VARARGS},
                         {.ml_name = "renegotiate",
                          .ml_meth = (PyCFunction)renegotiate,
                          .ml_flags = METH_VARARGS},
                         {NULL}};


PyModuleDef module_def = {
    .m_base = PyModuleDef_HEAD_INIT, .m_name = "_ssl", .m_methods = methods};


PyMODINIT_FUNC PyInit__ssl() { return PyModule_Create(&module_def); }
