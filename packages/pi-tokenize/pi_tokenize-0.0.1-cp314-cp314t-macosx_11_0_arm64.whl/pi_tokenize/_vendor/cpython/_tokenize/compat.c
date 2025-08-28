#include "Python.h"

#include <stdio.h>
#include <errno.h>


Py_ssize_t
_PyPegen_byte_offset_to_character_offset_line(PyObject *line, Py_ssize_t col_offset, Py_ssize_t end_col_offset)
{
    const unsigned char *data = (const unsigned char*)PyUnicode_AsUTF8(line);

    Py_ssize_t len = 0;
    while (col_offset < end_col_offset) {
        Py_UCS4 ch = data[col_offset];
        if (ch < 0x80) {
            col_offset += 1;
        } else if ((ch & 0xe0) == 0xc0) {
            col_offset += 2;
        } else if ((ch & 0xf0) == 0xe0) {
            col_offset += 3;
        } else if ((ch & 0xf8) == 0xf0) {
            col_offset += 4;
        } else {
            PyErr_SetString(PyExc_ValueError, "Invalid UTF-8 sequence");
            return -1;
        }
        len++;
    }
    return len;
}

Py_ssize_t
_PyPegen_byte_offset_to_character_offset_raw(const char* str, Py_ssize_t col_offset)
{
    Py_ssize_t len = (Py_ssize_t)strlen(str);
    if (col_offset > len + 1) {
        col_offset = len + 1;
    }
    assert(col_offset >= 0);
    PyObject *text = PyUnicode_DecodeUTF8(str, col_offset, "replace");
    if (!text) {
        return -1;
    }
    Py_ssize_t size = PyUnicode_GET_LENGTH(text);
    Py_DECREF(text);
    return size;
}

Py_ssize_t
_PyPegen_byte_offset_to_character_offset(PyObject *line, Py_ssize_t col_offset)
{
    const char *str = PyUnicode_AsUTF8(line);
    if (!str) {
        return -1;
    }
    return _PyPegen_byte_offset_to_character_offset_raw(str, col_offset);
}



// Forward declaration for tokenizeriter_new_impl (defined in module.c)
PyObject *tokenizeriter_new_impl(PyTypeObject *type, PyObject *readline,
                                int extra_tokens, const char *encoding);

// Clinic-generated wrapper function for tokenizeriter_new
PyObject *
tokenizeriter_new(PyTypeObject *type, PyObject *args, PyObject *kwargs)
{
    PyObject *return_value = NULL;
    static const char * const _keywords[] = {"", "extra_tokens", "encoding", NULL};
    PyObject *readline;
    int extra_tokens;
    const char *encoding = NULL;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "Op|z:tokenizeriter", (char**)_keywords,
                                     &readline, &extra_tokens, &encoding)) {
        goto exit;
    }
    return_value = tokenizeriter_new_impl(type, readline, extra_tokens, encoding);

exit:
    return return_value;
}

#ifndef PyImport_ImportModuleAttrString
// Helper function to replace PyImport_ImportModuleAttrString
PyObject *
PyImport_ImportModuleAttrString(const char *module_name, const char *attr_name)
{
    PyObject *module = PyImport_ImportModule(module_name);
    if (module == NULL) {
        return NULL;
    }

    PyObject *attr = PyObject_GetAttrString(module, attr_name);
    Py_DECREF(module);
    return attr;
}
#endif


#ifndef _Py_UniversalNewlineFgetsWithSize
char *
_Py_UniversalNewlineFgetsWithSize(char *buf, int n, FILE *stream, PyObject *fobj, size_t* size)
{
    char *p = buf;
    int c;

    if (fobj) {
        errno = ENXIO;          /* What can you do... */
        return NULL;
    }
    while (--n > 0 && (c = getc(stream)) != EOF ) {
        if (c == '\r') {
            // A \r is translated into a \n, and we skip an adjacent \n, if any.
            c = getc(stream);
            if (c != '\n') {
                ungetc(c, stream);
                c = '\n';
            }
        }
        *p++ = c;
        if (c == '\n') {
            break;
        }
    }
    *p = '\0';
    if (p == buf) {
        return NULL;
    }
    *size = p - buf;
    return buf;
}
#endif
