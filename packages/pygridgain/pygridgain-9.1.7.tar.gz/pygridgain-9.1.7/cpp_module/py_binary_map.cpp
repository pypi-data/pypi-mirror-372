/*
 * Copyright (C) GridGain Systems. All Rights Reserved.
 *  _________        _____ __________________        _____
 *  __  ____/___________(_)______  /__  ____/______ ____(_)_______
 *  _  / __  __  ___/__  / _  __  / _  / __  _  __ `/__  / __  __ \
 *  / /_/ /  _  /    _  /  / /_/ /  / /_/ /  / /_/ / _  /  _  / / /
 *  \____/   /_/     /_/   \_,__/   \____/   \__,_/  /_/   /_/ /_/
 */


#include "py_binary_map.h"
#include "py_errors.h"
#include "module.h"
#include "utils.h"

#include "ignite/protocol/reader.h"
#include "ignite/tuple/binary_tuple_builder.h"

#include <Python.h>

#include <string>
#include <optional>

#define PY_BINARY_MAP_CLASS_NAME "_PyBinaryMap"

namespace {

using namespace ignite;

/**
 * PyBinaryMap data.
 */
struct py_binary_map_data {
    py_binary_map_data() = default;

    /** The underlying table name in the canonical form. */
    std::string m_full_name{};

    /** Table ID. */
    std::int64_t m_table_id = 0;
};

/**
 * Connection Python object.
 */
struct py_binary_map {
    PyObject_HEAD

    /** The underlying table name in the canonical form. */
    py_binary_map_data *m_data;
};

/**
 * Write table operation header.
 *
 * @param writer Writer.
 * @param table_id Table ID.
 */
void write_table_operation_header(protocol::writer &writer, std::int32_t table_id) {
    writer.write(table_id);
    writer.write_nil(); // Transaction
    writer.write(1); // Schema version. Never changes for Map
}

std::vector<std::byte> pack_key_value(bytes_view key, bytes_view value) {
    binary_tuple_builder builder{2};

    builder.start();

    builder.claim_varlen(key);
    builder.claim_varlen(value);

    builder.layout();

    builder.append_varlen(key);
    builder.append_varlen(value);

    return builder.build();
}

std::vector<std::byte> pack_key(bytes_view key) {
    binary_tuple_builder builder{1};

    builder.start();
    builder.claim_varlen(key);
    builder.layout();
    builder.append_varlen(key);

    return builder.build();
}

void write_key_value(protocol::writer &writer, bytes_view key, bytes_view value) {
    auto tuple_data = pack_key_value(key, value);

    std::array<std::byte, 1> bitset = { std::byte(0) };
    writer.write_bitset(bitset);
    writer.write_binary(tuple_data);
}

void write_key(protocol::writer &writer, bytes_view key) {
    auto tuple_data = pack_key(key);

    std::array<std::byte, 1> bitset = { std::byte(0) };
    writer.write_bitset(bitset);
    writer.write_binary(tuple_data);
}

PyObject* py_binary_map_make_put_request(py_binary_map *self, PyObject *args) {
    long long req_id = 0;
    PyObject *key_arg = nullptr;
    PyObject *value_arg = nullptr;

    int parsed = PyArg_ParseTuple(args, "LOO", &req_id, &key_arg, &value_arg);
    if (!parsed)
        return nullptr;

    auto key = get_py_binary_data(key_arg);
    if (key.empty())
        return nullptr;

    auto value = get_py_binary_data(value_arg);
    if (value.empty())
        return nullptr;

    auto wr = [self, key, value] (protocol::writer& writer) {
        write_table_operation_header(writer, self->m_data->m_table_id);
        write_key_value(writer, key, value);

        return true;
    };

    auto req = pack_request(protocol::client_operation::TUPLE_GET_AND_UPSERT, req_id, wr);

    // TODO: GG-44605 Eliminate unnecessary memory allocations
    return PyBytes_FromStringAndSize(reinterpret_cast<const char *>(req.data()), req.size());
}

PyObject* py_binary_map_make_key_request(py_binary_map *self, PyObject *args, protocol::client_operation op) {
    long long req_id = 0;
    PyObject *key_arg = nullptr;

    int parsed = PyArg_ParseTuple(args, "LO", &req_id, &key_arg);
    if (!parsed)
        return nullptr;

    auto key = get_py_binary_data(key_arg);
    if (key.empty())
        return nullptr;

    auto wr = [self, key] (protocol::writer& writer) {
        write_table_operation_header(writer, self->m_data->m_table_id);
        write_key(writer, key);

        return true;
    };

    auto req = pack_request(op, req_id, wr);

    // TODO: GG-44605 Eliminate unnecessary memory allocations
    return PyBytes_FromStringAndSize(reinterpret_cast<const char *>(req.data()), req.size());
}

PyObject* py_binary_map_make_get_request(py_binary_map *self, PyObject *args) {
    return py_binary_map_make_key_request(self, args, protocol::client_operation::TUPLE_GET);
}

PyObject* py_binary_map_make_remove_request(py_binary_map *self, PyObject *args) {
    return py_binary_map_make_key_request(self, args, protocol::client_operation::TUPLE_GET_AND_DELETE);
}

PyObject* py_binary_map_make_contains_request(py_binary_map *self, PyObject *args) {
    return py_binary_map_make_key_request(self, args, protocol::client_operation::TUPLE_CONTAINS_KEY);
}

PyObject* py_binary_map_make_put_all_request(py_binary_map *self, PyObject *args) {
    long long req_id = 0;
    PyObject *entries_arg = nullptr;

    int parsed = PyArg_ParseTuple(args, "LO", &req_id, &entries_arg);
    if (!parsed)
        return nullptr;

    auto is_dict = PyDict_Check(entries_arg);
    if (!is_dict) {
        py_set_ignite_error("Dictionary is expected in format: {Binary, Binary}");
        return nullptr;
    }

    auto wr = [self, entries_arg] (protocol::writer& writer) {
        write_table_operation_header(writer, self->m_data->m_table_id);

        auto size = PyDict_Size(entries_arg);
        writer.write(std::int64_t(size));

        PyObject *py_key;
        PyObject *py_value;
        Py_ssize_t pos = 0;

        while (PyDict_Next(entries_arg, &pos, &py_key, &py_value)) {
            auto key = get_py_binary_data(py_key);
            if (key.empty())
                return false;

            auto value = get_py_binary_data(py_value);
            if (key.empty())
                return false;

            write_key_value(writer, key, value);
        }

        return true;
    };

    auto req = pack_request(protocol::client_operation::TUPLE_UPSERT_ALL, req_id, wr);
    if (req.empty())
        return nullptr;

    // TODO: GG-44605 Eliminate unnecessary memory allocations
    return PyBytes_FromStringAndSize(reinterpret_cast<const char *>(req.data()), req.size());
}

std::optional<bytes_view> read_value(protocol::reader &reader) {
    if (reader.try_read_nil())
        return std::nullopt;

    auto tuple_data = reader.read_binary();

    binary_tuple_parser parser(2, tuple_data);
    parser.get_next(); // key
    auto val = parser.get_next();

    return binary_tuple_parser::get_varlen(val);
}

void skip_schema(protocol::reader &reader) {
    auto schema_ver = reader.read_int32();
    UNUSED_VALUE schema_ver;
}

template<typename PayloadHandler>
PyObject* parse_message(PyObject* message_arg, PayloadHandler payload_handler) {
    auto message = get_py_binary_data(message_arg);
    if (message.empty())
        return nullptr;

    try {
        protocol::reader reader(message);
        skip_schema(reader);

        return payload_handler(reader);
    } catch (ignite_error &err) {
        py_set_ignite_error(err);
        return nullptr;
    }
}

PyObject* py_binary_map_parse_value_response(py_binary_map *, PyObject* message_arg) {
    return parse_message(message_arg, [](protocol::reader &reader) {
        auto value = read_value(reader);
        if (!value) {
            Py_RETURN_NONE;
        }

        // TODO: GG-44605 Eliminate unnecessary memory allocations
        return PyBytes_FromStringAndSize(reinterpret_cast<const char *>(value->data()), value->size());
    });
}

PyObject* py_binary_map_parse_bool_response(py_binary_map *, PyObject* message_arg) {
    return parse_message(message_arg, [](protocol::reader &reader) {
        return PyBool_FromLong(reader.read_bool() ? 1L : 0L);
    });
}

PyObject* py_binary_map_table_name(py_binary_map *self, PyObject*) {
    auto &name = self->m_data->m_full_name;
    return PyUnicode_FromStringAndSize(name.c_str(), name.size());
}

PyTypeObject py_binary_map_type = {
    PyVarObject_HEAD_INIT(nullptr, 0)
    EXT_MODULE_NAME "." PY_BINARY_MAP_CLASS_NAME
};

PyMethodDef py_binary_map_methods[] = {
    {"make_put_request", PyCFunction(py_binary_map_make_put_request), METH_VARARGS, nullptr},
    {"make_get_request", PyCFunction(py_binary_map_make_get_request), METH_VARARGS, nullptr},
    {"make_remove_request", PyCFunction(py_binary_map_make_remove_request), METH_VARARGS, nullptr},
    {"make_contains_request", PyCFunction(py_binary_map_make_contains_request), METH_VARARGS, nullptr},
    {"make_put_all_request", PyCFunction(py_binary_map_make_put_all_request), METH_VARARGS, nullptr},
    {"parse_value_response", PyCFunction(py_binary_map_parse_value_response), METH_O, nullptr},
    {"parse_bool_response", PyCFunction(py_binary_map_parse_bool_response), METH_O, nullptr},
    {"table_name", PyCFunction(py_binary_map_table_name), METH_NOARGS, nullptr},
    {nullptr, nullptr, 0, nullptr}
};

} // anonymous namespace

/**
 * Binary Map init function.
 */
int py_binary_map_init(py_binary_map *self, PyObject *, PyObject *)
{
    self->m_data = nullptr;

    return 0;
}

/**
 * Binary Map dealloc function.
 */
void py_binary_map_dealloc(py_binary_map *self)
{
    delete self->m_data;
    self->m_data = nullptr;

    Py_TYPE(self)->tp_free(self);
}

int prepare_py_binary_map_type() {
    py_binary_map_type.tp_new = PyType_GenericNew;
    py_binary_map_type.tp_basicsize = sizeof(py_binary_map);
    py_binary_map_type.tp_dealloc = reinterpret_cast<destructor>(py_binary_map_dealloc);
    py_binary_map_type.tp_flags = Py_TPFLAGS_DEFAULT;
    py_binary_map_type.tp_methods = py_binary_map_methods;
    py_binary_map_type.tp_init = reinterpret_cast<initproc>(py_binary_map_init);

    return PyType_Ready(&py_binary_map_type);
}

int register_py_binary_map_type(PyObject* mod) {
    auto res = PyModule_AddObject(mod, PY_BINARY_MAP_CLASS_NAME, reinterpret_cast<PyObject *>(&py_binary_map_type));
    if (res < 0) {
        Py_DECREF(reinterpret_cast<PyObject *>(&py_binary_map_type));
    }
    return res;
}

PyObject *make_py_binary_map(std::string full_table_name, std::int64_t table_id) {
    py_binary_map* py_obj = PyObject_New(py_binary_map, &py_binary_map_type);
    if (!py_obj)
        return nullptr;

    py_obj->m_data = new py_binary_map_data();
    py_obj->m_data->m_full_name = std::move(full_table_name);
    py_obj->m_data->m_table_id = table_id;

    return reinterpret_cast<PyObject *>(py_obj);
}
