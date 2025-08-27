#include "ministring.h"
#include <string.h>

// Helper function to determine UTF-8 character length from first byte
int utf8_char_length(unsigned char first_byte) {
    if ((first_byte & 0x80) == 0) return 1;      // 0xxxxxxx
    if ((first_byte & 0xE0) == 0xC0) return 2;   // 110xxxxx
    if ((first_byte & 0xF0) == 0xE0) return 3;   // 1110xxxx
    if ((first_byte & 0xF8) == 0xF0) return 4;   // 11110xxx
    return 1; // Invalid UTF-8, treat as single byte
}

// Count UTF-8 codepoints in a byte string
int utf8_codepoint_count(const char *data, Py_ssize_t size) {
    int count = 0;
    Py_ssize_t i = 0;

    while (i < size) {
        int char_len = utf8_char_length((unsigned char)data[i]);
        count++;
        i += char_len;
        if (i > size) break; // Prevent overrun on invalid UTF-8
    }

    return count;
}

// Build offset table for O(1) indexing
void build_offset_table(Utf8StringObject *self) {
    if (self->offsets) {
        PyMem_Free(self->offsets);
    }

    self->offsets = (int32_t *)PyMem_Malloc((self->length + 1) * sizeof(int32_t));
    if (!self->offsets) {
        return; // Memory allocation failed
    }

    int32_t byte_pos = 0;
    int32_t codepoint_pos = 0;

    self->offsets[0] = 0;

    while (byte_pos < self->utf8_size && codepoint_pos < self->length) {
        int char_len = utf8_char_length((unsigned char)self->utf8_data[byte_pos]);
        byte_pos += char_len;
        codepoint_pos++;
        if (codepoint_pos <= self->length) {
            self->offsets[codepoint_pos] = byte_pos;
        }
    }
}

// Deallocation function
static void Utf8String_dealloc(Utf8StringObject *self) {
    if (self->utf8_data) {
        PyMem_Free(self->utf8_data);
    }
    if (self->offsets) {
        PyMem_Free(self->offsets);
    }
    Py_TYPE(self)->tp_free((PyObject *)self);
}

// __len__ method
static Py_ssize_t Utf8String_length(Utf8StringObject *self) {
    return self->length;
}

// __getitem__ method
static PyObject *Utf8String_getitem(Utf8StringObject *self, Py_ssize_t index) {
    if (index < 0) {
        index += self->length;
    }

    if (index < 0 || index >= self->length) {
        PyErr_SetString(PyExc_IndexError, "string index out of range");
        return NULL;
    }

    if (!self->offsets) {
        build_offset_table(self);
        if (!self->offsets) {
            PyErr_SetString(PyExc_MemoryError, "Failed to build offset table");
            return NULL;
        }
    }

    int32_t start_byte = self->offsets[index];
    int32_t end_byte = (index + 1 < self->length) ? self->offsets[index + 1] : self->utf8_size;

    return PyUnicode_FromStringAndSize(self->utf8_data + start_byte, end_byte - start_byte);
}

// Slicing support
static PyObject *Utf8String_getslice(Utf8StringObject *self, Py_ssize_t start, Py_ssize_t stop) {
    if (start < 0) start = 0;
    if (stop > self->length) stop = self->length;
    if (start >= stop) {
        return Utf8String_FromUTF8("", 0);
    }

    if (!self->offsets) {
        build_offset_table(self);
        if (!self->offsets) {
            PyErr_SetString(PyExc_MemoryError, "Failed to build offset table");
            return NULL;
        }
    }

    int32_t start_byte = self->offsets[start];
    int32_t end_byte = (stop < self->length) ? self->offsets[stop] : self->utf8_size;

    return Utf8String_FromUTF8(self->utf8_data + start_byte, end_byte - start_byte);
}

// Mapping protocol for indexing and slicing
static PyObject *Utf8String_subscript(Utf8StringObject *self, PyObject *key) {
    if (PyIndex_Check(key)) {
        Py_ssize_t index = PyNumber_AsSsize_t(key, PyExc_IndexError);
        if (index == -1 && PyErr_Occurred()) {
            return NULL;
        }
        return Utf8String_getitem(self, index);
    }
    else if (PySlice_Check(key)) {
        Py_ssize_t start, stop, step, slicelength;
        if (PySlice_GetIndicesEx(key, self->length, &start, &stop, &step, &slicelength) < 0) {
            return NULL;
        }
        if (step != 1) {
            PyErr_SetString(PyExc_NotImplementedError, "Step slicing not supported");
            return NULL;
        }
        return Utf8String_getslice(self, start, stop);
    }
    else {
        PyErr_Format(PyExc_TypeError, "string indices must be integers or slices, not %.200s",
                     Py_TYPE(key)->tp_name);
        return NULL;
    }
}

// __str__ method
static PyObject *Utf8String_str(Utf8StringObject *self) {
    return PyUnicode_FromStringAndSize(self->utf8_data, self->utf8_size);
}

// __repr__ method
static PyObject *Utf8String_repr(Utf8StringObject *self) {
    PyObject *str_obj = PyUnicode_FromStringAndSize(self->utf8_data, self->utf8_size);
    if (!str_obj) return NULL;

    PyObject *repr_obj = PyObject_Repr(str_obj);
    Py_DECREF(str_obj);
    return repr_obj;
}

// Hash function
static Py_hash_t Utf8String_hash(Utf8StringObject *self) {
    if (self->hash != -1) {
        return self->hash;
    }

    PyObject *str_obj = PyUnicode_FromStringAndSize(self->utf8_data, self->utf8_size);
    if (!str_obj) return -1;

    self->hash = PyObject_Hash(str_obj);
    Py_DECREF(str_obj);
    return self->hash;
}

// Equality comparison
static PyObject *Utf8String_richcompare(Utf8StringObject *self, PyObject *other, int op) {
    if (op != Py_EQ && op != Py_NE) {
        Py_RETURN_NOTIMPLEMENTED;
    }

    const char *other_data;
    Py_ssize_t other_size;

    if (Py_TYPE(other) == &Utf8StringType) {
        Utf8StringObject *other_utf8 = (Utf8StringObject *)other;
        other_data = other_utf8->utf8_data;
        other_size = other_utf8->utf8_size;
    }
    else if (PyUnicode_Check(other)) {
        other_data = PyUnicode_AsUTF8AndSize(other, &other_size);
        if (!other_data) return NULL;
    }
    else {
        Py_RETURN_NOTIMPLEMENTED;
    }

    int equal = (self->utf8_size == other_size) &&
                (memcmp(self->utf8_data, other_data, self->utf8_size) == 0);

    if (op == Py_EQ) {
        return PyBool_FromLong(equal);
    } else {
        return PyBool_FromLong(!equal);
    }
}

// Sequence protocol
static PySequenceMethods Utf8String_as_sequence = {
    (lenfunc)Utf8String_length,     // sq_length
    0,                              // sq_concat
    0,                              // sq_repeat
    (ssizeargfunc)Utf8String_getitem, // sq_item
    0,                              // sq_slice (deprecated)
    0,                              // sq_ass_item
    0,                              // sq_ass_slice (deprecated)
    0,                              // sq_contains
    0,                              // sq_inplace_concat
    0,                              // sq_inplace_repeat
};

// Mapping protocol
static PyMappingMethods Utf8String_as_mapping = {
    (lenfunc)Utf8String_length,           // mp_length
    (binaryfunc)Utf8String_subscript,     // mp_subscript
    0,                                    // mp_ass_subscript
};

// Type definition
PyTypeObject Utf8StringType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "ministring.Utf8String",              // tp_name
    sizeof(Utf8StringObject),             // tp_basicsize
    0,                                    // tp_itemsize
    (destructor)Utf8String_dealloc,       // tp_dealloc
    0,                                    // tp_vectorcall_offset
    0,                                    // tp_getattr
    0,                                    // tp_setattr
    0,                                    // tp_as_async
    (reprfunc)Utf8String_repr,            // tp_repr
    0,                                    // tp_as_number
    &Utf8String_as_sequence,              // tp_as_sequence
    &Utf8String_as_mapping,               // tp_as_mapping
    (hashfunc)Utf8String_hash,            // tp_hash
    0,                                    // tp_call
    (reprfunc)Utf8String_str,             // tp_str
    0,                                    // tp_getattro
    0,                                    // tp_setattro
    0,                                    // tp_as_buffer
    Py_TPFLAGS_DEFAULT,                   // tp_flags
    "Compact UTF-8 string type",          // tp_doc
    0,                                    // tp_traverse
    0,                                    // tp_clear
    (richcmpfunc)Utf8String_richcompare,  // tp_richcompare
    0,                                    // tp_weaklistoffset
    0,                                    // tp_iter
    0,                                    // tp_iternext
    0,                                    // tp_methods
    0,                                    // tp_members
    0,                                    // tp_getset
    0,                                    // tp_base
    0,                                    // tp_dict
    0,                                    // tp_descr_get
    0,                                    // tp_descr_set
    0,                                    // tp_dictoffset
    0,                                    // tp_init
    0,                                    // tp_alloc
    0,                                    // tp_new
};

// Constructor function
PyObject *Utf8String_FromUTF8(const char *data, Py_ssize_t size) {
    if (size < 0) {
        size = strlen(data);
    }

    Utf8StringObject *self = (Utf8StringObject *)PyObject_New(Utf8StringObject, &Utf8StringType);
    if (!self) {
        return NULL;
    }

    // Copy UTF-8 data
    self->utf8_data = (char *)PyMem_Malloc(size + 1);
    if (!self->utf8_data) {
        Py_DECREF(self);
        return PyErr_NoMemory();
    }

    memcpy(self->utf8_data, data, size);
    self->utf8_data[size] = '\0';
    self->utf8_size = size;

    // Count codepoints
    self->length = utf8_codepoint_count(data, size);

    // Initialize other fields
    self->offsets = NULL;
    self->hash = -1;

    return (PyObject *)self;
}

// Python wrapper for constructor
static PyObject *ministr_function(PyObject *self, PyObject *args) {
    PyObject *obj = NULL;

    if (!PyArg_ParseTuple(args, "|O", &obj)) {
        return NULL;
    }

    if (obj == NULL) {
        return Utf8String_FromUTF8("", 0);
    }

    if (PyUnicode_Check(obj)) {
        Py_ssize_t size;
        const char *data = PyUnicode_AsUTF8AndSize(obj, &size);
        if (!data) return NULL;

        return Utf8String_FromUTF8(data, size);
    }

    // Try to convert to string first
    PyObject *str_obj = PyObject_Str(obj);
    if (!str_obj) return NULL;

    Py_ssize_t size;
    const char *data = PyUnicode_AsUTF8AndSize(str_obj, &size);
    if (!data) {
        Py_DECREF(str_obj);
        return NULL;
    }

    PyObject *result = Utf8String_FromUTF8(data, size);
    Py_DECREF(str_obj);
    return result;
}

// Module methods
static PyMethodDef ministring_methods[] = {
    {"ministr", ministr_function, METH_VARARGS, "Create a new Utf8String"},
    {NULL, NULL, 0, NULL}
};

// Module definition
static struct PyModuleDef ministring_module = {
    PyModuleDef_HEAD_INIT,
    "ministring",
    "Experimental compact UTF-8 string type for CPython",
    -1,
    ministring_methods
};

// Module initialization
PyMODINIT_FUNC PyInit_ministring(void) {
    PyObject *module;

    if (PyType_Ready(&Utf8StringType) < 0) {
        return NULL;
    }

    module = PyModule_Create(&ministring_module);
    if (module == NULL) {
        return NULL;
    }

    Py_INCREF(&Utf8StringType);
    if (PyModule_AddObject(module, "Utf8String", (PyObject *)&Utf8StringType) < 0) {
        Py_DECREF(&Utf8StringType);
        Py_DECREF(module);
        return NULL;
    }

    return module;
}
