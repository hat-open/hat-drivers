#include <Python.h>
#include <openssl/ssl.h>


typedef struct {
    PyObject ob_base;
    PyObject *socket;
    SSL *ssl;
} PartialPySSLSocket;


static int pass_cb(char *buf, int size, int rwflag, void *u) { return -1; }


static void free_cert(PyObject *self) {
    X509 *cert = PyCapsule_GetPointer(self, NULL);
    X509_free(cert);
}


static void free_crl(PyObject *self) {
    X509_CRL *crl = PyCapsule_GetPointer(self, NULL);
    X509_CRL_free(crl);
}


static void free_pub_key(PyObject *self) {
    EVP_PKEY *key = PyCapsule_GetPointer(self, NULL);
    EVP_PKEY_free(key);
}


static PyObject *key_update(PyObject *self, PyObject *args) {
    PartialPySSLSocket *sslobj;
    int updatetype;
    if (!PyArg_ParseTuple(args, "OI", &sslobj, &updatetype))
        return NULL;

    PyThreadState *state = PyEval_SaveThread();
    int result = SSL_key_update(sslobj->ssl, updatetype);
    PyEval_RestoreThread(state);

    return PyLong_FromLong(result);
}


static PyObject *renegotiate(PyObject *self, PyObject *args) {
    PartialPySSLSocket *sslobj;
    if (!PyArg_ParseTuple(args, "O", &sslobj))
        return NULL;

    PyThreadState *state = PyEval_SaveThread();
    int result = SSL_renegotiate(sslobj->ssl);
    PyEval_RestoreThread(state);

    return PyLong_FromLong(result);
}


static PyObject *get_peer_cert(PyObject *self, PyObject *args) {
    PartialPySSLSocket *sslobj;
    if (!PyArg_ParseTuple(args, "O", &sslobj))
        return NULL;

    if (!SSL_is_init_finished(sslobj->ssl)) {
        PyErr_SetString(PyExc_ValueError, "handshake not done yet");
        return NULL;
    }

    X509 *cert = SSL_get_peer_certificate(sslobj->ssl);
    if (!cert) {
        Py_INCREF(Py_None);
        return Py_None;
    }

    PyObject *result = PyCapsule_New(cert, NULL, free_cert);
    if (!result) {
        X509_free(cert);
        return NULL;
    }

    return result;
}


static PyObject *load_crl(PyObject *self, PyObject *args) {
    char *path;
    if (!PyArg_ParseTuple(args, "s", &path))
        return NULL;

    FILE *fp = fopen(path, "rb");
    if (!fp) {
        PyErr_SetString(PyExc_Exception, "error opening file");
        return NULL;
    }

    X509_CRL *crl = PEM_read_X509_CRL(fp, NULL, pass_cb, NULL);
    fclose(fp);
    if (!crl) {
        PyErr_SetString(PyExc_Exception, "PEM_read_X509_CRL error");
        return NULL;
    }

    PyObject *result = PyCapsule_New(crl, NULL, free_crl);
    if (!result) {
        X509_CRL_free(crl);
        return NULL;
    }

    return result;
}


static PyObject *get_cert_pub_key(PyObject *self, PyObject *args) {
    PyObject *cert_obj;
    if (!PyArg_ParseTuple(args, "O", &cert_obj))
        return NULL;

    X509 *cert = PyCapsule_GetPointer(cert_obj, NULL);
    if (!cert)
        return NULL;

    EVP_PKEY *key = X509_get_pubkey(cert);
    if (!key) {
        PyErr_SetString(PyExc_Exception, "X509_get_pubkey error");
        return NULL;
    }

    PyObject *result = PyCapsule_New(key, NULL, free_pub_key);
    if (!result) {
        EVP_PKEY_free(key);
        return NULL;
    }

    return result;
}


static PyObject *get_cert_bytes(PyObject *self, PyObject *args) {
    PyObject *cert_obj;
    if (!PyArg_ParseTuple(args, "O", &cert_obj))
        return NULL;

    X509 *cert = PyCapsule_GetPointer(cert_obj, NULL);
    if (!cert)
        return NULL;

    unsigned char *bytes_buf = NULL;
    int len = i2d_X509(cert, &bytes_buf);
    if (len < 0) {
        PyErr_SetString(PyExc_Exception, "i2d_X509 error");
        return NULL;
    }

    PyObject *result = PyBytes_FromStringAndSize((const char *)bytes_buf, len);
    OPENSSL_free(bytes_buf);
    return result;
}


static PyObject *is_pub_key_rsa(PyObject *self, PyObject *args) {
    PyObject *key_obj;
    if (!PyArg_ParseTuple(args, "O", &key_obj))
        return NULL;

    EVP_PKEY *key = PyCapsule_GetPointer(key_obj, NULL);
    if (!key)
        return NULL;

    int result = EVP_PKEY_base_id(key) == EVP_PKEY_RSA;
    return PyBool_FromLong(result);
}


static PyObject *get_pub_key_size(PyObject *self, PyObject *args) {
    PyObject *key_obj;
    if (!PyArg_ParseTuple(args, "O", &key_obj))
        return NULL;

    EVP_PKEY *key = PyCapsule_GetPointer(key_obj, NULL);
    if (!key)
        return NULL;

    int result = EVP_PKEY_bits(key);
    return PyLong_FromLong(result);
}


static PyObject *crl_contains_cert(PyObject *self, PyObject *args) {
    PyObject *crl_obj;
    PyObject *cert_obj;
    if (!PyArg_ParseTuple(args, "OO", &crl_obj, &cert_obj))
        return NULL;

    X509_CRL *crl = PyCapsule_GetPointer(crl_obj, NULL);
    if (!crl)
        return NULL;

    X509 *cert = PyCapsule_GetPointer(cert_obj, NULL);
    if (!cert)
        return NULL;

    X509_REVOKED *ret;
    int result = X509_CRL_get0_by_cert(crl, &ret, cert);
    return PyBool_FromLong(result);
}


PyMethodDef methods[] = {{.ml_name = "key_update",
                          .ml_meth = (PyCFunction)key_update,
                          .ml_flags = METH_VARARGS},
                         {.ml_name = "renegotiate",
                          .ml_meth = (PyCFunction)renegotiate,
                          .ml_flags = METH_VARARGS},
                         {.ml_name = "get_peer_cert",
                          .ml_meth = (PyCFunction)get_peer_cert,
                          .ml_flags = METH_VARARGS},
                         {.ml_name = "load_crl",
                          .ml_meth = (PyCFunction)load_crl,
                          .ml_flags = METH_VARARGS},
                         {.ml_name = "get_cert_pub_key",
                          .ml_meth = (PyCFunction)get_cert_pub_key,
                          .ml_flags = METH_VARARGS},
                         {.ml_name = "get_cert_bytes",
                          .ml_meth = (PyCFunction)get_cert_bytes,
                          .ml_flags = METH_VARARGS},
                         {.ml_name = "is_pub_key_rsa",
                          .ml_meth = (PyCFunction)is_pub_key_rsa,
                          .ml_flags = METH_VARARGS},
                         {.ml_name = "get_pub_key_size",
                          .ml_meth = (PyCFunction)get_pub_key_size,
                          .ml_flags = METH_VARARGS},
                         {.ml_name = "crl_contains_cert",
                          .ml_meth = (PyCFunction)crl_contains_cert,
                          .ml_flags = METH_VARARGS},
                         {NULL}};


PyModuleDef module_def = {
    .m_base = PyModuleDef_HEAD_INIT, .m_name = "_ssl", .m_methods = methods};


PyMODINIT_FUNC PyInit__ssl() { return PyModule_Create(&module_def); }
