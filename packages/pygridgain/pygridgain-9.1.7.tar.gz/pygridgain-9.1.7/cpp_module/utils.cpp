/*
 * Copyright (C) GridGain Systems. All Rights Reserved.
 *  _________        _____ __________________        _____
 *  __  ____/___________(_)______  /__  ____/______ ____(_)_______
 *  _  / __  __  ___/__  / _  __  / _  / __  _  __ `/__  / __  __ \
 *  / /_/ /  _  /    _  /  / /_/ /  / /_/ /  / /_/ / _  /  _  / / /
 *  \____/   /_/     /_/   \_,__/   \____/   \__,_/  /_/   /_/ /_/
 */

#include "utils.h"
#include "py_errors.h"
#include "ignite/protocol/messages.h"
#include "ignite/protocol/reader.h"

using namespace ignite;

bytes_view get_py_binary_data(PyObject* py_data) {
    auto is_bytes = PyBytes_Check(py_data);
    if (is_bytes) {
        auto *data = reinterpret_cast<std::byte*>(PyBytes_AsString(py_data));
        auto len = PyBytes_Size(py_data);
        return {data, std::size_t(len)};
    }

    auto is_bytearray = PyByteArray_Check(py_data);
    if (is_bytearray) {
        auto *data = reinterpret_cast<std::byte*>(PyByteArray_AsString(py_data));
        auto len = PyByteArray_Size(py_data);
        return {data, std::size_t(len)};
    }

    py_set_ignite_error("Expected bytes or bytearray as an argument");
    return {};
}
