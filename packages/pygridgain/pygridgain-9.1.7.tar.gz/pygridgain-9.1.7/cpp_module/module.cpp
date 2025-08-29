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
#include "py_binary_map.h"
#include "py_classes.h"
#include "py_errors.h"
#include "py_sql_result_set.h"
#include "py_sql_result_set_row.h"
#include "py_string.h"

#include "ignite/protocol/client_operation.h"
#include "ignite/protocol/protocol_context.h"
#include "ignite/protocol/writer.h"
#include "ignite/protocol/reader.h"
#include "ignite/protocol/messages.h"

#include "ignite/common/detail/string_utils.h"
#include "ignite/common/detail/name_utils.h"

#include <Python.h>


namespace {

using namespace ignite;

std::optional<std::int64_t> int64_from_py_object(PyObject* obj) {
    auto is_int = PyLong_Check(obj);
    if (!is_int) {
        py_set_ignite_error("The Object is not an int");
        return std::nullopt;
    }

    auto val = PyLong_AsLongLong(obj);
    if (PyErr_Occurred()) {
        return std::nullopt;
    }

    return val;
}

std::optional<protocol::protocol_version> version_from_py_tuple(PyObject *tuple) {
    auto is_tuple = PyTuple_Check(tuple);
    if (!is_tuple) {
        py_set_ignite_error("The version is not a tuple. Expected a version in a tuple format: (int, int, int)");
        return std::nullopt;
    }

    auto size = PyTuple_GET_SIZE(tuple);
    if (size != 3) {
        py_set_ignite_error("Unexpected version tuple size: " + std::to_string(size) +
            "Expected a version in a tuple format: (int, int, int)");
        return std::nullopt;
    }

    auto major = int64_from_py_object(PyTuple_GET_ITEM(tuple, 0));
    if (!major.has_value()) {
        return std::nullopt;
    }
    if (*major < 0 || *major > std::numeric_limits<std::int16_t>::max()) {
        py_set_ignite_error("Unexpected value for the major protocol version: " + std::to_string(*major));
        return std::nullopt;
    }
    auto major_i16 = std::int16_t(*major);

    auto minor = int64_from_py_object(PyTuple_GET_ITEM(tuple, 1));
    if (!minor.has_value()) {
        return std::nullopt;
    }
    if (*minor < 0 || *minor > std::numeric_limits<std::int16_t>::max()) {
        py_set_ignite_error("Unexpected value for the minor protocol version: " + std::to_string(*minor));
        return std::nullopt;
    }
    auto minor_i16 = std::int16_t(*minor);

    auto maintenance = int64_from_py_object(PyTuple_GET_ITEM(tuple, 2));
    if (!maintenance.has_value()) {
        return std::nullopt;
    }
    if (*maintenance < 0 || *maintenance > std::numeric_limits<std::int16_t>::max()) {
        py_set_ignite_error("Unexpected value for the maintenance protocol version: " + std::to_string(*maintenance));
        return std::nullopt;
    }
    auto maintenance_i16 = std::int16_t(*maintenance);

    return protocol::protocol_version{major_i16, minor_i16, maintenance_i16};
}

py_object version_to_py_tuple(const protocol::protocol_version &version) {
    py_object tuple{PyTuple_New(3)};
    if (!tuple) {
        return tuple;
    }

    PyTuple_SET_ITEM(tuple.get(), 0, PyLong_FromLong(version.get_major()));
    PyTuple_SET_ITEM(tuple.get(), 1, PyLong_FromLong(version.get_minor()));
    PyTuple_SET_ITEM(tuple.get(), 2, PyLong_FromLong(version.get_patch()));

    return tuple;
}

std::optional<std::map<std::string, std::string>> map_from_py_dict(PyObject *extra) {
    auto is_dict = PyDict_Check(extra);
    if (!is_dict) {
        py_set_ignite_error("Dictionary is expected in format: {str, str}");
        return std::nullopt;
    }

    PyObject *key, *value;
    Py_ssize_t pos = 0;

    std::map<std::string, std::string> res;
    while (PyDict_Next(extra, &pos, &key, &value)) {
        if (!PyUnicode_Check(key)) {
            py_set_ignite_error("Expected a dictionary of strings: {str, str}");
            return std::nullopt;
        }

        auto key_str = py_string::try_from_py_utf8(key);
        if (!key_str) {
            py_set_ignite_error("Can not convert dictionary key to UTF-8");
            return std::nullopt;
        }

        auto value_str = py_string::try_from_py_utf8(value);
        if (!value_str) {
            py_set_ignite_error("Can not convert dictionary value to UTF-8");
            return std::nullopt;
        }

        res.emplace(std::make_pair(key_str.get_data(), value_str.get_data()));
    }

    return res;
}

PyObject* pygridgain_make_handshake(PyObject*, PyObject* args, PyObject*) {
    static constexpr std::int8_t CLIENT_CODE = 5;

    PyObject *version_arg = nullptr;
    PyObject *extra_arg = nullptr;

    int parsed = PyArg_ParseTuple(args, "OO", &version_arg, &extra_arg);
    if (!parsed)
        return nullptr;

    auto version = version_from_py_tuple(version_arg);
    if (!version) {
        return nullptr;
    }

    auto extra = map_from_py_dict(extra_arg);
    if (!extra) {
        return nullptr;
    }

    std::vector<std::byte> message = protocol::make_handshake_request(CLIENT_CODE, *version, *extra);
    // TODO: GG-44605 Eliminate unnecessary memory allocations
    return PyBytes_FromStringAndSize(reinterpret_cast<const char *>(message.data()), message.size());
}

PyObject* make_py_handshake_response(const protocol::handshake_response &rsp) {
    auto handshake_response_class = py_get_handshake_response_class();
    if (!handshake_response_class)
        return nullptr;

    py_object args{PyTuple_New(4)};
    if (!args)
        return nullptr;

    auto version_tuple = version_to_py_tuple(rsp.context.get_version());
    if (!version_tuple)
        return nullptr;

    py_object py_err;
    if (rsp.error) {
        py_err = py_get_ignite_error(*rsp.error);
    }

    PyTuple_SET_ITEM(args.get(), 0, version_tuple.release());
    PyTuple_SET_ITEM(args.get(), 1, py_err ? py_err.release() : Py_None);
    PyTuple_SET_ITEM(args.get(), 2, PyLong_FromLongLong(rsp.observable_timestamp));
    PyTuple_SET_ITEM(args.get(), 3, PyLong_FromLongLong(rsp.idle_timeout_ms));

    return PyObject_Call(handshake_response_class, args.get(), nullptr);
}

PyObject* pygridgain_parse_handshake(PyObject*, PyObject* message_arg) {
    auto message = get_py_binary_data(message_arg);
    if (message.empty())
        return nullptr;

    try {
        auto response = protocol::parse_handshake_response(message);
        return make_py_handshake_response(response);
    } catch (ignite_error &err) {
        py_set_ignite_error(err);
        return nullptr;
    }
}

PyObject* pygridgain_make_map_request(PyObject*, PyObject* args, PyObject*) {
    long long req_id = 0;
    const char *name = nullptr;

    int parsed = PyArg_ParseTuple(args, "Ls", &req_id, &name);
    if (!parsed)
        return nullptr;

    auto wr = [name] (protocol::writer& writer) {
        writer.write(name);
        writer.write_nil();
        writer.write_nil();
        writer.write_nil();
        writer.write_nil();

        return true;
    };

    auto req = pack_request(protocol::client_operation::MAP_GET_OR_CREATE, req_id, wr);

    // TODO: GG-44605 Eliminate unnecessary memory allocations
    return PyBytes_FromStringAndSize(reinterpret_cast<const char *>(req.data()), req.size());
}

PyObject* pygridgain_parse_create_map_response(PyObject*, PyObject* data) {
    auto message = get_py_binary_data(data);
    if (message.empty())
        return nullptr;

    try {
        protocol::reader reader(message);

        auto schema_name = reader.read_string();
        auto table_name = reader.read_string();
        auto table_id = reader.read_int64();

        auto full_name = detail::to_canonical_name(schema_name, table_name,
        detail::name_utils_constant::QUOTE_CHAR, detail::name_utils_constant::SEPARATOR_CHAR);

        return make_py_binary_map(std::move(full_name), table_id);
    } catch (ignite_error &err) {
        py_set_ignite_error(err);
        return nullptr;
    }
}

PyObject* pygridgain_read_req_id(PyObject*, PyObject* data) {
    auto message = get_py_binary_data(data);
    if (message.empty())
        return nullptr;

    try {
        protocol::reader reader(message);
        auto req_id = reader.read_int64();

        return PyLong_FromLongLong(req_id);
    } catch (ignite_error &err) {
        py_set_ignite_error(err);
        return nullptr;
    }
}

PyObject* pygridgain_read_response_header(PyObject*, PyObject* data) {
    auto resp = get_py_binary_data(data);
    if (resp.empty())
        return nullptr;

    protocol::reader reader(resp);

    auto req_id = reader.read_int64();
    std::optional<std::int64_t> assignment_ts{};

    auto flags = reader.read_int32();
    if (test_flag(flags, protocol::response_flag::PARTITION_ASSIGNMENT_CHANGED)) {
        assignment_ts = reader.read_int64();
    }

    auto observable_ts = reader.read_int64();
    py_object py_err;
    if (test_flag(flags, protocol::response_flag::ERROR_FLAG)) {
        auto err = read_error(reader);
        py_err = py_get_ignite_error(err);
        if (!py_err)
            return nullptr;
    }

    auto rsp_header_class = py_get_response_header_class();
    if (!rsp_header_class)
        return nullptr;

    py_object args{PyTuple_New(5)};
    if (!args)
        return nullptr;

    PyTuple_SET_ITEM(args.get(), 0, PyLong_FromLongLong(req_id));
    PyTuple_SET_ITEM(args.get(), 1, assignment_ts ? PyLong_FromLongLong(*assignment_ts) : Py_None);
    PyTuple_SET_ITEM(args.get(), 2, PyLong_FromLongLong(observable_ts));
    PyTuple_SET_ITEM(args.get(), 3, py_err ? py_err.release() : Py_None);
    PyTuple_SET_ITEM(args.get(), 4, PyLong_FromSize_t(reader.position()));

    return PyObject_Call(rsp_header_class, args.get(), nullptr);
}

PyObject* pygridgain_make_sql_request(PyObject*, PyObject* args, PyObject*) {
    long long req_id = 0;
    long long observable_ts = 0;
    const char *query = nullptr;

    int parsed = PyArg_ParseTuple(args, "LLs", &req_id, &observable_ts, &query);
    if (!parsed)
        return nullptr;

    auto wr = [query, observable_ts] (protocol::writer& writer) {
        writer.write_nil();

        // These values are not important for the current implementation
        // as we're only using SQL API for some Map operations
        writer.write("PUBLIC"); // Schema
        writer.write(1024); // Page size
        writer.write(0); // Timeout in ms
        writer.write_nil(); // Session timeout (unused, session is closed by the server immediately).
        writer.write_nil(); // Timezone
        writer.write(0); // Properties
        writer.write_binary_empty(); // Properties

        writer.write(query);

        writer.write_nil(); // args
        writer.write(std::int64_t(observable_ts));

        return true;
    };

    auto req = pack_request(protocol::client_operation::SQL_EXEC, req_id, wr);

    // TODO: GG-44605 Eliminate unnecessary memory allocations
    return PyBytes_FromStringAndSize(reinterpret_cast<const char *>(req.data()), req.size());
}

PyObject* pygridgain_parse_sql_response(PyObject*, PyObject* data) {
    auto message = get_py_binary_data(data);
    if (message.empty())
        return nullptr;

    try {
        protocol::reader reader(message);

        return make_py_sql_result_set(reader);
    } catch (ignite_error &err) {
        py_set_ignite_error(err);
        return nullptr;
    }
}

PyObject* pygridgain_make_heartbeat_request(PyObject*, PyObject* req_id_arg) {
    if (!PyLong_Check(req_id_arg)) {
        py_set_ignite_error("Request ID must be a long");
        return nullptr;
    }
    auto req_id = PyLong_AsLongLong(req_id_arg);

    auto wr = [] (auto&) { return true; };
    auto req = pack_request(protocol::client_operation::HEARTBEAT, req_id, wr);

    // TODO: GG-44605 Eliminate unnecessary memory allocations
    return PyBytes_FromStringAndSize(reinterpret_cast<const char *>(req.data()), req.size());
}

PyMethodDef methods[] = {
    {"make_handshake", PyCFunction(pygridgain_make_handshake), METH_VARARGS, nullptr},
    {"parse_handshake", PyCFunction(pygridgain_parse_handshake), METH_O, nullptr},
    {"make_map_request", PyCFunction(pygridgain_make_map_request), METH_VARARGS, nullptr},
    {"parse_create_map_response", PyCFunction(pygridgain_parse_create_map_response), METH_O, nullptr},
    {"read_response_header", PyCFunction(pygridgain_read_response_header), METH_O, nullptr},
    {"make_sql_request", PyCFunction(pygridgain_make_sql_request), METH_VARARGS, nullptr},
    {"parse_sql_response", PyCFunction(pygridgain_parse_sql_response), METH_O, nullptr},
    {"make_heartbeat_request", PyCFunction(pygridgain_make_heartbeat_request), METH_O, nullptr},
    {nullptr, nullptr, 0, nullptr}       /* Sentinel */
};

PyModuleDef module_def = {
    PyModuleDef_HEAD_INIT,
    EXT_MODULE_NAME,
    nullptr,                /* m_doc */
    -1,                     /* m_size */
    methods,                /* m_methods */
    nullptr,                /* m_slots */
    nullptr,                /* m_traverse */
    nullptr,                /* m_clear */
    nullptr,                /* m_free */
};

} // anonymous namespace

PyMODINIT_FUNC PyInit__native_extension(void) { // NOLINT(*-reserved-identifier)
    PyObject *mod = PyModule_Create(&module_def);
    if (mod == nullptr)
        return nullptr;

    prepare_py_binary_map_type();
    prepare_py_sql_result_set_type();
    prepare_py_sql_result_set_row_type();

    register_py_binary_map_type(mod);
    register_py_sql_result_set_type(mod);
    register_py_sql_result_set_row_type(mod);

    return mod;
}