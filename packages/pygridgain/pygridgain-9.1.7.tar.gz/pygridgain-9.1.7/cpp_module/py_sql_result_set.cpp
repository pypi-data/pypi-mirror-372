/*
 * Copyright (C) GridGain Systems. All Rights Reserved.
 *  _________        _____ __________________        _____
 *  __  ____/___________(_)______  /__  ____/______ ____(_)_______
 *  _  / __  __  ___/__  / _  __  / _  / __  _  __ `/__  / __  __ \
 *  / /_/ /  _  /    _  /  / /_/ /  / /_/ /  / /_/ / _  /  _  / / /
 *  \____/   /_/     /_/   \_,__/   \____/   \__,_/  /_/   /_/ /_/
 */


#include "module.h"
#include "utils.h"
#include "py_errors.h"
#include "py_sql_result_set.h"
#include "py_sql_result_set_row.h"

#include "ignite/protocol/reader.h"

#include <Python.h>

#include <string>
#include <optional>


#define PY_SQL_RESULT_SET_CLASS_NAME "_PySqlResultSet"

namespace {

using namespace ignite;

/**
 * _PySqlResultSet data.
 */
struct py_sql_result_set_data {
    py_sql_result_set_data() = default;

    /** Result set metadata. */
    std::vector<ignite_type> m_meta;

    /** Has a row set. */
    bool m_has_rowset{false};

    /** Affected rows. */
    std::int64_t m_affected_rows{-1};

    /** statement was applied. */
    bool m_was_applied{false};

    /** Resource ID. */
    std::optional<std::int64_t> m_resource_id;

    /** Has more pages. */
    bool m_has_more_pages{false};

    /** Current page data. */
    std::vector<std::byte> m_page_data;

    /** Current page size. */
    std::int32_t m_page_size{0};

    /** Current page. */
    std::vector<bytes_view> m_page;
};

/**
 * _PySqlResultSet Python object.
 */
struct py_sql_result_set {
    PyObject_HEAD

    /** The underlying table name in the canonical form. */
    py_sql_result_set_data *m_data;
};

void read_page(py_sql_result_set_data& data, protocol::reader &reader) {
    data.m_page_size = reader.read_int32();
    data.m_page_data.assign(reader.left_data().cbegin(), reader.left_data().cend());

    auto reader0 = protocol::reader(data.m_page_data);
    data.m_page.clear();
    data.m_page.reserve(data.m_page_size);
    for (std::int32_t i = 0; i < data.m_page_size; ++i) {
        data.m_page.push_back(reader0.read_binary());
    }

    reader = std::move(reader0);
}

PyObject* py_sql_result_set_cursor_request(py_sql_result_set *self, PyObject* req_id_arg, protocol::client_operation op) {
    if (!self->m_data->m_resource_id) {
        py_set_ignite_error(ignite_error{error::code::CURSOR_ALREADY_CLOSED, "Cursor already closed"});
        return nullptr;
    }

    if (!PyLong_Check(req_id_arg)) {
        py_set_ignite_error("Request ID must be a long");
        return nullptr;
    }
    auto req_id = PyLong_AsLongLong(req_id_arg);

    auto cursor_id = *self->m_data->m_resource_id;
    auto wr = [cursor_id] (protocol::writer& writer) {
        writer.write(cursor_id);
        return true;
    };

    auto req = pack_request(op, req_id, wr);

    // TODO: GG-44605 Eliminate unnecessary memory allocations
    return PyBytes_FromStringAndSize(reinterpret_cast<const char *>(req.data()), req.size());
}

PyObject* py_sql_result_set_make_close_request(py_sql_result_set *self, PyObject* req_id_arg) {
    if (!self->m_data->m_resource_id) {
        Py_RETURN_NONE;
    }

    return py_sql_result_set_cursor_request(self, req_id_arg, protocol::client_operation::SQL_CURSOR_CLOSE);
}

PyObject* py_sql_result_set_make_next_page_request(py_sql_result_set *self, PyObject* req_id_arg) {
    return py_sql_result_set_cursor_request(self, req_id_arg, protocol::client_operation::SQL_CURSOR_NEXT_PAGE);
}

PyObject* py_sql_result_set_parse_next_page_response(py_sql_result_set *self, PyObject* message_arg) {
    auto message = get_py_binary_data(message_arg);
    if (message.empty())
        return nullptr;

    try {
        protocol::reader reader(message);
        read_page(*self->m_data, reader);
        self->m_data->m_has_more_pages = reader.read_bool();

        Py_RETURN_NONE;
    } catch (ignite_error &err) {
        py_set_ignite_error(err);
        return nullptr;
    }
}

PyObject* py_sql_result_set_has_row(py_sql_result_set *self, PyObject* row_idx_arg) {
    if (!PyLong_Check(row_idx_arg)) {
        py_set_ignite_error("Row ID must be a long");
        return nullptr;
    }
    auto row_idx = PyLong_AsLongLong(row_idx_arg);

    if (row_idx < self->m_data->m_page_size) {
        Py_RETURN_TRUE;
    }

    Py_RETURN_FALSE;
}

PyObject* py_sql_result_set_get_row(py_sql_result_set *self, PyObject* row_idx_arg) {
    if (!PyLong_Check(row_idx_arg)) {
        py_set_ignite_error("Row ID must be a long");
        return nullptr;
    }

    auto row_idx = PyLong_AsLongLong(row_idx_arg);
    auto &data = *self->m_data;

    if (row_idx >= data.m_page_size) {
        Py_RETURN_NONE;
    }

    return make_py_sql_result_set_row(data.m_page[row_idx], data.m_meta);
}

PyObject* py_sql_result_set_closed_remotely(py_sql_result_set *self, PyObject*) {
    if (self->m_data->m_has_rowset && self->m_data->m_has_more_pages) {
        Py_RETURN_FALSE;
    }
    Py_RETURN_TRUE;
}

PyTypeObject py_sql_result_set_type = {
    PyVarObject_HEAD_INIT(nullptr, 0)
    EXT_MODULE_NAME "." PY_SQL_RESULT_SET_CLASS_NAME
};

PyMethodDef py_sql_result_set_methods[] = {
    {"make_close_request", PyCFunction(py_sql_result_set_make_close_request), METH_O, nullptr},
    {"make_next_page_request", PyCFunction(py_sql_result_set_make_next_page_request), METH_O, nullptr},
    {"parse_next_page_response", PyCFunction(py_sql_result_set_parse_next_page_response), METH_O, nullptr},
    {"has_row", PyCFunction(py_sql_result_set_has_row), METH_O, nullptr},
    {"get_row", PyCFunction(py_sql_result_set_get_row), METH_O, nullptr},
    {"closed_remotely", PyCFunction(py_sql_result_set_closed_remotely), METH_NOARGS, nullptr},
    {nullptr, nullptr, 0, nullptr}
};

} // anonymous namespace

/**
 * _PySqlResultSet init function.
 */
int py_sql_result_set_init(py_sql_result_set *self, PyObject *, PyObject *)
{
    self->m_data = nullptr;

    return 0;
}

/**
 * _PySqlResultSet dealloc function.
 */
void py_sql_result_set_dealloc(py_sql_result_set *self)
{
    delete self->m_data;
    self->m_data = nullptr;

    Py_TYPE(self)->tp_free(self);
}

int prepare_py_sql_result_set_type() {
    py_sql_result_set_type.tp_new = PyType_GenericNew;
    py_sql_result_set_type.tp_basicsize = sizeof(py_sql_result_set);
    py_sql_result_set_type.tp_dealloc = reinterpret_cast<destructor>(py_sql_result_set_dealloc);
    py_sql_result_set_type.tp_flags = Py_TPFLAGS_DEFAULT;
    py_sql_result_set_type.tp_methods = py_sql_result_set_methods;
    py_sql_result_set_type.tp_init = reinterpret_cast<initproc>(py_sql_result_set_init);

    return PyType_Ready(&py_sql_result_set_type);
}

int register_py_sql_result_set_type(PyObject* mod) {
    auto res = PyModule_AddObject(mod, PY_SQL_RESULT_SET_CLASS_NAME, reinterpret_cast<PyObject *>(&py_sql_result_set_type));
    if (res < 0) {
        Py_DECREF(reinterpret_cast<PyObject *>(&py_sql_result_set_type));
    }
    return res;
}

static std::vector<ignite_type> read_meta(protocol::reader &reader) {
    auto size = reader.read_int32();

    std::vector<ignite_type> columns;
    columns.reserve(size);

    for (std::int32_t i = 0; i < size; ++i) {
        auto fields_num = reader.read_int32();
        assert(fields_num >= 6); // There should be at least six fields.

        auto name = reader.read_string();
        auto nullable = reader.read_bool();
        auto typ = ignite_type(reader.read_int32());
        auto scale = reader.read_int32();
        auto precision = reader.read_int32();
        bool origin_present = reader.read_bool();

        UNUSED_VALUE name;
        UNUSED_VALUE nullable;
        UNUSED_VALUE scale;
        UNUSED_VALUE precision;
        UNUSED_VALUE origin_present;

        reader.skip(fields_num - 6);

        columns.push_back(typ);
    }

    return columns;
}

PyObject *make_py_sql_result_set(protocol::reader &reader) {
    py_sql_result_set* py_obj = PyObject_New(py_sql_result_set, &py_sql_result_set_type);
    if (!py_obj)
        return nullptr;

    py_obj->m_data = new py_sql_result_set_data();

    auto &data = *py_obj->m_data;

    data.m_resource_id = reader.read_object_nullable<std::int64_t>();
    data.m_has_rowset = reader.read_bool();
    data.m_has_more_pages = reader.read_bool();
    data.m_was_applied = reader.read_bool();
    data.m_affected_rows = reader.read_int64();

    if (data.m_has_rowset) {
        data.m_meta = read_meta(reader);
        read_page(data, reader);
    }

    return reinterpret_cast<PyObject *>(py_obj);
}
