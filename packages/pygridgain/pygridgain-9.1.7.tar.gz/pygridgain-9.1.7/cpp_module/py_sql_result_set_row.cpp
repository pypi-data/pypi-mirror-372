/*
 * Copyright (C) GridGain Systems. All Rights Reserved.
 *  _________        _____ __________________        _____
 *  __  ____/___________(_)______  /__  ____/______ ____(_)_______
 *  _  / __  __  ___/__  / _  __  / _  / __  _  __ `/__  / __  __ \
 *  / /_/ /  _  /    _  /  / /_/ /  / /_/ /  / /_/ / _  /  _  / / /
 *  \____/   /_/     /_/   \_,__/   \____/   \__,_/  /_/   /_/ /_/
 */


#include "py_sql_result_set_row.h"
#include "module.h"
#include "utils.h"
#include "py_errors.h"

#include "ignite/protocol/reader.h"

#include <Python.h>

#define PY_SQL_RESULT_SET_ROW_CLASS_NAME "_PySqlResultSetRow"

namespace {

using namespace ignite;

/**
 * _PySqlResultSetRow data.
 */
struct py_sql_result_set_row_data {
    py_sql_result_set_row_data() = default;

    /** Row size. */
    std::int32_t m_row_size;

    /** Columns. */
    std::vector<primitive> m_columns;
};

/**
 * _PySqlResultSetRow Python object.
 */
struct py_sql_result_set_row {
    PyObject_HEAD

    /** Data. */
    py_sql_result_set_row_data *m_data;
};

PyObject* py_sql_result_set_row_long_value(py_sql_result_set_row *self, PyObject* idx_arg) {
    if (!PyLong_Check(idx_arg)) {
        py_set_ignite_error("Row ID must be a long");
        return nullptr;
    }

    auto idx = PyLong_AsLongLong(idx_arg);
    auto &data = *self->m_data;

    if (idx >= data.m_row_size) {
        py_set_ignite_error("Column index out of range: idx=" + std::to_string(idx)
            + ", row_size=" + std::to_string(data.m_row_size));
        return nullptr;
    }

    auto &column = data.m_columns[idx];

    std::int64_t value = 0;
    switch (column.get_type()) {
        case ignite_type::INT8: {
            value = column.get<std::int8_t>();
            break;
        }
        case ignite_type::INT16: {
            value = column.get<std::int16_t>();
            break;
        }
        case ignite_type::INT32: {
            value = column.get<std::int32_t>();
            break;
        }
        case ignite_type::INT64: {
            value = column.get<std::int64_t>();
            break;
        }
        default: {
            py_set_ignite_error("Column type not an integer: type_id=" + std::to_string(int(column.get_type())));
            return nullptr;
        }
    }

    return PyLong_FromLongLong(value);
}

PyObject* py_sql_result_set_row_binary_value(py_sql_result_set_row *self, PyObject* idx_arg) {
    if (!PyLong_Check(idx_arg)) {
        py_set_ignite_error("Row ID must be a long");
        return nullptr;
    }

    auto idx = PyLong_AsLongLong(idx_arg);
    auto &data = *self->m_data;

    if (idx >= data.m_row_size) {
        py_set_ignite_error("Column index out of range: idx=" + std::to_string(idx)
            + ", row_size=" + std::to_string(data.m_row_size));
        return nullptr;
    }

    auto &column = data.m_columns[idx];

    switch (column.get_type()) {
        case ignite_type::BYTE_ARRAY: {
            auto value = column.get<std::vector<std::byte>>();
            // TODO: GG-44605 Eliminate unnecessary memory allocations
            return PyBytes_FromStringAndSize(reinterpret_cast<const char *>(value.data()), value.size());
        }
        default: {
            py_set_ignite_error("Column type not an integer: type_id=" + std::to_string(int(column.get_type())));
            return nullptr;
        }
    }
}

PyTypeObject py_sql_result_set_row_type = {
    PyVarObject_HEAD_INIT(nullptr, 0)
    EXT_MODULE_NAME "." PY_SQL_RESULT_SET_ROW_CLASS_NAME
};

PyMethodDef py_sql_result_set_methods[] = {
    {"binary_value", PyCFunction(py_sql_result_set_row_binary_value), METH_O, nullptr},
    {"long_value", PyCFunction(py_sql_result_set_row_long_value), METH_O, nullptr},
    {nullptr, nullptr, 0, nullptr}
};

} // anonymous namespace

/**
 * _PySqlResultSetRow init function.
 */
int py_sql_result_set_row_init(py_sql_result_set_row *self, PyObject *, PyObject *)
{
    self->m_data = nullptr;

    return 0;
}

/**
 * _PySqlResultSetRow dealloc function.
 */
void py_sql_result_set_row_dealloc(py_sql_result_set_row *self)
{
    delete self->m_data;
    self->m_data = nullptr;

    Py_TYPE(self)->tp_free(self);
}

int prepare_py_sql_result_set_row_type() {
    py_sql_result_set_row_type.tp_new = PyType_GenericNew;
    py_sql_result_set_row_type.tp_basicsize = sizeof(py_sql_result_set_row);
    py_sql_result_set_row_type.tp_dealloc = reinterpret_cast<destructor>(py_sql_result_set_row_dealloc);
    py_sql_result_set_row_type.tp_flags = Py_TPFLAGS_DEFAULT;
    py_sql_result_set_row_type.tp_methods = py_sql_result_set_methods;
    py_sql_result_set_row_type.tp_init = reinterpret_cast<initproc>(py_sql_result_set_row_init);

    return PyType_Ready(&py_sql_result_set_row_type);
}

int register_py_sql_result_set_row_type(PyObject* mod) {
    auto res = PyModule_AddObject(mod, PY_SQL_RESULT_SET_ROW_CLASS_NAME,
        reinterpret_cast<PyObject *>(&py_sql_result_set_row_type));

    if (res < 0) {
        Py_DECREF(reinterpret_cast<PyObject *>(&py_sql_result_set_row_type));
    }
    return res;
}

PyObject *make_py_sql_result_set_row(bytes_view row_data, const std::vector<ignite_type> &meta) {
    py_sql_result_set_row* py_obj = PyObject_New(py_sql_result_set_row, &py_sql_result_set_row_type);
    if (!py_obj)
        return nullptr;

    py_obj->m_data = new py_sql_result_set_row_data();

    auto &data = *py_obj->m_data;

    data.m_row_size = meta.size();
    data.m_columns.reserve(data.m_row_size);

    binary_tuple_parser parser(data.m_row_size, row_data);
    for (const auto &column : meta) {
        data.m_columns.push_back(protocol::read_next_column(parser, column, 0));
    }

    return reinterpret_cast<PyObject *>(py_obj);
}
