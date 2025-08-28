#ifndef PI_TOKENIZE_COMPAT_H
#define PI_TOKENIZE_COMPAT_H

#include "Python.h"
#include "./pythoncapi_compat.h"

Py_ssize_t _PyPegen_byte_offset_to_character_offset_line(PyObject *line, Py_ssize_t col_offset, Py_ssize_t end_col_offset);
Py_ssize_t _PyPegen_byte_offset_to_character_offset(PyObject *line, Py_ssize_t col_offset);
Py_ssize_t _PyPegen_byte_offset_to_character_offset_raw(const char*, Py_ssize_t col_offset);

PyObject *
tokenizeriter_new(PyTypeObject *type, PyObject *args, PyObject *kwargs);

PyObject *
tokenizeriter_new_impl(PyTypeObject *type, PyObject *readline,
                       int extra_tokens, const char *encoding);

PyObject *
tokenize_string(PyObject *self, PyObject *args, PyObject *kwargs);

#ifndef PyImport_ImportModuleAttrString
PyObject *
PyImport_ImportModuleAttrString(const char *module_name, const char *attr_name);
#endif


#ifndef _Py_UniversalNewlineFgetsWithSize
extern char *
_Py_UniversalNewlineFgetsWithSize(char *, int n, FILE *, PyObject *, size_t*);
#endif

#endif /* PI_TOKENIZE_COMPAT_H */

